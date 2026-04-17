from pathlib import Path

"""
dashboard.py — SentryAgent AI Command Center
Enterprise-grade autonomous bug detection & self-healing dashboard.
"""

import os
import sys
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from agent_tools import (
    read_file, write_file,
    run_app, run_tests,
    get_error_log, get_last_log_entry, count_log_entries,
    extract_crash_context, parse_ai_response,
    infer_test_path,
    APP_PATH, TEST_PATH,
)

# ─── Page Config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="AutoFix Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Kill expander arrow via JS MutationObserver ─────────────────────────────
st.markdown("""
<script>
(function() {
    function purgeArrows() {
        document.querySelectorAll('[data-testid="stExpanderToggleIcon"]').forEach(function(el) {
            el.style.cssText = 'display:none!important;width:0!important;height:0!important;';
        });
        document.querySelectorAll('[data-testid="stExpander"] summary p').forEach(function(el) {
            if (el.innerText && el.innerText.trim().indexOf('arrow') !== -1) {
                el.style.cssText = 'display:none!important;font-size:0!important;width:0!important;';
            }
        });
        document.querySelectorAll('[data-testid="stExpander"] summary svg').forEach(function(el) {
            el.style.display = 'none';
        });
    }
    purgeArrows();
    new MutationObserver(purgeArrows).observe(document.body, {childList:true, subtree:true});
})();
</script>
""", unsafe_allow_html=True)

# ─── OpenAI Client ────────────────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("API_KEY")

# ─── CSS: Modern Dark Tech Aesthetic ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary:     #0d1117;
    --bg-surface:     #161b22;
    --bg-elevated:    #21262d;
    --bg-hover:       #1c2128;
    --border-subtle:  #21262d;
    --border-default: #30363d;
    --border-accent:  #388bfd40;
    --text-primary:   #ffffff;
    --text-secondary: #f0f6fc;
    --text-muted:     #c9d1d9;
    --accent-blue:    #58a6ff;
    --accent-green:   #3fb950;
    --accent-red:     #f85149;
    --accent-amber:   #d29922;
    --accent-purple:  #bc8cff;
    --accent-cyan:    #39c5cf;
    --glow-blue:      rgba(56, 139, 253, 0.15);
    --glow-green:     rgba(63, 185, 80, 0.15);
    --glow-red:       rgba(248, 81, 73, 0.15);
    --font-sans:      'Space Grotesk', sans-serif;
    --font-mono:      'JetBrains Mono', monospace;
    --radius-sm:      6px;
    --radius-md:      10px;
    --radius-lg:      14px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background-color: var(--bg-primary) !important;
    font-family: var(--font-sans) !important;
    color: var(--text-primary) !important;
    font-size: 20px;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-surface); }
::-webkit-scrollbar-thumb { background: var(--border-default); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

.block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1400px !important;
}

section[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

h1, h2, h3, h4 {
    font-family: var(--font-sans) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
}
p, li, span, label { font-family: var(--font-sans) !important; }
code, pre, .stCode { font-family: var(--font-mono) !important; }

.metric-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.25rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent-line, var(--border-default));
}
.metric-card:hover {
    border-color: var(--border-default);
    transform: translateY(-1px);
}
.metric-card .card-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
    font-family: var(--font-mono) !important;
}
.metric-card .card-value {
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1;
    font-family: var(--font-mono) !important;
}
.metric-card .card-sub {
    font-size: 0.72rem;
    color: var(--text-secondary);
    margin-top: 0.35rem;
    font-family: var(--font-sans) !important;
}
.metric-card.status-ok  { --accent-line: var(--accent-green); }
.metric-card.status-ok .card-value  { color: var(--accent-green); }
.metric-card.status-err { --accent-line: var(--accent-red); }
.metric-card.status-err .card-value { color: var(--accent-red); }
.metric-card.status-warn{ --accent-line: var(--accent-amber); }
.metric-card.status-warn .card-value{ color: var(--accent-amber); }
.metric-card.status-info{ --accent-line: var(--accent-blue); }
.metric-card.status-info .card-value{ color: var(--accent-blue); }
.metric-card.status-neutral { --accent-line: var(--border-default); }
.metric-card.status-neutral .card-value { color: var(--text-primary); }

