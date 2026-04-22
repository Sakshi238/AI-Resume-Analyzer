from pathlib import Path

from pypdf import PdfReader


def extract_text(file_path: str | Path) -> str:
    reader = PdfReader(str(file_path))
    pages_text: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages_text.append(page_text)

    return "\n".join(pages_text).strip()
