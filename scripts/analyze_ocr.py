from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize OCR output quality.")
    parser.add_argument("--out", type=Path, required=True, help="OCR output directory containing pages/page_*.txt")
    parser.add_argument("--short-threshold", type=int, default=80)
    args = parser.parse_args()

    pages_dir = args.out / "pages"
    if not pages_dir.exists():
        raise FileNotFoundError(pages_dir)

    rows = []
    for page_file in sorted(pages_dir.glob("page_*.txt")):
        page_no = int(page_file.stem.split("_")[1])
        text = page_file.read_text(encoding="utf-8").strip()
        preview = text[:80].replace("\n", " ")
        rows.append((page_no, len(text), preview))

    total_chars = sum(length for _, length, _ in rows)
    empty = [page for page, length, _ in rows if length == 0]
    short = [(page, length, preview) for page, length, preview in rows if 0 < length < args.short_threshold]
    errors = [(page, preview) for page, _, preview in rows if "OCR_ERROR" in preview]

    report_lines = [
        "# OCR Quality Report",
        "",
        f"Pages processed: {len(rows)}",
        f"Total characters: {total_chars}",
        f"Empty pages: {len(empty)}",
        f"Short non-empty pages (<{args.short_threshold} chars): {len(short)}",
        f"Error pages: {len(errors)}",
        "",
        "## Empty Pages",
        ", ".join(map(str, empty)) if empty else "None",
        "",
        "## Short Page Samples",
    ]
    for page, length, preview in short[:80]:
        report_lines.append(f"- Page {page}: chars={length} preview={preview}")
    if len(short) > 80:
        report_lines.append(f"- ... {len(short) - 80} more")

    if errors:
        report_lines.extend(["", "## Error Pages"])
        for page, preview in errors:
            report_lines.append(f"- Page {page}: {preview}")

    report = "\n".join(report_lines) + "\n"
    (args.out / "ocr_quality_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()