.panel {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1.25rem;
}
.panel-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-subtle);
}
.panel-header .panel-title {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-secondary);
    font-family: var(--font-mono) !important;
}
.panel-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--dot-color, var(--accent-blue));
    box-shadow: 0 0 6px var(--dot-color, var(--accent-blue));
}

.diff-wrapper {
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    overflow: hidden;
    background: var(--bg-primary);
    font-family: var(--font-mono) !important;
}
.diff-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border-subtle);
    font-size: 0.72rem;
    font-weight: 500;
    font-family: var(--font-mono) !important;
}
.diff-header.before { color: var(--accent-red); }
.diff-header.after  { color: var(--accent-green); }
.diff-badge {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    font-family: var(--font-mono) !important;
}
.diff-badge.before {
    background: rgba(248,81,73,0.12);
    color: var(--accent-red);
    border: 1px solid rgba(248,81,73,0.25);
}
.diff-badge.after {
    background: rgba(63,185,80,0.12);
    color: var(--accent-green);
    border: 1px solid rgba(63,185,80,0.25);
}

.insight-box {
    background: linear-gradient(135deg, rgba(56,139,253,0.07) 0%, rgba(188,140,255,0.05) 100%);
    border: 1px solid rgba(56,139,253,0.2);
    border-radius: var(--radius-md);
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
    color: var(--text-primary);
    line-height: 1.65;
}

.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-family: var(--font-mono) !important;
}
.tag-blue   { background: rgba(56,139,253,0.12);  color: var(--accent-blue);   border: 1px solid rgba(56,139,253,0.25); }

.crash-ctx {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 0.75rem;
    margin: 0.75rem 0;
}
.crash-ctx-item {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 0.6rem 0.9rem;
}
.crash-ctx-item .ctx-key {
    font-size: 0.62rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: var(--font-mono) !important;
    margin-bottom: 0.2rem;
}
.crash-ctx-item .ctx-val {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-primary);
    font-family: var(--font-mono) !important;
    word-break: break-all;
}

.stButton > button {
    font-family: var(--font-sans) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border-default) !important;
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    border-color: var(--accent-blue) !important;
    background: rgba(56,139,253,0.08) !important;
    color: var(--accent-blue) !important;
}
.stButton [data-testid="baseButton-primary"] {
    background: var(--accent-blue) !important;
    color: white !important;
    border-color: var(--accent-blue) !important;
}

details {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
}
details summary {
    font-family: var(--font-sans) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    padding: 0.6rem 0.9rem !important;
    list-style: none !important;
}
details summary::-webkit-details-marker { display: none !important; }
details[open] summary { border-bottom: 1px solid var(--border-subtle) !important; }
details > div { background: var(--bg-surface) !important; padding: 0.75rem !important; }

[data-testid="stExpander"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--font-sans) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    background: var(--bg-elevated) !important;
    display: flex !important;
    align-items: center !important;
    padding: 0.65rem 1rem !important;
    gap: 0.5rem !important;
}
[data-testid="stExpanderDetails"] {
    background: var(--bg-surface) !important;
    border-top: 1px solid var(--border-subtle) !important;
}
[data-testid="stExpander"] summary,
.streamlit-expanderHeader {
    font-size: 0px !important;
    color: transparent !important;
    line-height: 0 !important;
    display: flex !important;
    align-items: center !important;
    padding: 0.65rem 1rem !important;
    background: var(--bg-elevated) !important;
    cursor: pointer !important;
}
[data-testid="stExpander"] summary p,
.streamlit-expanderHeader p {
    font-size: 0.82rem !important;
    font-family: var(--font-sans) !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    visibility: visible !important;
    line-height: 1.5 !important;
    display: block !important;
    margin: 0 !important;
}
[data-testid="stExpander"] summary svg,
[data-testid="stExpanderToggleIcon"] {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
}
[data-testid="stExpander"] summary::before {
    content: "›" !important;
    font-size: 1.1rem !important;
    font-family: monospace !important;
    color: var(--accent-blue) !important;
    margin-right: 0.5rem !important;
    visibility: visible !important;
    display: inline-block !important;
    transition: transform 0.2s ease !important;
    line-height: 1 !important;
}
[data-testid="stExpander"] details[open] > summary::before {
    transform: rotate(90deg) !important;
}

.stCode, .stCodeBlock, [data-testid="stCode"] {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
}

