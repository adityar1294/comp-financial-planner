import streamlit as st
import plotly.graph_objects as go
import json
import math
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="WealthPath · Retirement Planner",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── DESIGN SYSTEM ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #0d0f1a !important;
    color: #e8eaf0 !important;
}

/* ── Global text colour overrides — catch every Streamlit text node ── */
p, span, div, li, td, th, label,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stText"],
.stMarkdown, .stText,
[class*="st-"] { color: #e8eaf0; }

/* Streamlit default dark-on-light overrides */
.stApp [data-testid="stVerticalBlock"] p { color: #e8eaf0 !important; }
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span { color: rgba(255,255,255,0.5) !important; }

/* Dataframe / table text */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] span { color: #e8eaf0 !important; }

/* Expander header text */
[data-testid="stExpander"] summary span { color: rgba(255,255,255,0.6) !important; }

/* Select / dropdown option text */
[data-testid="stSelectbox"] span,
[data-testid="stSelectbox"] div { color: #e8eaf0 !important; }

/* Slider value labels */
[data-testid="stSlider"] span,
[data-testid="stSlider"] p { color: rgba(255,255,255,0.5) !important; }

/* Radio option text */
[data-testid="stRadio"] span { color: #e8eaf0 !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px !important; }

/* ── Background gradient blobs ── */
.stApp::before {
    content: '';
    position: fixed; top: -20%; left: -10%;
    width: 55vw; height: 55vw;
    background: radial-gradient(circle, rgba(99,66,199,0.13) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}
.stApp::after {
    content: '';
    position: fixed; bottom: -15%; right: -5%;
    width: 45vw; height: 45vw;
    background: radial-gradient(circle, rgba(32,178,170,0.10) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}

/* ── Typography ── */
h1, h2, h3 { font-family: 'Sora', sans-serif; }

/* ── Glass card ── */
.glass {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    padding: 1.5rem 1.75rem;
    position: relative;
    overflow: hidden;
}
.glass::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}

/* ── Section label ── */
.sec-label {
    font-size: 10px; font-weight: 600; letter-spacing: .12em;
    text-transform: uppercase; color: rgba(255,255,255,0.35);
    margin-bottom: 1.1rem; margin-top: 0.25rem;
}

/* ── Page header ── */
.page-header {
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 2rem;
}
.logo-mark {
    width: 42px; height: 42px; border-radius: 12px;
    background: linear-gradient(135deg, #6342c7 0%, #20b2aa 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
.page-header h1 {
    font-size: 22px; font-weight: 700; margin: 0;
    background: linear-gradient(135deg, #c4b5fd 0%, #67e8f9 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.page-header p { font-size: 13px; color: rgba(255,255,255,0.4); margin: 2px 0 0; }

/* ── Hero corpus card ── */
.hero-card {
    background: linear-gradient(135deg, #1e1540 0%, #0f2a3d 60%, #0d1f2d 100%);
    border: 1px solid rgba(99,66,199,0.35);
    border-radius: 24px;
    padding: 2rem 2.25rem;
    position: relative; overflow: hidden;
    margin-bottom: 1.25rem;
}
.hero-card::before {
    content: '';
    position: absolute; top: -40%; right: -10%;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(99,66,199,0.25) 0%, transparent 65%);
    border-radius: 50%;
}
.hero-card::after {
    content: '';
    position: absolute; bottom: -30%; left: 20%;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(32,178,170,0.15) 0%, transparent 65%);
    border-radius: 50%;
}
.hero-label {
    font-size: 11px; font-weight: 600; letter-spacing: .1em;
    text-transform: uppercase; color: rgba(255,255,255,0.4);
    margin-bottom: 6px;
}
.hero-value {
    font-family: 'Sora', sans-serif;
    font-size: 44px; font-weight: 700; line-height: 1;
    background: linear-gradient(135deg, #fff 0%, #c4b5fd 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
}
.hero-sub { font-size: 13px; color: rgba(255,255,255,0.4); }
.hero-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(32,178,170,0.15); border: 1px solid rgba(32,178,170,0.3);
    border-radius: 20px; padding: 4px 12px;
    font-size: 12px; color: #67e8f9; font-weight: 500;
    margin-top: 12px;
}

/* ── KPI mini cards ── */
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 1.25rem; }
.kpi-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 1rem 1.1rem;
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.kpi-accent-purple::before { background: linear-gradient(90deg, #6342c7, #a78bfa); }
.kpi-accent-teal::before   { background: linear-gradient(90deg, #20b2aa, #67e8f9); }
.kpi-accent-rose::before   { background: linear-gradient(90deg, #e11d48, #fb7185); }
.kpi-accent-amber::before  { background: linear-gradient(90deg, #d97706, #fbbf24); }
.kpi-label { font-size: 11px; color: rgba(255,255,255,0.38); font-weight: 500; margin-bottom: 6px; }
.kpi-value { font-size: 19px; font-weight: 600; color: #f1f3f9; font-family: 'Sora', sans-serif; }
.kpi-sub   { font-size: 10px; color: rgba(255,255,255,0.28); margin-top: 3px; }

/* ── Streamlit inputs restyled ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
    font-size: 14px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(99,66,199,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,66,199,0.15) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label {
    font-size: 12px !important; color: rgba(255,255,255,0.45) !important;
    font-weight: 500 !important;
}
/* Number input arrows */
[data-testid="stNumberInput"] button {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.1) !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div { border-radius: 10px !important; }

/* ── Slider ── */
[data-testid="stSlider"] > div > div > div {
    background: rgba(99,66,199,0.3) !important;
}
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    background: #6342c7 !important; border-radius: 6px !important;
    font-size: 12px !important;
}
.stSlider label { font-size: 12px !important; color: rgba(255,255,255,0.45) !important; font-weight: 500 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6342c7 0%, #4f35a3 100%) !important;
    border: none !important; border-radius: 12px !important;
    color: white !important; font-weight: 600 !important;
    font-size: 14px !important; padding: 0.6rem 1.5rem !important;
    transition: all .2s !important;
    box-shadow: 0 4px 15px rgba(99,66,199,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,66,199,0.5) !important;
}
.stDownloadButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important; color: #e8eaf0 !important;
    font-size: 13px !important; font-weight: 500 !important;
    transition: all .2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
}

/* ── Risk pills (radio) ── */
[data-testid="stRadio"] > div {
    display: flex; flex-direction: row; gap: 8px; flex-wrap: wrap;
}
[data-testid="stRadio"] label {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px; padding: 6px 16px;
    font-size: 13px !important; color: #e8eaf0 !important;
    cursor: pointer; transition: all .15s;
}
[data-testid="stRadio"] label:has(input:checked) {
    background: rgba(99,66,199,0.25);
    border-color: rgba(99,66,199,0.6);
    color: #c4b5fd !important;
}
[data-testid="stRadio"] > label {
    font-size: 12px !important; color: rgba(255,255,255,0.45) !important; font-weight: 500 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 14px !important; padding: 5px !important;
    gap: 3px !important; border: 1px solid rgba(255,255,255,0.07) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important; font-size: 13px !important;
    font-weight: 500 !important; color: rgba(255,255,255,0.45) !important;
    padding: 7px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,66,199,0.3) !important;
    color: #c4b5fd !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem !important; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
}
[data-testid="stExpander"] summary {
    font-size: 13px !important; font-weight: 500 !important;
    color: rgba(255,255,255,0.55) !important;
}

/* ── DataFrame ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important; overflow: hidden;
}

/* ── File uploader — compact ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] section {
    padding: 0.35rem 0.6rem !important;
    min-height: unset !important;
}
[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
[data-testid="stFileUploader"] section small { display: none !important; }
[data-testid="stFileUploader"] section button {
    padding: 4px 12px !important; font-size: 12px !important;
    border-radius: 8px !important;
    background: rgba(99,66,199,0.2) !important;
    border: 1px solid rgba(99,66,199,0.4) !important;
    color: #c4b5fd !important;
}
[data-testid="stFileUploader"] label {
    font-size: 12px !important;
    color: rgba(255,255,255,0.45) !important; font-weight: 500 !important;
}

/* ── Success / info banners ── */
[data-testid="stSuccess"] { background: rgba(32,178,170,0.12) !important; border-radius: 10px !important; border-color: rgba(32,178,170,0.3) !important; }
[data-testid="stError"]   { background: rgba(225,29,72,0.12)  !important; border-radius: 10px !important; border-color: rgba(225,29,72,0.3)  !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }

/* ── Caption / helper text ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: rgba(255,255,255,0.3) !important; font-size: 11px !important;
}

/* ── Disclaimer ── */
.disclaimer {
    font-size: 11px; color: rgba(255,255,255,0.25);
    background: rgba(255,255,255,0.03);
    border-left: 2px solid rgba(99,66,199,0.4);
    padding: 10px 14px; border-radius: 0 10px 10px 0;
    line-height: 1.7; margin-top: 1rem;
}
.disclaimer a { color: rgba(103,232,249,0.7); }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def fmt_inr(v):
    if v >= 1e7:  return f"₹{v/1e7:.2f} Cr"
    if v >= 1e5:  return f"₹{v/1e5:.2f} L"
    return f"₹{v:,.0f}"

RISK_META = {
    "Very Aggressive": {"color": "#e11d48", "return": 15.0,  "desc": "100% equity / small-cap"},
    "Aggressive":      {"color": "#d97706", "return": 13.5,  "desc": "Large & mid-cap dominant"},
    "Balanced":        {"color": "#6342c7", "return": 12.0,  "desc": "60% equity / 40% debt"},
    "Conservative":    {"color": "#20b2aa", "return": 10.0,  "desc": "Debt-heavy, FD + liquid"},
}

def calculate_corpus(sip, stepup_pct, annual_rate_pct, years):
    r = (annual_rate_pct / 100) / 12
    corpus, invested = 0.0, 0.0
    yc, yi = [], []
    m_sip = sip
    for y in range(1, years + 1):
        for _ in range(12):
            corpus = (corpus + m_sip) * (1 + r)
            invested += m_sip
        yc.append(corpus); yi.append(invested)
        if y < years: m_sip *= (1 + stepup_pct / 100)
    return corpus, invested, yc, yi

# ─── PAGE HEADER + IMPORT/EXPORT ROW ─────────────────────────────────────────

hdr_left, hdr_right = st.columns([2, 1], gap="large")

with hdr_left:
    st.markdown("""
    <div class="page-header">
      <div class="logo-mark">✦</div>
      <div>
        <h1>WealthPath</h1>
        <p>Retirement corpus planner · India</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

with hdr_right:
    st.markdown('<p class="sec-label" style="margin-top:0.6rem">Plan file</p>', unsafe_allow_html=True)
    imp_col, exp_col = st.columns(2, gap="small")
    with imp_col:
        uploaded = st.file_uploader(
            "⬆ Import", type="json",
            label_visibility="visible",
            help="Upload a previously exported WealthPath .json plan"
        )

# export button rendered into exp_col after export_payload is built (below)
imported = {}
if uploaded:
    try:
        imported = json.load(uploaded)
        st.toast("Plan imported — fields updated ✓", icon="✅")
    except Exception:
        st.toast("Could not read file. Please upload a valid plan JSON.", icon="⚠️")

def iv(key, default):
    return imported.get("client", {}).get(key, default)
def rv(key, default):
    return imported.get("custom_returns", {}).get(key, default)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# INPUT SECTION
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="sec-label">Client details</p>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns([1.2, 1, 1])
with col_a:
    client_name = st.text_input("Client name", value=iv("name", "Arjun Sharma"))
with col_b:
    current_age = st.number_input("Current age", 18, 70, int(iv("age", 30)), 1)
with col_c:
    retire_age = st.number_input("Retirement age", 40, 80, int(iv("retirement_age", 60)), 1)

years_to_ret = int(retire_age - current_age)
if years_to_ret <= 0:
    st.error("Retirement age must be greater than current age.")
    st.stop()

st.markdown('<p class="sec-label" style="margin-top:1.25rem">Monthly financials (₹)</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    monthly_income = st.number_input("Monthly income", 10_000, 10_000_000, int(iv("monthly_income", 150_000)), 5_000, format="%d")
with col2:
    monthly_expenses = st.number_input("Monthly expenses", 5_000, 9_000_000, int(iv("monthly_expenses", 80_000)), 5_000, format="%d")
with col3:
    monthly_sip = st.number_input("Monthly SIP", 500, 5_000_000, int(iv("monthly_sip", 30_000)), 500, format="%d")

savings_rate = ((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income else 0
sip_pct = (monthly_sip / monthly_income * 100) if monthly_income else 0
st.caption(f"Savings rate: **{savings_rate:.1f}%**  ·  SIP as % of income: **{sip_pct:.1f}%**  ·  Investable surplus: **{fmt_inr(monthly_income - monthly_expenses)}** / mo")

st.markdown('<p class="sec-label" style="margin-top:1.25rem">Growth assumptions</p>', unsafe_allow_html=True)

col4, col5 = st.columns(2)
with col4:
    annual_stepup = st.slider("Annual SIP step-up (%)", 0.0, 25.0, float(iv("annual_stepup", 10.0)), 0.5)
with col5:
    inflation = st.slider("General inflation (%)", 2.0, 12.0, float(iv("inflation", 6.0)), 0.5)

st.markdown('<p class="sec-label" style="margin-top:1.25rem">Risk profile</p>', unsafe_allow_html=True)

risk_options = list(RISK_META.keys())
saved_risk = iv("risk_profile", "Balanced")
risk_idx = risk_options.index(saved_risk) if saved_risk in risk_options else 2
risk_profile = st.radio("Risk appetite", risk_options, index=risk_idx, horizontal=True, label_visibility="collapsed")
meta = RISK_META[risk_profile]
st.caption(f"{meta['desc']}  ·  Default assumed return: **{meta['return']}% p.a.**")

with st.expander("⚙  Edit assumed returns (%)"):
    rc1, rc2, rc3, rc4 = st.columns(4)
    ret_va = rc1.number_input("Very Aggressive", 5.0, 30.0, float(rv("very_aggressive", 15.0)),  0.5, format="%.1f")
    ret_a  = rc2.number_input("Aggressive",      5.0, 25.0, float(rv("aggressive",      13.5)),  0.5, format="%.1f")
    ret_b  = rc3.number_input("Balanced",        3.0, 20.0, float(rv("balanced",         12.0)), 0.5, format="%.1f")
    ret_c  = rc4.number_input("Conservative",    2.0, 15.0, float(rv("conservative",     10.0)), 0.5, format="%.1f")

custom_returns = {"Very Aggressive": ret_va, "Aggressive": ret_a, "Balanced": ret_b, "Conservative": ret_c}
annual_return = custom_returns[risk_profile]

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════════

corpus, total_invested, year_corpus, year_invested = calculate_corpus(
    monthly_sip, annual_stepup, annual_return, years_to_ret
)
total_returns = corpus - total_invested
real_value    = corpus / ((1 + inflation / 100) ** years_to_ret)
monthly_swp   = (corpus * 0.04) / 12
ages          = list(range(current_age + 1, retire_age + 1))
ages_str      = [str(a) for a in ages]
final_sip     = monthly_sip * ((1 + annual_stepup / 100) ** (years_to_ret - 1))

# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="sec-label">Projection results</p>', unsafe_allow_html=True)

# ── Hero + quick stats ──
hero_col, stats_col = st.columns([1.3, 1], gap="medium")

with hero_col:
    st.markdown(f"""
    <div class="hero-card">
      <div class="hero-label">Retirement corpus at age {retire_age}</div>
      <div class="hero-value">{fmt_inr(corpus)}</div>
      <div class="hero-sub">{client_name} · {years_to_ret}-year journey · {annual_return}% p.a.</div>
      <div class="hero-pill">
        <span>✦</span>
        <span>{corpus/total_invested:.1f}x wealth multiple · Real value {fmt_inr(real_value)}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with stats_col:
    st.markdown(f"""
    <div class="kpi-grid" style="grid-template-columns:1fr 1fr; gap:10px;">
      <div class="kpi-card kpi-accent-purple">
        <div class="kpi-label">Total invested</div>
        <div class="kpi-value">{fmt_inr(total_invested)}</div>
        <div class="kpi-sub">Principal over {years_to_ret} yrs</div>
      </div>
      <div class="kpi-card kpi-accent-teal">
        <div class="kpi-label">Wealth created</div>
        <div class="kpi-value">{fmt_inr(total_returns)}</div>
        <div class="kpi-sub">{total_returns/total_invested*100:.0f}% gain on principal</div>
      </div>
      <div class="kpi-card kpi-accent-rose">
        <div class="kpi-label">Monthly SWP (4%)</div>
        <div class="kpi-value">{fmt_inr(monthly_swp)}</div>
        <div class="kpi-sub">Est. monthly drawdown</div>
      </div>
      <div class="kpi-card kpi-accent-amber">
        <div class="kpi-label">Final monthly SIP</div>
        <div class="kpi-value">{fmt_inr(final_sip)}</div>
        <div class="kpi-sub">After {years_to_ret} step-ups</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["  📊  Growth chart  ", "  📋  Yearly breakdown  ", "  ⚖  Scenario comparison  "])

PLOT_BG    = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255,255,255,0.05)"
FONT_COLOR = "rgba(255,255,255,0.45)"
FONT_FMLY  = "Inter, sans-serif"

with tab1:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=ages_str, y=year_invested,
        name="Amount invested",
        fill="tozeroy",
        fillcolor="rgba(32,178,170,0.08)",
        line=dict(color="rgba(32,178,170,0.5)", width=1.5, dash="dot"),
        hovertemplate="Age %{x}<br>Invested: %{customdata}<extra></extra>",
        customdata=[fmt_inr(v) for v in year_invested],
    ))
    fig.add_trace(go.Scatter(
        x=ages_str, y=year_corpus,
        name="Corpus value",
        fill="tonexty",
        fillcolor="rgba(99,66,199,0.15)",
        line=dict(color="#a78bfa", width=2.5),
        hovertemplate="Age %{x}<br>Corpus: %{customdata}<extra></extra>",
        customdata=[fmt_inr(v) for v in year_corpus],
    ))

    # Milestone: first ₹1 Cr
    for i, v in enumerate(year_corpus):
        if v >= 1e7:
            fig.add_annotation(
                x=ages_str[i], y=v,
                text=f"₹1 Cr @ {ages[i]}",
                showarrow=True, arrowhead=2,
                arrowcolor="#f472b6", font=dict(size=11, color="#f472b6"),
                bgcolor="rgba(20,10,40,0.85)", bordercolor="#f472b6",
                borderwidth=1, borderpad=5, ax=35, ay=-45,
            )
            break

    # Milestone: ₹5 Cr
    for i, v in enumerate(year_corpus):
        if v >= 5e7:
            fig.add_annotation(
                x=ages_str[i], y=v,
                text=f"₹5 Cr @ {ages[i]}",
                showarrow=True, arrowhead=2,
                arrowcolor="#67e8f9", font=dict(size=11, color="#67e8f9"),
                bgcolor="rgba(20,10,40,0.85)", bordercolor="#67e8f9",
                borderwidth=1, borderpad=5, ax=-40, ay=-45,
            )
            break

    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=12, color=FONT_COLOR), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Age", showgrid=False, tickfont=dict(size=11, color=FONT_COLOR),
                   title_font=dict(color=FONT_COLOR), linecolor="rgba(255,255,255,0.08)"),
        yaxis=dict(title="Portfolio value", showgrid=True, gridcolor=GRID_COLOR,
                   tickformat=".2s", tickprefix="₹",
                   tickfont=dict(size=11, color=FONT_COLOR),
                   title_font=dict(color=FONT_COLOR)),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(family=FONT_FMLY),
        hoverlabel=dict(bgcolor="rgba(15,10,35,0.95)", bordercolor="rgba(99,66,199,0.5)",
                        font=dict(size=12, color="#e8eaf0", family=FONT_FMLY)),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="disclaimer">
    ⚠ Projections assume a constant annual return and do not account for market volatility, TER (fund expense ratio),
    or LTCG taxation. Actual returns on equity mutual funds will vary significantly year to year.
    For illustrative purposes only — consult a SEBI-registered investment advisor before investing.
    Verify current regulations at <a href="https://incometaxindia.gov.in" target="_blank">incometaxindia.gov.in</a>
    and <a href="https://sebi.gov.in" target="_blank">sebi.gov.in</a>.
    </div>
    """, unsafe_allow_html=True)


with tab2:
    sip_now = monthly_sip
    rows = []
    for i in range(years_to_ret):
        rows.append({
            "Year": i + 1,
            "Age": current_age + i + 1,
            "Monthly SIP": fmt_inr(sip_now),
            "Total invested": fmt_inr(year_invested[i]),
            "Corpus value": fmt_inr(year_corpus[i]),
            "Wealth multiple": f"{year_corpus[i]/year_invested[i]:.2f}x",
            "Real value (infl-adj.)": fmt_inr(year_corpus[i] / ((1 + inflation/100) ** (i+1))),
        })
        sip_now *= (1 + annual_stepup / 100)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True, height=420)
    st.download_button(
        "⬇  Download as CSV",
        data=df.to_csv(index=False),
        file_name=f"{client_name.replace(' ','_')}_yearly_breakdown.csv",
        mime="text/csv",
    )


with tab3:
    st.markdown('<p class="sec-label">All risk profiles — same SIP inputs</p>', unsafe_allow_html=True)

    fig2 = go.Figure()
    scenario_rows = []
    clr = {"Very Aggressive": "#fb7185", "Aggressive": "#fbbf24", "Balanced": "#a78bfa", "Conservative": "#34d399"}

    for profile, ret in custom_returns.items():
        c, ti, yc, _ = calculate_corpus(monthly_sip, annual_stepup, ret, years_to_ret)
        rv2  = c / ((1 + inflation/100) ** years_to_ret)
        swp2 = (c * 0.04) / 12
        scenario_rows.append({
            "Profile": profile, "Return (% p.a.)": f"{ret:.1f}%",
            "Corpus": fmt_inr(c), "Real value": fmt_inr(rv2),
            "Monthly SWP (4%)": fmt_inr(swp2), "Multiple": f"{c/ti:.1f}x",
        })
        fig2.add_trace(go.Scatter(
            x=ages_str, y=yc,
            name=f"{profile} · {ret}%",
            line=dict(color=clr[profile],
                      width=3 if profile == risk_profile else 1.5,
                      dash="solid" if profile == risk_profile else "dot"),
            hovertemplate=f"{profile} | Age %{{x}}: %{{customdata}}<extra></extra>",
            customdata=[fmt_inr(v) for v in yc],
        ))

    fig2.update_layout(
        height=360, margin=dict(l=0, r=0, t=10, b=0),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=11, color=FONT_COLOR), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Age", showgrid=False, tickfont=dict(size=11, color=FONT_COLOR),
                   title_font=dict(color=FONT_COLOR)),
        yaxis=dict(title="Portfolio value", showgrid=True, gridcolor=GRID_COLOR,
                   tickformat=".2s", tickprefix="₹",
                   tickfont=dict(size=11, color=FONT_COLOR), title_font=dict(color=FONT_COLOR)),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(family=FONT_FMLY),
        hoverlabel=dict(bgcolor="rgba(15,10,35,0.95)", bordercolor="rgba(99,66,199,0.5)",
                        font=dict(size=12, color="#e8eaf0", family=FONT_FMLY)),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(pd.DataFrame(scenario_rows), use_container_width=True, hide_index=True)

# ─── EXPORT ───────────────────────────────────────────────────────────────────

export_payload = {
    "version": "1.1",
    "exported_at": datetime.now().isoformat(),
    "client": {
        "name": client_name, "age": current_age,
        "retirement_age": retire_age,
        "monthly_income": monthly_income, "monthly_expenses": monthly_expenses,
        "monthly_sip": monthly_sip, "annual_stepup": annual_stepup,
        "inflation": inflation, "risk_profile": risk_profile,
    },
    "custom_returns": {
        "very_aggressive": ret_va, "aggressive": ret_a,
        "balanced": ret_b, "conservative": ret_c,
    },
    "summary": {
        "corpus": round(corpus, 2), "total_invested": round(total_invested, 2),
        "real_value": round(real_value, 2), "monthly_swp": round(monthly_swp, 2),
        "wealth_multiple": round(corpus / total_invested, 2),
    }
}

# ── Export button rendered into the header right sub-column ──
with exp_col:
    st.markdown('<p class="sec-label" style="margin-top:0">⬇ Export</p>', unsafe_allow_html=True)
    st.download_button(
        "Export plan",
        data=json.dumps(export_payload, indent=2),
        file_name=f"{client_name.replace(' ','_')}_retirement_plan.json",
        mime="application/json",
        use_container_width=True,
    )

st.divider()
st.markdown("""
<p style="font-size:11px;color:rgba(255,255,255,0.18);text-align:center">
WealthPath is a planning support tool for SEBI-registered advisors. Not investment advice. Returns not guaranteed.<br>
Verify regulations at incometaxindia.gov.in · sebi.gov.in · pfrda.org.in
</p>
""", unsafe_allow_html=True)
