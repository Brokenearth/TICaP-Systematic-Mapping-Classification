import unittest

from scripts.pipeline_lib import (
    classify_record,
    confirm_unresolved_duplicates,
    apply_manual_duplicate_pairs,
    detect_duplicate_groups,
    normalize_doi,
    normalize_title,
    parse_bibtex,
    validate_abstract_candidate,
)


class BibtexParsingTests(unittest.TestCase):
    def test_parses_braced_fields_without_losing_nested_content(self) -> None:
        text = """@article{Clave2024,
          title = {IoT for {Nile tilapia} farming},
          abstract = {A sensor {network} was validated in ponds.},
          author = {Ana Pérez and Bob Smith},
          doi = {https://doi.org/10.1000/ABC},
          year = {2024}
        }"""

        records = parse_bibtex(text)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["citation_key"], "Clave2024")
        self.assertEqual(records[0]["title"], "IoT for {Nile tilapia} farming")
        self.assertEqual(records[0]["abstract"], "A sensor {network} was validated in ponds.")

    def test_parses_fields_when_abstract_has_enumeration_parentheses(self) -> None:
        text = """@article{Gmez2023,
          abstract = {Se aplicó una metodología en tres fases: i) pregunta; ii) búsqueda; y ii) revisión. Se usó Web of Science (WOS).},
          author = {Jhordani Guélac Gómez},
          doi = {10.29019/ENFOQUEUTE.894},
          title = {Impacto del uso de herramientas tecnológicas en la producción acuícola},
          year = {2023}
        }"""

        records = parse_bibtex(text)

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["title"],
            "Impacto del uso de herramientas tecnológicas en la producción acuícola",
        )
        self.assertEqual(records[0]["year"], "2023")
        self.assertEqual(records[0]["author"], "Jhordani Guélac Gómez")
        self.assertNotIn("title =", records[0]["abstract"])


class NormalizationTests(unittest.TestCase):
    def test_normalizes_doi_and_title_for_comparison(self) -> None:
        self.assertEqual(normalize_doi(" https://DOI.org/10.1000/ABC. "), "10.1000/abc")
        self.assertEqual(
            normalize_title("{IoT}-Based Fish–Farm Monitoring!"),
            "iot based fish farm monitoring",
        )


class DuplicateTests(unittest.TestCase):
    def test_groups_records_with_the_same_doi_without_deleting_them(self) -> None:
        records = [
            {
                "id": "TICAP-0001",
                "doi_normalized": "10.1/example",
                "title_normalized": "one",
                "year_normalized": "2024",
                "authors_normalized": "a",
            },
            {
                "id": "TICAP-0002",
                "doi_normalized": "10.1/example",
                "title_normalized": "another",
                "year_normalized": "2024",
                "authors_normalized": "b",
            },
        ]

        groups = detect_duplicate_groups(records)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["method"], "DOI_IDENTICO")
        self.assertEqual(groups[0]["member_ids"], ["TICAP-0001", "TICAP-0002"])


class AbstractQualityTests(unittest.TestCase):
    def test_rejects_candidate_when_doi_conflicts(self) -> None:
        record = {
            "title": "IoT fish farm monitoring",
            "doi_normalized": "10.1/correct",
            "year_normalized": "2024",
            "authors_normalized": "ana perez",
        }
        candidate = {
            "abstract": "A complete abstract about IoT fish farm monitoring and sensors.",
            "title": "IoT fish farm monitoring",
            "doi": "10.1/wrong",
            "year": "2024",
            "authors": "Ana Perez",
        }

        status, _reason = validate_abstract_candidate(record, candidate)

        self.assertEqual(status, "POSIBLE_ERROR_DE_COINCIDENCIA")


