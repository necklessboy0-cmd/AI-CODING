import streamlit as st
import io
import zipfile
from datetime import datetime
import json
import re
import copy
from google import genai
from google.genai import types
from openai import OpenAI as GrokOpenAI

GEMINI_MODEL = "gemini-3.5-flash-lite"
GROK_REVIEW_MODEL = "grok-4.3"

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
# GEMINI & GROK CONFIGURATION
# ============================================================

def get_gemini_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None

def get_gemini_client():
    api_key = get_gemini_api_key()
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None

def get_grok_api_key():
    try:
        return st.secrets["GROK_API_KEY"]
    except Exception:
        return None

def get_grok_client():
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
    "voice_transcript": "",
    "voice_analysis": "",
    "prompt_text": "",
    "sync_prompt_editor": False,
    "voice_input_version": 0,
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
    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(129, 140, 248, 0.14), transparent 30%),
            radial-gradient(circle at 90% 20%, rgba(236, 72, 153, 0.10), transparent 30%),
            radial-gradient(circle at 50% 100%, rgba(45, 212, 191, 0.08), transparent 35%),
            linear-gradient(135deg, #182235 0%, #202b3d 50%, #172233 100%);
        color: #f8fafc;
    }
    .block-container { max-width: 1450px; padding-top: 2rem; padding-bottom: 4rem; }
    .app-header {
        padding: 28px 30px; margin-bottom: 25px; border-radius: 24px;
        background: linear-gradient(135deg, rgba(42, 55, 75, 0.92), rgba(24, 34, 51, 0.88));
        border: 1px solid rgba(255, 255, 255, 0.10);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(16px);
    }
    .app-title {
        font-size: 38px; font-weight: 800; letter-spacing: -1px; margin-bottom: 6px;
        background: linear-gradient(90deg, #ffffff, #c4b5fd, #f9a8d4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .app-subtitle { font-size: 16px; color: #cbd5e1; margin-top: 4px; }
    .section-card {
        padding: 24px; margin-bottom: 20px; border-radius: 22px;
        background: rgba(30, 42, 60, 0.68);
        border: 1px solid rgba(255, 255, 255, 0.09);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
        backdrop-filter: blur(14px);
    }
    .section-title { font-size: 21px; font-weight: 750; margin-bottom: 6px; color: #f8fafc; }
    .section-description { font-size: 14px; color: #94a3b8; margin-bottom: 18px; }
    .step-container { display: flex; gap: 10px; margin: 10px 0 25px 0; flex-wrap: wrap; }
    .step {
        padding: 9px 15px; border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #cbd5e1; font-size: 13px;
    }
    .step-active {
        background: rgba(129, 140, 248, 0.14);
        border: 1px solid rgba(129, 140, 248, 0.45);
        color: #ddd6fe;
    }
    .status-card {
        padding: 16px 18px; border-radius: 16px;
        background: rgba(255, 255, 255, 0.045);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin: 10px 0;
    }
    .status-text { color: #cbd5e1; font-size: 14px; }
    .footer { text-align: center; margin-top: 35px; padding: 20px; color: #64748b; font-size: 12px; }
    div[data-testid="stTextArea"] textarea {
        border-radius: 16px !important; background: rgba(30, 42, 60, 0.72) !important;
        color: #f8fafc !important; border: 1px solid rgba(255, 255, 255, 0.10) !important;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 14px !important; background: rgba(30, 42, 60, 0.72) !important; color: #f8fafc !important;
    }
    div[data-testid="stSelectbox"] > div { border-radius: 14px !important; }
    button { border-radius: 12px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER & STEPS
# ============================================================

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">🚀 AI Code Builder</div>
        <div class="app-subtitle">
            Turn your idea into a structured, reviewed and production-ready coding project.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
            <div class="status-text">Configure your project before generating code.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    programming_language = st.selectbox(
        "💻 Programming Language",
        ["Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#", "Go", "Rust", "PHP", "Ruby", "Kotlin", "Swift"],
        index=0,
    )

    coding_skill = st.selectbox(
        "🎯 Coding Skill / Project Type",
        ["General Application", "Web Application", "Streamlit Application", "API / Backend", "Automation Script", "Data Analysis", "Machine Learning", "AI Application", "CLI Application", "Game", "Other"],
        index=0,
    )

    output_style = st.selectbox(
        "✨ Code Style",
        ["Production Ready", "Clean & Beginner Friendly", "Professional & Modular", "Performance Focused"],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 📁 Optional Project Context")

    uploaded_file = st.file_uploader(
        "Upload an existing project/file",
        type=["py", "js", "ts", "java", "cpp", "c", "cs", "go", "rs", "php", "rb", "txt", "md", "json", "zip"],
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
        <div class="section-title">🧠 Describe Your Project</div>
        <div class="section-description">
            Write your idea, requirements or coding prompt below. The AI workflow will review the prompt before generating the project.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sync application data into the widget key BEFORE the widget is instantiated.
# This avoids StreamlitWidgetAlreadyInstantiatedError when voice/clear actions update the prompt.
if st.session_state.get("sync_prompt_editor", False):
    st.session_state.prompt_editor = st.session_state.get("prompt_text", "")
    st.session_state.sync_prompt_editor = False

if "prompt_editor" not in st.session_state:
    st.session_state.prompt_editor = st.session_state.get("prompt_text", "")

prompt = st.text_area(
    "Your Project Prompt",
    placeholder="Example:\n\nCreate a Streamlit application that analyzes a user's text and generates a detailed report...",
    height=240,
    label_visibility="collapsed",
    key="prompt_editor",
)

# prompt_text is application data; prompt_editor is the widget-owned state.
st.session_state.prompt_text = prompt


# ============================================================
# VOICE PROMPT INPUT
# ============================================================

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">🎙️ Voice Prompt</div>
        <div class="section-description">
            Record your project idea naturally. Gemini will understand the recording, extract the requirements and add the analyzed voice input to your main prompt.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

voice_audio = st.audio_input(
    "Record your project idea",
    sample_rate=16000,
    key=f"voice_prompt_audio_{st.session_state.voice_input_version}",
    help="Speak clearly about the project, features, behavior, UI and requirements.",
)

voice_col1, voice_col2 = st.columns(2)
with voice_col1:
    analyze_voice_button = st.button(
        "🎙️ Analyze Voice & Add to Prompt",
        use_container_width=True,
        disabled=voice_audio is None,
    )
with voice_col2:
    clear_voice_button = st.button(
        "🗑️ Clear / Cancel Voice",
        use_container_width=True,
        disabled=voice_audio is None and not st.session_state.voice_analysis,
    )

def analyze_voice_with_gemini(audio_bytes):
    client = get_gemini_client()
    if client is None:
        return {"success": False, "error": "Please add GEMINI_API_KEY to Streamlit Secrets.", "analysis": ""}
    try:
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
        instruction = """
You are the voice-input analyzer for an AI Code Builder.
Listen carefully to the user's recording and understand the coding or project request.
Extract the actual project idea, explicit features, UI requirements, inputs and outputs, behavior/workflow, technical constraints, programming preferences, and important technical names, numbers, package names and model names. Be faithful to what the user said. Do not invent unrelated requirements. If something is genuinely unclear, write [unclear] rather than guessing. Do not generate application code.

Return these sections:
VOICE TRANSCRIPT
VOICE-DERIVED REQUIREMENTS
VOICE-DERIVED CONSTRAINTS
VOICE-UNCERTAINTIES
PROMPT-READY VOICE INPUT
"""
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[instruction, audio_part],
        )
        analysis = (response.text or "").strip()
        if not analysis:
            return {"success": False, "error": "Gemini returned an empty voice analysis.", "analysis": ""}
        return {"success": True, "error": "", "analysis": analysis}
    except Exception as error:
        return {"success": False, "error": f"Voice analysis failed: {error}", "analysis": ""}

if clear_voice_button:
    # Never mutate the prompt_editor widget key after text_area has been instantiated.
    # Mark it for synchronization on the next rerun, before the widget is created.
    st.session_state.voice_transcript = ""
    st.session_state.voice_analysis = ""
    st.session_state.prompt_text = ""
    st.session_state.sync_prompt_editor = True
    st.session_state.voice_input_version += 1
    st.rerun()

if analyze_voice_button and voice_audio is not None:
    voice_box = st.empty()
    voice_box.markdown(
        """<div class="status-card"><div style="font-size:32px;">🎙️</div><div class="status-text"><strong>Gemini is analyzing your voice...</strong><br>Extracting your project intent and requirements.</div></div>""",
        unsafe_allow_html=True,
    )
    st.session_state.is_processing = True
    st.session_state.processing_message = "Gemini is analyzing your voice..."

    result = analyze_voice_with_gemini(voice_audio.getvalue())

    # Keep the status visible until the API result has been handled.
    voice_box.empty()
    st.session_state.is_processing = False
    st.session_state.processing_message = ""

    if result["success"]:
        st.session_state.voice_analysis = result["analysis"]
        st.session_state.voice_transcript = result["analysis"]

        existing = st.session_state.get("prompt_text", "").strip()
        voice_block = (
            "--- VOICE INPUT ANALYZED BY GEMINI ---\n"
            + result["analysis"].strip()
            + "\n--- END VOICE INPUT ---"
        )

        # Prevent duplicate insertion by checking the stable section marker.
        marker = "--- VOICE INPUT ANALYZED BY GEMINI ---"
        if marker not in existing:
            new_prompt = f"{existing}\n\n{voice_block}".strip() if existing else voice_block
            st.session_state.prompt_text = new_prompt
            st.session_state.sync_prompt_editor = True

        st.success("🎙️ Voice input analyzed and added to the prompt.")
        st.rerun()
    else:
        st.error(f"❌ {result['error']}")

if st.session_state.voice_analysis:
    st.info("🎙️ Voice analysis is included in the main prompt and will be reviewed by Grok before code generation.")


# ============================================================
# OPTIONAL CONTEXT & VALIDATION
# ============================================================

if uploaded_file is not None:
    st.markdown(f"""<div class="status-card">📎 <strong>Uploaded:</strong> {uploaded_file.name}</div>""", unsafe_allow_html=True)

if github_url.strip():
    st.markdown(f"""<div class="status-card">🔗 <strong>GitHub Repository:</strong> {github_url}</div>""", unsafe_allow_html=True)

prompt_ready = bool(prompt.strip())
if not prompt_ready:
    st.info("💡 Enter your project idea above to begin.")


# ============================================================
# PRIMARY ACTION AREA
# ============================================================

st.markdown("### 🚀 Start AI Workflow")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    review_button = st.button("🔍 Review Prompt", use_container_width=True, disabled=not prompt_ready)
with col2:
    clear_button = st.button("🗑️ Clear", use_container_width=True)
with col3:
    preview_button = st.button("👁️ Preview Settings", use_container_width=True)

if clear_button:
    # Reset only application-owned state now. The prompt widget is synchronized
    # safely on the next rerun before it is instantiated.
    for key, value in DEFAULT_STATE.items():
        if key in {"prompt_text", "sync_prompt_editor", "voice_input_version"}:
            continue
        st.session_state[key] = copy.deepcopy(value)
    st.session_state.prompt_text = ""
    st.session_state.sync_prompt_editor = True
    st.session_state.voice_input_version += 1
    st.rerun()

if preview_button:
    st.markdown("""<div class="section-card"><div class="section-title">📋 Project Configuration</div></div>""", unsafe_allow_html=True)
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.write(f"**Language:** {programming_language}")
        st.write(f"**Project Type:** {coding_skill}")
    with pcol2:
        st.write(f"**Code Style:** {output_style}")
        st.write(f"**Uploaded Context:** {uploaded_file.name if uploaded_file else 'None'}")


# ============================================================
# GEMINI PROMPT REVIEW & HANDLERS
# ============================================================

def review_prompt_with_grok(user_prompt, programming_language, coding_skill, output_style, github_url=""):
    client = get_grok_client()
    if client is None:
        return {
            "success": False,
            "error": "GROK_API_KEY is not configured. Add GROK_API_KEY to Streamlit Secrets.",
            "reviewed_prompt": "",
        }

    review_instruction = f"""
You are the dedicated prompt-review specialist for an AI Code Builder.
Your ONLY job in this stage is to review, clarify, structure, and improve the user's coding request.
Do not generate application code. Do not invent requirements. Preserve explicit technical choices.

Programming Language: {programming_language}
Project Type: {coding_skill}
Requested Code Style: {output_style}
GitHub Repository: {github_url if github_url else "Not provided"}

USER PROMPT:
{user_prompt}

Return these sections:
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

    try:
        response = client.chat.completions.create(
            model=GROK_REVIEW_MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a senior prompt architect. Review only; do not write application code."},
                {"role": "user", "content": review_instruction},
            ],
        )
        reviewed_prompt = ((response.choices[0].message.content if response.choices else "") or "").strip()
        if not reviewed_prompt:
            return {"success": False, "error": "Grok returned an empty review.", "reviewed_prompt": ""}
        return {"success": True, "error": "", "reviewed_prompt": reviewed_prompt}
    except Exception as error:
        return {"success": False, "error": f"Grok prompt review failed: {error}", "reviewed_prompt": ""}

if review_button and prompt_ready:
    pbox = st.empty()
    pbox.markdown("""<div class="status-card"><div style="font-size:32px;">😂</div><div class="status-text"><strong>Grok is reviewing your prompt...</strong><br>Checking requirements, logic and missing details.</div></div>""", unsafe_allow_html=True)
    res = review_prompt_with_grok(prompt, programming_language, coding_skill, output_style, github_url)
    pbox.empty()
    if res["success"]:
        st.session_state.reviewed_prompt = res["reviewed_prompt"]
        st.session_state.prompt_review_complete = True
        st.success("✅ Prompt review completed successfully.")
    else:
        st.error(f"❌ {res['error']}")

if st.session_state.prompt_review_complete:
    st.markdown("---")
    st.markdown("""<div class="section-card"><div class="section-title">🔍 AI Prompt Review</div><div class="section-description">Grok has analyzed and structured your original request.</div></div>""", unsafe_allow_html=True)
    st.session_state.reviewed_prompt = st.text_area("Reviewed Master Prompt", value=st.session_state.reviewed_prompt, height=420, key="reviewed_prompt_editor")
    st.markdown("""<div class="status-card"><div class="status-text">✅ <strong>Prompt Review Complete</strong></div></div>""", unsafe_allow_html=True)
    
    generate_button = st.button("⚡ Generate Project", type="primary", use_container_width=True)
else:
    generate_button = False


# ============================================================
# PROJECT CODE GENERATION
# ============================================================

def extract_json_from_response(text):
    if not text:
        return None
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return None
    return None

def generate_project_with_gemini(master_prompt, programming_language, coding_skill, output_style):
    client = get_gemini_client()
    if client is None:
        return {"success": False, "error": "Please add GEMINI_API_KEY to Streamlit Secrets.", "files": {}}
    instruction = f"""
You are the senior software engineer for AI Code Builder. Generate the complete project from the approved Master Prompt.

Programming Language: {programming_language}
Project Type: {coding_skill}
Code Style: {output_style}

APPROVED MASTER PROMPT:
{master_prompt}

Return ONLY valid JSON with no Markdown fences matching:
{{
  "files": {{
    "app.py": "complete source code",
    "requirements.txt": "complete requirements",
    "README.md": "complete README"
  }}
}}
"""
    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=instruction)
        project_data = extract_json_from_response((response.text or "").strip())
        if not project_data:
            return {"success": False, "error": "Gemini returned an invalid project structure.", "files": {}}
        files = project_data.get("files", {})
        if not isinstance(files, dict):
            return {"success": False, "error": "Gemini returned an invalid files object.", "files": {}}
        files = {str(k): str(v) for k, v in files.items() if str(k).strip()}
        if not files.get("app.py"):
            return {"success": False, "error": "Gemini did not generate app.py.", "files": files}
        files.setdefault("requirements.txt", "")
        files.setdefault("README.md", "# Generated Project\n")
        return {"success": True, "error": "", "files": files}
    except Exception as error:
        return {"success": False, "error": f"Gemini code generation failed: {error}", "files": {}}

if generate_button:
    gbox = st.empty()
    gbox.markdown("""<div class="status-card"><div style="font-size:32px;">😂</div><div class="status-text"><strong>Generating project files...</strong></div></div>""", unsafe_allow_html=True)
    gen_result = generate_project_with_gemini(st.session_state.reviewed_prompt, programming_language, coding_skill, output_style)
    gbox.empty()
    if gen_result["success"]:
        st.session_state.project_files = gen_result["files"]
        st.session_state.generation_complete = True
        st.success("✅ Code generation complete.")
        st.rerun()
    else:
        st.error(f"❌ {gen_result['error']}")

def create_project_zip(files):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files.items():
            zip_file.writestr(filename, str(content or ""))
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

if st.session_state.generation_complete:
    st.markdown("---")
    st.markdown("""<div class="section-card"><div class="section-title">📥 Download Your Project</div></div>""", unsafe_allow_html=True)
    files = st.session_state.project_files
    
    if "app.py" in files:
        st.download_button("⬇️ Download app.py", data=files["app.py"], file_name="app.py", mime="text/x-python", use_container_width=True)
    if "requirements.txt" in files:
        st.download_button("⬇️ Download requirements.txt", data=files["requirements.txt"], file_name="requirements.txt", mime="text/plain", use_container_width=True)
    if "README.md" in files:
        st.download_button("⬇️ Download README.md", data=files["README.md"], file_name="README.md", mime="text/markdown", use_container_width=True)
    
    project_zip = create_project_zip(files)
    st.download_button("📦 Download Complete Project ZIP", data=project_zip, file_name="ai_generated_project.zip", mime="application/zip", type="primary", use_container_width=True)


# ============================================================
# GEMINI FINAL ERROR DETECTION & CORRECTION
# ============================================================

def check_and_correct_code_with_gemini(app_code, requirements, master_prompt):
    client = get_gemini_client()
    if client is None:
        return {
            "success": False,
            "error": "GEMINI_API_KEY is not configured in Streamlit Secrets.",
            "corrected_code": "",
            "error_report": "",
        }

    validation_prompt = f"""
You are the final senior Python/Streamlit debugging engineer. Inspect the generated app.py against the approved master prompt and requirements.
Find syntax errors, runtime errors, Streamlit widget/session-state errors, invalid API usage, broken imports, unsafe state mutation, incorrect callbacks, duplicate logic, and obvious deployment blockers.
Then return a COMPLETE corrected app.py. Preserve the intended functionality. Do not omit working features.

APPROVED MASTER PROMPT:
{master_prompt}

REQUIREMENTS.TXT:
{requirements}

GENERATED APP.PY:
{app_code}

Return ONLY valid JSON:
{{
  "error_report": "Detailed list of detected issues and fixes.",
  "has_errors": true,
  "corrected_code": "COMPLETE corrected app.py"
}}
"""

    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=validation_prompt)
        result = extract_json_from_response((response.text or "").strip())
        if not result:
            return {"success": False, "error": "Gemini returned an invalid validation response.", "corrected_code": "", "error_report": ""}
        corrected = str(result.get("corrected_code", "")).strip() or app_code
        report = str(result.get("error_report", "No issues found.")).strip()
        return {
            "success": True,
            "error": "",
            "corrected_code": corrected,
            "error_report": report,
            "has_errors": bool(result.get("has_errors", False)),
        }
    except Exception as error:
        return {"success": False, "error": f"Validation failed: {error}", "corrected_code": "", "error_report": ""}

if st.session_state.generation_complete:
    st.markdown("---")
    st.markdown("""<div class="section-card"><div class="section-title">🛡️ Final Error Detection & Correction</div></div>""", unsafe_allow_html=True)
    error_check_button = st.button("🔎 Run Final Error Detection & Auto-Fix", type="primary", use_container_width=True)
else:
    error_check_button = False

if error_check_button:
    app_code_to_check = st.session_state.project_files.get("app.py", "")
    requirements_to_check = st.session_state.project_files.get("requirements.txt", "")
    master_prompt_to_check = st.session_state.reviewed_prompt

    if not app_code_to_check.strip():
        st.error("No generated app.py is available for validation.")
    else:
        ebox = st.empty()
        ebox.markdown("""<div class="status-card"><div style="font-size:32px;">😂</div><div class="status-text"><strong>Gemini is validating and correcting your app.py...</strong></div></div>""", unsafe_allow_html=True)
        validation_result = check_and_correct_code_with_gemini(app_code_to_check, requirements_to_check, master_prompt_to_check)
        ebox.empty()
        if validation_result["success"]:
            st.session_state.error_report = validation_result["error_report"]
            st.session_state.corrected_code = validation_result["corrected_code"]
            st.session_state.project_files["app.py"] = validation_result["corrected_code"]
            st.session_state.error_check_complete = True
            st.success("✅ Error detection and correction completed.")
        else:
            st.error(f"❌ {validation_result['error']}")

if st.session_state.error_check_complete:
    st.markdown("---")
    with st.expander("View Error Detection & Correction Report", expanded=True):
        st.markdown(st.session_state.error_report)
    st.markdown("### ✅ Final Corrected app.py")
    st.code(st.session_state.corrected_code, language="python")

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer">
        AI Code Builder • Prompt → Grok Review → Gemini Generate → Gemini Validate → Fix
    </div>
    """,
    unsafe_allow_html=True,
)
