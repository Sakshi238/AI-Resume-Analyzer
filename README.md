# AI Resume Analyzer

AI Resume Analyzer is a Python project that evaluates resumes against role requirements using OpenAI, FastAPI, and Streamlit.
It lets you upload PDF resumes, extract text, and generate structured analysis including skills, missing skills, ATS score, and improvement suggestions.

## Key Features
- PDF resume upload and text extraction using `pypdf`
- AI-powered resume analysis with strict JSON output validation
- ATS-style score (`0-100`) with actionable suggestions
- Job description aware skill-gap analysis
- FastAPI backend with ready-to-use endpoints
- Streamlit UI for quick local usage

## Tech Stack
- Python
- FastAPI
- Streamlit
- OpenAI API
- Pydantic
- pypdf

## Project Structure
```text
Resume Analyzer/
|-- app/
|   |-- main.py                  # FastAPI app entrypoint
|   |-- routes/resume.py         # Upload + analysis endpoints
|   |-- services/ai_service.py   # OpenAI integration + schema validation
|   |-- utils/parser.py          # PDF text extraction
|-- streamlit_app.py             # Streamlit frontend
|-- requirements.txt
|-- .env.example
|-- README.md
```

## Prerequisites
- Python 3.10+
- OpenAI API key

## Local Setup
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create your environment file:
   ```bash
   copy .env.example .env
   ```
5. Update `.env` with your real API key.

## Environment Variables
| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | - | API key used for resume analysis |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model used for analysis |

Example:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Run FastAPI Backend
```bash
uvicorn app.main:app --reload
```

### Useful Endpoints
- `GET /` -> API status message
- `GET /health` -> health check text
- `GET /resume/sample` -> route sanity check
- `POST /upload-resume` -> upload PDF + return extracted text preview
- `POST /analyze` -> upload PDF + optional job description, return structured analysis

### Example Analyze Request
```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "file=@resume.pdf" \
  -F "job_description=Looking for a Python developer with FastAPI, AWS, and CI/CD experience"
```

## Run Streamlit UI
```bash
streamlit run streamlit_app.py
```

In the UI:
1. Upload a PDF resume.
2. Paste an optional job description.
3. Click **Analyze Resume**.
4. Review ATS score, skills, missing skills, and suggestions.

## Error Handling
The app returns clear errors for common scenarios:
- Non-PDF file uploads
- Empty or non-extractable PDF text
- Missing `OPENAI_API_KEY`
- OpenAI response/schema validation failures

## GitHub Preparation Checklist
- Add `.env` to `.gitignore`
- Do not commit real API keys
- If `.env` was already tracked once, untrack it before pushing:
  ```bash
  git rm --cached .env
  ```

## Future Enhancements
- Resume keyword highlighting for missing skills
- Bulk resume comparison for recruiters
- Export analysis report as PDF/JSON
- Historical analysis dashboard

## License
Add your preferred license (for example, MIT) before publishing.






