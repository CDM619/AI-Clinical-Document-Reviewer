
import io

import pymupdf
import pytesseract
from PIL import Image, ImageOps


# Windows Tesseract OCR installation path.
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
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