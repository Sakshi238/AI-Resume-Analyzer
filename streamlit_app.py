from pathlib import Path

import streamlit as st

from app.services.ai_service import AIServiceError, analyze_resume
from app.utils.parser import extract_text


UPLOAD_DIR = Path("uploads")


def _save_upload(uploaded_file) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / uploaded_file.name
    file_path.write_bytes(uploaded_file.getbuffer())
    return file_path


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Fraunces:opsz,wght@9..144,600&display=swap');

            :root {
                --bg: #f6faf8;
                --card: #ffffff;
                --mint: #d9eee4;
                --accent: #1c7c62;
                --text: #20322b;
                --subtext: #5d7168;
            }

            .stApp {
                background: radial-gradient(circle at top right, #eef8f3, var(--bg) 50%);
                color: var(--text);
                font-family: "Manrope", sans-serif;
            }

            h1, h2, h3 {
                font-family: "Fraunces", serif;
                color: #153a2f;
            }

            .card {
                background: var(--card);
                border: 1px solid #e4efe9;
                border-radius: 18px;
                padding: 1rem 1.2rem;
                box-shadow: 0 8px 24px rgba(28, 124, 98, 0.07);
            }

            .label {
                color: var(--subtext);
                font-size: 0.96rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Resume Analyzer",
        page_icon=":page_facing_up:",
        layout="centered",
    )
    _apply_styles()

    st.markdown("<h1>AI Resume Analyzer</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='label'>Upload your PDF resume and compare it directly against a job description.</p>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Choose a resume PDF", type=["pdf"])
    job_description = st.text_area(
        "Paste Job Description (optional but recommended)",
        placeholder="Paste the job posting here for better skill-gap comparison...",
        height=180,
    )

    if uploaded_file is None:
        return

    file_path = _save_upload(uploaded_file)
    st.success(f"Uploaded: {uploaded_file.name}")

    resume_text = extract_text(file_path)
    preview = resume_text[:500] if resume_text else ""

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Text Preview")
        st.write(preview or "No extractable text found in this PDF.")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Analyze Resume", use_container_width=True):
        if not resume_text.strip():
            st.error("No extractable text found in this PDF.")
            return

        with st.spinner("Analyzing resume..."):
            try:
                result = analyze_resume(
                    text=resume_text,
                    job_description=job_description.strip() or None,
                )
            except AIServiceError as exc:
                st.error(str(exc))
                return
            except Exception:
                st.error("Failed to analyze resume.")
                return

        data = result.model_dump()
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(f"ATS Score: {data['ATS_score']}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Skills")
            st.write(data["skills"] or ["No skills identified"])
        with col2:
            st.markdown("### Missing Skills")
            st.write(data["missing_skills"] or ["No missing skills identified"])

        st.markdown("### Suggestions")
        st.write(data["suggestions"] or ["No suggestions provided"])
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
