import re
from pathlib import Path
from typing import Dict, List

# try optional heavy libs
_pdfplumber = None
_docx = None
_fitz = None

try:
    import pdfplumber as _pdfplumber  # pip install pdfplumber
except Exception:
    _pdfplumber = None

try:
    import docx as _docx  # pip install python-docx
except Exception:
    _docx = None

try:
    import fitz as _fitz  # pip install PyMuPDF
except Exception:
    _fitz = None


class ResumeParser:
    """Extracts text from various resume formats with graceful fallbacks."""

    def __init__(self):
        self.supported_formats = [".pdf", ".docx", ".doc"]

    def parse_resume(self, file_path: str) -> Dict[str, str]:
        file_ext = Path(file_path).suffix.lower()

        if file_ext == ".pdf":
            text = self._extract_pdf(file_path)
        elif file_ext in [".docx", ".doc"]:
            text = self._extract_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        return {"raw_text": text or "", "file_name": Path(file_path).name, "file_format": file_ext}

    def _extract_pdf(self, file_path: str) -> str:
        """Try pdfplumber, then PyMuPDF, otherwise return empty string with warning text."""
        # pdfplumber preferred
        if _pdfplumber:
            try:
                text = ""
                with _pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        ptext = page.extract_text()
                        if ptext:
                            text += ptext + "\n"
                return text.strip()
            except Exception:
                # fall through to next method
                pass

        # PyMuPDF fallback
        if _fitz:
            try:
                doc = _fitz.open(file_path)
                text = ""
                for page in doc:
                    ptext = page.get_text("text")
                    if ptext:
                        text += ptext + "\n"
                return text.strip()
            except Exception:
                pass

        # Last resort: return an informative placeholder (avoid raising at import)
        return "[PDF parsing not available: install pdfplumber or PyMuPDF in the venv]"

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx if available."""
        if _docx:
            try:
                doc = _docx.Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs]).strip()
            except Exception:
                pass

        return "[DOCX parsing not available: install python-docx in the venv]"

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume text"""
        contact_info = {}

        # Email
        email_pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, text or "")
        contact_info["email"] = emails[0] if emails else None

        # Phone
        phone_pattern = r"\+?1?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        phones = re.findall(phone_pattern, text or "")
        contact_info["phone"] = phones[0] if phones else None

        # LinkedIn
        linkedin_pattern = r"linkedin\.com/in/[a-zA-Z0-9\-]+"
        linkedin = re.findall(linkedin_pattern, text or "", re.IGNORECASE)
        contact_info["linkedin"] = linkedin[0] if linkedin else None

        return contact_info
    