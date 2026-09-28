
import io
import os
import shutil

import pymupdf
import pytesseract
from PIL import Image, ImageOps


# Use an explicitly configured Tesseract path when provided.
# Otherwise, use the Windows installation path if it exists,
# or let pytesseract locate Tesseract on Linux.
configured_tesseract_path = os.getenv("TESSERACT_CMD")

if configured_tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = configured_tesseract_path
elif os.name == "nt":
    windows_tesseract_path = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    if os.path.isfile(windows_tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = (
            windows_tesseract_path
        )
else:
    linux_tesseract_path = shutil.which("tesseract")
    if linux_tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = (
            linux_tesseract_path
        )


def extract_text_from_image(contents: bytes) -> str:
    """Extract text from an image using OCR."""
    try:
        with Image.open(io.BytesIO(contents)) as image:
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")

            extracted_text = pytesseract.image_to_string(
                image,
                config="--psm 3",
            )

        return extracted_text.strip()

    except Exception as exc:
        raise ValueError(
            "Unable to read the image or perform OCR."
        ) from exc


def extract_text_from_pdf(contents: bytes) -> str:
    """
    Extract text from every PDF page.

    Pages with selectable text use direct extraction.
    Pages without selectable text are rendered and processed with OCR.
    This supports PDFs containing a mixture of scanned and digital pages.
    """
    extracted_pages = []

    try:
        with pymupdf.open(
            stream=contents,
            filetype="pdf",
        ) as document:

            if document.needs_pass:
                raise ValueError(
                    "The PDF is password-protected."
                )

            if len(document) == 0:
                raise ValueError("The PDF contains no pages.")

            for page_number, page in enumerate(document, start=1):
                page_text = page.get_text("text").strip()

                # Run OCR when the page has no selectable text.
                if not page_text:
                    pixmap = page.get_pixmap(
                        dpi=200,
                        alpha=False,
                    )

                    image_bytes = pixmap.tobytes("png")
                    page_text = extract_text_from_image(image_bytes)

                if page_text:
                    extracted_pages.append(
                        f"--- Page {page_number} ---\n{page_text}"
                    )

        return "\n\n".join(extracted_pages).strip()

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError(
            "Unable to read the PDF or extract its text."
        ) from exc


def extract_text_from_scanned_pdf(contents: bytes) -> str:
    """
    Compatibility wrapper for existing router imports.

    PDF extraction now handles scanned pages automatically.
    """
    return extract_text_from_pdf(contents)