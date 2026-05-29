# Scanned Book OCR Reader

An agent skill and reusable Python workflow for turning scanned or image-only book PDFs into OCR text and personalized reading reports.

It is designed for local, free OCR first:

- Detect whether a PDF already has a text layer.
- Install missing local OCR dependencies when needed.
- OCR scanned pages with per-page caching and resume support.
- Export both Markdown and plain text.
- Run basic OCR quality checks.
- Guide an agent through chapter-level compression and personalized reading reports.

## Repository Layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── report_template.md
└── scripts/
    ├── analyze_ocr.py
    ├── check_deps.py
    └── ocr_book.py
```

## Install As A Codex Skill

Copy or clone this repository into your Codex skills directory:

```powershell
git clone https://github.com/YOUR_NAME/scanned-book-ocr-reader.git "$env:USERPROFILE\.codex\skills\scanned-book-ocr-reader"
```

Then invoke it naturally:

```text
Use $scanned-book-ocr-reader to OCR this scanned PDF and create a personalized reading report.
```

## Use The Scripts Directly

Check dependencies:

```powershell
py -X utf8 scripts/check_deps.py
```

Install missing free local OCR dependencies:

```powershell
py -X utf8 scripts/check_deps.py --install
```

Run a small sample first:

```powershell
py -X utf8 scripts/ocr_book.py --pdf "C:\path\book.pdf" --out "C:\tmp\book_ocr\book-name" --start 30 --end 32 --ocr --force
```

Run the full book:

```powershell
py -X utf8 scripts/ocr_book.py --pdf "C:\path\book.pdf" --out "C:\tmp\book_ocr\book-name"
```

Analyze OCR output:

```powershell
py -X utf8 scripts/analyze_ocr.py --out "C:\tmp\book_ocr\book-name"
```

Outputs:

- `book_ocr.md`
- `book_ocr.txt`
- `pages/page_001.txt`, `pages/page_002.txt`, ...
- `ocr_quality_report.md`

## Personalization Workflow

When creating a personalized reading report, the agent should separate:

- What the book says.
- What applies to the user based on known facts.
- What requires more user context.
- What is risky or should not be copied blindly.

If more detail is needed, ask a short set of questions about the user's goal, current stage, decision, risk preference, and available resources.

## Privacy And Copyright

Do not commit:

- Source PDFs.
- OCR outputs.
- Full book text.
- Personal documents.
- Private reading reports.

This repository contains only the workflow, scripts, and templates.

## License

MIT

