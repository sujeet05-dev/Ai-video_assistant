import streamlit as st
import time
import os
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant — Meeting Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS Design System ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Design Tokens ── */
:root {
    --bg: #0b0c13;
    --surface: #13141f;
    --surface-2: #1b1c2b;
    --surface-3: #232538;
    --border: #26283d;
    --border-hover: #3b3e5e;
    --accent: #8b5cf6;
    --accent-glow: #a78bfa;
    --accent-2: #06b6d4;
    --accent-3: #f43f5e;
    --text: #f1f2f8;
    --text-secondary: #c2c5dc;
    --text-muted: #797d9e;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* ── Global Typography & Background ── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Subtle architectural grid pattern */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        radial-gradient(circle at 15% 15%, rgba(139, 92, 246, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 85% 85%, rgba(6, 182, 212, 0.06) 0%, transparent 40%),
        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 48px 48px, 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* ── Streamlit Header Bar Fix ── */
[data-testid="stHeader"] {
    background: transparent !important;
    color: var(--text) !important;
}

header {
    background: transparent !important;
}

.stDeployButton, [data-testid="stToolbar"] {
    display: none !important;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* ── Sidebar Styling ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* ── Hero Title ── */
.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 800;
    line-height: 1.15;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
}

.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: var(--text-muted);
    font-weight: 400;
    margin-top: 0.35rem;
}

/* ── Bordered Containers (Cards) ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.4rem 1.6rem !important;
    margin-bottom: 1.25rem !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--border-hover) !important;
}

/* Equal height column alignment */
[data-testid="column"] > [data-testid="stVerticalBlockBorderWrapper"] {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

/* ── Header Row inside Content Boxes ── */
.card-header-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 0.85rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

.card-header-left {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.card-icon {
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

/* ── Badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
}

.badge-purple { background: rgba(139, 92, 246, 0.16); color: var(--accent-glow); border: 1px solid rgba(139, 92, 246, 0.35); }
.badge-cyan   { background: rgba(6, 182, 212, 0.15); color: var(--accent-2);    border: 1px solid rgba(6, 182, 212, 0.3); }
.badge-green  { background: rgba(16, 185, 129, 0.15); color: var(--success);    border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-amber  { background: rgba(245, 158, 11, 0.15); color: var(--warning);    border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-gray   { background: rgba(255, 255, 255, 0.06); color: var(--text-muted); border: 1px solid var(--border); }

/* ── Session Banner ── */
.session-banner {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(6, 182, 212, 0.06) 100%);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}

.session-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}

.session-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.25;
    margin-top: 0.35rem;
    margin-bottom: 0.75rem;
}

.metadata-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
}

/* ── Modern Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: var(--surface) !important;
    padding: 7px;
    border-radius: 12px;
    border: 1px solid var(--border);
    margin-bottom: 1.25rem;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0 20px !important;
    border: none !important;
    background-color: transparent !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
    background-color: var(--surface-2) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.25), rgba(6, 182, 212, 0.15)) !important;
    color: #ffffff !important;
    border: 1px solid rgba(139, 92, 246, 0.45) !important;
    box-shadow: 0 4px 16px rgba(139, 92, 246, 0.2) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

/* ── Markdown Content Styling ── */
[data-testid="stMarkdownContainer"] p {
    font-size: 0.93rem !important;
    line-height: 1.75 !important;
    color: var(--text-secondary) !important;
    margin-bottom: 0.75rem !important;
}

[data-testid="stMarkdownContainer"] ul, 
[data-testid="stMarkdownContainer"] ol {
    margin-left: 1.25rem !important;
    margin-bottom: 0.85rem !important;
}

[data-testid="stMarkdownContainer"] li {
    font-size: 0.92rem !important;
    line-height: 1.7 !important;
    color: var(--text-secondary) !important;
    margin-bottom: 0.45rem !important;
}

[data-testid="stMarkdownContainer"] strong {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Tables */
table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 1rem 0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}

th {
    background: var(--surface-2) !important;
    color: var(--accent-glow) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid var(--border) !important;
}

td {
    padding: 10px 14px !important;
    border-bottom: 1px solid var(--border) !important;
    font-size: 0.88rem !important;
    color: var(--text-secondary) !important;
}

tr:hover td {
    background: rgba(139, 92, 246, 0.05) !important;
}

/* ── Status Bar ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-2);
    border-radius: 8px;
    margin: 0.4rem 0;
    border: 1px solid var(--border);
    font-size: 0.84rem;
    font-weight: 500;
}

.status-dot {
    width: 9px; height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active   { background: var(--accent-glow); box-shadow: 0 0 10px var(--accent-glow); animation: pulse 1.4s infinite; }
.dot-done     { background: var(--success); }
.dot-pending  { background: var(--border); }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.4; transform: scale(0.9); }
}

/* ── Chat System ── */
.chat-container {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 460px;
    overflow-y: auto;
    margin-bottom: 1.25rem;
}

