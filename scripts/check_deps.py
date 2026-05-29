from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys


REQUIRED = {
    "pdfplumber": "pdfplumber",
    "pypdfium2": "pypdfium2",
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "rapidocr_onnxruntime": "rapidocr-onnxruntime",
    "numpy": "numpy",
}


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def install(packages: list[str]) -> int:
    cmd = [sys.executable, "-m", "pip", "install", *packages]
    print("Installing:", " ".join(packages), flush=True)
    return subprocess.call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check and optionally install OCR dependencies.")
    parser.add_argument("--install", action="store_true", help="Install missing packages with pip.")
    args = parser.parse_args()

    missing_modules = [module for module in REQUIRED if not has_module(module)]
    missing_packages = [REQUIRED[module] for module in missing_modules]

    if not missing_modules:
        print("All required OCR dependencies are available.")
        return

    print("Missing modules:")
    for module, package in zip(missing_modules, missing_packages):
        print(f"- {module} (pip package: {package})")

    if not args.install:
        print("Run again with --install to install missing free local OCR dependencies.")
        raise SystemExit(1)

    code = install(missing_packages)
    if code != 0:
        raise SystemExit(code)

    still_missing = [module for module in REQUIRED if not has_module(module)]
    if still_missing:
        print("Still missing after install:", ", ".join(still_missing))
        raise SystemExit(1)

    print("Dependencies installed and importable.")


if __name__ == "__main__":
    main()

