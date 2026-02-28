"""
Document ingestion — loads .txt, .md, .pdf, .html, .csv, and .json files
into a unified Document container.

The loader normalises content from any supported format into plain text
so downstream code never needs to know the original file type.
"""

from __future__ import annotations

import logging
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """
    Immutable container for loaded document content.

    Attributes:
        content:    Full extracted text.
        filename:   Original filename.
        file_type:  File extension (e.g. ".pdf").
        char_count: Number of characters.
        word_count: Approximate word count.
    """
    content: str
    filename: str
    file_type: str
    char_count: int
    word_count: int

    @property
    def summary_line(self) -> str:
        """One-line description for CLI output."""
        return (
            f"{self.filename} ({self.file_type}) — "
            f"{self.word_count:,} words, {self.char_count:,} chars"
        )


# ── Format Registry ────────────────────────────────────────────────────────

_FORMAT_READERS: dict[str, str] = {
    ".txt":  "_read_text",
    ".md":   "_read_text",
    ".html": "_read_text",
    ".json": "_read_text",
    ".csv":  "_read_text",
    ".pdf":  "_read_pdf",
}


class DocumentLoader:
    """
    Reads files from disk and returns unified Document objects.

    Supported formats: .txt, .md, .pdf, .html, .csv, .json
    """

    SUPPORTED_EXTENSIONS = set(_FORMAT_READERS.keys())

    # ── Load from File ──────────────────────────────────────────────────

    @classmethod
    def load(cls, path: str | Path) -> Document:
        """
        Load a document from a file path.

        Args:
            path: Absolute or relative path to the file.

        Returns:
            A populated Document.

        Raises:
            FileNotFoundError: If the path doesn't exist.
            ValueError: If the format is unsupported or the file is empty.
        """
        path = Path(path).resolve()

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        ext = path.suffix.lower()
        if ext not in _FORMAT_READERS:
            supported = ", ".join(sorted(_FORMAT_READERS))
            raise ValueError(
                f"Unsupported file type '{ext}'. Supported: {supported}"
            )

        reader = getattr(cls, _FORMAT_READERS[ext])
        content: str = reader(path).strip()

        if not content:
            raise ValueError(f"File is empty after extraction: {path.name}")

        doc = Document(
            content=content,
            filename=path.name,
            file_type=ext,
            char_count=len(content),
            word_count=len(content.split()),
        )
        logger.info("Loaded: %s", doc.summary_line)
        return doc

    # ── Load from String ────────────────────────────────────────────────

    @classmethod
    def load_text(cls, text: str, filename: str = "input.txt") -> Document:
        """
        Create a Document directly from a string.

        Useful for CLI --text mode and MCP tool inputs.
        """
        content = text.strip()
        if not content:
            raise ValueError("Input text is empty.")

        return Document(
            content=content,
            filename=filename,
            file_type=".txt",
            char_count=len(content),
            word_count=len(content.split()),
        )

    # ── Format-Specific Readers ─────────────────────────────────────────

    @staticmethod
    def _read_text(path: Path) -> str:
        """Read any plain-text format."""
        return path.read_text(encoding="utf-8", errors="replace")

    @staticmethod
    def _read_pdf(path: Path) -> str:
        """Extract text from all pages of a PDF."""
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "pypdf is required for PDF support. Install it with: "
                "pip install pypdf"
            )

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)