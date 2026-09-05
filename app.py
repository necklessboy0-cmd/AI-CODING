# ============================================================
# AI CODE BUILDER — app.py
# ============================================================
# Part 1 includes:
# - Imports
# - Streamlit page configuration
# - Modern professional UI
# - Custom CSS
# - Modern background/theme
# - Prompt input area
# - Language selector
# - Coding-skill selector
# - Upload area/theme
# - Session state
# - Main UI structure
# - Loading/processing visual foundation
#
# API integrations and generation logic are included below.
# ============================================================

import streamlit as st
import io
import zipfile
from datetime import datetime


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Code Builder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "reviewed_prompt": "",
    "generated_code": "",
    "corrected_code": "",
    "requirements": "",
    "project_files": {},
    "error_report": "",
    "prompt_review_complete": False,
    "generation_complete": False,
    "error_check_complete": False,
    "is_processing": False,
    "processing_message": "",
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# MODERN UI / CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(129, 140, 248, 0.20),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(236, 72, 153, 0.16),
                transparent 30%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(45, 212, 191, 0.12),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #0b1020 0%,
                #111827 50%,
                #0f172a 100%
            );
        color: #f8fafc;
    }

    /* Main content width */

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* --------------------------------------------------------
       HEADER
       -------------------------------------------------------- */

    .app-header {
        padding: 28px 30px;
        margin-bottom: 25px;
        border-radius: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(30, 41, 59, 0.92),
                rgba(15, 23, 42, 0.88)
            );

        border: 1px solid rgba(255, 255, 255, 0.10);

        box-shadow:
            0 20px 60px rgba(0, 0, 0, 0.25);

        backdrop-filter: blur(16px);
    }

    .app-title {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 6px;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #c4b5fd,
                #f9a8d4
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .app-subtitle {
        font-size: 16px;
        color: #cbd5e1;
        margin-top: 4px;
    }


    /* --------------------------------------------------------
       SECTION CARDS
       -------------------------------------------------------- */

    .section-card {
        padding: 24px;
        margin-bottom: 20px;
        border-radius: 22px;

        background:
            rgba(15, 23, 42, 0.72);

        border:
            1px solid rgba(255, 255, 255, 0.09);

        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.18);

        backdrop-filter: blur(14px);
    }

    .section-title {
        font-size: 21px;
        font-weight: 750;
        margin-bottom: 6px;
        color: #f8fafc;
    }

    .section-description {
        font-size: 14px;
        color: #94a3b8;
        margin-bottom: 18px;
    }


    /* --------------------------------------------------------
       PROMPT AREA
       -------------------------------------------------------- */

    .prompt-wrapper {
        padding: 6px;
        border-radius: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(129, 140, 248, 0.18),
                rgba(236, 72, 153, 0.12)
            );
    }


    /* --------------------------------------------------------
       STEP INDICATOR
       -------------------------------------------------------- */

    .step-container {
        display: flex;
        gap: 10px;
        margin: 10px 0 25px 0;
        flex-wrap: wrap;
    }

    .step {
        padding: 9px 15px;
        border-radius: 999px;

        background:
            rgba(255, 255, 255, 0.06);

        border:
            1px solid rgba(255, 255, 255, 0.08);

        color: #cbd5e1;
        font-size: 13px;
    }

    .step-active {
        background:
            rgba(129, 140, 248, 0.20);

        border:
            1px solid rgba(129, 140, 248, 0.45);

        color: #ddd6fe;
    }


    /* --------------------------------------------------------
       INFO / STATUS
       -------------------------------------------------------- */

    .status-card {
        padding: 16px 18px;
        border-radius: 16px;

        background:
            rgba(255, 255, 255, 0.045);

        border:
            1px solid rgba(255, 255, 255, 0.08);

        margin: 10px 0;
    }

    .status-text {
        color: #cbd5e1;
        font-size: 14px;
    }


    /* --------------------------------------------------------
       FOOTER
       -------------------------------------------------------- */

    .footer {
        text-align: center;
        margin-top: 35px;
        padding: 20px;
        color: #64748b;
        font-size: 12px;
    }


    /* --------------------------------------------------------
       STREAMLIT ELEMENTS
       -------------------------------------------------------- */

    div[data-testid="stTextArea"] textarea {
        border-radius: 16px !important;
        background: rgba(15, 23, 42, 0.75) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 14px !important;
        background: rgba(15, 23, 42, 0.75) !important;
        color: #f8fafc !important;
    }

    div[data-testid="stSelectbox"] > div {
        border-radius: 14px !important;
    }

    button {
        border-radius: 12px !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">🚀 AI Code Builder</div>
        <div class="app-subtitle">
            Turn your idea into a structured, reviewed and
            production-ready coding project.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# WORKFLOW STEPS
# ============================================================

st.markdown(
    """
    <div class="step-container">
        <div class="step step-active">① Prompt</div>
        <div class="step">② AI Prompt Review</div>
        <div class="step">③ Code Generation</div>
        <div class="step">④ Error Detection</div>
        <div class="step">⑤ Correction</div>
        <div class="step">⑥ Download Project</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ Project Settings")

    st.markdown(
        """
        <div class="status-card">
            <div class="status-text">
                Configure your project before generating code.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    programming_language = st.selectbox(
        "💻 Programming Language",
        [
            "Python",
            "JavaScript",
            "TypeScript",
            "Java",
            "C++",
            "C",
            "C#",
            "Go",
            "Rust",
            "PHP",
            "Ruby",
            "Kotlin",
            "Swift",
        ],
        index=0,
    )

    coding_skill = st.selectbox(
        "🎯 Coding Skill / Project Type",
        [
            "General Application",
            "Web Application",
            "Streamlit Application",
            "API / Backend",
            "Automation Script",
            "Data Analysis",
            "Machine Learning",
            "AI Application",
            "CLI Application",
            "Game",
            "Other",
        ],
        index=0,
    )

    output_style = st.selectbox(
        "✨ Code Style",
        [
            "Production Ready",
            "Clean & Beginner Friendly",
            "Professional & Modular",
            "Performance Focused",
        ],
        index=0,
    )

    st.markdown("---")

    st.markdown("### 📁 Optional Project Context")

    uploaded_file = st.file_uploader(
        "Upload an existing project/file",
        type=[
            "py",
            "js",
            "ts",
            "java",
            "cpp",
            "c",
            "cs",
            "go",
            "rs",
            "php",
            "rb",
            "txt",
            "md",
            "json",
            "zip",
        ],
        help="Optional. Upload an existing file or project for AI analysis.",
    )

    github_url = st.text_input(
        "🔗 GitHub Repository (Optional)",
        placeholder="https://github.com/username/repository",
    )

    st.markdown("---")

    st.caption("🔐 API keys will be handled through Streamlit Secrets.")
    st.caption("Your users will not need to enter API keys.")


# ============================================================
# MAIN PROMPT SECTION
# ============================================================

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">
            🧠 Describe Your Project
        </div>

        <div class="section-description">
            Write your idea, requirements or coding prompt below.
            The AI workflow will review the prompt before generating
            the project.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Prompt input

prompt = st.text_area(
    "Your Project Prompt",
    placeholder=(
        "Example:\n\n"
        "Create a Streamlit application that analyzes a user's "
        "text and generates a detailed report..."
    ),
    height=240,
    label_visibility="collapsed",
)


# ============================================================
# OPTIONAL CONTEXT DISPLAY
# ============================================================

if uploaded_file is not None:

    st.markdown(
        f"""
        <div class="status-card">
            📎 <strong>Uploaded:</strong>
            {uploaded_file.name}
        </div>
        """,
        unsafe_allow_html=True,
    )


if github_url.strip():

    st.markdown(
        f"""
        <div class="status-card">
            🔗 <strong>GitHub Repository:</strong>
            {github_url}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROMPT VALIDATION
# ============================================================

prompt_ready = bool(prompt.strip())

if not prompt_ready:

    st.info(
        "💡 Enter your project idea above to begin."
    )


# ============================================================
# PRIMARY ACTION AREA
# ============================================================

st.markdown("### 🚀 Start AI Workflow")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:

    review_button = st.button(
        "🔍 Review Prompt",
        use_container_width=True,
        disabled=not prompt_ready,
    )


with col2:

    clear_button = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )


with col3:

    preview_button = st.button(
        "👁️ Preview Settings",
        use_container_width=True,
    )


# ============================================================
# CLEAR
# ============================================================

if clear_button:

    st.session_state.reviewed_prompt = ""
    st.session_state.generated_code = ""
    st.session_state.corrected_code = ""
    st.session_state.requirements = ""
    st.session_state.project_files = {}
    st.session_state.error_report = ""

    st.session_state.prompt_review_complete = False
    st.session_state.generation_complete = False
    st.session_state.error_check_complete = False

    st.rerun()


# ============================================================
# SETTINGS PREVIEW
# ============================================================

if preview_button:

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                📋 Project Configuration
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    preview_col1, preview_col2 = st.columns(2)

    with preview_col1:
        st.write(
            f"**Language:** {programming_language}"
        )
        st.write(
            f"**Project Type:** {coding_skill}"
        )

    with preview_col2:
        st.write(
            f"**Code Style:** {output_style}"
        )

        if uploaded_file:
            st.write(
                f"**Uploaded Context:** {uploaded_file.name}"
            )
        else:
            st.write(
                "**Uploaded Context:** None"
            )


# ============================================================
# LOADING / PROCESSING HELPER
# ============================================================

def show_processing(message: str):
    """
    Modern processing indicator.

    Later parts of the application will use this helper
    during Gemini, OpenAI and Grok operations.
    """

    st.session_state.is_processing = True
    st.session_state.processing_message = message

    placeholder = st.empty()

    placeholder.markdown(
        f"""
        <div class="status-card">
            <div style="font-size:28px;">
                😂
            </div>

            <div class="status-text">
                <strong>{message}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return placeholder


# ============================================================
# PROMPT REVIEW PLACEHOLDER
# ============================================================

if review_button:

    # This is intentionally only the UI foundation.
    # Gemini integration will be added in PART 2.

    st.session_state.is_processing = True
    st.session_state.processing_message = (
        "Preparing your prompt for AI review..."
    )

    st.markdown(
        """
        <div class="status-card">
            <div style="font-size:28px;">😂</div>
            <div class="status-text">
                <strong>
                    Preparing your prompt for AI review...
                </strong>
                <br>
                Gemini prompt-review integration will run here.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CURRENT PROJECT INFORMATION
# ============================================================

if (
    st.session_state.reviewed_prompt
    or st.session_state.generated_code
    or st.session_state.corrected_code
):

    st.markdown("---")

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                📦 Current Project
            </div>

            <div class="section-description">
                Your generated project will appear here as the
                AI workflow progresses.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        AI Code Builder • Prompt → Review → Generate → AI Validate → Fix
    </div>
    """,
    unsafe_allow_html=True,
)
# ============================================================
# AI CODE BUILDER — app.py
# ============================================================
# Includes:
# - Gemini API integration
# - Secure Streamlit Secrets
# - Prompt review
# - Prompt improvement
# - AI review status UI
# - Reviewed prompt display
# - Error handling
# ============================================================

from google import genai


# ============================================================
# GEMINI CONFIGURATION
# Current model: Gemini 3.5 Flash-Lite
# ============================================================

def get_gemini_api_key():
    """
    Reads the Gemini API key from Streamlit Secrets.

    The user does NOT enter an API key.
    The deployed app owner configures it in Streamlit Cloud.
    """

    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def get_gemini_client():
    """
    Creates the current Google GenAI client using Streamlit Secrets.
    """

    api_key = get_gemini_api_key()

    if not api_key:
        return None

    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


# ============================================================
# GEMINI PROMPT REVIEW FUNCTION
# ============================================================

def review_prompt_with_gemini(
    user_prompt,
    programming_language,
    coding_skill,
    output_style,
    github_url="",
):
    """
    Sends the user's project idea to Gemini.

    Gemini's role:
    1. Understand the user's idea.
    2. Detect ambiguity.
    3. Detect missing requirements.
    4. Improve the prompt.
    5. Produce a structured coding specification.
    """

    client = get_gemini_client()

    if client is None:
        return {
            "success": False,
            "error": (
                "Gemini API key is not configured. "
                "Please add GEMINI_API_KEY to Streamlit Secrets."
            ),
            "reviewed_prompt": "",
        }

    try:

        review_instruction = f"""
You are the Prompt Architect for an AI Code Builder.

Your job is NOT to generate the final application code.

Your job is to analyze and improve the user's coding request
so another AI coding model can generate the application
accurately.

PROJECT INFORMATION
-------------------
Programming Language:
{programming_language}

Project Type:
{coding_skill}

Requested Code Style:
{output_style}

GitHub Repository:
{github_url if github_url else "Not provided"}

USER PROMPT
-----------
{user_prompt}

TASK
----
Analyze the user's request carefully.

Identify:

1. The actual goal of the application.
2. Required features.
3. User interface requirements.
4. Inputs and outputs.
5. Required files.
6. Required dependencies.
7. Expected application behavior.
8. Possible missing requirements.
9. Ambiguous or contradictory requirements.
10. Potential implementation problems.

Then create a clean, detailed, implementation-ready prompt.

The final improved prompt must:

- Preserve the user's original intent.
- Remove unnecessary ambiguity.
- Make requirements explicit.
- Define expected behavior.
- Define expected files.
- Mention security considerations.
- Avoid exposing API keys.
- Be suitable for a second AI model that will generate code.

IMPORTANT:

Do not invent unrelated features.

Do not generate the final application code.

Return the response using these sections:

PROJECT UNDERSTANDING
REQUIREMENTS
UI REQUIREMENTS
FUNCTIONAL REQUIREMENTS
SECURITY REQUIREMENTS
FILES TO GENERATE
DEPENDENCIES
POTENTIAL ISSUES
IMPROVED MASTER PROMPT
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=review_instruction,
        )

        reviewed_prompt = (response.text or "").strip()

        if not reviewed_prompt:
            return {
                "success": False,
                "error": "Gemini returned an empty response.",
                "reviewed_prompt": "",
            }

        return {
            "success": True,
            "error": "",
            "reviewed_prompt": reviewed_prompt,
        }

    except Exception as error:

        return {
            "success": False,
            "error": f"Gemini prompt review failed: {error}",
            "reviewed_prompt": "",
        }


# ============================================================
# GEMINI REVIEW BUTTON ACTION
# ============================================================

if review_button and prompt_ready:

    processing_box = st.empty()

    processing_box.markdown(
        """
        <div class="status-card">
            <div style="font-size:32px;">😂</div>

            <div class="status-text">
                <strong>Gemini is reviewing your prompt...</strong>
                <br>
                Checking requirements, logic and missing details.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    result = review_prompt_with_gemini(
        user_prompt=prompt,
        programming_language=programming_language,
        coding_skill=coding_skill,
        output_style=output_style,
        github_url=github_url,
    )

    processing_box.empty()

    if result["success"]:

        st.session_state.reviewed_prompt = (
            result["reviewed_prompt"]
        )

        st.session_state.prompt_review_complete = True
        st.session_state.is_processing = False

        st.success(
            "✅ Prompt review completed successfully."
        )

    else:

        st.session_state.is_processing = False

        st.error(
            f"❌ {result['error']}"
        )


# ============================================================
# REVIEWED PROMPT DISPLAY
# ============================================================

if st.session_state.prompt_review_complete:

    st.markdown("---")

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                🔍 AI Prompt Review
            </div>

            <div class="section-description">
                Gemini has analyzed and structured your original
                request. Review the improved master prompt before
                code generation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    reviewed_prompt = st.text_area(
        "Reviewed Master Prompt",
        value=st.session_state.reviewed_prompt,
        height=420,
        key="reviewed_prompt_editor",
    )

    # Allow the user to make a final adjustment if required.
    st.session_state.reviewed_prompt = reviewed_prompt


# ============================================================
# REVIEW STATUS
# ============================================================

if st.session_state.prompt_review_complete:

    st.markdown(
        """
        <div class="status-card">
            <div class="status-text">
                ✅ <strong>Prompt Review Complete</strong>
                <br>
                The reviewed prompt is now ready for the
                code-generation stage.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# NEXT STAGE PREPARATION
# ============================================================

if st.session_state.prompt_review_complete:

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                🤖 Ready for Code Generation
            </div>

            <div class="section-description">
                The next stage will send the approved master
                prompt to the code-generation AI and create the
                project files automatically.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    generate_button = st.button(
        "⚡ Generate Project",
        type="primary",
        use_container_width=True,
    )

else:

    generate_button = False


# ============================================================
# PART 2 STATUS
# ============================================================

st.markdown(
    """
    <div class="status-card">
        <div class="status-text">
            🧠 Stage 2: Gemini Prompt Architecture
            <br>
            <small>
                Prompt → Analysis → Review → Master Prompt
            </small>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 
# ============================================================
# ============================================================
# ============================================================
# OpenAI Code Generation
# Generates:
# - app.py
# - requirements.txt
# - README.md
# - Supporting project files when required
# - ZIP download package
# ============================================================

from openai import OpenAI
import json
import re


# ============================================================
# OPENAI CONFIGURATION
# Current model: GPT-5.6 Luna
# ============================================================

def get_openai_api_key():
    """
    Reads the OpenAI API key securely from Streamlit Secrets.
    The end user never enters the API key.
    """

    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None


def get_openai_client():
    """
    Creates the OpenAI client using the deployment's secret.
    """

    api_key = get_openai_api_key()

    if not api_key:
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


# ============================================================
# RESPONSE EXTRACTION
# ============================================================

def extract_json_from_response(text):
    """
    Extract JSON from an AI response.

    Handles responses that contain:
    - Plain JSON
    - JSON inside ```json ... ```
    - Extra explanatory text around JSON
    """

    if not text:
        return None

    text = text.strip()

    # Remove Markdown code fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^```\s*",
        "",
        text,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to locate the first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        try:
            return json.loads(
                text[start:end + 1]
            )
        except Exception:
            return None

    return None


# ============================================================
# OPENAI PROJECT GENERATOR
# ============================================================

def generate_project_with_openai(
    master_prompt,
    programming_language,
    coding_skill,
    output_style,
):
    """
    Uses OpenAI to generate the complete project.

    The AI must return structured JSON so the application can
    automatically separate app.py, requirements.txt,
    README.md and additional files.
    """

    client = get_openai_client()

    if client is None:

        return {
            "success": False,
            "error": (
                "OpenAI API key is not configured. "
                "Please add OPENAI_API_KEY to "
                "Streamlit Secrets."
            ),
            "files": {},
        }

    generation_instruction = f"""
You are the senior software engineer responsible for
generating a complete coding project.

A separate AI has already reviewed and structured the user's
original request.

Your job is now to generate the actual project.

PROJECT SETTINGS
----------------
Programming Language:
{programming_language}

Project Type:
{coding_skill}

Code Style:
{output_style}

APPROVED MASTER PROMPT
----------------------
{master_prompt}

IMPORTANT REQUIREMENTS
----------------------

1. Generate working, complete code.

2. Do not provide pseudocode.

3. Do not leave TODO placeholders for required functionality.

4. Keep the implementation consistent with the approved
   master prompt.

5. Include all required imports.

6. Include proper error handling.

7. Keep secrets and API keys out of the generated source code.

8. If environment variables or Streamlit Secrets are required,
   use secure configuration.

9. Generate a correct requirements.txt containing the actual
   third-party dependencies required by the project.

10. Generate a useful README.md explaining how to run and
    deploy the project.

11. If additional files are genuinely required, create them.

12. Do not generate unnecessary files.

13. The main application file must be named app.py whenever
    the project is a Streamlit application.

14. The generated code must be internally consistent.

15. Imports must match requirements.txt.

16. Do not invent package names.

17. Do not put explanations outside the JSON response.

RETURN FORMAT
-------------

Return ONLY valid JSON using this exact structure:

{{
    "files": {{
        "app.py": "complete source code",
        "requirements.txt": "complete requirements",
        "README.md": "complete README"
    }}
}}

If additional files are required, add them inside "files".

Example:

{{
    "files": {{
        "app.py": "...",
        "requirements.txt": "...",
        "README.md": "...",
        "config.py": "..."
    }}
}}

The JSON must be valid and parseable.
"""

    try:

        response = client.chat.completions.create(
            model="gpt-5.6-luna",
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior production software "
                        "engineer. Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": generation_instruction,
                },
            ],
        )

        content = response.choices[0].message.content

        project_data = extract_json_from_response(
            content
        )

        if not project_data:
            return {
                "success": False,
                "error": (
                    "OpenAI returned an invalid project "
                    "structure."
                ),
                "files": {},
            }

        files = project_data.get("files", {})

        if not isinstance(files, dict):
            return {
                "success": False,
                "error": (
                    "OpenAI returned an invalid files object."
                ),
                "files": {},
            }

        if "app.py" not in files:
            return {
                "success": False,
                "error": (
                    "The generated project does not contain "
                    "app.py."
                ),
                "files": files,
            }

        if "requirements.txt" not in files:
            return {
                "success": False,
                "error": (
                    "The generated project does not contain "
                    "requirements.txt."
                ),
                "files": files,
            }

        return {
            "success": True,
            "error": "",
            "files": files,
        }

    except Exception as error:

        return {
            "success": False,
            "error": (
                f"OpenAI code generation failed: {error}"
            ),
            "files": {},
        }


# ============================================================
# GENERATE PROJECT BUTTON
# ============================================================

if generate_button:

    if not st.session_state.reviewed_prompt.strip():

        st.error(
            "Please review the prompt before generating "
            "the project."
        )

    else:

        processing_box = st.empty()

        processing_box.markdown(
            """
            <div class="status-card">
                <div style="font-size:32px;">😂</div>

                <div class="status-text">
                    <strong>
                        OpenAI is generating your project...
                    </strong>
                    <br>
                    Building app.py, requirements.txt and
                    supporting project files.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        generation_result = (
            generate_project_with_openai(
                master_prompt=(
                    st.session_state.reviewed_prompt
                ),
                programming_language=(
                    programming_language
                ),
                coding_skill=coding_skill,
                output_style=output_style,
            )
        )

        processing_box.empty()

        if generation_result["success"]:

            st.session_state.project_files = (
                generation_result["files"]
            )

            st.session_state.generated_code = (
                generation_result["files"].get(
                    "app.py",
                    "",
                )
            )

            st.session_state.requirements = (
                generation_result["files"].get(
                    "requirements.txt",
                    "",
                )
            )

            st.session_state.generation_complete = True

            st.success(
                "✅ Project generated successfully."
            )

        else:

            st.error(
                f"❌ {generation_result['error']}"
            )


# ============================================================
# GENERATED PROJECT DISPLAY
# ============================================================

if st.session_state.generation_complete:

    st.markdown("---")

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                🛠️ Generated Project
            </div>

            <div class="section-description">
                OpenAI has generated the project files.
                The files will now be passed automatically to
                the final error-detection and correction stage.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    generated_files = st.session_state.project_files

    # --------------------------------------------------------
    # FILE LIST
    # --------------------------------------------------------

    st.markdown("### 📁 Project Files")

    for filename in generated_files.keys():

        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-text">
                    📄 <strong>{filename}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # APP.PY PREVIEW
    # --------------------------------------------------------

    if "app.py" in generated_files:

        st.markdown("### 🐍 app.py")

        st.code(
            generated_files["app.py"],
            language="python",
        )


    # --------------------------------------------------------
    # REQUIREMENTS PREVIEW
    # --------------------------------------------------------

    if "requirements.txt" in generated_files:

        st.markdown(
            "### 📦 requirements.txt"
        )

        st.code(
            generated_files["requirements.txt"],
            language="text",
        )


    # --------------------------------------------------------
    # README PREVIEW
    # --------------------------------------------------------

    if "README.md" in generated_files:

        st.markdown(
            "### 📘 README.md"
        )

        with st.expander(
            "View README.md"
        ):

            st.markdown(
                generated_files["README.md"]
            )


# ============================================================
# DOWNLOAD HELPERS
# ============================================================

def create_project_zip(files):
    """
    Creates an in-memory ZIP file containing all generated
    project files.
    """

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zip_file:

        for filename, content in files.items():

            if content is None:
                content = ""

            zip_file.writestr(
                filename,
                str(content),
            )

    zip_buffer.seek(0)

    return zip_buffer.getvalue()


# ============================================================
# DOWNLOAD SECTION
# ============================================================

if st.session_state.generation_complete:

    st.markdown("---")

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                📥 Download Your Project
            </div>

            <div class="section-description">
                Download individual files or the complete
                project as a ZIP package.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    files = st.session_state.project_files


    # --------------------------------------------------------
    # DOWNLOAD APP.PY
    # --------------------------------------------------------

    if "app.py" in files:

        st.download_button(
            label="⬇️ Download app.py",
            data=files["app.py"],
            file_name="app.py",
            mime="text/x-python",
            use_container_width=True,
        )


    # --------------------------------------------------------
    # DOWNLOAD REQUIREMENTS.TXT
    # --------------------------------------------------------

    if "requirements.txt" in files:

        st.download_button(
            label="⬇️ Download requirements.txt",
            data=files["requirements.txt"],
            file_name="requirements.txt",
            mime="text/plain",
            use_container_width=True,
        )


    # --------------------------------------------------------
    # DOWNLOAD README.MD
    # --------------------------------------------------------

    if "README.md" in files:

        st.download_button(
            label="⬇️ Download README.md",
            data=files["README.md"],
            file_name="README.md",
            mime="text/markdown",
            use_container_width=True,
        )


    # --------------------------------------------------------
    # DOWNLOAD COMPLETE ZIP
    # --------------------------------------------------------

    project_zip = create_project_zip(files)

    st.download_button(
        label="📦 Download Complete Project ZIP",
        data=project_zip,
        file_name="ai_generated_project.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# COPY APP.PY
# ============================================================

if st.session_state.generation_complete:

    st.markdown("### 📋 Copy Generated Code")

    app_code = st.session_state.project_files.get(
        "app.py",
        "",
    )

    if app_code:

        st.text_area(
            "Copy app.py",
            value=app_code,
            height=300,
        )


# ============================================================
# PROJECT GENERATION STATUS
# ============================================================

if st.session_state.generation_complete:

    st.markdown(
        """
        <div class="status-card">
            <div class="status-text">
                ✅ <strong>Code Generation Complete</strong>
                <br>
                The generated app.py is already available
                internally for the next AI validation stage.
                The user does not need to download and
                re-upload it.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
  )
  # ============================================================
# ============================================================
# Includes:
# - Grok API integration
# - Automatic app.py error detection
# - Automatic correction
# - No re-upload required
# - Original vs corrected code
# - Final requirements.txt
# - Final project ZIP
# - Copy/download controls
# - Final validation status
# ============================================================

from openai import OpenAI as GrokOpenAI


# ============================================================
# GROK CONFIGURATION
# Current model: Grok 4.6
# ============================================================

def get_grok_api_key():
    """
    Reads the Grok API key securely from Streamlit Secrets.
    """

    try:
        return st.secrets["GROK_API_KEY"]
    except Exception:
        return None


def get_grok_client():
    """
    Creates an OpenAI-compatible client pointing to xAI's
    Grok API.
    """

    api_key = get_grok_api_key()

    if not api_key:
        return None

    try:
        return GrokOpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )
    except Exception:
        return None


# ============================================================
# GROK ERROR DETECTION + CORRECTION
# ============================================================

def check_and_correct_code_with_grok(
    app_code,
    requirements,
    master_prompt,
):
    """
    Sends the internally generated app.py to Grok.

    Grok:
    - Detects syntax errors
    - Detects import problems
    - Checks logic
    - Checks missing functionality
    - Checks requirements consistency
    - Corrects the code
    """

    client = get_grok_client()

    if client is None:

        return {
            "success": False,
            "error": (
                "GROK_API_KEY is not configured. "
                "Please add GROK_API_KEY to "
                "Streamlit Secrets."
            ),
            "corrected_code": "",
            "error_report": "",
        }

    review_prompt = f"""
You are the final senior code-review and debugging system.

An AI coding model generated the following Streamlit project.

Your responsibility is to inspect the generated app.py and
correct it before the project is delivered to the user.

APPROVED MASTER PROMPT
----------------------
{master_prompt}

GENERATED requirements.txt
--------------------------
{requirements}

GENERATED app.py
----------------
{app_code}

CHECK THE CODE FOR:

1. Python syntax errors.
2. Incorrect imports.
3. Missing dependencies.
4. Incorrect Streamlit APIs.
5. Runtime errors.
6. Undefined variables.
7. Incorrect function calls.
8. Broken control flow.
9. Logical inconsistencies.
10. Missing functionality required by the master prompt.
11. Security problems.
12. Hard-coded API keys or secrets.
13. Incorrect requirements.txt compatibility.
14. Problems that could prevent Streamlit Cloud deployment.
15. Obvious issues that would cause the generated application
    to fail.

IMPORTANT:

- Preserve the intended functionality.
- Do not remove required features merely to avoid errors.
- Do not add unrelated features.
- Keep the code production-oriented.
- Do not expose secrets.
- Correct the code rather than merely describing the fix.
- Return the COMPLETE corrected app.py.
- Do not return partial code.

Return ONLY valid JSON in this structure:

{{
    "error_report": "Detailed list of detected issues and fixes.",
    "has_errors": true,
    "corrected_code": "COMPLETE corrected app.py"
}}

If no errors are found, return the original code as
corrected_code and set has_errors to false.
"""


    try:

        response = client.chat.completions.create(
            model="grok-4.6",
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior Python and Streamlit "
                        "debugging engineer. Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": review_prompt,
                },
            ],
        )

        response_text = (
            response.choices[0].message.content
        )

        result = extract_json_from_response(
            response_text
        )

        if not result:

            return {
                "success": False,
                "error": (
                    "Grok returned an invalid validation "
                    "response."
                ),
                "corrected_code": "",
                "error_report": "",
            }

        corrected_code = result.get(
            "corrected_code",
            "",
        )

        error_report = result.get(
            "error_report",
            "No detailed error report was returned.",
        )

        if not corrected_code.strip():

            return {
                "success": False,
                "error": (
                    "Grok did not return corrected app.py."
                ),
                "corrected_code": "",
                "error_report": error_report,
            }

        return {
            "success": True,
            "error": "",
            "corrected_code": corrected_code,
            "error_report": error_report,
            "has_errors": result.get(
                "has_errors",
                True,
            ),
        }

    except Exception as error:

        return {
            "success": False,
            "error": (
                f"Grok validation failed: {error}"
            ),
            "corrected_code": "",
            "error_report": "",
        }


