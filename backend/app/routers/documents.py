
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.services.document_processor import (
    extract_text_from_pdf,
    extract_text_from_image,
    extract_text_from_scanned_pdf,
)
from app.services.ai_analyzer import analyze_clinical_text
from app.services.report_storage import (
    save_report,
    get_report_by_id,
    get_report_history,
)

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_TYPES = {
    ".pdf": ["application/pdf"],
    ".png": ["image/png"],
    ".jpg": ["image/jpeg"],
    ".jpeg": ["image/jpeg"],
    ".webp": ["image/webp"],
}


class ClinicalText(BaseModel):
    text: str


def generate_report(text: str):
    try:
        return analyze_clinical_text(text)
    except Exception as exc:
        print(f"AI analysis failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail=(
                "AI analysis failed. Check that Ollama is running "
                "and the configured model is installed."
            ),
        ) from exc


@router.post("/analyze/text")
def analyze_text(request: ClinicalText):
    clinical_text = request.text.strip()

    if not clinical_text:
        raise HTTPException(
            status_code=400,
            detail="Clinical text cannot be empty.",
        )

    report = generate_report(clinical_text)
    report_data = report.model_dump()

    try:
        report_id = save_report(
            report=report_data,
            input_type="text",
            character_count=len(clinical_text),
        )
    except Exception as exc:
        print(f"Report saving failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail="The report was generated but could not be saved.",
        ) from exc

    return {
        "report_id": report_id,
        "input_type": "text",
        "status": "processed",
        "report": report_data,
    }


@router.post("/analyze/file")
async def analyze_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type.",
        )

    if file.content_type not in ALLOWED_TYPES[extension]:
        raise HTTPException(
            status_code=415,
            detail="File extension and content type do not match.",
        )

    contents = await file.read()
    await file.close()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB size limit.",
        )

    try:
        if extension == ".pdf":
            extracted_text = extract_text_from_pdf(contents)

            if not extracted_text.strip():
                extracted_text = extract_text_from_scanned_pdf(contents)

            input_type = "pdf"
        else:
            extracted_text = extract_text_from_image(contents)
            input_type = "image"

    except Exception as exc:
        print(
            f"Document extraction failed: "
            f"{type(exc).__name__}: {exc}"
        )
        raise HTTPException(
            status_code=422,
            detail=(
                "Unable to extract text from this document. "
                "Please check the file or upload a clearer version."
            ),
        ) from exc

    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text was detected in the document.",
        )

    # TEMPORARY DEBUGGING: inspect extracted document text.
    print("\n========== EXTRACTED DOCUMENT TEXT ==========")
    print(f"Filename: {filename}")
    print(f"File type: {input_type}")
    print(f"Total characters extracted: {len(extracted_text)}")
    print(extracted_text[:4000])
    print("========== END EXTRACTED TEXT ==========\n")

    report = await run_in_threadpool(
        generate_report,
        extracted_text,
    )
    report_data = report.model_dump()

    try:
        report_id = save_report(
            report=report_data,
            input_type=input_type,
            character_count=len(extracted_text),
            filename=filename,
        )
    except Exception as exc:
        print(f"Report saving failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail="The report was generated but could not be saved.",
        ) from exc

    return {
        "report_id": report_id,
        "filename": filename,
        "input_type": input_type,
        "character_count": len(extracted_text),
        "status": "processed",
        "report": report_data,
    }


@router.get("/reports")
def list_reports(
    limit: int = Query(default=50, ge=1, le=100),
):
    return {
        "reports": get_report_history(limit=limit),
    }


@router.get("/reports/{report_id}")
def read_report(report_id: int):
    saved_report = get_report_by_id(report_id)

    if saved_report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    return saved_report