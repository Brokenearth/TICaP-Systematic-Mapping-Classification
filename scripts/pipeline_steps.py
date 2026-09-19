from __future__ import annotations

import csv
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from scripts.pipeline_lib import (
    ACCEPTED_TYPES,
    DECISIONS,
    OFFICIAL_COLUMNS,
    classify_record,
    detect_duplicate_groups,
    interpret_screening_note,
    confirm_unresolved_duplicates,
    apply_manual_duplicate_pairs,
    DOUBTFUL_EXCLUDE_IDS,
    DOUBTFUL_INCLUDE_IDS,
    MANUAL_DUPLICATE_OF,
    normalize_record,
    parse_bibtex,
    read_jsonl,
    retrieve_abstract_candidate,
    sha256_file,
    utc_now,
    validate_abstract_candidate,
    write_csv,
    write_jsonl,
    write_master_bib,
)
from scripts.screening_reasons import SCREENING_REASONS, is_stale_screening_text


def _paths(root: Path) -> dict[str, Path]:
    return {
        "raw": root / "data" / "raw" / "mendeley_original.bib",
        "imported": root / "data" / "interim" / "registros_importados.jsonl",
        "normalized": root / "data" / "interim" / "registros_normalizados.jsonl",
        "deduplicated": root / "data" / "interim" / "registros_con_duplicados.jsonl",
        "abstracts": root / "data" / "interim" / "registros_con_abstracts.jsonl",
        "master": root / "data" / "master" / "TICaP_master.bib",
        "base": root / "data" / "interim" / "base_clasificacion.csv",
        "classification": root / "output" / "clasificacion" / "clasificacion_preliminar.csv",
        "excel": root / "output" / "excel" / "TICaP_clasificacion_titulo_abstract.xlsx",
        "completed_excel_dir": root / "output" / "excel completo",
        "activity": root / "logs" / "registro_actividades.csv",
        "provenance": root / "output" / "abstracts" / "procedencia_abstracts.csv",
    }


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeError(f"No se pudo determinar la codificación de {path}")


def _log(
    root: Path,
    phase: str,
    activity: str,
    input_path: Path | str,
    output_path: Path | str,
    processed: int,
    modified: int,
    errors: int = 0,
    observations: str = "",
) -> None:
    path = _paths(root)["activity"]
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "fecha",
        "fase",
        "actividad",
        "archivo_entrada",
        "archivo_salida",
        "registros_procesados",
        "registros_modificados",
        "errores",
        "observaciones",
    ]
    exists = path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "fase": phase,
                "actividad": activity,
                "archivo_entrada": str(input_path),
                "archivo_salida": str(output_path),
                "registros_procesados": processed,
                "registros_modificados": modified,
                "errores": errors,
                "observaciones": observations,
            }
        )


def run_import(root: Path) -> list[dict[str, object]]:
    paths = _paths(root)
    records = parse_bibtex(_read_text(paths["raw"]))
    if not records:
        raise ValueError("El BibTeX no contiene registros reconocibles.")
    imported: list[dict[str, object]] = []
    id_rows: list[dict[str, object]] = []
    seen_keys: Counter[str] = Counter()
    for index, record in enumerate(records, start=1):
        identifier = f"TICAP-{index:04d}"
        item: dict[str, object] = dict(record)
        item["id"] = identifier
        item["source_index"] = index
        imported.append(item)
        citation_key = str(item.get("citation_key", ""))
        seen_keys[citation_key] += 1
        id_rows.append(
            {
                "ID": identifier,
                "orden_origen": index,
                "clave_bibtex": citation_key,
                "clave_repetida": "SI" if seen_keys[citation_key] > 1 else "NO",
            }
        )
    write_jsonl(paths["imported"], imported)
    write_csv(
        root / "data" / "interim" / "id_map.csv",
        id_rows,
        ("ID", "orden_origen", "clave_bibtex", "clave_repetida"),
    )
    write_csv(
        root / "output" / "reportes" / "informe_importacion.csv",
        [
            {"metrica": "registros_parseados", "valor": len(imported)},
            {"metrica": "claves_bibtex_repetidas", "valor": sum(count - 1 for count in seen_keys.values() if count > 1)},
            {"metrica": "sha256_original", "valor": sha256_file(paths["raw"])},
        ],
        ("metrica", "valor"),
    )
    _log(
        root,
        "Fase 1",
        "Importación y asignación de IDs",
        paths["raw"],
        paths["imported"],
        len(imported),
        len(imported),
    )
    return imported