# ============================================================
# FINAL ERROR DETECTION BUTTON
# ============================================================

if st.session_state.generation_complete:

    st.markdown("---")

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                🛡️ Final Error Detection & Correction
            </div>

            <div class="section-description">
                The generated app.py is already available
                internally. You do not need to download or
                upload it again.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    error_check_button = st.button(
        "🔎 Run Error Detection & Auto-Fix",
        type="primary",
        use_container_width=True,
    )

else:

    error_check_button = False


# ============================================================
# RUN GROK VALIDATION
# ============================================================

if error_check_button:

    app_code_to_check = (
        st.session_state.project_files.get(
            "app.py",
            "",
        )
    )

    requirements_to_check = (
        st.session_state.project_files.get(
            "requirements.txt",
            "",
        )
    )

    master_prompt_to_check = (
        st.session_state.reviewed_prompt
    )

    if not app_code_to_check.strip():

        st.error(
            "No generated app.py is available for validation."
        )

    else:

        processing_box = st.empty()

        processing_box.markdown(
            """
            <div class="status-card">
                <div style="font-size:32px;">😂</div>

                <div class="status-text">
                    <strong>
                        Grok is checking your generated app.py...
                    </strong>
                    <br>
                    Detecting errors, logic problems and
                    deployment issues.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        grok_result = (
            check_and_correct_code_with_grok(
                app_code=app_code_to_check,
                requirements=requirements_to_check,
                master_prompt=master_prompt_to_check,
            )
        )

        processing_box.empty()

        if grok_result["success"]:

            st.session_state.error_report = (
                grok_result["error_report"]
            )

            st.session_state.corrected_code = (
                grok_result["corrected_code"]
            )

            # Replace the internally stored app.py with the
            # final corrected version.
            st.session_state.project_files[
                "app.py"
            ] = grok_result["corrected_code"]

            st.session_state.generated_code = (
                grok_result["corrected_code"]
            )

            st.session_state.error_check_complete = True

            st.success(
                "✅ Error detection and correction completed."
            )

        else:

            st.error(
                f"❌ {grok_result['error']}"
            )


# ============================================================
# ERROR REPORT
# ============================================================

if st.session_state.error_check_complete:

    st.markdown("---")

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                🔍 Error Detection Report
            </div>

            <div class="section-description">
                Grok's final code-review results.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(
        "View Error Detection & Correction Report",
        expanded=True,
    ):

        st.markdown(
            st.session_state.error_report
        )


# ============================================================
# FINAL CORRECTED APP.PY
# ============================================================

if st.session_state.error_check_complete:

    st.markdown("### ✅ Final Corrected app.py")

    final_app_code = (
        st.session_state.corrected_code
    )

    st.code(
        final_app_code,
        language="python",
    )


# ============================================================
# FINAL REQUIREMENTS
# ============================================================

if st.session_state.error_check_complete:

    st.markdown("### 📦 Final requirements.txt")

    final_requirements = (
        st.session_state.project_files.get(
            "requirements.txt",
            "",
        )
    )

    st.code(
        final_requirements,
        language="text",
    )


# ============================================================
# FINAL DOWNLOADS
# ============================================================

if st.session_state.error_check_complete:

    st.markdown("---")

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                🎉 Your Project Is Ready
            </div>

            <div class="section-description">
                The generated code has passed through the final
                AI review and correction stage.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    final_files = (
        st.session_state.project_files
    )


    # --------------------------------------------------------
    # FINAL APP.PY
    # --------------------------------------------------------

    if "app.py" in final_files:

        st.download_button(
            label="⬇️ Download Final app.py",
            data=final_files["app.py"],
            file_name="app.py",
            mime="text/x-python",
            use_container_width=True,
        )


    # --------------------------------------------------------
    # FINAL REQUIREMENTS.TXT
    # --------------------------------------------------------

    if "requirements.txt" in final_files:

        st.download_button(
            label="⬇️ Download Final requirements.txt",
            data=final_files["requirements.txt"],
            file_name="requirements.txt",
            mime="text/plain",
            use_container_width=True,
        )


    # --------------------------------------------------------
    # FINAL README
    # --------------------------------------------------------

    if "README.md" in final_files:

        st.download_button(
            label="⬇️ Download README.md",
            data=final_files["README.md"],
            file_name="README.md",
            mime="text/markdown",
            use_container_width=True,
        )


    # --------------------------------------------------------
    # COMPLETE FINAL ZIP
    # --------------------------------------------------------

    final_zip = create_project_zip(
        final_files
    )

    st.download_button(
        label="📦 Download Final Complete Project ZIP",
        data=final_zip,
        file_name="ai_code_builder_project.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# FINAL COPY AREA
# ============================================================

if st.session_state.error_check_complete:

    st.markdown("### 📋 Copy Final app.py")

    st.text_area(
        "Final corrected application code",
        value=st.session_state.corrected_code,
        height=400,
        key="final_app_copy_area",
    )


# ============================================================
# FINAL STATUS
# ============================================================

if st.session_state.error_check_complete:

    st.markdown(
        """
        <div class="status-card">
            <div class="status-text">
                🎯 <strong>AI Workflow Complete</strong>
                <br><br>
                🧠 Gemini → Prompt Review
                <br>
                🤖 OpenAI → Code Generation
                <br>
                🛡️ Grok → Error Detection & Correction
                <br>
                📦 Final Project → Download
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
