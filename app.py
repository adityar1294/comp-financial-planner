import streamlit as st
import plotly.graph_objects as go
import json
import math
from datetime import datetime
from io import StringIO

st.set_page_config(
    page_title="Retirement Corpus Planner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f8f9fa;
    border-right: 1px solid #e9ecef;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
div[data-testid="metric-container"] label {
    font-size: 12px !important;
    color: #6c757d !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 600 !important;
    color: #212529 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 12px !important;
}

/* Section headers */
.section-header {
    font-size: 11px;
    font-weight: 600;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.75rem;
    margin-top: 1.25rem;
    padding-bottom: 6px;
    border-bottom: 1px solid #e9ecef;
}

/* Risk badge */
.risk-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.risk-va  { background: #fff5f5; color: #c0392b; border: 1px solid #f5c6cb; }
.risk-a   { background: #fff9f0; color: #e67e22; border: 1px solid #ffeeba; }
.risk-b   { background: #f0f8ff; color: #2980b9; border: 1px solid #bee5eb; }
.risk-c   { background: #f0fff4; color: #27ae60; border: 1px solid #c3e6cb; }

/* Summary card */
.summary-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    color: white;
    margin-bottom: 1.5rem;
}
.summary-card h2 { font-size: 14px; opacity: 0.7; margin-bottom: 4px; font-weight: 400; }
.summary-card h1 { font-size: 36px; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.summary-card p  { font-size: 12px; opacity: 0.6; margin-top: 4px; }

/* Disclaimer */
.disclaimer {
    font-size: 11px;
    color: #adb5bd;
    background: #f8f9fa;
    border-left: 3px solid #dee2e6;
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    line-height: 1.6;
    margin-top: 1rem;
}

/* Staggered columns gap fix */
div[data-testid="column"] {
    padding: 0 0.4rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #f8f9fa;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# ─── Helper functions ─────────────────────────────────────────────────────────

def fmt_inr(value: float) -> str:
    """Format a number as Indian currency with Cr/L suffix."""
    if value >= 1e7:
        return f"₹{value/1e7:.2f} Cr"
    elif value >= 1e5:
        return f"₹{value/1e5:.2f} L"
    else:
        return f"₹{value:,.0f}"


def fmt_inr_full(value: float) -> str:
    """Full Indian comma-formatted number."""
    if value >= 1e7:
        return f"₹{value/1e7:.2f} Cr  (₹{value:,.0f})"
    elif value >= 1e5:
        return f"₹{value/1e5:.2f} L  (₹{value:,.0f})"
    return f"₹{value:,.0f}"


RISK_META = {
    "Very Aggressive": {"key": "va", "color": "#c0392b", "default_return": 15.0,
                        "badge_class": "risk-va", "desc": "100% equity / small-cap heavy"},
    "Aggressive":      {"key": "a",  "color": "#e67e22", "default_return": 13.5,
                        "badge_class": "risk-a",  "desc": "Large & mid-cap equity dominant"},
    "Balanced":        {"key": "b",  "color": "#2980b9", "default_return": 12.0,
                        "badge_class": "risk-b",  "desc": "60% equity / 40% debt blend"},
    "Conservative":    {"key": "c",  "color": "#27ae60", "default_return": 10.0,
                        "badge_class": "risk-c",  "desc": "Debt-heavy, FD + liquid funds"},
}


def calculate_corpus(sip, stepup_pct, annual_rate_pct, years):
    """
    Year-by-year SIP corpus with annual step-up.
    Returns (corpus, total_invested, year_corpus_list, year_invested_list)
    """
    monthly_rate = (annual_rate_pct / 100) / 12
    corpus = 0.0
    total_invested = 0.0
    year_corpus = []
    year_invested = []
    monthly_sip = sip

    for y in range(1, years + 1):
        for _ in range(12):
            corpus = (corpus + monthly_sip) * (1 + monthly_rate)
            total_invested += monthly_sip
        year_corpus.append(corpus)
        year_invested.append(total_invested)
        if y < years:
            monthly_sip *= (1 + stepup_pct / 100)

    return corpus, total_invested, year_corpus, year_invested


# ─── Sidebar: Inputs ──────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📋 Client details")

    # Import
    uploaded = st.file_uploader("Import saved plan (.json)", type="json", label_visibility="collapsed")
    imported = {}
    if uploaded:
        try:
            imported = json.load(uploaded)
            st.success("Plan imported successfully!")
        except Exception:
            st.error("Invalid file. Please upload a valid plan JSON.")

    def iv(key, default):
        """Get value from imported dict or fall back to default."""
        return imported.get("client", {}).get(key, default)

    def rv(key, default):
        return imported.get("custom_returns", {}).get(key, default)

    st.markdown('<div class="section-header">Personal</div>', unsafe_allow_html=True)
    client_name   = st.text_input("Client name", value=iv("name", "Arjun Sharma"))
    col1, col2   = st.columns(2)
    current_age  = col1.number_input("Current age", 18, 70, int(iv("age", 30)), 1)
    retire_age   = col2.number_input("Retirement age", 40, 80, int(iv("retirement_age", 60)), 1)
    years_to_ret = int(retire_age - current_age)

    if years_to_ret <= 0:
        st.error("Retirement age must be greater than current age.")
        st.stop()

    st.markdown('<div class="section-header">Financials (₹ / month)</div>', unsafe_allow_html=True)
    monthly_income   = st.number_input("Monthly income",   10_000, 10_000_000, int(iv("monthly_income", 150_000)),   5_000, format="%d")
    monthly_expenses = st.number_input("Monthly expenses", 5_000,  9_000_000,  int(iv("monthly_expenses", 80_000)),  5_000, format="%d")
    monthly_sip      = st.number_input("Monthly SIP",      500,    5_000_000,  int(iv("monthly_sip", 30_000)),       500,   format="%d")

    savings_rate = ((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income else 0
    sip_pct      = (monthly_sip / monthly_income * 100) if monthly_income else 0
    st.caption(f"Savings rate: **{savings_rate:.1f}%** · SIP as % of income: **{sip_pct:.1f}%**")

    st.markdown('<div class="section-header">Growth assumptions</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    annual_stepup = col3.number_input("SIP step-up (% / yr)", 0.0, 30.0, float(iv("annual_stepup", 10.0)), 0.5, format="%.1f")
    inflation     = col4.number_input("Inflation (% / yr)",   2.0, 15.0, float(iv("inflation", 6.0)),       0.5, format="%.1f")

    st.markdown('<div class="section-header">Risk profile</div>', unsafe_allow_html=True)
    risk_options  = list(RISK_META.keys())
    saved_risk    = iv("risk_profile", "Balanced")
    risk_idx      = risk_options.index(saved_risk) if saved_risk in risk_options else 2
    risk_profile  = st.selectbox("Risk appetite", risk_options, index=risk_idx)
    meta          = RISK_META[risk_profile]
    st.markdown(f'<span class="risk-badge {meta["badge_class"]}">{risk_profile}</span> <span style="font-size:11px;color:#6c757d">{meta["desc"]}</span>', unsafe_allow_html=True)

    with st.expander("⚙️ Edit assumed returns (%)"):
        ret_va = st.number_input("Very Aggressive", 5.0, 30.0, float(rv("very_aggressive", 15.0)),  0.5, format="%.1f")
        ret_a  = st.number_input("Aggressive",      5.0, 25.0, float(rv("aggressive",      13.5)),  0.5, format="%.1f")
        ret_b  = st.number_input("Balanced",        3.0, 20.0, float(rv("balanced",         12.0)), 0.5, format="%.1f")
        ret_c  = st.number_input("Conservative",    2.0, 15.0, float(rv("conservative",     10.0)), 0.5, format="%.1f")

    custom_returns = {"Very Aggressive": ret_va, "Aggressive": ret_a, "Balanced": ret_b, "Conservative": ret_c}
    annual_return  = custom_returns[risk_profile]

    st.divider()

    # Export
    export_payload = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "client": {
            "name": client_name,
            "age": current_age,
            "retirement_age": retire_age,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "monthly_sip": monthly_sip,
            "annual_stepup": annual_stepup,
            "inflation": inflation,
            "risk_profile": risk_profile,
        },
        "custom_returns": {
            "very_aggressive": ret_va,
            "aggressive": ret_a,
            "balanced": ret_b,
            "conservative": ret_c,
        }
    }
    st.download_button(
        label="⬇️  Export plan (.json)",
        data=json.dumps(export_payload, indent=2),
        file_name=f"{client_name.replace(' ', '_')}_retirement_plan.json",
        mime="application/json",
        use_container_width=True,
    )


# ─── Main calculations ────────────────────────────────────────────────────────

corpus, total_invested, year_corpus, year_invested = calculate_corpus(
    monthly_sip, annual_stepup, annual_return, years_to_ret
)

total_returns    = corpus - total_invested
real_value       = corpus / ((1 + inflation / 100) ** years_to_ret)
monthly_swp_4pct = (corpus * 0.04) / 12
ages             = list(range(current_age + 1, retire_age + 1))
years_labels     = [str(a) for a in ages]

# ─── Page header ─────────────────────────────────────────────────────────────

st.markdown(f"## 📈 {client_name}'s Retirement Corpus Planner")
st.caption(f"Age {current_age} → {retire_age}  ·  {years_to_ret} years  ·  {risk_profile} profile  ·  {annual_return}% p.a. assumed")
st.divider()

# ─── Summary hero card ────────────────────────────────────────────────────────

col_hero1, col_hero2 = st.columns([1.4, 1])

with col_hero1:
    st.markdown(f"""
    <div class="summary-card">
        <h2>Projected retirement corpus at age {retire_age}</h2>
        <h1>{fmt_inr(corpus)}</h1>
        <p>Real value (today's ₹): {fmt_inr(real_value)} · Wealth multiple: {corpus/total_invested:.1f}x</p>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    st.metric("Monthly SWP (4% rule)", fmt_inr(monthly_swp_4pct), "Estimated monthly drawdown")
    st.metric("SIP at retirement", fmt_inr(monthly_sip * ((1 + annual_stepup/100) ** (years_to_ret - 1))), f"After {years_to_ret} step-ups")

# ─── KPI metrics ─────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">Key metrics</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total invested",    fmt_inr(total_invested),  "Principal")
c2.metric("Total returns",     fmt_inr(total_returns),   f"{total_returns/total_invested*100:.0f}% gain")
c3.metric("Corpus",            fmt_inr(corpus),          f"at age {retire_age}")
c4.metric("Real value",        fmt_inr(real_value),      f"at {inflation}% inflation")
c5.metric("Wealth multiple",   f"{corpus/total_invested:.1f}x", "return on investment")

st.divider()

# ─── Tabs: Chart | Yearly table | Scenario comparison ─────────────────────────

tab1, tab2, tab3 = st.tabs(["📊 Growth chart", "📋 Yearly breakdown", "⚖️ Scenario comparison"])

with tab1:
    fig = go.Figure()

    # Invested area
    fig.add_trace(go.Scatter(
        x=years_labels, y=year_invested,
        name="Amount invested",
        fill="tozeroy",
        fillcolor="rgba(39,174,96,0.10)",
        line=dict(color="#27ae60", width=1.5, dash="dot"),
        hovertemplate="Age %{x}<br>Invested: ₹%{customdata}<extra></extra>",
        customdata=[f"{v/1e7:.2f} Cr" if v >= 1e7 else f"{v/1e5:.2f} L" for v in year_invested],
    ))

    # Corpus area
    fig.add_trace(go.Scatter(
        x=years_labels, y=year_corpus,
        name="Corpus value",
        fill="tonexty",
        fillcolor="rgba(41,128,185,0.12)",
        line=dict(color="#2980b9", width=2.5),
        hovertemplate="Age %{x}<br>Corpus: ₹%{customdata}<extra></extra>",
        customdata=[f"{v/1e7:.2f} Cr" if v >= 1e7 else f"{v/1e5:.2f} L" for v in year_corpus],
    ))

    # Milestone: first ₹1 Cr
    for i, v in enumerate(year_corpus):
        if v >= 1e7:
            fig.add_annotation(
                x=years_labels[i], y=v,
                text=f"₹1 Cr @ age {ages[i]}",
                showarrow=True, arrowhead=2, arrowcolor="#e74c3c",
                font=dict(size=11, color="#e74c3c"),
                bgcolor="white", bordercolor="#e74c3c", borderwidth=1,
                borderpad=4, ax=30, ay=-40,
            )
            break

    fig.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font=dict(size=12)),
        xaxis=dict(title="Age", showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(
            title="Portfolio value (₹)",
            showgrid=True,
            gridcolor="#f0f0f0",
            tickformat=".2s",
            tickprefix="₹",
            tickfont=dict(size=11),
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="disclaimer">
    ⚠️ <strong>Disclaimer:</strong> Projections assume a constant annual return rate and do not account for market volatility, 
    fund expenses (TER), or taxation on LTCG. Actual returns on equity mutual funds will vary. 
    This tool is for illustrative purposes only — consult a SEBI-registered investment advisor before making investment decisions.
    Verify current tax slabs and regulations at <a href="https://incometaxindia.gov.in" target="_blank">incometaxindia.gov.in</a>.
    </div>
    """, unsafe_allow_html=True)


with tab2:
    st.markdown('<div class="section-header">Year-by-year projection</div>', unsafe_allow_html=True)

    import pandas as pd
    monthly_sip_progression = []
    sip_now = monthly_sip
    for y in range(years_to_ret):
        monthly_sip_progression.append(sip_now)
        sip_now *= (1 + annual_stepup / 100)

    table_data = []
    for i in range(years_to_ret):
        yr = i + 1
        table_data.append({
            "Year": yr,
            "Age": current_age + yr,
            "Monthly SIP (₹)": f"₹{monthly_sip_progression[i]:,.0f}",
            "Total invested": fmt_inr(year_invested[i]),
            "Corpus value": fmt_inr(year_corpus[i]),
            "Wealth multiple": f"{year_corpus[i]/year_invested[i]:.2f}x",
            "Real value (inflation-adj.)": fmt_inr(year_corpus[i] / ((1 + inflation/100) ** (i+1))),
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True, height=420)

    csv = df.to_csv(index=False)
    st.download_button(
        "⬇️  Download table as CSV",
        data=csv,
        file_name=f"{client_name.replace(' ','_')}_yearly_breakdown.csv",
        mime="text/csv",
    )


with tab3:
    st.markdown('<div class="section-header">All risk profiles side by side</div>', unsafe_allow_html=True)
    st.caption("Comparing your SIP inputs across all four risk profiles. Edit returns in the sidebar.")

    fig2 = go.Figure()
    colors_map = {"Very Aggressive": "#c0392b", "Aggressive": "#e67e22",
                  "Balanced": "#2980b9", "Conservative": "#27ae60"}

    scenario_rows = []
    for profile, ret in custom_returns.items():
        c, ti, yc, _ = calculate_corpus(monthly_sip, annual_stepup, ret, years_to_ret)
        rv2 = c / ((1 + inflation/100) ** years_to_ret)
        swp2 = (c * 0.04) / 12
        scenario_rows.append({
            "Profile": profile,
            "Return (% p.a.)": f"{ret:.1f}%",
            "Corpus at retirement": fmt_inr(c),
            "Real value": fmt_inr(rv2),
            "Monthly SWP (4%)": fmt_inr(swp2),
            "Wealth multiple": f"{c/ti:.1f}x",
        })
        fig2.add_trace(go.Scatter(
            x=years_labels, y=yc,
            name=f"{profile} ({ret}%)",
            line=dict(color=colors_map[profile], width=2 if profile == risk_profile else 1.2,
                      dash="solid" if profile == risk_profile else "dot"),
            hovertemplate=f"{profile} | Age %{{x}}: ₹%{{customdata}}<extra></extra>",
            customdata=[f"{v/1e7:.2f} Cr" if v >= 1e7 else f"{v/1e5:.2f} L" for v in yc],
        ))

    fig2.update_layout(
        height=360,
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=11)),
        xaxis=dict(title="Age", showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(title="Portfolio value (₹)", showgrid=True, gridcolor="#f0f0f0",
                   tickformat=".2s", tickprefix="₹", tickfont=dict(size=11)),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    import pandas as pd
    st.dataframe(pd.DataFrame(scenario_rows), use_container_width=True, hide_index=True)
