import os
import re
import csv
import hashlib
from pathlib import Path

def escape_bibtex_dollars(val: str) -> str:
    """Escapes unescaped literal dollar signs ($ -> \\$) for BibTeX / Better BibTeX compatibility."""
    if not val or '$' not in val:
        return val
    return re.sub(r'(?<!\\)\$', r'\\$', val)

def generate_zotero_exports(root_dir: str | Path = ".") -> dict[str, int]:
    root = Path(root_dir).resolve()
    master_bib_path = root / "TICaP-509" / "data" / "master" / "TICaP_master.bib"
    mirror_bib_path = root / "TICaPALL" / "masterall509.bib"
    csv_path = root / "TICaP-509" / "output" / "clasificacion" / "clasificacion_preliminar.csv"
    export_dir = root / "zotero_export"
    export_dir.mkdir(parents=True, exist_ok=True)

    # Hashes before
    h_master_before = hashlib.sha256(master_bib_path.read_bytes()).hexdigest()
    h_mirror_before = hashlib.sha256(mirror_bib_path.read_bytes()).hexdigest()

    # Read classifications
    with open(csv_path, encoding='utf-8-sig') as f:
        csv_rows = list(csv.DictReader(f))

    classifications = {
        r['ID']: {
            'decision': r['Decisión'],
            'criterio': r['Criterio aplicado']
        }
        for r in csv_rows
    }

    # Read master bib
    master_text = master_bib_path.read_text(encoding='utf-8')
    entries_raw = [e.strip() for e in re.split(r'\n(?=@(?:article|inproceedings)\s*\{)', master_text) if e.strip()]

    internal_fields = {
        'abstract_status', 'abstract_source', 'source_index', 
        'abstract_original_no_validado', 'ticap_id'
    }

    desired_fields_order = [
        'title', 'author', 'year', 'month', 'journal', 'booktitle',
        'volume', 'issue', 'number', 'pages', 'publisher', 'doi', 'url',
        'issn', 'isbn', 'abstract', 'keywords', 'language'
    ]

    master_entries = []
    subsets = {
        'INCLUIR': [],
        'EXCLUIR': [],
        'DUPLICADO': [],
        'TIPO_NO_ADMITIDO': []
    }

    for e in entries_raw:
        m_header = re.match(r'@([A-Za-z]+)\s*\{\s*([^,\s]+)\s*,', e)
        if not m_header:
            raise ValueError(f"Cabecera inválida:\n{e[:100]}")
        entry_type = m_header.group(1).lower()

        m_id = re.search(r'ticap_id\s*=\s*\{(TICAP-\d{4})\}', e)
        if not m_id:
            raise ValueError(f"ticap_id no encontrado:\n{e[:100]}")
        ticap_id = m_id.group(1)

        # Extract fields with brace matching
        fields = {}
        pos = m_header.end()
        while pos < len(e):
            m_f = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', e[pos:])
            if not m_f:
                break
            f_name = m_f.group(1).lower()
            val_start = pos + m_f.end()

            depth = 1
            val_end = val_start
            while val_end < len(e) and depth > 0:
                if e[val_end] == '\\':
                    val_end += 2
                    continue
                if e[val_end] == '{':
                    depth += 1
                elif e[val_end] == '}':
                    depth -= 1
                val_end += 1

            f_val = e[val_start:val_end-1]
            fields[f_name] = f_val
            pos = val_end

        # Decision tags
        c_info = classifications[ticap_id]
        decision = c_info['decision']
        criterio = c_info['criterio']

        tag_decision = f"TICaP:{decision}"
        tag_criterio = f"TICaP:{criterio}"

        # Keywords handling
        orig_keywords = fields.get('keywords', '').strip()
        if orig_keywords:
            kw_list = [k.strip() for k in re.split(r'[,;]', orig_keywords) if k.strip()]
            if tag_decision not in kw_list:
                kw_list.append(tag_decision)
            if tag_criterio not in kw_list:
                kw_list.append(tag_criterio)
            new_keywords = ", ".join(kw_list)
        else:
            new_keywords = f"{tag_decision}, {tag_criterio}"

        fields['keywords'] = new_keywords

        # Remove internal fields
        for internal in internal_fields:
            fields.pop(internal, None)

        # Apply escaping to all text fields ($ -> \\$)
        for f_name in list(fields.keys()):
            fields[f_name] = escape_bibtex_dollars(fields[f_name])

        # Construct entry lines
        lines = [f"@{entry_type}{{{ticap_id},"]
        for f_name in desired_fields_order:
            if f_name in fields:
                lines.append(f"  {f_name} = {{{fields[f_name]}}},")
        for f_name, f_val in fields.items():
            if f_name not in desired_fields_order:
                lines.append(f"  {f_name} = {{{f_val}}},")

        lines[-1] = lines[-1].rstrip(',')
        lines.append("}\n")

        entry_str = "\n".join(lines)
        master_entries.append(entry_str)
        subsets[decision].append(entry_str)

    # Write files
    (export_dir / "TICaP_Zotero_Master_509.bib").write_text("\n".join(master_entries), encoding='utf-8')
    (export_dir / "TICaP_Zotero_01_Incluidos_229.bib").write_text("\n".join(subsets['INCLUIR']), encoding='utf-8')
    (export_dir / "TICaP_Zotero_02_Excluidos_261.bib").write_text("\n".join(subsets['EXCLUIR']), encoding='utf-8')
    (export_dir / "TICaP_Zotero_03_Duplicados_18.bib").write_text("\n".join(subsets['DUPLICADO']), encoding='utf-8')
    (export_dir / "TICaP_Zotero_04_Tipo_No_Admitido_1.bib").write_text("\n".join(subsets['TIPO_NO_ADMITIDO']), encoding='utf-8')

    # Verify hashes unchanged
    assert hashlib.sha256(master_bib_path.read_bytes()).hexdigest() == h_master_before
    assert hashlib.sha256(mirror_bib_path.read_bytes()).hexdigest() == h_mirror_before

    return {
        "master": len(master_entries),
        "incluidos": len(subsets['INCLUIR']),
        "excluidos": len(subsets['EXCLUIR']),
        "duplicados": len(subsets['DUPLICADO']),
        "tipo_no_admitido": len(subsets['TIPO_NO_ADMITIDO']),
    }

if __name__ == "__main__":
    counts = generate_zotero_exports()
    print("Export results:", counts)
