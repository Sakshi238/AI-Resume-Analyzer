from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.services.ai_service import AIServiceError, ResumeAnalysis, analyze_resume
from app.utils.parser import extract_text

router = APIRouter(tags=["resume"])
UPLOAD_DIR = Path("uploads")


def _validate_pdf(file: UploadFile) -> None:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")


async def _save_upload(file: UploadFile) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / file.filename

    content = await file.read()
    with file_path.open("wb") as output_file:
        output_file.write(content)

    return file_path


@router.get("/resume/sample")
def sample_resume_route() -> dict[str, str]:
    return {"message": "Resume routes are set up"}


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)) -> dict[str, str]:
    _validate_pdf(file)
    file_path = await _save_upload(file)

    extracted_text = extract_text(file_path)
    preview = extracted_text[:500]

    return {"filename": file.filename, "preview": preview}


@router.post("/analyze", response_model=ResumeAnalysis)
async def analyze_uploaded_resume(
    file: UploadFile = File(...),
    job_description: str = Form(default=""),
) -> ResumeAnalysis:
    _validate_pdf(file)
    file_path = await _save_upload(file)

    extracted_text = extract_text(file_path)
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found in PDF")

    try:
        analysis = analyze_resume(
            text=extracted_text,
            job_description=job_description.strip() or None,
        )
    except AIServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to analyze resume") from exc

    return analysis