def run_normalization(root: Path) -> list[dict[str, object]]:
    paths = _paths(root)
    imported = read_jsonl(paths["imported"])
    normalized = [normalize_record(record) for record in imported]
    write_jsonl(paths["normalized"], normalized)
    changes: list[dict[str, object]] = []
    for record in normalized:
        for field in ("doi", "title", "authors", "year", "type"):
            original_key = f"{field}_original"
            normalized_key = f"{field}_normalized"
            if str(record.get(original_key, "")) != str(record.get(normalized_key, "")):
                changes.append(
                    {
                        "ID": record["id"],
                        "campo": field,
                        "valor_original": record.get(original_key, ""),
                        "valor_normalizado": record.get(normalized_key, ""),
                    }
                )
    write_csv(
        root / "output" / "reportes" / "cambios_normalizacion.csv",
        changes,
        ("ID", "campo", "valor_original", "valor_normalizado"),
    )
    _log(
        root,
        "Fase 2",
        "Normalización sin generación de metadatos",
        paths["imported"],
        paths["normalized"],
        len(normalized),
        len({str(row["ID"]) for row in changes}),
    )
    return normalized


def run_duplicates(root: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    paths = _paths(root)
    records = read_jsonl(paths["normalized"])
    groups = detect_duplicate_groups(records)
    records_by_id = {str(record["id"]): record for record in records}
    group_rows: list[dict[str, object]] = []
    manual_rows: list[dict[str, object]] = []
    for group in groups:
        members = [str(item) for item in group["member_ids"]]
        group_rows.append(
            {
                "grupo": group["group_id"],
                "método": group["method"],
                "estado": group["status"],
                "registro_principal": group["principal_id"],
                "miembros": "|".join(members),
            }
        )
        for member_id in members:
            record = records_by_id[member_id]
            record["duplicate_group"] = group["group_id"]
            if group["status"] == "CONFIRMADO" and member_id != group["principal_id"]:
                record["duplicate_of"] = group["principal_id"]
            elif group["status"] == "REQUIERE_REVISION":
                record["duplicate_review"] = True
                manual_rows.append(
                    {
                        "grupo": group["group_id"],
                        "ID": member_id,
                        "título": record.get("title", ""),
                        "año": record.get("year_normalized", ""),
                        "autores": record.get("author", ""),
                        "método": group["method"],
                        "decisión_manual": "",
                        "revisor": "",
                        "fecha": "",
                        "motivo": "",
                    }
                )
    write_jsonl(paths["deduplicated"], records)
    write_csv(
        root / "data" / "interim" / "grupos_duplicados.csv",
        group_rows,
        ("grupo", "método", "estado", "registro_principal", "miembros"),
    )
    write_csv(
        root / "data" / "manual" / "duplicados_por_revisar.csv",
        manual_rows,
        (
            "grupo",
            "ID",
            "título",
            "año",
            "autores",
            "método",
            "decisión_manual",
            "revisor",
            "fecha",
            "motivo",
        ),
    )
    confirmed_duplicates = sum(
        len(group["member_ids"]) - 1
        for group in groups
        if group["status"] == "CONFIRMADO"
    )
    _log(
        root,
        "Fase 3",
        "Detección de duplicados sin borrado",
        paths["normalized"],
        paths["deduplicated"],
        len(records),
        confirmed_duplicates,
        observations=f"{len(manual_rows)} candidatos requieren revisión.",
    )
    return records, groups


def _provenance_row(
    record: dict[str, object],
    source: str,
    source_url: str,
    status: str,
    reason: str,
    original_or_recovered: str,
    abstract_text: str,
) -> dict[str, object]:
    return {
        "ID": record["id"],
        "fuente": source,
        "URL_fuente": source_url,
        "fecha_consulta": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "origen": original_or_recovered,
        "estado": status,
        "motivo": reason,
        "abstract": abstract_text,
    }


def run_abstract_recovery(
    root: Path,
    allow_network: bool = True,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    paths = _paths(root)
    records = read_jsonl(paths["deduplicated"])
    provenance: list[dict[str, object]] = []
    network_errors: list[dict[str, object]] = []
    for index, record in enumerate(records, start=1):
        existing = str(record.get("abstract", "")).strip()
        if existing:
            candidate = {
                "abstract": existing,
                "title": record.get("title", ""),
                "doi": record.get("doi_normalized", ""),
                "year": record.get("year_normalized", ""),
                "authors": record.get("author", ""),
            }
            status, reason = validate_abstract_candidate(record, candidate)
            source = "BibTeX original (Mendeley)"
            source_url = ""
            origin = "EXISTENTE"
        elif record.get("duplicate_of"):
            status = "SIN_ABSTRACT"
            reason = "No se recupera de nuevo un registro duplicado confirmado."
            candidate = {"abstract": ""}
            source = ""
            source_url = ""
            origin = "NO_ENCONTRADO"
        elif allow_network:
            candidate, errors = retrieve_abstract_candidate(record)
            for error in errors:
                network_errors.append({"ID": record["id"], "error": error})
            if candidate:
                status, reason = validate_abstract_candidate(record, candidate)
                source = str(candidate.get("source", ""))
                source_url = str(candidate.get("source_url", ""))
                origin = "RECUPERADO"
            else:
                status = "SIN_ABSTRACT"
                reason = "No se encontró evidencia suficiente en las fuentes consultadas."
                candidate = {"abstract": ""}
                source = ""
                source_url = ""
                origin = "NO_ENCONTRADO"
        else:
            status = "SIN_ABSTRACT"
            reason = "Recuperación de red deshabilitada."
            candidate = {"abstract": ""}
            source = ""
            source_url = ""
            origin = "NO_ENCONTRADO"

        abstract_text = str(candidate.get("abstract", "")).strip()
        record["abstract_status"] = status
        record["abstract_source"] = source
        record["abstract_source_url"] = source_url
        record["abstract_quality_reason"] = reason
        record["abstract_retrieved_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if status == "APTO_PARA_CLASIFICAR":
            record["abstract"] = abstract_text
        else:
            if existing:
                record["abstract_original_no_validado"] = existing
            record.pop("abstract", None)
            if abstract_text:
                record["abstract_candidate"] = abstract_text
        provenance.append(
            _provenance_row(
                record,
                source,
                source_url,
                status,
                reason,
                origin,
                abstract_text,
            )
        )
        if index % 10 == 0:
            write_jsonl(paths["abstracts"], records)
            write_csv(
                root / "output" / "abstracts" / "procedencia_abstracts.csv",
                provenance,
                ("ID", "fuente", "URL_fuente", "fecha_consulta", "origen", "estado", "motivo", "abstract"),
            )

    repeated: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        abstract = str(record.get("abstract", "")).strip()
        if abstract and not record.get("duplicate_of"):
            repeated[abstract.casefold()].append(record)
    repeated_ids = {
        str(record["id"])
        for matches in repeated.values()
        if len(matches) > 1
        for record in matches
    }
    if repeated_ids:
        for record in records:
            if str(record["id"]) in repeated_ids:
                record["abstract_status"] = "POSIBLE_ERROR_DE_COINCIDENCIA"
                record["abstract_quality_reason"] = "El mismo abstract aparece en documentos principales diferentes."
                record["abstract_candidate"] = record.pop("abstract", "")
        for row in provenance:
            if str(row["ID"]) in repeated_ids:
                row["estado"] = "POSIBLE_ERROR_DE_COINCIDENCIA"
                row["motivo"] = "El mismo abstract aparece en documentos principales diferentes."

    write_jsonl(paths["abstracts"], records)
    write_master_bib(paths["master"], records)
    write_csv(
        root / "output" / "abstracts" / "procedencia_abstracts.csv",
        provenance,
        ("ID", "fuente", "URL_fuente", "fecha_consulta", "origen", "estado", "motivo", "abstract"),
    )
    apt = [row for row in provenance if row["estado"] == "APTO_PARA_CLASIFICAR"]
    review = [row for row in provenance if row["estado"] != "APTO_PARA_CLASIFICAR"]
    write_csv(
        root / "output" / "abstracts" / "abstracts_aptos.csv",
        apt,
        ("ID", "fuente", "URL_fuente", "fecha_consulta", "origen", "estado", "motivo", "abstract"),
    )
    write_csv(
        root / "output" / "abstracts" / "abstracts_revision.csv",
        review,
        ("ID", "fuente", "URL_fuente", "fecha_consulta", "origen", "estado", "motivo", "abstract"),
    )
    write_csv(
        root / "data" / "manual" / "abstracts_por_revisar.csv",
        review,
        ("ID", "fuente", "URL_fuente", "fecha_consulta", "origen", "estado", "motivo", "abstract"),
    )
    write_csv(
        root / "logs" / "errores_recuperacion_abstracts.csv",
        network_errors,
        ("ID", "error"),
    )
    _log(
        root,
        "Fases 4-5",
        "Recuperación y control de calidad de abstracts",
        paths["deduplicated"],
        paths["master"],
        len(records),
        sum(1 for row in provenance if row["origen"] == "RECUPERADO" and row["estado"] == "APTO_PARA_CLASIFICAR"),
        len(network_errors),
        observations=f"{len(review)} abstracts requieren revisión o no fueron encontrados.",
    )
    return records, provenance


def resolve_completed_excel_path(root: Path, excel_path: Path | None = None) -> Path:
    if excel_path is not None:
        path = excel_path if excel_path.is_absolute() else root / excel_path
        if path.is_dir():
            candidates = sorted(path.glob("*.xlsx"))
            if not candidates:
                raise FileNotFoundError(f"No hay archivos .xlsx en {path}")
            return candidates[0]
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el Excel completo: {path}")
        return path
    folder = _paths(root)["completed_excel_dir"]
    candidates = sorted(folder.glob("*.xlsx"))
    if not candidates:
        raise FileNotFoundError(
            f"No hay un Excel completo en {folder}. Indique --excel-abstracts."
        )
    return candidates[0]


def read_classification_excel(path: Path) -> dict[str, dict[str, str]]:
    from openpyxl import load_workbook

    workbook = load_workbook(path, data_only=True)
    sheet = workbook.active
    headers = [
        str(cell.value).strip() if cell.value else ""
        for cell in next(sheet.iter_rows(min_row=1, max_row=1))
    ]
    rows: dict[str, dict[str, str]] = {}
    for values in sheet.iter_rows(min_row=2, values_only=True):
        row = {
            headers[index]: "" if value is None else str(value).strip()
            for index, value in enumerate(values)
            if index < len(headers)
        }
        identifier = row.get("ID", "").strip()
        if identifier:
            rows[identifier] = row
    return rows


def apply_completed_excel_abstracts(
    records: list[dict[str, object]],
    excel_rows: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], list[str]]:
    changed_ids: list[str] = []
    timestamp = utc_now()
    for record in records:
        identifier = str(record.get("id", ""))
        excel_row = excel_rows.get(identifier)
        if not excel_row:
            continue
        excel_text = str(excel_row.get("Abstract") or "").strip()
        current = str(record.get("abstract") or "").strip()
        if current or not excel_text:
            continue
        note = interpret_screening_note(excel_text)
        record["abstract_source"] = "Excel completado manualmente"
        record["abstract_source_url"] = ""
        record["abstract_origin"] = "MANUAL"
        record["abstract_retrieved_at"] = timestamp
        if note:
            record["screening_note"] = excel_text
            record.pop("abstract", None)
            record["abstract_status"] = "NOTA_DESCARTE"
            record["abstract_quality_reason"] = note["justification"]
        else:
            record["abstract"] = excel_text
            record.pop("abstract_candidate", None)
            record["abstract_status"] = "APTO_PARA_CLASIFICAR"
            record["abstract_quality_reason"] = "Abstract aportado en el Excel completo."
        changed_ids.append(identifier)
    return records, changed_ids


def _write_abstract_outputs(
    root: Path,
    records: list[dict[str, object]],
    provenance: list[dict[str, object]],
) -> None:
    write_csv(
        root / "output" / "abstracts" / "procedencia_abstracts.csv",
        provenance,
        ("ID", "fuente", "URL_fuente", "fecha_consulta", "origen", "estado", "motivo", "abstract"),
    )
    apt = [row for row in provenance if row["estado"] == "APTO_PARA_CLASIFICAR"]
    review = [row for row in provenance if row["estado"] != "APTO_PARA_CLASIFICAR"]
    write_csv(
        root / "output" / "abstracts" / "abstracts_aptos.csv",
        apt,
        ("ID", "fuente", "URL_fuente", "fecha_consulta", "origen", "estado", "motivo", "abstract"),
    )
    write_csv(
        root / "output" / "abstracts" / "abstracts_revision.csv",
        review,
        ("ID", "fuente", "URL_fuente", "fecha_consulta", "origen", "estado", "motivo", "abstract"),
    )
    write_csv(
        root / "data" / "manual" / "abstracts_por_revisar.csv",
        review,
        ("ID", "fuente", "URL_fuente", "fecha_consulta", "origen", "estado", "motivo", "abstract"),
    )


def run_reclassify_from_completed_excel(
    root: Path,
    excel_path: Path | None = None,
) -> dict[str, object]:
    paths = _paths(root)
    completed_excel = resolve_completed_excel_path(root, excel_path)
    records = read_jsonl(paths["abstracts"])
    excel_rows = read_classification_excel(completed_excel)
    records, changed_ids = apply_completed_excel_abstracts(records, excel_rows)
    confirmed_duplicates = confirm_unresolved_duplicates(records)
    confirmed_duplicates.extend(apply_manual_duplicate_pairs(records))
    changed_ids = list(dict.fromkeys([*changed_ids, *confirmed_duplicates]))
    changed = set(changed_ids)

    provenance_path = paths["provenance"]
    with provenance_path.open("r", encoding="utf-8-sig", newline="") as stream:
        provenance = list(csv.DictReader(stream))
    provenance_by_id = {str(row.get("ID", "")): row for row in provenance}
    for record in records:
        identifier = str(record.get("id", ""))
        if identifier not in changed:
            continue
        origin = "MANUAL"
        status = str(record.get("abstract_status", ""))
        provenance_by_id[identifier] = _provenance_row(
            record,
            str(record.get("abstract_source", "")),
            str(record.get("abstract_source_url", "")),
            status,
            str(record.get("abstract_quality_reason", "")),
            origin,
            str(record.get("abstract") or record.get("screening_note") or ""),
        )
    provenance = [provenance_by_id[str(record.get("id", ""))] for record in records]
    write_jsonl(paths["abstracts"], records)
    write_master_bib(paths["master"], records)
    _write_abstract_outputs(root, records, provenance)
    base = run_prepare_classification(root)
    classification = run_classification_offline(root)
    excel, counts = run_export(root)
    annotated = annotate_doubtful_recommendations(completed_excel, classification)
    published = publish_ticapall(root)
    _log(
        root,
        "Fases 7-11",
        "Reclasificación con Excel de abstracts completos",
        completed_excel,
        excel,
        len(records),
        len(changed_ids),
        observations=f"{len(changed_ids)} abstracts o notas incorporados desde el Excel completo.",
    )
    return {
        "completed_excel": str(completed_excel),
        "abstracts_incorporados": len(changed_ids),
        "duplicados_confirmados": confirmed_duplicates,
        "classification_base": len(base),
        "classified": len(classification),
        "excel": str(excel),
        "ticapall": str(published),
        "recomendaciones_dudosos": annotated,
        "prisma": counts,
    }


def _replace_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def publish_ticapall(source_root: Path, destination: Path | None = None) -> Path:
    dest = destination or source_root.parent / "TICaPALL"
    dest.mkdir(parents=True, exist_ok=True)
    original_bib = dest / "TICaP-509All.bib"
    original_backup = original_bib.read_bytes() if original_bib.exists() else None

    for folder in ("criteria", "prompts", "logs"):
        _replace_tree(source_root / folder, dest / folder)

    data_dest = dest / "data"
    data_dest.mkdir(parents=True, exist_ok=True)
    _replace_tree(source_root / "data" / "raw", data_dest / "raw")
    _replace_tree(source_root / "data" / "master", data_dest / "master")
    _replace_tree(source_root / "data" / "manual", data_dest / "manual")

    _replace_tree(source_root / "output", dest / "output")

    completed_src = source_root / "output" / "excel completo"
    if completed_src.exists():
        _replace_tree(completed_src, dest / "output" / "excel completo")

    master_src = source_root / "data" / "master" / "TICaP_master.bib"
    if master_src.exists():
        shutil.copy2(master_src, dest / "masterall509.bib")
        shutil.copy2(master_src, dest / "data" / "master" / "masterall509.bib")

    plan_text = """# TICaPALL (corpus de 509)

Carpeta principal del mapeo de 509 documentos. El entorno de trabajo reproducible sigue en `TICaP-509/`; aquí se publican los entregables finales.

## Contenido principal

- Original inmutable: `TICaP-509All.bib`
- Maestro completo: `masterall509.bib`
- Excel de clasificación: `output/excel/TICaP_clasificacion_titulo_abstract.xlsx`
- Excel con abstracts completos: `output/excel completo/`
- Reportes PRISMA: `output/reportes/`
- Copia de criterios: `criteria/`

## Reglas

- Periodo: 2020-2025 inclusive.
- Tipos admitidos: `article` e `inproceedings`.
- Clasificación solo por título y abstract.
- El original `TICaP-509All.bib` no se modifica.
"""
    (dest / "plan.md").write_text(plan_text, encoding="utf-8")
    if original_backup is not None:
        original_bib.write_bytes(original_backup)
    return dest


def annotate_doubtful_recommendations(
    excel_path: Path,
    official_rows: list[dict[str, str]] | None = None,
) -> dict[str, int]:
    from openpyxl import load_workbook

    workbook = load_workbook(excel_path)
    sheet = workbook.active
    headers = [
        str(cell.value or "").strip()
        for cell in next(sheet.iter_rows(min_row=1, max_row=1))
    ]
    columns = {name: index for index, name in enumerate(headers, start=1)}
    id_col = columns["ID"]
    decision_col = columns["Decisión"]
    observation_col = columns["Observación"]
    official_by_id = {
        str(row.get("ID", "")): row for row in (official_rows or [])
    }
    justification_col = columns.get("Justificación breve")
    criterion_col = columns.get("Criterio aplicado")
    technology_col = columns.get("Tecnología identificada")
    application_col = columns.get("Aplicación acuícola/piscícola")
    category_col = columns.get("Categoría temática")
    counts = {"incluir": 0, "excluir": 0, "duplicado": 0, "sincronizados": 0, "razones": 0}

    def apply_reason(identifier: str) -> bool:
        reason = SCREENING_REASONS.get(identifier)
        if not reason:
            return False
        if justification_col and reason.get("justification"):
            sheet.cell(row_idx, justification_col).value = reason["justification"]
        if observation_col and reason.get("observation"):
            sheet.cell(row_idx, observation_col).value = reason["observation"]
        if criterion_col and reason.get("criterion"):
            sheet.cell(row_idx, criterion_col).value = reason["criterion"]
        if technology_col and reason.get("technology"):
            sheet.cell(row_idx, technology_col).value = reason["technology"]
        if application_col and reason.get("application"):
            sheet.cell(row_idx, application_col).value = reason["application"]
        if category_col and reason.get("category"):
            sheet.cell(row_idx, category_col).value = reason["category"]
        counts["razones"] += 1
        return True

    def sync_official_fields(official_row: dict[str, str], *, skip_justification: bool = False) -> None:
        mapping = {
            criterion_col: official_row.get("Criterio aplicado"),
            technology_col: official_row.get("Tecnología identificada"),
            application_col: official_row.get("Aplicación acuícola/piscícola"),
            category_col: official_row.get("Categoría temática"),
        }
        if not skip_justification:
            mapping[justification_col] = official_row.get("Justificación breve")
        for column, value in mapping.items():
            if column and value:
                sheet.cell(row_idx, column).value = value

    for row_idx in range(2, sheet.max_row + 1):
        identifier = str(sheet.cell(row_idx, id_col).value or "").strip()
        official = official_by_id.get(identifier, {})
        official_decision = str(official.get("Decisión") or "").strip()
        current_justification = (
            sheet.cell(row_idx, justification_col).value if justification_col else ""
        )
        current_observation = sheet.cell(row_idx, observation_col).value
        if identifier in MANUAL_DUPLICATE_OF:
            sheet.cell(row_idx, decision_col).value = "DUPLICADO"
            sync_official_fields(official)
            if not apply_reason(identifier):
                sheet.cell(row_idx, observation_col).value = (
                    f"Duplicado confirmado del ID {MANUAL_DUPLICATE_OF[identifier]}."
                )
                if justification_col:
                    sheet.cell(row_idx, justification_col).value = (
                        f"Registro duplicado confirmado del ID {MANUAL_DUPLICATE_OF[identifier]}."
                    )
            counts["duplicado"] += 1
            continue
        if official_decision == "DUDOSO" or identifier in DOUBTFUL_INCLUDE_IDS | DOUBTFUL_EXCLUDE_IDS:
            sync_official_fields(official)
            if identifier in DOUBTFUL_INCLUDE_IDS:
                sheet.cell(row_idx, decision_col).value = "Dudoso (incluir)"
                counts["incluir"] += 1
            elif identifier in DOUBTFUL_EXCLUDE_IDS:
                sheet.cell(row_idx, decision_col).value = "Dudoso (excluir)"
                counts["excluir"] += 1
            apply_reason(identifier)
            continue
        if official_decision:
            sheet.cell(row_idx, decision_col).value = official_decision
            sync_official_fields(official)
            if apply_reason(identifier):
                counts["sincronizados"] += 1
                continue
            if is_stale_screening_text(current_observation) or is_stale_screening_text(
                current_justification
            ):
                if justification_col and official.get("Justificación breve"):
                    sheet.cell(row_idx, justification_col).value = official["Justificación breve"]
                sheet.cell(row_idx, observation_col).value = official.get(
                    "Justificación breve"
                ) or official.get("Observación")
            elif official.get("Observación") and is_stale_screening_text(current_observation):
                sheet.cell(row_idx, observation_col).value = official.get("Observación")
            counts["sincronizados"] += 1
    try:
        workbook.save(excel_path)
    except PermissionError:
        fallback = excel_path.with_name(excel_path.stem + "_actualizado.xlsx")
        workbook.save(fallback)
    return counts


def run_prepare_classification(root: Path) -> list[dict[str, object]]:
    paths = _paths(root)
    records = read_jsonl(paths["abstracts"])
    base_rows: list[dict[str, object]] = []
    eligibility_rows: list[dict[str, object]] = []
    for record in records:
        administrative = classify_record(
            {
                **record,
                "abstract": record.get("abstract", ""),
            }
        )
        is_administrative = administrative["decision"] in {
            "DUPLICADO",
            "FUERA_DE_PERIODO",
            "TIPO_NO_ADMITIDO",
        }
        eligibility_rows.append(
            {
                "ID": record["id"],
                "decisión_administrativa": administrative["decision"] if is_administrative else "",
                "criterio_administrativo": administrative["criterion"] if is_administrative else "",
                "justificación": administrative["justification"] if is_administrative else "",
            }
        )
        if not is_administrative:
            base_rows.append(
                {
                    "ID": record["id"],
                    "Título": record.get("title", ""),
                    "Abstract": record.get("abstract", ""),
                    "Año": record.get("year_normalized", ""),
                    "Tipo documental": record.get("type_normalized", ""),
                }
            )
    write_csv(
        paths["base"],
        base_rows,
        ("ID", "Título", "Abstract", "Año", "Tipo documental"),
    )
    write_csv(
        root / "data" / "interim" / "decisiones_administrativas.csv",
        eligibility_rows,
        ("ID", "decisión_administrativa", "criterio_administrativo", "justificación"),
    )
    criteria_path = root / "criteria" / "CriteriosPertinencia-Título y Abstract.pdf"
    manifest_rows = [
        {"archivo": str(paths["base"]), "sha256": sha256_file(paths["base"])},
        {"archivo": str(criteria_path), "sha256": sha256_file(criteria_path)},
        {"archivo": str(paths["master"]), "sha256": sha256_file(paths["master"])},
    ]
    write_csv(
        root / "data" / "interim" / "manifiesto_base_clasificacion.csv",
        manifest_rows,
        ("archivo", "sha256"),
    )
    _log(
        root,
        "Fase 6",
        "Preparación y congelación de base de clasificación",
        paths["abstracts"],
        paths["base"],
        len(records),
        len(base_rows),
    )
    return base_rows


def _official_row(result: dict[str, str]) -> dict[str, str]:
    return {
        "ID": result["id"],
        "Título": result["title"],
        "Abstract": result["abstract"],
        "Decisión": result["decision"],
        "Criterio aplicado": result["criterion"],
        "Justificación breve": result["justification"],
        "Tecnología identificada": result["technology"],
        "Aplicación acuícola/piscícola": result["application"],
        "Categoría temática": result["category"],
        "Observación": result["observation"],
    }


def run_classification_offline(root: Path) -> list[dict[str, str]]:
    paths = _paths(root)
    records = read_jsonl(paths["abstracts"])
    rows: list[dict[str, str]] = []
    pending: list[dict[str, str]] = []
    for record in records:
        result = classify_record(record)
        status = str(record.get("abstract_status", ""))
        if result["decision"] == "DUDOSO" and status in {
            "REQUIERE_REVISION",
            "POSIBLE_ERROR_DE_COINCIDENCIA",
        }:
            result["observation"] = (
                "Abstract dudoso."
                if status == "REQUIERE_REVISION"
                else "Diferencia entre título y abstract."
            )
        row = _official_row(result)
        rows.append(row)
        if row["Decisión"] == "DUDOSO" or status in {
            "REQUIERE_REVISION",
            "POSIBLE_ERROR_DE_COINCIDENCIA",
        } or record.get("duplicate_review"):
            pending.append(row)
    write_csv(paths["classification"], rows, OFFICIAL_COLUMNS)
    write_csv(
        root / "data" / "manual" / "decisiones_manual.csv",
        [
            {
                **row,
                "Decisión preliminar": row["Decisión"],
                "Decisión manual": "",
                "Revisor": "",
                "Fecha": "",
                "Motivo": "",
            }
            for row in pending
        ],
        (
            *OFFICIAL_COLUMNS,
            "Decisión preliminar",
            "Decisión manual",
            "Revisor",
            "Fecha",
            "Motivo",
        ),
    )
    generate_excel(
        pending,
        root / "output" / "revision_manual" / "casos_pendientes.xlsx",
        sheet_name="Revisión manual",
    )
    _log(
        root,
        "Fases 7-9",
        "Clasificación offline, variables y preparación de revisión manual",
        paths["base"],
        paths["classification"],
        len(rows),
        len(rows),
        observations=f"{len(pending)} casos pendientes de revisión manual.",
    )
    return rows


def generate_excel(
    rows: list[dict[str, object]],
    output_path: Path,
    sheet_name: str = "Clasificación",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    sheet.append(list(OFFICIAL_COLUMNS))
    for row in rows:
        sheet.append([row.get(column, "") for column in OFFICIAL_COLUMNS])
    header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in sheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = f"A1:J{max(1, sheet.max_row)}"
    widths = [16, 45, 80, 22, 22, 55, 35, 45, 32, 38]
    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    validation = DataValidation(
        type="list",
        formula1='"' + ",".join(DECISIONS) + '"',
        allow_blank=False,
        error="Use uno de los valores uniformes definidos.",
        errorTitle="Decisión no válida",
    )
    sheet.add_data_validation(validation)
    validation.add(f"D2:D{max(2, sheet.max_row)}")
    temporary = output_path.with_suffix(".tmp.xlsx")
    workbook.save(temporary)
    try:
        temporary.replace(output_path)
    except PermissionError:
        # Windows may lock an open workbook; write a sibling file instead of failing.
        fallback = output_path.with_name(output_path.stem + "_actualizado.xlsx")
        temporary.replace(fallback)
        output_path = fallback
    return output_path


def validate_classification_rows(rows: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    identifiers: set[str] = set()
    for index, row in enumerate(rows, start=2):
        identifier = str(row.get("ID", ""))
        decision = str(row.get("Decisión", ""))
        criterion = str(row.get("Criterio aplicado", ""))
        if not identifier:
            errors.append(f"Fila {index}: ID vacío.")
        elif identifier in identifiers:
            errors.append(f"Fila {index}: ID duplicado {identifier}.")
        identifiers.add(identifier)
        if decision not in DECISIONS:
            errors.append(f"Fila {index}: decisión no válida {decision!r}.")
        if not criterion:
            errors.append(f"Fila {index}: criterio vacío.")
        if decision == "EXCLUIR" and not criterion.startswith("CE"):
            errors.append(f"Fila {index}: exclusión sin código CE.")
        if not str(row.get("Justificación breve", "")).strip():
            errors.append(f"Fila {index}: justificación vacía.")
    return errors


def build_prisma_counts(
    rows: list[dict[str, object]],
    existing_abstracts: int,
    recovered_abstracts: int,
    doubtful_abstracts: int = 0,
    missing_abstracts: int | None = None,
) -> dict[str, int]:
    decisions = Counter(str(row.get("Decisión", "")) for row in rows)
    no_abstract = (
        missing_abstracts
        if missing_abstracts is not None
        else sum(
            "Abstract no encontrado" in str(row.get("Observación", ""))
            for row in rows
        )
    )
    return {
        "registros_iniciales": len(rows),
        "duplicados": decisions["DUPLICADO"],
        "fuera_del_periodo": decisions["FUERA_DE_PERIODO"],
        "tipos_no_admitidos": decisions["TIPO_NO_ADMITIDO"],
        "abstracts_existentes": existing_abstracts,
        "abstracts_recuperados": recovered_abstracts,
        "abstracts_dudosos": doubtful_abstracts,
        "abstracts_no_encontrados": no_abstract,
        "incluidos": decisions["INCLUIR"],
        "excluidos": decisions["EXCLUIR"],
        "dudosos": decisions["DUDOSO"],
        "pendientes_revision_manual": sum(
            decision == "DUDOSO"
            or "dudoso" in str(row.get("Observación", "")).casefold()
            or "revisión manual" in str(row.get("Observación", "")).casefold()
            for row, decision in (
                (row, str(row.get("Decisión", ""))) for row in rows
            )
        ),
    }


def run_export(root: Path) -> tuple[Path, dict[str, int]]:
    paths = _paths(root)
    with paths["classification"].open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    errors = validate_classification_rows(rows)
    write_csv(
        root / "output" / "reportes" / "errores_validacion.csv",
        [{"error": error} for error in errors],
        ("error",),
    )
    if errors:
        raise ValueError("La clasificación no superó la validación: " + "; ".join(errors[:5]))
    excel_path = generate_excel(rows, paths["excel"])

    provenance_path = root / "output" / "abstracts" / "procedencia_abstracts.csv"
    with provenance_path.open("r", encoding="utf-8-sig", newline="") as stream:
        provenance = list(csv.DictReader(stream))
    counts = build_prisma_counts(
        rows,
        existing_abstracts=sum(
            row["origen"] == "EXISTENTE"
            for row in provenance
        ),
        recovered_abstracts=sum(
            row["origen"] == "RECUPERADO"
            for row in provenance
        ),
        doubtful_abstracts=sum(
            row["estado"] in {"REQUIERE_REVISION", "POSIBLE_ERROR_DE_COINCIDENCIA"}
            for row in provenance
        ),
        missing_abstracts=sum(
            row["estado"] == "SIN_ABSTRACT"
            for row in provenance
        ),
    )
    write_csv(
        root / "output" / "reportes" / "resumen_prisma.csv",
        [{"métrica": key, "conteo": value} for key, value in counts.items()],
        ("métrica", "conteo"),
    )
    markdown = [
        "# Resumen para PRISMA",
        "",
        "Conteos generados automáticamente desde el universo importado y la clasificación consolidada.",
        "",
    ]
    markdown.extend(f"- {key.replace('_', ' ').capitalize()}: {value}" for key, value in counts.items())
    (root / "output" / "reportes" / "resumen_prisma.md").write_text(
        "\n".join(markdown) + "\n",
        encoding="utf-8",
    )
    _log(
        root,
        "Fases 10-11",
        "Validación, Excel final y resumen PRISMA",
        paths["classification"],
        excel_path,
        len(rows),
        len(rows),
    )
    return excel_path, counts


def run_all(root: Path, allow_network: bool = True) -> dict[str, object]:
    imported = run_import(root)
    normalized = run_normalization(root)
    _records, groups = run_duplicates(root)
    records_with_abstracts, provenance = run_abstract_recovery(root, allow_network)
    base = run_prepare_classification(root)
    classification = run_classification_offline(root)
    excel, counts = run_export(root)
    return {
        "imported": len(imported),
        "normalized": len(normalized),
        "duplicate_groups": len(groups),
        "records_with_abstracts": len(records_with_abstracts),
        "abstract_provenance": len(provenance),
        "classification_base": len(base),
        "classified": len(classification),
        "excel": str(excel),
        "prisma": counts,
    }

