import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai import OpenAIError
from pydantic import BaseModel, Field, ValidationError

load_dotenv()


class AIServiceError(Exception):
    """Raised when resume analysis fails in the AI service layer."""


class ResumeAnalysis(BaseModel):
    skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    ATS_score: int = Field(ge=0, le=100)
    suggestions: list[str] = Field(default_factory=list)


BASELINE_SKILLS = [
    "Python",
    "SQL",
    "Git",
    "REST APIs",
    "FastAPI",
    "Docker",
    "AWS",
    "CI/CD",
    "Testing",
    "Communication",
]

SKILL_KEYWORDS = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "SQL",
    "NoSQL",
    "FastAPI",
    "Django",
    "Flask",
    "React",
    "Node.js",
    "REST APIs",
    "GraphQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "CI/CD",
    "Git",
    "Testing",
    "PyTest",
    "Communication",
]


def _clean_json_content(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()
    return cleaned


def _extract_skills_from_jd(job_description: str) -> list[str]:
    jd_lower = job_description.lower()
    return [skill for skill in SKILL_KEYWORDS if skill.lower() in jd_lower]


def _infer_missing_skills(
    text: str,
    detected_skills: list[str],
    job_description: str | None = None,
) -> list[str]:
    combined_text = f"{text} {' '.join(detected_skills)}".lower()
    target_skills = (
        _extract_skills_from_jd(job_description) if job_description else BASELINE_SKILLS
    )
    if not target_skills:
        target_skills = BASELINE_SKILLS

    missing: list[str] = []
    for skill in target_skills:
        if skill.lower() not in combined_text:
            missing.append(skill)
    return missing[:5]


def analyze_resume(text: str, job_description: str | None = None) -> ResumeAnalysis:
    if not text.strip():
        raise AIServiceError("Resume text is empty")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIServiceError("OPENAI_API_KEY is not set")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    comparison_context = (
        f"Job Description:\n{job_description.strip()}\n\n"
        if job_description and job_description.strip()
        else ""
    )

    prompt = f"""
Analyze the following resume text{" against the provided job description" if comparison_context else ""}.
Return JSON only (no markdown, no extra text).
Use exactly this schema and keys:
{{
  "skills": [],
  "missing_skills": [],
  "ATS_score": 0,
  "suggestions": []
}}
Rules:
- skills, missing_skills, suggestions must be arrays of strings.
- ATS_score must be an integer between 0 and 100.
- missing_skills must list realistic gaps.
- If a job description is provided, missing_skills and suggestions must be based on JD requirements.
- If the resume is very strong, still include up to 3 improvement areas as missing_skills.

{comparison_context}Resume text:
{text}
""".strip()

    try:
        response = client.chat.completions.create(
            model=model,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "resume_analysis",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "skills": {"type": "array", "items": {"type": "string"}},
                            "missing_skills": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "ATS_score": {"type": "integer", "minimum": 0, "maximum": 100},
                            "suggestions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["skills", "missing_skills", "ATS_score", "suggestions"],
                    },
                },
            },
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a resume analysis assistant. "
                        "Return strict JSON only with the required schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(_clean_json_content(content))
    except json.JSONDecodeError as exc:
        raise AIServiceError("Model response was not valid JSON") from exc
    except OpenAIError as exc:
        raise AIServiceError("OpenAI request failed") from exc
    except Exception as exc:
        raise AIServiceError("Unexpected error during resume analysis") from exc

    try:
        analysis = ResumeAnalysis.model_validate(parsed)
    except ValidationError as exc:
        raise AIServiceError("Model response did not match expected schema") from exc

    if not analysis.missing_skills:
        analysis.missing_skills = _infer_missing_skills(
            text=text,
            detected_skills=analysis.skills,
            job_description=job_description,
        )

    return analysis
