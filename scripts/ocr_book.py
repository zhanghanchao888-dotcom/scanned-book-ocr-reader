from __future__ import annotations

import argparse
import re
import time
from pathlib import Path

import numpy as np
import pdfplumber
import pypdfium2 as pdfium
from rapidocr_onnxruntime import RapidOCR


NOISE_PATTERNS = [
    re.compile(r"图书库"),
    re.compile(r"微信"),
    re.compile(r"QQ?\s*[0-9xX]{6,}"),
]


def is_noise(line: str) -> bool:
    compact = re.sub(r"\s+", "", line)
    if not compact:
        return True
    if len(compact) <= 2 and compact.isdigit():
        return True
    return any(pattern.search(compact) for pattern in NOISE_PATTERNS)


def sort_ocr_result(result: list | None) -> list[str]:
    rows = []
    for box, text, score in result or []:
        if score < 0.45:
            continue
        y = min(point[1] for point in box)
        x = min(point[0] for point in box)
        text = str(text).strip()
        if text and not is_noise(text):
            rows.append((y, x, text))
    return [text for _, _, text in sorted(rows)]


def merge_wrapped_lines(lines: list[str]) -> str:
    paragraphs: list[str] = []
    current = ""
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if not current:
            current = line
            continue
        if re.search(r"[。！？：；.!?;:]$", current):
            paragraphs.append(current)
            current = line
        elif re.search(r"[\u4e00-\u9fffA-Za-z0-9]$", current) and re.match(r"^[\u4e00-\u9fffA-Za-z0-9]", line):
            current += line
        else:
            current += " " + line
    if current:
        paragraphs.append(current)
    return "\n\n".join(paragraphs)


def sample_text_layer(pdf_path: Path, sample_pages: int = 8) -> tuple[int, int]:
    with pdfplumber.open(str(pdf_path)) as pdf:
        page_count = len(pdf.pages)
        chars = 0
        for page in pdf.pages[: min(sample_pages, page_count)]:
            chars += len(page.extract_text() or "")
    return page_count, chars


def extract_text_layer(pdf_path: Path, out: Path) -> None:
    pages_dir = out / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    with pdfplumber.open(str(pdf_path)) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            (pages_dir / f"page_{index:03}.txt").write_text(text.strip() + "\n", encoding="utf-8")
    combine_pages(pdf_path, out, len(pdf.pages), "text-layer")


def ocr_page(pdf: pdfium.PdfDocument, ocr: RapidOCR, index: int, scale: float) -> str:
    image = pdf[index].render(scale=scale).to_pil().convert("RGB")
    result, _ = ocr(np.array(image))
    return merge_wrapped_lines(sort_ocr_result(result))


def combine_pages(pdf_path: Path, out: Path, page_count: int, mode: str) -> None:
    pages_dir = out / "pages"
    md_parts = [f"# OCR/Text: {pdf_path.stem}\n\nSource: `{pdf_path}`\nMode: `{mode}`\n"]
    txt_parts = []
    for page_no in range(1, page_count + 1):
        page_file = pages_dir / f"page_{page_no:03}.txt"
        if not page_file.exists():
            continue
        text = page_file.read_text(encoding="utf-8").strip()
        if not text:
            continue
        md_parts.append(f"\n\n## Page {page_no}\n\n{text}\n")
        txt_parts.append(f"\n\n[Page {page_no}]\n{text}\n")
    (out / "book_ocr.md").write_text("".join(md_parts), encoding="utf-8")
    (out / "book_ocr.txt").write_text("".join(txt_parts).strip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract or OCR a book PDF into per-page TXT plus combined Markdown/TXT.")
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scale", type=float, default=1.5)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--ocr", action="store_true", help="Force OCR even if a text layer is detected.")
    args = parser.parse_args()

    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    args.out.mkdir(parents=True, exist_ok=True)
    page_count, sample_chars = sample_text_layer(pdf_path)
    if sample_chars >= 200 and not args.ocr and args.start == 1 and args.end is None:
        print(f"Usable text layer detected in first pages ({sample_chars} chars). Extracting without OCR.")
        extract_text_layer(pdf_path, args.out)
        return

    pages_dir = args.out / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    page_count = len(pdf)
    start = max(1, args.start)
    end = min(args.end or page_count, page_count)

    ocr = RapidOCR()
    (args.out / "manifest.txt").write_text(
        f"pdf={pdf_path}\npages={page_count}\nscale={args.scale}\nrange={start}-{end}\nmode=ocr\n",
        encoding="utf-8",
    )

    for page_no in range(start, end + 1):
        page_file = pages_dir / f"page_{page_no:03}.txt"
        if page_file.exists() and page_file.stat().st_size > 0 and not args.force:
            print(f"[skip] {page_no}/{page_count}")
            continue
        t0 = time.time()
        try:
            text = ocr_page(pdf, ocr, page_no - 1, args.scale)
        except Exception as exc:
            text = f"[OCR_ERROR page={page_no}: {type(exc).__name__}: {exc}]"
        page_file.write_text(text.strip() + "\n", encoding="utf-8")
        print(f"[done] {page_no}/{page_count} chars={len(text)} sec={time.time() - t0:.1f}", flush=True)

    combine_pages(pdf_path, args.out, page_count, "ocr")
    print(f"[combined] {args.out / 'book_ocr.md'}")
    print(f"[combined] {args.out / 'book_ocr.txt'}")


if __name__ == "__main__":
    main()