hr { border-color: var(--border-subtle) !important; margin: 1.25rem 0 !important; }
.stSpinner > div { border-top-color: var(--accent-blue) !important; }

.stSuccess { background: var(--glow-green) !important; border-color: var(--accent-green) !important; }
.stError   { background: var(--glow-red) !important; border-color: var(--accent-red) !important; }
.stWarning { background: rgba(210,153,34,0.12) !important; }

.brand-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.3rem;
}
.brand-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #388bfd 0%, #bc8cff 100%);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    box-shadow: 0 0 16px rgba(56,139,253,0.3);
}
.brand-name {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #e6edf3 0%, #8b949e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: var(--font-sans) !important;
}
.brand-version {
    font-size: 0.62rem;
    font-family: var(--font-mono) !important;
    color: var(--text-muted);
    letter-spacing: 0.06em;
}
.brand-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.04em;
    font-family: var(--font-mono) !important;
    margin-top: 0.1rem;
}

.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: var(--font-mono) !important;
    margin: 1.5rem 0 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border-subtle);
}

.log-viewer {
    background: var(--bg-primary);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1rem;
    max-height: 260px;
    overflow-y: auto;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.6;
}

.sidebar-control-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: var(--font-mono) !important;
    margin-bottom: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "bug_found": False,
        "insight": "",
        "suggested_fix": "",
        "original_code": "",
        "debug_explanation": None,
        "last_run_status": None,
        "last_run_output": "",
        "last_verify_status": None,
        "last_verify_output": "",
        "crash_context": {},
        "fix_applied": False,
        "api_key_override": "",
        "target_file": str(APP_PATH),
        "test_path": str(TEST_PATH),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_client() -> OpenAI | None:
    key = st.session_state.api_key_override or API_KEY
    if not key:
        return None
    return OpenAI(api_key=key)

def call_gpt(messages: list[dict], model="gpt-4o", max_tokens=2048) -> str:
    c = get_client()
    if c is None:
        st.error("⚠️ API key not configured. Set API_KEY.")
        st.stop()
    resp = c.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens)
    return resp.choices[0].message.content

def metric_card(label: str, value: str, sub: str = "", status: str = "neutral") -> str:
    return f"""
    <div class="metric-card status-{status}">
        <div class="card-label">{label}</div>
        <div class="card-value">{value}</div>
        {'<div class="card-sub">' + sub + '</div>' if sub else ''}
    </div>"""

