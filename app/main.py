from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from app.routes.resume import router as resume_router


app = FastAPI(title="AI Resume Analyzer API")
app.include_router(resume_router)


@app.get("/")
def home():
    return {"message": "API is running"}


@app.get("/health", response_class=PlainTextResponse)
def health_check() -> str:
    return "API is running"
