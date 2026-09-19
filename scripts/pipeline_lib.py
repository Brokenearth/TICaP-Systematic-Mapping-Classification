from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Iterator


ROOT = Path(__file__).resolve().parents[1]
RAW_BIB = ROOT / "data" / "raw" / "mendeley_original.bib"
MASTER_BIB = ROOT / "data" / "master" / "TICaP_master.bib"
INTERIM = ROOT / "data" / "interim"
MANUAL = ROOT / "data" / "manual"
OUTPUT = ROOT / "output"
LOGS = ROOT / "logs"

DECISIONS = (
    "INCLUIR",
    "EXCLUIR",
    "DUDOSO",
    "DUPLICADO",
    "FUERA_DE_PERIODO",
    "TIPO_NO_ADMITIDO",
)
ACCEPTED_TYPES = {"article", "inproceedings"}
OFFICIAL_COLUMNS = (
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
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_jsonl(path: Path, records: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    temporary.replace(path)


def read_jsonl(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_csv(
    path: Path,
    rows: Iterable[dict[str, object]],
    fieldnames: Iterable[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    columns = list(fieldnames)
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})
    temporary.replace(path)


def log_activity(
    phase: str,
    activity: str,
    input_path: str,
    output_path: str,
    processed: int,
    modified: int,
    errors: int = 0,
    observations: str = "",
) -> None:
    path = LOGS / "registro_actividades.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
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
    with path.open("a", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "fecha": utc_now(),
                "fase": phase,
                "actividad": activity,
                "archivo_entrada": input_path,
                "archivo_salida": output_path,
                "registros_procesados": processed,
                "registros_modificados": modified,
                "errores": errors,
                "observaciones": observations,
            }
        )


def _matching_brace(text: str, start: int) -> int:
    opening = text[start]
    closing = "}" if opening == "{" else ")"
    depth = 0
    in_quote = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if in_quote:
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index
    raise ValueError(f"Entrada BibTeX sin cierre desde la posición {start}")


def _split_top_level(text: str, delimiter: str = ",") -> list[str]:
    """Split BibTeX entry bodies on top-level commas.

    Only braces and quotes delimit values. Parentheses inside fields (e.g. ``i)``,
    ``(WOS)``) are plain text and must not affect field boundaries.
    """
    parts: list[str] = []
    start = 0
    brace_depth = 0
    in_quote = False
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
        elif not in_quote:
            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
            elif char == delimiter and brace_depth == 0:
                parts.append(text[start:index])
                start = index + 1
    parts.append(text[start:])
    return parts


def _unwrap_bib_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and (
        (value[0] == "{" and value[-1] == "}")
        or (value[0] == '"' and value[-1] == '"')
    ):
        return value[1:-1].strip()
    return value


def parse_bibtex(text: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    position = 0
    entry_pattern = re.compile(r"@([A-Za-z]+)\s*([\{\(])", re.MULTILINE)
    while match := entry_pattern.search(text, position):
        entry_type = match.group(1).lower()
        if entry_type in {"comment", "preamble", "string"}:
            end = _matching_brace(text, match.start(2))
            position = end + 1
            continue
        end = _matching_brace(text, match.start(2))
        body = text[match.end() : end]
        parts = _split_top_level(body)
        citation_key = parts[0].strip()
        record: dict[str, str] = {
            "entry_type": entry_type,
            "citation_key": citation_key,
        }
        for field_part in parts[1:]:
            if not field_part.strip() or "=" not in field_part:
                continue
            name, value = field_part.split("=", 1)
            field_name = name.strip().lower()
            if field_name:
                record[field_name] = _unwrap_bib_value(value)
        records.append(record)
        position = end + 1
    return records


def normalize_doi(value: object) -> str:
    doi = str(value or "").strip().lower()
    doi = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi.rstrip(".,;:) ")


def normalize_title(value: object) -> str:
    title = str(value or "")
    title = re.sub(r"\\[A-Za-z]+\s*", " ", title)
    title = title.replace("{", "").replace("}", "")
    title = unicodedata.normalize("NFKD", title)
    title = "".join(char for char in title if not unicodedata.combining(char))
    title = title.casefold()
    title = re.sub(r"[\W_]+", " ", title, flags=re.UNICODE)
    return re.sub(r"\s+", " ", title).strip()


def normalize_authors(value: object) -> str:
    authors = normalize_title(value)
    authors = re.sub(r"\s+and\s+", ";", authors)
    return authors


def normalize_year(value: object) -> str:
    match = re.search(r"\b(19|20)\d{2}\b", str(value or ""))
    return match.group(0) if match else ""


def normalize_type(value: object) -> str:
    entry_type = normalize_title(value).replace(" ", "")
    mapping = {
        "article": "article",
        "journalarticle": "article",
        "inproceedings": "inproceedings",
        "conferencepaper": "inproceedings",
        "proceedingsarticle": "inproceedings",
    }
    return mapping.get(entry_type, entry_type)


def normalize_record(record: dict[str, object]) -> dict[str, object]:
    normalized = dict(record)
    normalized["doi_original"] = str(record.get("doi", ""))
    normalized["doi_normalized"] = normalize_doi(record.get("doi", ""))
    normalized["title_original"] = str(record.get("title", ""))
    normalized["title_normalized"] = normalize_title(record.get("title", ""))
    normalized["authors_original"] = str(record.get("author", ""))
    normalized["authors_normalized"] = normalize_authors(record.get("author", ""))
    normalized["year_original"] = str(record.get("year", ""))
    normalized["year_normalized"] = normalize_year(record.get("year", ""))
    normalized["type_original"] = str(record.get("entry_type", ""))
    normalized["type_normalized"] = normalize_type(record.get("entry_type", ""))
    return normalized


class _UnionFind:
    def __init__(self, identifiers: Iterable[str]) -> None:
        self.parent = {identifier: identifier for identifier in identifiers}

    def find(self, identifier: str) -> str:
        parent = self.parent[identifier]
        if parent != identifier:
            self.parent[identifier] = self.find(parent)
        return self.parent[identifier]

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def _author_tokens(authors: object) -> set[str]:
    return {
        token
        for token in normalize_title(authors).split()
        if len(token) > 2 and token not in {"and", "the"}
    }


def _completeness(record: dict[str, object]) -> tuple[int, int]:
    useful = ("abstract", "doi_normalized", "author", "journal", "booktitle", "pages")
    score = sum(bool(str(record.get(field, "")).strip()) for field in useful)
    abstract_length = len(str(record.get("abstract", "")))
    return score, abstract_length


def detect_duplicate_groups(
    records: list[dict[str, object]],
) -> list[dict[str, object]]:
    identifiers = [str(record["id"]) for record in records]
    finder = _UnionFind(identifiers)
    evidence: dict[frozenset[str], str] = {}
    for left_index, left in enumerate(records):
        for right in records[left_index + 1 :]:
            left_id = str(left["id"])
            right_id = str(right["id"])
            method = ""
            left_doi = str(left.get("doi_normalized", ""))
            right_doi = str(right.get("doi_normalized", ""))
            left_title = str(left.get("title_normalized", ""))
            right_title = str(right.get("title_normalized", ""))
            same_year = (
                bool(left.get("year_normalized"))
                and left.get("year_normalized") == right.get("year_normalized")
            )
            if left_doi and left_doi == right_doi:
                method = "DOI_IDENTICO"
            elif left_title and left_title == right_title and same_year:
                method = "TITULO_IDENTICO"
            elif left_title and right_title and same_year:
                similarity = SequenceMatcher(None, left_title, right_title).ratio()
                authors_overlap = _author_tokens(left.get("authors_normalized", "")) & _author_tokens(
                    right.get("authors_normalized", "")
                )
                if similarity >= 0.92 and authors_overlap:
                    method = "TITULO_PARECIDO_ANIO_AUTORES"
            if method:
                finder.union(left_id, right_id)
                evidence[frozenset((left_id, right_id))] = method

    members_by_root: dict[str, list[str]] = defaultdict(list)
    records_by_id = {str(record["id"]): record for record in records}
    for identifier in identifiers:
        members_by_root[finder.find(identifier)].append(identifier)

    groups: list[dict[str, object]] = []
    for members in members_by_root.values():
        if len(members) < 2:
            continue
        methods = {
            method
            for pair, method in evidence.items()
            if pair.issubset(set(members))
        }
        if "DOI_IDENTICO" in methods:
            method = "DOI_IDENTICO"
        elif "TITULO_IDENTICO" in methods:
            method = "TITULO_IDENTICO"
        else:
            method = "TITULO_PARECIDO_ANIO_AUTORES"
        status = (
            "REQUIERE_REVISION"
            if method == "TITULO_PARECIDO_ANIO_AUTORES"
            else "CONFIRMADO"
        )
        principal = max(
            members,
            key=lambda identifier: (
                _completeness(records_by_id[identifier]),
                -int(identifier.split("-")[-1]),
            ),
        )
        groups.append(
            {
                "group_id": f"DUP-{len(groups) + 1:04d}",
                "method": method,
                "status": status,
                "principal_id": principal,
                "member_ids": sorted(members),
            }
        )
    return groups


def _strip_markup(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _candidate_authors(value: object) -> str:
    if isinstance(value, list):
        names: list[str] = []
        for author in value:
            if isinstance(author, dict):
                names.append(
                    " ".join(
                        part
                        for part in (
                            str(author.get("given", "")),
                            str(author.get("family", "")),
                            str(author.get("display_name", "")),
                            str(author.get("name", "")),
                        )
                        if part
                    )
                )
            else:
                names.append(str(author))
        return " and ".join(names)
    return str(value or "")


def validate_abstract_candidate(
    record: dict[str, object],
    candidate: dict[str, object],
) -> tuple[str, str]:
    abstract = _strip_markup(str(candidate.get("abstract", "")))
    if not abstract:
        return "SIN_ABSTRACT", "La fuente no entregó abstract."

    record_doi = normalize_doi(record.get("doi_normalized", record.get("doi", "")))
    candidate_doi = normalize_doi(candidate.get("doi", ""))
    if record_doi and candidate_doi and record_doi != candidate_doi:
        return "POSIBLE_ERROR_DE_COINCIDENCIA", "El DOI de la fuente no coincide."
    if len(abstract) < 80:
        return "REQUIERE_REVISION", "El texto es demasiado breve para confirmarlo como abstract."
    if re.fullmatch(r"(?i)\s*(keywords?|palabras clave)\s*:?.*", abstract):
        return "REQUIERE_REVISION", "El texto parece ser solo una lista de palabras clave."

    record_title = normalize_title(record.get("title", ""))
    candidate_title = normalize_title(candidate.get("title", ""))
    if candidate_title and SequenceMatcher(None, record_title, candidate_title).ratio() < 0.72:
        return "POSIBLE_ERROR_DE_COINCIDENCIA", "El título de la fuente no coincide suficientemente."

    record_year = normalize_year(record.get("year_normalized", record.get("year", "")))
    candidate_year = normalize_year(candidate.get("year", ""))
    if record_year and candidate_year and abs(int(record_year) - int(candidate_year)) > 1:
        return "REQUIERE_REVISION", "El año de la fuente es incompatible."

    record_authors = _author_tokens(record.get("authors_normalized", record.get("author", "")))
    candidate_authors = _author_tokens(_candidate_authors(candidate.get("authors", "")))
    if record_authors and candidate_authors and not (record_authors & candidate_authors):
        return "REQUIERE_REVISION", "No se pudo confirmar coincidencia de autores."
    return "APTO_PARA_CLASIFICAR", "Título, identificadores y metadatos son compatibles."


@dataclass(frozen=True)
class HttpResult:
    data: object
    final_url: str


def _http_json(url: str, timeout: float = 20.0) -> HttpResult:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "TICaP-Systematic-Mapping/1.0 (academic reproducibility workflow)",
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return HttpResult(
                    json.loads(response.read().decode("utf-8")),
                    response.geturl(),
                )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"No fue posible consultar {url}: {last_error}")


def _http_text(url: str, timeout: float = 20.0) -> HttpResult:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "User-Agent": "TICaP-Systematic-Mapping/1.0 (academic reproducibility workflow)",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        encoding = response.headers.get_content_charset() or "utf-8"
        return HttpResult(response.read().decode(encoding, errors="replace"), response.geturl())


def _crossref_candidate(record: dict[str, object]) -> dict[str, object] | None:
    doi = str(record.get("doi_normalized", ""))
    if not doi:
        return None
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    message = _http_json(url).data
    if not isinstance(message, dict):
        return None
    item = message.get("message", {})
    if not isinstance(item, dict) or not item.get("abstract"):
        return None
    title = item.get("title", [""])
    return {
        "abstract": _strip_markup(str(item["abstract"])),
        "title": title[0] if isinstance(title, list) and title else str(title),
        "doi": item.get("DOI", doi),
        "year": _crossref_year(item),
        "authors": item.get("author", []),
        "source": "Crossref",
        "source_url": url,
    }


def _crossref_year(item: dict[str, object]) -> str:
    for field in ("published-print", "published-online", "issued", "created"):
        value = item.get(field)
        if isinstance(value, dict):
            date_parts = value.get("date-parts")
            if isinstance(date_parts, list) and date_parts and date_parts[0]:
                return str(date_parts[0][0])
    return ""


def _openalex_abstract(inverted: object) -> str:
    if not isinstance(inverted, dict):
        return ""
    positions: list[tuple[int, str]] = []
    for word, indexes in inverted.items():
        if isinstance(indexes, list):
            positions.extend((int(index), str(word)) for index in indexes)
    return " ".join(word for _index, word in sorted(positions))


def _openalex_candidate(record: dict[str, object]) -> dict[str, object] | None:
    doi = str(record.get("doi_normalized", ""))
    if not doi:
        return None
    work_id = "https://doi.org/" + doi
    url = "https://api.openalex.org/works/" + urllib.parse.quote(work_id, safe="")
    item = _http_json(url).data
    if not isinstance(item, dict):
        return None
    abstract = _openalex_abstract(item.get("abstract_inverted_index"))
    if not abstract:
        return None
    authorships = item.get("authorships", [])
    authors = []
    if isinstance(authorships, list):
        authors = [
            authorship.get("author", {}).get("display_name", "")
            for authorship in authorships
            if isinstance(authorship, dict)
        ]
    return {
        "abstract": abstract,
        "title": item.get("title", ""),
        "doi": doi,
        "year": item.get("publication_year", ""),
        "authors": authors,
        "source": "OpenAlex",
        "source_url": url,
    }


def _semantic_scholar_candidate(record: dict[str, object]) -> dict[str, object] | None:
    doi = str(record.get("doi_normalized", ""))
    if not doi:
        return None
    paper_id = urllib.parse.quote("DOI:" + doi, safe="")
    fields = "title,abstract,year,authors,externalIds,url"
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields={fields}"
    item = _http_json(url).data
    if not isinstance(item, dict) or not item.get("abstract"):
        return None
    external_ids = item.get("externalIds", {})
    candidate_doi = external_ids.get("DOI", doi) if isinstance(external_ids, dict) else doi
    return {
        "abstract": item.get("abstract", ""),
        "title": item.get("title", ""),
        "doi": candidate_doi,
        "year": item.get("year", ""),
        "authors": item.get("authors", []),
        "source": "Semantic Scholar",
        "source_url": item.get("url", url),
    }


class _MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.casefold() != "meta":
            return
        values = {key.casefold(): value or "" for key, value in attrs}
        name = (values.get("name") or values.get("property") or "").casefold()
        content = values.get("content", "")
        if name and content and name not in self.meta:
            self.meta[name] = content


def _publisher_candidate(record: dict[str, object]) -> dict[str, object] | None:
    doi = str(record.get("doi_normalized", ""))
    if not doi:
        return None
    result = _http_text("https://doi.org/" + urllib.parse.quote(doi, safe="/"))
    parser = _MetaParser()
    parser.feed(str(result.data))
    abstract = (
        parser.meta.get("citation_abstract")
        or parser.meta.get("dc.description")
        or parser.meta.get("description")
        or parser.meta.get("og:description")
        or ""
    )
    if not abstract:
        return None
    return {
        "abstract": _strip_markup(abstract),
        "title": parser.meta.get("citation_title", parser.meta.get("dc.title", "")),
        "doi": parser.meta.get("citation_doi", doi),
        "year": parser.meta.get("citation_publication_date", ""),
        "authors": parser.meta.get("citation_author", ""),
        "source": "Página oficial del artículo",
        "source_url": result.final_url,
    }


def _crossref_title_candidate(record: dict[str, object]) -> dict[str, object] | None:
    title = str(record.get("title", "")).strip()
    if not title:
        return None
    params = urllib.parse.urlencode({"query.title": title, "rows": 5, "select": "DOI,title,abstract,author,issued"})
    url = "https://api.crossref.org/works?" + params
    response = _http_json(url).data
    if not isinstance(response, dict):
        return None
    message = response.get("message", {})
    items = message.get("items", []) if isinstance(message, dict) else []
    best: tuple[float, dict[str, object]] | None = None
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict) or not item.get("abstract"):
            continue
        candidate_title_value = item.get("title", [""])
        candidate_title = (
            candidate_title_value[0]
            if isinstance(candidate_title_value, list) and candidate_title_value
            else str(candidate_title_value)
        )
        score = SequenceMatcher(None, normalize_title(title), normalize_title(candidate_title)).ratio()
        candidate = {
            "abstract": _strip_markup(str(item["abstract"])),
            "title": candidate_title,
            "doi": item.get("DOI", ""),
            "year": _crossref_year(item),
            "authors": item.get("author", []),
            "source": "Crossref (búsqueda por título)",
            "source_url": url,
        }
        if best is None or score > best[0]:
            best = score, candidate
    return best[1] if best and best[0] >= 0.9 else None


def retrieve_abstract_candidate(
    record: dict[str, object],
) -> tuple[dict[str, object] | None, list[str]]:
    errors: list[str] = []
    for fetcher in (
        _crossref_candidate,
        _openalex_candidate,
        _semantic_scholar_candidate,
        _publisher_candidate,
        _crossref_title_candidate,
    ):
        try:
            candidate = fetcher(record)
            if candidate:
                return candidate, errors
        except Exception as error:  # Network failures are recorded per source.
            errors.append(f"{fetcher.__name__}: {error}")
        time.sleep(0.2)
    return None, errors


TECHNOLOGIES: dict[str, tuple[str, ...]] = {
    "IoT": ("iot", "internet of things"),
    "Sensores": ("sensor", "sensing", "sonda", "probe"),
    "Inteligencia artificial": ("artificial intelligence", "inteligencia artificial", " ai "),
    "Aprendizaje automático": ("machine learning", "deep learning", "neural network"),
    "Visión artificial": ("computer vision", "machine vision", "image processing", "video analysis"),
    "Big Data/analítica": ("big data", "data analytics", "predictive analytics"),
    "Blockchain": ("blockchain", "distributed ledger"),
    "Software/plataforma": ("software", "platform", "dashboard", "mobile app", "web application"),
    "Automatización/robótica": ("automat", "robot", "smart feeder"),
    "Teledetección": ("remote sensing", "satellite", "drone", "uav"),
    "Redes/comunicación": ("wireless", "wifi", "wi-fi", "lora", "zigbee", "gsm"),
    "Sistemas embebidos": ("arduino", "raspberry", "microcontroller", "embedded system"),
    "Computación en la nube": ("cloud computing", "cloud-based", "edge computing"),
}

APPLICATIONS: dict[str, tuple[str, ...]] = {
    "Monitoreo de calidad del agua o ambiente": (
        "water quality",
        "calidad del agua",
        "temperature",
        "temperatura",
        "dissolved oxygen",
        "oxigeno disuelto",
        "ph",
        "turbidity",
        "salinity",
    ),
    "Alimentación": ("feeding", "feeder", "feed intake", "alimentacion", "alimento"),
    "Crecimiento y biomasa": ("biomass", "growth estimation", "weight estimation", "fish size"),
    "Sanidad": ("disease detection", "health monitoring", "pathogen", "mortality prediction"),
    "Comportamiento": ("fish behavior", "fish behaviour", "swimming behavior", "activity recognition"),
    "Trazabilidad y certificación": ("traceability", "trazabilidad", "certification", "supply chain"),
    "Gestión productiva": ("farm management", "production management", "gestion productiva"),
    "Apoyo a decisiones": ("decision support", "decision-making", "prediction", "forecast"),
    "Control de calidad": ("quality control", "freshness", "product quality"),
    "Automatización del cultivo": ("automation", "automated", "robot", "control system"),
}

CATEGORY_BY_APPLICATION = {
    "Monitoreo de calidad del agua o ambiente": "Monitoreo ambiental",
    "Alimentación": "Alimentación",
    "Crecimiento y biomasa": "Crecimiento y biomasa",
    "Sanidad": "Sanidad",
    "Comportamiento": "Comportamiento",
    "Trazabilidad y certificación": "Trazabilidad y certificación",
    "Gestión productiva": "Gestión empresarial",
    "Apoyo a decisiones": "Apoyo a decisiones",
    "Control de calidad": "Control de calidad",
    "Automatización del cultivo": "Automatización",
}


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _detect_labels(text: str, mapping: dict[str, tuple[str, ...]]) -> list[str]:
    return [label for label, terms in mapping.items() if _contains_any(text, terms)]


SCREENING_NOTES: dict[str, dict[str, str]] = {
    "duplicado": {
        "decision": "DUPLICADO",
        "criterion": "ADM_DUPLICADO",
        "justification": "El registro se identificó como duplicado en la revisión manual del Excel.",
        "observation": "Nota de descarte en lugar de abstract.",
    },
    "libro": {
        "decision": "TIPO_NO_ADMITIDO",
        "criterion": "ADM_TIPO",
        "justification": "El documento corresponde a un libro o capítulo de libro, tipo no admitido.",
        "observation": "Nota de descarte en lugar de abstract.",
    },
    "pagina caida": {
        "decision": "EXCLUIR",
        "criterion": "CE9",
        "justification": "La fuente no estuvo disponible y el título no permite una decisión de inclusión.",
        "observation": "Página caída; sin abstract recuperable.",
    },
}


MANUAL_DUPLICATE_OF: dict[str, str] = {
    "TICAP-0254": "TICAP-0172",
}

DOUBTFUL_INCLUDE_IDS: frozenset[str] = frozenset(
    {
        "TICAP-0172",
        "TICAP-0229",
        "TICAP-0243",
        "TICAP-0253",
        "TICAP-0256",
        "TICAP-0270",
        "TICAP-0319",
        "TICAP-0345",
        "TICAP-0353",
        "TICAP-0364",
        "TICAP-0376",
        "TICAP-0421",
        "TICAP-0480",
        "TICAP-0493",
        "TICAP-0500",
    }
)

DOUBTFUL_EXCLUDE_IDS: frozenset[str] = frozenset(
    {
        "TICAP-0051",
        "TICAP-0090",
        "TICAP-0097",
        "TICAP-0136",
        "TICAP-0159",
        "TICAP-0160",
        "TICAP-0170",
        "TICAP-0176",
        "TICAP-0183",
        "TICAP-0191",
        "TICAP-0196",
        "TICAP-0210",
        "TICAP-0219",
        "TICAP-0220",
        "TICAP-0246",
        "TICAP-0265",
        "TICAP-0267",
        "TICAP-0280",
        "TICAP-0309",
        "TICAP-0397",
        "TICAP-0418",
        "TICAP-0453",
        "TICAP-0455",
        "TICAP-0495",
        "TICAP-0509",
    }
)


def apply_manual_duplicate_pairs(records: list[dict[str, object]]) -> list[str]:
    """Applies reviewed duplicate pairs without deleting the secondary abstract."""
    by_id = {str(record.get("id", "")): record for record in records}
    confirmed: list[str] = []
    for secondary_id, principal_id in MANUAL_DUPLICATE_OF.items():
        record = by_id.get(secondary_id)
        principal = by_id.get(principal_id)
        if record is None or principal is None:
            continue
        record["duplicate_of"] = principal_id
        record["duplicate_review"] = True
        confirmed.append(secondary_id)
    return confirmed


def confirm_unresolved_duplicates(
    records: list[dict[str, object]],
) -> list[str]:
    """Confirms review-duplicate groups when only one member now has an abstract."""
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        group_id = str(record.get("duplicate_group") or "").strip()
        if group_id and record.get("duplicate_review") and not record.get("duplicate_of"):
            groups[group_id].append(record)

    confirmed: list[str] = []
    for members in groups.values():
        with_abstract = [
            record
            for record in members
            if str(record.get("abstract") or "").strip()
        ]
        without_abstract = [
            record
            for record in members
            if not str(record.get("abstract") or "").strip()
        ]
        if not with_abstract or not without_abstract:
            continue
        principal = max(with_abstract, key=_completeness)
        principal_id = str(principal.get("id", ""))
        for record in without_abstract:
            record["duplicate_of"] = principal_id
            record["screening_note"] = str(record.get("screening_note") or "Duplicado")
            record["abstract_status"] = "NOTA_DESCARTE"
            record["abstract_source"] = record.get("abstract_source") or "Excel completado manualmente"
            record["abstract_origin"] = "MANUAL"
            record["abstract_quality_reason"] = (
                f"Registro duplicado confirmado del ID {principal_id}."
            )
            confirmed.append(str(record.get("id", "")))
    return confirmed


def interpret_screening_note(value: object) -> dict[str, str] | None:
    """Detects short discard notes that are not scientific abstracts."""
    text = _strip_markup(str(value or "")).strip()
    if not text:
        return None
    normalized = normalize_title(text)
    matched = SCREENING_NOTES.get(normalized)
    if matched:
        return dict(matched)
    return None


def classify_record(record: dict[str, object]) -> dict[str, str]:
    year = normalize_year(record.get("year_normalized", record.get("year", "")))
    entry_type = normalize_type(record.get("type_normalized", record.get("entry_type", "")))
    title = str(record.get("title", "")).strip()
    abstract = _strip_markup(str(record.get("abstract", "")).strip())
    screening_note = _strip_markup(str(record.get("screening_note", "")).strip())
    duplicate_of = str(record.get("duplicate_of", "")).strip()

    base = {
        "id": str(record.get("id", "")),
        "title": title,
        "abstract": abstract,
        "decision": "",
        "criterion": "",
        "justification": "",
        "technology": "",
        "application": "",
        "category": "",
        "observation": "",
    }
    if duplicate_of:
        return {
            **base,
            "decision": "DUPLICADO",
            "criterion": "ADM_DUPLICADO",
            "justification": f"Registro duplicado confirmado del ID {duplicate_of}.",
            "observation": "Posible duplicado." if record.get("duplicate_review") else "",
        }
    if not year or not 2020 <= int(year) <= 2025:
        return {
            **base,
            "decision": "FUERA_DE_PERIODO",
            "criterion": "ADM_PERIODO",
            "justification": f"El año registrado ({year or 'sin año'}) no está entre 2020 y 2025.",
        }
    if entry_type not in ACCEPTED_TYPES:
        return {
            **base,
            "decision": "TIPO_NO_ADMITIDO",
            "criterion": "ADM_TIPO",
            "justification": f"El tipo documental registrado es {entry_type or 'desconocido'}.",
            "observation": "Tipo documental sin confirmar." if not entry_type else "",
        }
    note = interpret_screening_note(screening_note or abstract)
    if note:
        return {
            **base,
            **note,
            "abstract": screening_note or abstract,
        }
    if not abstract:
        return {
            **base,
            "decision": "DUDOSO",
            "criterion": "REVISION_MANUAL",
            "justification": "El título por sí solo no aporta evidencia suficiente para una decisión definitiva.",
            "observation": "Abstract no encontrado.",
        }

    text = f" {normalize_title(title)} {normalize_title(abstract)} "
    fish_terms = (
        "fish",
        "tilapia",
        "salmon",
        "trout",
        "carp",
        "catfish",
        "piscicultura",
        "piscicola",
        "alevin",
    )
    aquaculture_terms = ("aquaculture", "aquacultura", "acuicultura", "fish farm", "fish farming")
    nonproductive_terms = (
        "wildlife",
        "wild fish",
        "capture fisheries",
        "fisheries management",
        "oceanography",
        "limnology",
        "marine ecology",
        "conservation",
    )
    nonfish_terms = (
        "shrimp",
        "prawn",
        "crustacean",
        "mollusc",
        "mollusk",
        "oyster",
        "seaweed",
        "algae",
        "crab",
        "sea cucumber",
        "camaron",
        "molusco",
        "alga",
    )
    technologies = _detect_labels(text, TECHNOLOGIES)
    applications = _detect_labels(text, APPLICATIONS)
    has_fish = _contains_any(text, fish_terms)
    has_aquaculture = _contains_any(text, aquaculture_terms)
    has_nonfish = _contains_any(text, nonfish_terms)
    review_terms = (
        " systematic review ",
        " literature review ",
        " bibliometric ",
        " scoping review ",
        " meta analysis ",
        " perspective ",
        " research agenda ",
    )
    concrete_terms = (
        " develop",
        " implement",
        " validat",
        " evaluat",
        " prototype",
        " propose",
        " deploy",
        " architecture",
        " model",
        " system",
        " case study",
        " experiment",
    )

    technology = ", ".join(technologies)
    application = ", ".join(applications)
    category = CATEGORY_BY_APPLICATION.get(applications[0], "") if applications else ""
    enrichment = {
        "technology": technology,
        "application": application,
        "category": category,
    }
    if not has_fish and not has_aquaculture:
        criterion = "CE2" if _contains_any(text, nonproductive_terms) else "CE1"
        return {
            **base,
            **enrichment,
            "decision": "EXCLUIR",
            "criterion": criterion,
            "justification": "El título y abstract no sitúan el estudio en piscicultura o acuicultura productiva.",
        }
    if has_nonfish and not has_fish:
        return {
            **base,
            **enrichment,
            "decision": "EXCLUIR",
            "criterion": "CE7",
            "justification": "El título y abstract se centran exclusivamente en organismos no piscícolas.",
        }
    if _contains_any(text, review_terms):
        return {
            **base,
            **enrichment,
            "decision": "EXCLUIR",
            "criterion": "CE6",
            "justification": "El título o abstract identifica una revisión o estudio secundario sin validación primaria.",
        }
    if not technologies:
        return {
            **base,
            **enrichment,
            "decision": "EXCLUIR",
            "criterion": "CE3",
            "justification": "El título y abstract no evidencian una TIC o tecnología digital como aporte del estudio.",
        }
    if not applications:
        return {
            **base,
            **enrichment,
            "decision": "DUDOSO",
            "criterion": "CE4",
            "justification": "Se identifica una tecnología, pero su aplicación productiva acuícola no queda clara.",
            "observation": "Requiere revisión manual.",
        }
    if not _contains_any(text, concrete_terms):
        return {
            **base,
            **enrichment,
            "decision": "DUDOSO",
            "criterion": "CE5",
            "justification": "La aplicación parece pertinente, pero no se identifica con claridad desarrollo o validación concreta.",
            "observation": "Requiere revisión manual.",
        }
    return {
        **base,
        **enrichment,
        "decision": "INCLUIR",
        "criterion": "CUMPLE_MATRIZ",
        "justification": (
            "El título y abstract evidencian contexto piscícola, una TIC aplicada y "
            "desarrollo o validación tecnológica concreta."
        ),
    }


def _bib_escape(value: object) -> str:
    return str(value or "").replace("\r\n", " ").replace("\n", " ").strip()


def write_master_bib(path: Path, records: list[dict[str, object]]) -> None:
    preferred = [
        "ticap_id",
        "abstract",
        "abstract_source",
        "abstract_status",
        "author",
        "doi",
        "issn",
        "journal",
        "booktitle",
        "keywords",
        "pages",
        "publisher",
        "title",
        "volume",
        "number",
        "issue",
        "month",
        "year",
    ]
    ignored = {
        "id",
        "citation_key",
        "entry_type",
        "doi_original",
        "doi_normalized",
        "title_original",
        "title_normalized",
        "authors_original",
        "authors_normalized",
        "year_original",
        "year_normalized",
        "type_original",
        "type_normalized",
        "duplicate_of",
        "duplicate_group",
        "duplicate_review",
        "abstract_source_url",
        "abstract_retrieved_at",
        "abstract_quality_reason",
        "abstract_origin",
        "abstract_candidate",
        "screening_note",
    }
    chunks: list[str] = []
    for record in records:
        entry_type = str(record.get("type_normalized") or record.get("entry_type") or "misc")
        citation_key = str(record.get("citation_key") or record.get("id"))
        export_record = dict(record)
        export_record["ticap_id"] = record.get("id", "")
        if record.get("doi_normalized"):
            export_record["doi"] = record["doi_normalized"]
        if record.get("year_normalized"):
            export_record["year"] = record["year_normalized"]
        fields = [field for field in preferred if _bib_escape(export_record.get(field, ""))]
        fields.extend(
            sorted(
                field
                for field, value in export_record.items()
                if field not in fields
                and field not in ignored
                and _bib_escape(value)
                and isinstance(value, (str, int, float))
            )
        )
        lines = [f"@{entry_type}{{{citation_key},"]
        for field in fields:
            lines.append(f"  {field} = {{{_bib_escape(export_record[field])}}},")
        if len(lines) > 1:
            lines[-1] = lines[-1].rstrip(",")
        lines.append("}")
        chunks.append("\n".join(lines))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")
    temporary.replace(path)

