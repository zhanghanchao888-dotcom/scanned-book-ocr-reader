---
name: scanned-book-ocr-reader
description: Use when a user provides a scanned or image-only book PDF and asks to OCR, read, summarize, extract useful points, or create a personalized reading report. Handles free local OCR setup, per-page OCR caching, Markdown/TXT export, quality checks, chapter-level compression, and optional user-context questions for personalized reports.
---

# Scanned Book OCR Reader

## Use this when

- The user provides a PDF book whose text cannot be copied or extracted.
- The user asks to "read this book", "OCR this PDF", "make a reading report", "extract useful points", or "combine it with my situation".
- The source is a scanned Chinese or English PDF and local/free OCR is preferred.

## Core workflow

1. Confirm the PDF exists and inspect size/page count.
2. Try text extraction first with `pdfplumber`; skip OCR if the PDF already has a usable text layer.
3. If OCR is needed, run `scripts/check_deps.py --install` to install missing free local OCR dependencies.
4. Run a 1-3 page OCR sample before the full book.
5. If sample quality is readable, OCR the full book with `scripts/ocr_book.py`.
6. Run `scripts/analyze_ocr.py` on the output directory.
7. Read the generated `book_ocr.md` or `book_ocr.txt` by chapter, not all at once.
8. Extract table of contents, parts, chapter titles, page ranges, repeated concepts, and actionable ideas.
9. If the user wants personalization, ask the minimum useful questions before final synthesis.
10. Save final outputs beside the OCR results.

## Commands

Check or install dependencies:

```powershell
py -X utf8 scripts/check_deps.py --install
```

Run a sample:

```powershell
py -X utf8 scripts/ocr_book.py --pdf "C:\path\book.pdf" --out "C:\tmp\book_ocr\book-name" --start 30 --end 32 --force
```

Run the full book:

```powershell
py -X utf8 scripts/ocr_book.py --pdf "C:\path\book.pdf" --out "C:\tmp\book_ocr\book-name"
```

Analyze OCR output:

```powershell
py -X utf8 scripts/analyze_ocr.py --out "C:\tmp\book_ocr\book-name"
```

## Dependency policy

- Prefer free local OCR: `rapidocr-onnxruntime`, `pypdfium2`, `Pillow`, `opencv-python`.
- Do not use paid/cloud OCR unless the user explicitly asks or approves.
- Do not reinstall packages blindly. `check_deps.py` detects modules first.
- If installation fails, report the failed package and suggest alternatives such as Tesseract with Chinese language data or PaddleOCR.

## Personalization

When the user asks to combine the book with their situation, do not invent missing personal context. Use visible conversation facts and state assumptions.

Ask up to five questions when deeper personalization matters:

1. What problem should this book help with: career, money, startup, study, relationships, or life choices?
2. What stage are you in: student, employed, freelance, founder, transition, or other?
3. What concrete decision or question are you trying to answer?
4. What is your risk preference: conservative, balanced, or aggressive?
5. What resources can you invest: time per week, budget, skills, network?

Optional user materials: resume, annual goals, project list, reflection notes, career plan, reading notes, or current dilemmas. Ask the user to redact sensitive details.

## Report shape

Use `references/report_template.md` when producing a final report.

Always separate:

- What the book says.
- What applies to the user based on known facts.
- What needs more user context.
- What is risky or should not be copied blindly.

For large books, produce a short interim structure first, then the final report after chapter-level compression.