class ClassificationTests(unittest.TestCase):
    def test_assigns_administrative_period_decision_first(self) -> None:
        result = classify_record(
            {
                "id": "TICAP-0001",
                "title": "IoT fish farm",
                "abstract": "A validated sensor system for fish ponds.",
                "year_normalized": "2019",
                "type_normalized": "article",
            }
        )

        self.assertEqual(result["decision"], "FUERA_DE_PERIODO")
        self.assertEqual(result["criterion"], "ADM_PERIODO")

    def test_includes_clear_primary_technology_application(self) -> None:
        result = classify_record(
            {
                "id": "TICAP-0002",
                "title": "IoT based fish farming management",
                "abstract": (
                    "We developed and validated an IoT sensor prototype for real-time "
                    "water quality monitoring and feeding decisions in tilapia ponds."
                ),
                "year_normalized": "2025",
                "type_normalized": "inproceedings",
            }
        )

        self.assertEqual(result["decision"], "INCLUIR")
        self.assertIn("IoT", result["technology"])
        self.assertEqual(result["category"], "Monitoreo ambiental")

    def test_marks_missing_abstract_as_doubtful_not_excluded(self) -> None:
        result = classify_record(
            {
                "id": "TICAP-0003",
                "title": "IoT based fish farming management",
                "abstract": "",
                "year_normalized": "2025",
                "type_normalized": "inproceedings",
            }
        )

        self.assertEqual(result["decision"], "DUDOSO")
        self.assertEqual(result["observation"], "Abstract no encontrado.")

    def test_excludes_biological_study_without_ict(self) -> None:
        result = classify_record(
            {
                "id": "TICAP-0004",
                "title": "Dietary protein and growth in farmed tilapia",
                "abstract": (
                    "This feeding trial measured growth, physiology and nutrition "
                    "of cultured tilapia under three diets."
                ),
                "year_normalized": "2023",
                "type_normalized": "article",
            }
        )

        self.assertEqual(result["decision"], "EXCLUIR")
        self.assertEqual(result["criterion"], "CE3")

    def test_treats_manual_duplicate_note_as_duplicate(self) -> None:
        result = classify_record(
            {
                "id": "TICAP-0410",
                "title": "IoT based smart fish farming aquaculture monitoring system",
                "abstract": "Duplicado",
                "year_normalized": "2021",
                "type_normalized": "article",
            }
        )

        self.assertEqual(result["decision"], "DUPLICADO")
        self.assertEqual(result["criterion"], "ADM_DUPLICADO")

    def test_treats_book_note_as_non_admitted_type(self) -> None:
        result = classify_record(
            {
                "id": "TICAP-0463",
                "title": "Chapter-11 Fish Farming: IoT-Based Smart Monitoring System",
                "screening_note": "Libro",
                "year_normalized": "2022",
                "type_normalized": "article",
            }
        )

        self.assertEqual(result["decision"], "TIPO_NO_ADMITIDO")
        self.assertEqual(result["criterion"], "ADM_TIPO")

    def test_excludes_unavailable_source_note(self) -> None:
        result = classify_record(
            {
                "id": "TICAP-0470",
                "title": "IOT-BASED WATER QUALITY MEASUREMENT SYSTEM FOR FISH FARMING",
                "abstract": "Pagina caida",
                "year_normalized": "2020",
                "type_normalized": "article",
            }
        )

        self.assertEqual(result["decision"], "EXCLUIR")
        self.assertEqual(result["criterion"], "CE9")

    def test_confirms_review_duplicate_when_only_one_has_abstract(self) -> None:
        records = [
            {
                "id": "TICAP-0440",
                "duplicate_group": "DUP-0017",
                "duplicate_review": True,
                "title": "Automatic fish feeders",
            },
            {
                "id": "TICAP-0475",
                "duplicate_group": "DUP-0017",
                "duplicate_review": True,
                "abstract": "An IoT automatic fish feeding system was developed with Arduino.",
                "title": "Automatic fish feeders, J. Komput",
            },
        ]

        confirmed = confirm_unresolved_duplicates(records)

        self.assertEqual(confirmed, ["TICAP-0440"])
        self.assertEqual(records[0]["duplicate_of"], "TICAP-0475")
        self.assertNotIn("duplicate_of", records[1])

    def test_marks_spanish_aqui_aid_version_as_duplicate_of_journal_article(self) -> None:
        records = [
            {"id": "TICAP-0172", "title": "Parallelisation of decision-making techniques"},
            {
                "id": "TICAP-0254",
                "title": "Paralelización de técnicas de toma de decisiones",
                "abstract": "Resumen largo de la tesis.",
            },
        ]

        confirmed = apply_manual_duplicate_pairs(records)

        self.assertEqual(confirmed, ["TICAP-0254"])
        self.assertEqual(records[1]["duplicate_of"], "TICAP-0172")
        self.assertEqual(records[1]["abstract"], "Resumen largo de la tesis.")


if __name__ == "__main__":
    unittest.main()