def crash_ctx_html(ctx: dict) -> str:
    items = [
        ("File", ctx.get("file") or "—"),
        ("Line", str(ctx.get("line_number") or "—")),
        ("Function", ctx.get("function") or "—"),
        ("Exception", ctx.get("error_type") or "—"),
        ("Message", ctx.get("error_message") or "—"),
    ]
    cards = "".join(f"""
    <div class="crash-ctx-item">
        <div class="ctx-key">{k}</div>
        <div class="ctx-val">{v}</div>
    </div>""" for k, v in items)
    return f'<div class="crash-ctx">{cards}</div>'

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_target_name = Path(st.session_state.target_file).name

    st.markdown("""
    <div class="brand-header">
        <div class="brand-icon">🛡️</div>
        <div>
            <div class="brand-name">SentryAgent</div>
            <div class="brand-version">v2.0 · AI</div>
        </div>
    </div>
    <div class="brand-sub">Autonomous Bug Detection System</div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-control-label">Step 1 · Execute</div>', unsafe_allow_html=True)
    run_btn = st.button("▶  Run Target & Catch Errors", use_container_width=True)

    st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-control-label">Step 2 · Analyze & Heal</div>', unsafe_allow_html=True)
    scan_btn = st.button("🔬  Scan & Fix with AI", use_container_width=True, type="primary")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-control-label">Target</div>', unsafe_allow_html=True)
    st.markdown(f'<span class="tag tag-blue">{sidebar_target_name}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="brand-sub" style="margin-top:0.3rem">Python {sys.version.split()[0]}</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    bug_count = count_log_entries()
    st.markdown(
        f'<div class="sidebar-control-label">Total Crashes Logged</div>'
        f'<div style="font-size:1.4rem;font-weight:700;font-family:var(--font-mono);color:var(--accent-amber)">{bug_count}</div>',
        unsafe_allow_html=True
    )

# ─── Header Metrics ───────────────────────────────────────────────────────────
def build_metrics_row():
    if st.session_state.last_run_status == "ok":
        sys_status, sys_sub, sys_cls = "NOMINAL", "Last run succeeded", "status-ok"
    elif st.session_state.last_run_status == "error":
        sys_status, sys_sub, sys_cls = "CRASH", "Error captured to log", "status-err"
    else:
        sys_status, sys_sub, sys_cls = "IDLE", "Awaiting execution", "status-neutral"

    if st.session_state.last_verify_status == "passed":
        ver_val, ver_sub, ver_cls = "PASSED", "All assertions green", "status-ok"
    elif st.session_state.last_verify_status == "failed":
        ver_val, ver_sub, ver_cls = "FAILED", "Fix did not satisfy tests", "status-err"
    else:
        ver_val, ver_sub, ver_cls = "—", "Not yet verified", "status-neutral"

    bc = count_log_entries()
    bc_cls = "status-warn" if bc > 0 else "status-ok"

    if st.session_state.bug_found and not st.session_state.fix_applied:
        agent_val, agent_sub, agent_cls = "PENDING", "Fix ready to apply", "status-warn"
    elif st.session_state.fix_applied:
        agent_val, agent_sub, agent_cls = "HEALED", "Fix applied & verified", "status-ok"
    else:
        agent_val, agent_sub, agent_cls = "STANDBY", "No active session", "status-neutral"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("System Status", sys_status, sys_sub, sys_cls), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Crashes Logged", str(bc), "since session start", bc_cls), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Last Verification", ver_val, ver_sub, ver_cls), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("Agent State", agent_val, agent_sub, agent_cls), unsafe_allow_html=True)

# ─── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.25rem;">
  <div style="font-size:1.7rem;font-weight:700;letter-spacing:-0.04em;
              font-family:'Space Grotesk',sans-serif;color:#e6edf3;">
    SentryAgent <span style="color:#388bfd;">AI</span>
  </div>
  <span class="tag tag-blue">COMMAND CENTER</span>
</div>
<div style="font-size:0.78rem;color:#8b949e;font-family:'JetBrains Mono',monospace;
            letter-spacing:0.04em;margin-bottom:1.25rem;">
  Autonomous Bug Detection · Self-Healing Pipeline · Enterprise Edition
</div>
""", unsafe_allow_html=True)

build_metrics_row()
st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

# ─── Action: Run App ──────────────────────────────────────────────────────────
if run_btn:
    current_target_name = Path(st.session_state.target_file).name
    with st.status(f"⚡ Executing {current_target_name}...", expanded=True) as status_box:
        st.write("🔍 Spawning subprocess...")
        has_error, output = run_app(st.session_state.target_file)
        if has_error:
            st.session_state.last_run_status = "error"
            st.session_state.last_run_output = output
            st.write("❗ Crash detected — error appended to log.")
            status_box.update(label="💥 Crash detected. Error saved to log.", state="error")
        else:
            st.session_state.last_run_status = "ok"
            st.session_state.last_run_output = output
            st.write("✅ App exited cleanly.")
            status_box.update(label="✅ App ran successfully.", state="complete")
    st.rerun()

