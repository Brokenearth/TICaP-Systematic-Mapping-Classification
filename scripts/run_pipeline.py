from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.pipeline_steps import run_all, run_reclassify_from_completed_excel


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ejecuta el flujo reproducible del mapeo sistemático TICaP."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Raíz del proyecto.",
    )
    parser.add_argument(
        "--sin-internet",
        action="store_true",
        help="No consulta fuentes externas para abstracts.",
    )
    parser.add_argument(
        "--excel-abstracts",
        type=Path,
        nargs="?",
        const=Path("."),
        default=None,
        help=(
            "Reclasifica usando el Excel con abstracts completos. "
            "Si no se indica ruta, usa output/excel completo."
        ),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if args.excel_abstracts is not None:
        excel_arg = None if args.excel_abstracts == Path(".") else args.excel_abstracts
        summary = run_reclassify_from_completed_excel(root, excel_arg)
    else:
        summary = run_all(root, allow_network=not args.sin_internet)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

