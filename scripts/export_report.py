import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

from cloudsec_rag.export_report import export_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Export an eval run JSON to Markdown and CSV summaries.")
    parser.add_argument("report", type=Path, help="Path to a reports/runs/*.json file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/summaries"),
        help="Directory where summary files should be written",
    )
    args = parser.parse_args()

    markdown_path, csv_path = export_report(args.report, args.output_dir)
    print(f"Wrote Markdown summary to {markdown_path}")
    print(f"Wrote CSV summary to {csv_path}")


if __name__ == "__main__":
    main()