# ─── Action: Scan & Fix ───────────────────────────────────────────────────────
if scan_btn:
    log_content = get_last_log_entry()
    if not log_content.strip():
        st.warning("⚠️ Error log is empty. Run the target first to capture a crash.")
    else:
        st.session_state.debug_explanation = None
        st.session_state.fix_applied = False
        st.session_state.bug_found = False

        with st.status("🤖 SentryAgent is analyzing...", expanded=True) as agent_status:
            st.write("🔍 Parsing traceback & extracting crash context...")
            crash_ctx = extract_crash_context(log_content)

            target_file = crash_ctx.get("file") or str(APP_PATH)
            target_path = Path(target_file)
            target_file_name = target_path.name
            target_module_name = target_path.stem

            test_path = infer_test_path(target_file)
            test_file_name = test_path.name

            st.session_state.target_file = str(target_file)
            st.session_state.test_path = str(test_path)
            st.session_state.crash_context = crash_ctx

            original_code = read_file(target_file)
            st.session_state.original_code = original_code

            st.write(f"🧪 Generating reproduction test ({test_file_name})...")
            test_prompt = f"""You are a Senior QA Engineer AI. Your task is to write a robust pytest file for `{target_file_name}`.

TARGET TEST FILE:
- {test_file_name}

CRASH CONTEXT:
- File: {crash_ctx.get('file', target_file_name)}
- Function: {crash_ctx.get('function', 'unknown')}
- Exception: {crash_ctx.get('error_type', 'unknown')} — {crash_ctx.get('error_message', '')}
- Line: {crash_ctx.get('line_number', '?')}

FULL ERROR LOG ENTRY:
{log_content}

TARGET FILE ({target_file_name}) — read ALL functions before writing the test:
{original_code}

RULES:
1. Import functions directly from the `{target_module_name}` module.
2. Write tests that VERIFY the fixed behaviour — they must FAIL on the broken code and PASS on the healed code.
3. Match the logic of the current code instead of inventing unrelated behaviour.
4. Return ONLY valid Python code. No markdown fences. No explanations.
"""
            generated_test = call_gpt([{"role": "user", "content": test_prompt}])
            clean_test = generated_test.replace("```python", "").replace("```", "").strip()
            write_file(st.session_state.test_path, clean_test)

            st.write("🧠 Reasoning about root cause and generating fix...")
            fix_prompt = f"""You are SentryAgent AI — an expert autonomous debugging system.

CRASH CONTEXT (dynamically extracted):
- File:      {crash_ctx.get('file', target_file_name)}
- Function:  {crash_ctx.get('function', 'unknown')}
- Exception: {crash_ctx.get('error_type', 'unknown')} — {crash_ctx.get('error_message', '')}
- Line:      {crash_ctx.get('line_number', '?')}

FULL ERROR LOG ENTRY:
{log_content}

FULL SOURCE CODE ({target_file_name}):
{original_code}

STRICT HEALING RULES:
1. NONE-RETURN POLICY: Any data-retrieval pattern (dict.get, list access, db query, attribute access) that can fail MUST return Python None (not the string "None", not False, not 0).
2. TYPE SAFETY: Functions that process collections must gracefully skip invalid types instead of crashing.
3. PRESERVE ALL EXISTING FUNCTION SIGNATURES exactly — do not rename or remove functions.
4. Apply MINIMAL changes — only fix what caused the crash and any adjacent fragility.
5. Use the EXACT response format below:

EXPLANATION: <concise root-cause analysis, 2-4 sentences>
CODE: <complete healed {target_file_name}, no markdown fences>
"""
            fix_response = call_gpt([{"role": "user", "content": fix_prompt}])

            explanation, clean_code = parse_ai_response(fix_response)
            st.session_state.insight = explanation
            st.session_state.suggested_fix = clean_code
            st.session_state.bug_found = True

            agent_status.update(label="✅ Analysis complete. Review the fix below.", state="complete")

        st.rerun()