.chat-msg {
    margin-bottom: 1.15rem;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
}

.chat-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.chat-bubble {
    display: inline-block;
    padding: 0.75rem 1.15rem;
    border-radius: 12px;
    font-size: 0.92rem;
    line-height: 1.65;
    max-width: 88%;
}

.user-label  { color: var(--accent-glow); }
.bot-label   { color: var(--accent-2); }

.user-bubble {
    background: rgba(139, 92, 246, 0.18);
    border: 1px solid rgba(139, 92, 246, 0.35);
    align-self: flex-end;
    color: #ffffff;
}

.bot-bubble {
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.25);
    align-self: flex-start;
    color: var(--text);
}

/* ── Transcript Box ── */
.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem;
    font-size: 0.88rem;
    line-height: 1.85;
    max-height: 480px;
    overflow-y: auto;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Buttons & Forms ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #6d28d9) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(139, 92, 246, 0.35) !important;
}

.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--surface-3) !important;
    border-color: var(--border-hover) !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
    color: var(--text) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.25) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active":  return "dot-active"
    if s == "done":    return "dot-done"
    return "dot-pending"

def render_step_bar(label: str, key: str, icon: str):
    css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {css}"></div>
        <span>{icon} {label}</span>
    </div>""", unsafe_allow_html=True)

def build_full_report_text(r: dict) -> str:
    """Combine all results into a clean text document for download."""
    lines = [
        "=" * 70,
        f"MEETING INTELLIGENCE REPORT: {r['title']}",
        "=" * 70,
        "",
        "--- EXECUTIVE SUMMARY ---",
        r["summary"],
        "",
        "--- ACTION ITEMS ---",
        r["action_items"],
        "",
        "--- KEY DECISIONS ---",
        r["key_decisions"],
        "",
        "--- OPEN QUESTIONS & FOLLOW-UPS ---",
        r["open_questions"],
        "",
        "=" * 70,
        "--- FULL TRANSCRIPT ---",
        "=" * 70,
        r["transcript"],
    ]
    return "\n".join(lines)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.25rem">
        <div style="font-size:2rem">🎬</div>
        <div>
            <div class="hero-title" style="font-size:1.45rem">AI Video</div>
            <div class="hero-sub" style="font-size:0.78rem">Meeting Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<span class="badge badge-purple" style="margin-bottom:0.5rem">INPUT SOURCE</span>', unsafe_allow_html=True)
    source = st.text_input(
        "Source URL or Path",
        placeholder="https://youtube.com/watch?v=... or local file.mp4",
        label_visibility="collapsed",
    )

    st.markdown('<span class="badge badge-cyan" style="margin-top:0.75rem; margin-bottom:0.5rem">AUDIO LANGUAGE</span>', unsafe_allow_html=True)
    language = st.selectbox(
        "Audio Language",
        ["english", "hinglish"],
        index=0,
        label_visibility="collapsed",
        help="Choose English for standard Whisper, or Hinglish for Sarvam AI audio translation.",
    )

    run_btn = st.button("⚡  Analyze Video", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="badge badge-green" style="margin-bottom:0.5rem">PIPELINE STATUS</span>', unsafe_allow_html=True)
        for step, icon, label in [
            ("audio",      "🔊", "Audio Extraction"),
            ("transcript", "📝", "Whisper STT"),
            ("title",      "🏷️", "Title Generation"),
            ("summary",    "📋", "Executive Summary"),
            ("extract",    "🔍", "Action & Decisions"),
            ("rag",        "🧠", "RAG Engine Ready"),
        ]:
            render_step_bar(label, step, icon)

        st.markdown("---")
        if st.button("🔄 Reset & Analyze New", use_container_width=True, type="secondary"):
            st.session_state.result = None
            st.session_state.pipeline_done = False
            st.session_state.chat_history = []
            st.session_state.pipeline_steps = {}
            st.rerun()

# ─── Main Header ────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Video Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Automated Meeting Intelligence · Key Deliverables · Interactive Q&A</div>', unsafe_allow_html=True)
st.markdown("<hr style='margin: 1rem 0 1.5rem 0'>", unsafe_allow_html=True)

# ─── Pipeline Execution ─────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a valid YouTube URL or local video/audio file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("⚙️ Processing pipeline initialized. Live status updates in sidebar...")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items = extract_action_items(transcript)
            time.sleep(0.5)
            decisions = extract_key_decisions(transcript)
            time.sleep(0.5)
            questions = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
                "source": source,
                "language": language,
                "chunk_count": len(chunks) if "chunks" in locals() else 1,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis successfully completed!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio", "transcript", "title", "summary", "extract", "rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"❌ Error during processing: {e}")

# ─── Display Results ─────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
    word_count = len(r["transcript"].split())
    reading_time = max(1, round(word_count / 150))

    # Top Hero Session Banner
    st.markdown(f"""
    <div class="session-banner">
        <div style="display:flex; justify-content:space-between; align-items:center">
            <span class="badge badge-purple">INTELLIGENCE REPORT</span>
            <span class="badge badge-green">⚡ RAG READY</span>
        </div>
        <div class="session-title">{r['title']}</div>
        <div class="metadata-row">
            <span class="badge badge-gray">🌐 {r.get('language', 'English').capitalize()}</span>
            <span class="badge badge-gray">📦 {r.get('chunk_count', 1)} Chunks Processed</span>
            <span class="badge badge-gray">📝 ~{word_count:,} Words</span>
            <span class="badge badge-gray">⏱️ ~{reading_time} Min Read</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action Toolbar: Downloads & Exports
    export_col1, export_col2, export_col3 = st.columns([1, 1, 2], gap="small")
    with export_col1:
        st.download_button(
            label="📥 Download Full Report",
            data=build_full_report_text(r),
            file_name=f"Meeting_Report_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with export_col2:
        st.download_button(
            label="📝 Export Transcript",
            data=r["transcript"],
            file_name=f"Transcript_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

    # ── Tabs Architecture ───────────────────────────────────────────────────────
    tab_briefing, tab_chat, tab_transcript = st.tabs([
        "📊 Executive Briefing",
        "💬 Chat with Meeting",
        "📜 Full Transcript",
    ])

    # ── TAB 1: EXECUTIVE BRIEFING ──────────────────────────────────────────────
    with tab_briefing:
        # Full Width Executive Summary Card
        with st.container(border=True):
            st.markdown("""
            <div class="card-header-bar">
                <div class="card-header-left">
                    <span class="card-icon">📋</span>
                    <span class="card-title">Executive Summary</span>
                </div>
                <span class="badge badge-purple">Key Insights</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(r["summary"])

        # Balanced 2-Column Row: Action Items & Key Decisions
        col_actions, col_decisions = st.columns(2, gap="medium")

        with col_actions:
            with st.container(border=True):
                st.markdown("""
                <div class="card-header-bar">
                    <div class="card-header-left">
                        <span class="card-icon">✅</span>
                        <span class="card-title">Action Items & Deliverables</span>
                    </div>
                    <span class="badge badge-cyan">Tasks & Owners</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(r["action_items"])

        with col_decisions:
            with st.container(border=True):
                st.markdown("""
                <div class="card-header-bar">
                    <div class="card-header-left">
                        <span class="card-icon">🔑</span>
                        <span class="card-title">Key Decisions Made</span>
                    </div>
                    <span class="badge badge-green">Agreed Points</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(r["key_decisions"])

        # Full Width Bottom Card: Open Questions & Next Steps
        with st.container(border=True):
            st.markdown("""
            <div class="card-header-bar">
                <div class="card-header-left">
                    <span class="card-icon">❓</span>
                    <span class="card-title">Open Questions & Follow-ups</span>
                </div>
                <span class="badge badge-amber">Action Needed</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(r["open_questions"])

    # ── TAB 2: RAG CHAT WITH MEETING ───────────────────────────────────────────
    with tab_chat:
        with st.container(border=True):
            st.markdown("""
            <div class="card-header-bar">
                <div class="card-header-left">
                    <span class="card-icon">💬</span>
                    <span class="card-title">Interactive Q&A Assistant</span>
                </div>
                <span class="badge badge-cyan">Powered by LangChain & Mistral</span>
            </div>
            """, unsafe_allow_html=True)

            # Quick Prompt Suggestion Chips
            st.markdown("<div style='font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem'>💡 Suggested Questions:</div>", unsafe_allow_html=True)
            chip_col1, chip_col2, chip_col3 = st.columns(3, gap="small")
            
            prompt_to_ask = None
            with chip_col1:
                if st.button("📌 Top 3 Takeaways", use_container_width=True, type="secondary"):
                    prompt_to_ask = "What were the top 3 most important takeaways from this meeting?"
            with chip_col2:
                if st.button("👥 Who Owns What?", use_container_width=True, type="secondary"):
                    prompt_to_ask = "List all individuals mentioned and their assigned responsibilities."
            with chip_col3:
                if st.button("⚠️ Blockers & Risks", use_container_width=True, type="secondary"):
                    prompt_to_ask = "Were any blockers, risks, or unresolved concerns mentioned?"

            # Chat History Container
            if st.session_state.chat_history:
                chat_html = '<div class="chat-container">'
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        chat_html += f"""
                        <div class="chat-msg" style="align-items:flex-end">
                            <span class="chat-label user-label">You</span>
                            <div class="chat-bubble user-bubble">{msg['content']}</div>
                        </div>"""
                    else:
                        chat_html += f"""
                        <div class="chat-msg" style="align-items:flex-start">
                            <span class="chat-label bot-label">🤖 Meeting Assistant</span>
                            <div class="chat-bubble bot-bubble">{msg['content']}</div>
                        </div>"""
                chat_html += "</div>"
                st.markdown(chat_html, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center; padding: 2.5rem 1rem; background:var(--surface-2); border-radius:10px; margin-bottom:1rem; border:1px solid var(--border)">
                    <div style="font-size:2.5rem; margin-bottom:0.5rem">🧠</div>
                    <div style="font-weight:600; font-size:1.05rem; color:var(--text); margin-bottom:0.25rem">Ask anything about this meeting</div>
                    <div style="color:var(--text-muted); font-size:0.85rem">Ask about specific decisions, deadlines, speakers, or details from the transcript.</div>
                </div>
                """, unsafe_allow_html=True)

            # Chat Input Form
            with st.form("chat_form", clear_on_submit=True):
                chat_input_col, chat_btn_col = st.columns([5, 1], gap="small")
                with chat_input_col:
                    user_query = st.text_input(
                        "Your question",
                        placeholder="Type your question and hit Enter... (e.g. 'What was agreed about the budget?')",
                        label_visibility="collapsed",
                    )
                with chat_btn_col:
                    submit_query = st.form_submit_button("Ask →", use_container_width=True)

            active_question = prompt_to_ask or (user_query.strip() if submit_query and user_query.strip() else None)

            if active_question:
                with st.spinner("Analyzing meeting transcript..."):
                    bot_reply = ask_question(r["rag_chain"], active_question)
                st.session_state.chat_history.append({"role": "user", "content": active_question})
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                st.rerun()

            if st.session_state.chat_history:
                if st.button("🗑️ Clear Conversation", type="secondary"):
                    st.session_state.chat_history = []
                    st.rerun()

    # ── TAB 3: FULL TRANSCRIPT ─────────────────────────────────────────────────
    with tab_transcript:
        with st.container(border=True):
            st.markdown(f"""
            <div class="card-header-bar">
                <div class="card-header-left">
                    <span class="card-icon">📜</span>
                    <span class="card-title">Verbatim Transcript</span>
                </div>
                <span class="badge badge-gray">{word_count:,} Words</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

else:
    # ── Empty State ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:3.5rem 1rem; text-align:center">
        <div style="font-size:3.5rem; margin-bottom:0.75rem">🎬</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:1.6rem; font-weight:800; color:var(--text); margin-bottom:0.5rem">
            Ready to Analyze Your Meeting
        </div>
        <div style="color:var(--text-muted); font-size:0.92rem; max-width:480px; line-height:1.7; margin-bottom:2rem">
            Paste any YouTube URL or upload a local video/audio file in the left sidebar to generate structured executive summaries, action items, key decisions, and an interactive Q&A assistant.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature Grid
    col_f1, col_f2, col_f3 = st.columns(3, gap="medium")
    with col_f1:
        with st.container(border=True):
            st.markdown("""
            <div style="font-size:1.5rem; margin-bottom:0.5rem">🔊</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif; font-weight:700; font-size:1rem; margin-bottom:0.35rem">Local Transcription</div>
            <div style="color:var(--text-muted); font-size:0.85rem; line-height:1.6">OpenAI Whisper extracts high-fidelity transcripts directly on your machine with zero cloud audio leaks.</div>
            """, unsafe_allow_html=True)

    with col_f2:
        with st.container(border=True):
            st.markdown("""
            <div style="font-size:1.5rem; margin-bottom:0.5rem">📋</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif; font-weight:700; font-size:1rem; margin-bottom:0.35rem">Executive Intelligence</div>
            <div style="color:var(--text-muted); font-size:0.85rem; line-height:1.6">Automated extraction of action items, owners, firm decisions, and unresolved follow-up questions.</div>
            """, unsafe_allow_html=True)

    with col_f3:
        with st.container(border=True):
            st.markdown("""
            <div style="font-size:1.5rem; margin-bottom:0.5rem">🧠</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif; font-weight:700; font-size:1rem; margin-bottom:0.35rem">Interactive RAG Chat</div>
            <div style="color:var(--text-muted); font-size:0.85rem; line-height:1.6">Vector embeddings stored in ChromaDB allow you to converse and ask deep questions about the meeting.</div>
            """, unsafe_allow_html=True)