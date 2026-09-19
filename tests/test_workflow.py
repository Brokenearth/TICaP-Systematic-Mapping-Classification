import csv
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from scripts.pipeline_steps import (
    annotate_doubtful_recommendations,
    apply_completed_excel_abstracts,
    build_prisma_counts,
    generate_excel,
    publish_ticapall,
    run_import,
    run_normalization,
)


class WorkflowTests(unittest.TestCase):
    def test_import_and_normalization_preserve_count_and_stable_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "data" / "raw"
            raw.mkdir(parents=True)
            (raw / "mendeley_original.bib").write_text(
                """@article{A2024, title={Fish IoT}, author={A One}, year={2024},
                doi={https://doi.org/10.1/ABC}}
                @inproceedings{B2025, title={Smart pond}, author={B Two}, year={2025}}""",
                encoding="utf-8",
            )

            imported = run_import(root)
            normalized = run_normalization(root)

            self.assertEqual([item["id"] for item in imported], ["TICAP-0001", "TICAP-0002"])
            self.assertEqual(len(normalized), 2)
            self.assertEqual(normalized[0]["doi_normalized"], "10.1/abc")

    def test_prisma_counts_use_uniform_decisions(self) -> None:
        rows = [
            {"Decisión": "INCLUIR", "Observación": ""},
            {"Decisión": "EXCLUIR", "Observación": ""},
            {"Decisión": "DUPLICADO", "Observación": ""},
            {"Decisión": "DUDOSO", "Observación": "Abstract no encontrado."},
        ]

        counts = build_prisma_counts(rows, existing_abstracts=1, recovered_abstracts=1)

        self.assertEqual(counts["registros_iniciales"], 4)
        self.assertEqual(counts["duplicados"], 1)
        self.assertEqual(counts["incluidos"], 1)
        self.assertEqual(counts["abstracts_no_encontrados"], 1)

    def test_prisma_uses_provenance_count_for_missing_abstracts(self) -> None:
        rows = [{"Decisión": "DUPLICADO", "Observación": ""}]

        counts = build_prisma_counts(
            rows,
            existing_abstracts=0,
            recovered_abstracts=0,
            missing_abstracts=1,
        )

        self.assertEqual(counts["abstracts_no_encontrados"], 1)

    def test_excel_has_exact_official_columns_and_decision_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "final.xlsx"
            rows = [
                {
                    "ID": "TICAP-0001",
                    "Título": "Fish IoT",
                    "Abstract": "Validated system.",
                    "Decisión": "INCLUIR",
                    "Criterio aplicado": "CUMPLE_MATRIZ",
                    "Justificación breve": "Evidence in abstract.",
                    "Tecnología identificada": "IoT",
                    "Aplicación acuícola/piscícola": "Monitoreo",
                    "Categoría temática": "Monitoreo ambiental",
                    "Observación": "",
                }
            ]

            generate_excel(rows, output)
            workbook = load_workbook(output)
            sheet = workbook["Clasificación"]

            self.assertEqual(
                [cell.value for cell in sheet[1]],
                [
                    "ID",
                    "Título",
                    "Abstract",
                    "Decisión",
                    "Criterio aplicado",
                    "Justificación breve",
                    "Tecnología identificada",
                    "Aplicación acuícola/piscícola",
                    "Categoría temática",
                    "Observación",
                ],
            )
            self.assertEqual(len(sheet.data_validations.dataValidation), 1)

    def test_completed_excel_fills_missing_abstracts_and_keeps_existing(self) -> None:
        records = [
            {"id": "TICAP-0001", "abstract": "Existing abstract about tilapia IoT."},
            {"id": "TICAP-0002"},
            {"id": "TICAP-0003"},
        ]
        excel_rows = {
            "TICAP-0001": {"Abstract": "Should not overwrite"},
            "TICAP-0002": {"Abstract": "A recovered abstract for water quality sensors in fish ponds."},
            "TICAP-0003": {"Abstract": "Libro"},
        }

        updated, changed = apply_completed_excel_abstracts(records, excel_rows)

        self.assertEqual(changed, ["TICAP-0002", "TICAP-0003"])
        self.assertEqual(updated[0]["abstract"], "Existing abstract about tilapia IoT.")
        self.assertEqual(
            updated[1]["abstract"],
            "A recovered abstract for water quality sensors in fish ponds.",
        )
        self.assertEqual(updated[2].get("screening_note"), "Libro")
        self.assertNotIn("abstract", updated[2])
        self.assertEqual(updated[2]["abstract_status"], "NOTA_DESCARTE")

    def test_publish_ticapall_keeps_original_bib_and_writes_master(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "TICaP-509"
            dest = Path(directory) / "TICaPALL"
            (source / "data" / "master").mkdir(parents=True)
            (source / "output" / "excel").mkdir(parents=True)
            (source / "data" / "master" / "TICaP_master.bib").write_text("@article{A,}\n", encoding="utf-8")
            (source / "output" / "excel" / "TICaP_clasificacion_titulo_abstract.xlsx").write_bytes(b"xlsx")
            dest.mkdir()
            (dest / "TICaP-509All.bib").write_text("@article{ORIGINAL,}\n", encoding="utf-8")

            published = publish_ticapall(source, dest)

            self.assertEqual(published, dest)
            self.assertEqual((dest / "TICaP-509All.bib").read_text(encoding="utf-8"), "@article{ORIGINAL,}\n")
            self.assertEqual((dest / "masterall509.bib").read_text(encoding="utf-8"), "@article{A,}\n")
            self.assertTrue((dest / "output" / "excel" / "TICaP_clasificacion_titulo_abstract.xlsx").exists())

    def test_annotates_doubtful_recommendations_in_completed_excel(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "completo.xlsx"
            generate_excel(
                [
                    {
                        "ID": "TICAP-0229",
                        "Título": "UAV transparency",
                        "Abstract": "Prototype.",
                        "Decisión": "DUDOSO",
                        "Criterio aplicado": "CE4",
                        "Justificación breve": "Revisión.",
                        "Tecnología identificada": "Sensores",
                        "Aplicación acuícola/piscícola": "",
                        "Categoría temática": "",
                        "Observación": "",
                    },
                    {
                        "ID": "TICAP-0051",
                        "Título": "Cyclone",
                        "Abstract": "GIS study.",
                        "Decisión": "DUDOSO",
                        "Criterio aplicado": "CE5",
                        "Justificación breve": "Revisión.",
                        "Tecnología identificada": "",
                        "Aplicación acuícola/piscícola": "",
                        "Categoría temática": "",
                        "Observación": "",
                    },
                    {
                        "ID": "TICAP-0254",
                        "Título": "AquiAID tesis",
                        "Abstract": "Resumen largo.",
                        "Decisión": "DUDOSO",
                        "Criterio aplicado": "CE4",
                        "Justificación breve": "Revisión.",
                        "Tecnología identificada": "",
                        "Aplicación acuícola/piscícola": "",
                        "Categoría temática": "",
                        "Observación": "",
                    },
                    {
                        "ID": "TICAP-0408",
                        "Título": "IoT and AI based system for fish farming",
                        "Abstract": "Prototype in Benin.",
                        "Decisión": "INCLUIR",
                        "Criterio aplicado": "REVISION_MANUAL",
                        "Justificación breve": "El título por sí solo no aporta evidencia suficiente para una decisión definitiva.",
                        "Tecnología identificada": "",
                        "Aplicación acuícola/piscícola": "",
                        "Categoría temática": "",
                        "Observación": "Abstract no encontrado.",
                    },
                ],
                output,
            )

            counts = annotate_doubtful_recommendations(
                output,
                [
                    {
                        "ID": "TICAP-0408",
                        "Decisión": "INCLUIR",
                        "Criterio aplicado": "CUMPLE_MATRIZ",
                        "Justificación breve": "El título y abstract evidencian contexto piscícola.",
                        "Tecnología identificada": "IoT",
                        "Aplicación acuícola/piscícola": "Monitoreo de calidad del agua o ambiente",
                        "Categoría temática": "Monitoreo",
                        "Observación": "",
                    }
                ],
            )
            workbook = load_workbook(output)
            sheet = workbook["Clasificación"]

            self.assertEqual(counts["incluir"], 1)
            self.assertEqual(counts["excluir"], 1)
            self.assertEqual(counts["duplicado"], 1)
            self.assertEqual(sheet["D2"].value, "Dudoso (incluir)")
            self.assertEqual(sheet["D3"].value, "Dudoso (excluir)")
            self.assertEqual(sheet["D4"].value, "DUPLICADO")
            self.assertIn("transparencia", str(sheet["J2"].value).casefold())
            self.assertIn("ciclones", str(sheet["J3"].value).casefold())
            self.assertIn("0172", str(sheet["J4"].value))
            self.assertNotIn("Abstract no encontrado", str(sheet["J5"].value))
            self.assertIn("Benín", str(sheet["J5"].value))
            self.assertEqual(sheet["D5"].value, "INCLUIR")
            self.assertEqual(sheet["E5"].value, "CUMPLE_MATRIZ")

    def test_screening_reasons_cover_reviewed_ids(self) -> None:
        from scripts.pipeline_lib import (
            DOUBTFUL_EXCLUDE_IDS,
            DOUBTFUL_INCLUDE_IDS,
            MANUAL_DUPLICATE_OF,
        )
        from scripts.screening_reasons import SCREENING_REASONS, is_stale_screening_text

        missing = (DOUBTFUL_INCLUDE_IDS | DOUBTFUL_EXCLUDE_IDS | set(MANUAL_DUPLICATE_OF)) - set(
            SCREENING_REASONS
        )
        self.assertFalse(missing, f"Faltan razones para {sorted(missing)}")
        self.assertTrue(is_stale_screening_text("Abstract no encontrado."))
        self.assertFalse(is_stale_screening_text("Sistema IoT validado en estanques."))


if __name__ == "__main__":
    unittest.main()