# ─── Main Content: Analysis Results ───────────────────────────────────────────
if st.session_state.bug_found:
    current_target_name = Path(st.session_state.target_file).name
    current_test_name = Path(st.session_state.test_path).name

    st.markdown('<div class="section-title">Crash Analysis</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("""
        <div class="panel">
          <div class="panel-header">
            <div class="panel-dot" style="--dot-color:var(--accent-blue)"></div>
            <div class="panel-title">AI Root Cause Analysis</div>
          </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="insight-box">{st.session_state.insight}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        ctx = st.session_state.crash_context
        st.markdown("""
        <div class="panel">
          <div class="panel-header">
            <div class="panel-dot" style="--dot-color:var(--accent-red)"></div>
            <div class="panel-title">Crash Context</div>
          </div>""", unsafe_allow_html=True)
        st.markdown(crash_ctx_html(ctx), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("Deep Debugging · Mentor Mode", expanded=False):
            st.markdown("""
            <div style="font-size:0.72rem;color:var(--text-muted);
                        font-family:var(--font-mono);letter-spacing:0.04em;
                        margin-bottom:0.75rem;">
                Educational breakdown for developer growth
            </div>""", unsafe_allow_html=True)

            if st.session_state.debug_explanation is None:
                with st.spinner("🧠 Generating mentor explanation..."):
                    debug_prompt = f"""You are a Senior Software Engineer mentoring a junior developer.

Error Summary: {st.session_state.insight}
Crash Context: {st.session_state.crash_context}
Original Code:
{st.session_state.original_code}

Write a structured, educational explanation using EXACTLY this format:

**🔬 The Root Cause**
[Explain precisely WHY the crash happened at the technical level. Reference the specific line and data pattern.]

**⚠️ The Production Risk**
[Explain what disaster this causes in a real production system — data loss, cascade failures, user impact.]

**✅ Best Practice**
[Teach the correct defensive pattern using concrete code examples. Reference industry-standard approaches.]

**📚 Further Reading**
[Mention 1-2 relevant Python docs / PEPs / patterns by name only (no URLs needed).]

Be concise, precise, and use code examples where helpful.
"""
                    st.session_state.debug_explanation = call_gpt(
                        [{"role": "user", "content": debug_prompt}],
                        max_tokens=1200
                    )

            st.markdown(st.session_state.debug_explanation)

    st.markdown('<div class="section-title">Code Review · Proposed Patch</div>', unsafe_allow_html=True)

    col_before, col_after = st.columns(2)

    with col_before:
        st.markdown(f"""
            <div class="diff-wrapper">
              <div class="diff-header before">
                <span class="diff-badge before">BEFORE</span>
                {current_target_name} · original
              </div>
            </div>""", unsafe_allow_html=True)
        st.code(st.session_state.original_code, language="python")

    with col_after:
        st.markdown(f"""
            <div class="diff-wrapper">
              <div class="diff-header after">
                <span class="diff-badge after">AFTER</span>
                {current_target_name} · healed patch
              </div>
            </div>""", unsafe_allow_html=True)
        st.code(st.session_state.suggested_fix, language="python")

    with st.expander(f"🧪 View Generated Reproduction Test ({current_test_name})", expanded=False):
        test_content = read_file(st.session_state.test_path)
        if test_content:
            st.code(test_content, language="python")
        else:
            st.info(f"{current_test_name} not yet written.")

    st.markdown('<div class="section-title">Verification Gate</div>', unsafe_allow_html=True)

    cta_col, info_col = st.columns([1, 2])
    with cta_col:
        apply_btn = st.button("🚀 Apply Fix & Run Verification", type="primary", use_container_width=True)
    with info_col:
        st.markdown(
            f'<div class="insight-box" style="padding:0.6rem 1rem;font-size:0.78rem;">'
            f'⚡ This will overwrite <code>{current_target_name}</code> with the healed version, '
            f'then run <code>{current_test_name}</code> via pytest. The fix is only accepted '
            f'if all assertions pass.'
            f'</div>',
            unsafe_allow_html=True
        )

    if apply_btn:
        write_file(st.session_state.target_file, st.session_state.suggested_fix)

        with st.status("🧪 Running autonomous verification suite...", expanded=True) as verify_status:
            st.write(f"📝 Fix written to {current_target_name}.")
            st.write(f"⚙️ Invoking pytest on {current_test_name}...")
            passed, output = run_tests(st.session_state.test_path)
            st.session_state.last_verify_output = output
            st.session_state.last_verify_status = "passed" if passed else "failed"

            if passed:
                st.session_state.fix_applied = True
                verify_status.update(label="✅ Verification passed — code is healthy.", state="complete")
                st.balloons()
            else:
                verify_status.update(label="❌ Verification failed — review output below.", state="error")

        st.rerun()

    if st.session_state.last_verify_status is not None:
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        if st.session_state.last_verify_status == "passed":
            st.success("✅ All test assertions passed. The self-healing cycle is complete.")
        else:
            st.error("⚠️ The generated fix did not satisfy the autonomous test suite.")

        with st.expander("📋 Full pytest Output", expanded=(st.session_state.last_verify_status == "failed")):
            st.code(st.session_state.last_verify_output, language="text")

# ─── Error Log Viewer ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Error Log · Chronological History</div>', unsafe_allow_html=True)

log_body = get_error_log()
if log_body.strip():
    st.markdown(
        f'<div class="log-viewer">{log_body}</div>',
        unsafe_allow_html=True
    )
    if st.button("🗑 Clear Error Log", use_container_width=False):
        write_file("error_log.txt", "")
        st.session_state.last_run_status = None
        st.rerun()
else:
    st.markdown(
        '<div class="log-viewer" style="color:var(--text-muted);text-align:center;padding:2rem;">'
        'No crash entries yet. Run the target to begin monitoring.'
        '</div>',
        unsafe_allow_html=True
    )