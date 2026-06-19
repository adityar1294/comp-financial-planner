import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime

st.set_page_config(
    page_title="WealthPath · Retirement Planner",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS  —  only layout + custom HTML elements; let config.toml handle widgets
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* hide default chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebar"] { display: none !important; }

.block-container {
    padding: 2rem 3rem 5rem !important;
    max-width: 1300px !important;
}

/* ── ambient background blobs ── */
.stApp {
    background: radial-gradient(ellipse 80% 60% at 10% 0%,  rgba(124,92,252,0.12) 0%, transparent 60%),
                radial-gradient(ellipse 60% 50% at 90% 100%, rgba(56,189,248,0.08) 0%, transparent 55%),
                #0E1117 !important;
}

/* ── page header ── */
.wp-header {
    display: flex; align-items: center; gap: 14px; margin-bottom: 0.25rem;
}
.wp-logo {
    width: 46px; height: 46px; border-radius: 14px; flex-shrink: 0;
    background: linear-gradient(135deg, #7C5CFC 0%, #38BDF8 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 24px rgba(124,92,252,0.45);
}
.wp-title {
    font-size: 26px; font-weight: 800; margin: 0; line-height: 1.1;
    background: linear-gradient(120deg, #C4B5FD 0%, #7C5CFC 40%, #38BDF8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.wp-sub { font-size: 13px; color: rgba(250,250,250,0.4); margin: 2px 0 0; }

/* ── section chips ── */
.chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(124,92,252,0.12); border: 1px solid rgba(124,92,252,0.3);
    border-radius: 20px; padding: 4px 12px;
    font-size: 11px; font-weight: 600; letter-spacing: .06em;
    text-transform: uppercase; color: #A78BFA;
    margin-bottom: 0.85rem; margin-top: 1.5rem;
}

/* ── hero result card ── */
.hero {
    background: linear-gradient(135deg, #1C1438 0%, #0F2340 70%, #0E1117 100%);
    border: 1px solid rgba(124,92,252,0.3);
    border-radius: 24px; padding: 2rem 2.25rem;
    position: relative; overflow: hidden; margin-bottom: 1rem;
}
.hero::before {
    content: ''; position: absolute;
    top: -60%; right: -5%; width: 380px; height: 380px;
    background: radial-gradient(circle, rgba(124,92,252,0.22) 0%, transparent 65%);
    border-radius: 50%;
}
.hero::after {
    content: ''; position: absolute;
    bottom: -40%; left: 15%; width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 65%);
    border-radius: 50%;
}
.hero-eyebrow {
    font-size: 11px; font-weight: 600; letter-spacing: .1em;
    text-transform: uppercase; color: rgba(250,250,250,0.38); margin-bottom: 8px;
}
.hero-amount {
    font-size: 52px; font-weight: 800; line-height: 1; margin-bottom: 6px;
    background: linear-gradient(135deg, #fff 0%, #C4B5FD 60%, #38BDF8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-meta { font-size: 13px; color: rgba(250,250,250,0.38); }
.hero-badges { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; }
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    border-radius: 20px; padding: 5px 13px;
    font-size: 12px; font-weight: 600;
}
.badge-teal  { background: rgba(56,189,248,0.12); border: 1px solid rgba(56,189,248,0.28); color: #7DD3FC; }
.badge-green { background: rgba(52,211,153,0.10); border: 1px solid rgba(52,211,153,0.25); color: #6EE7B7; }
.badge-rose  { background: rgba(251,113,133,0.10); border: 1px solid rgba(251,113,133,0.25); color: #FDA4AF; }

/* ── KPI cards ── */
.kpi-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 1.5rem; }
.kpi {
    background: #1A1F2E;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px; padding: 1.1rem 1.2rem;
    position: relative; overflow: hidden;
    transition: border-color .2s;
}
.kpi::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    border-radius: 18px 18px 0 0;
}
.kpi-p::after { background: linear-gradient(90deg,#7C5CFC,#A78BFA); }
.kpi-t::after { background: linear-gradient(90deg,#0EA5E9,#38BDF8); }
.kpi-g::after { background: linear-gradient(90deg,#059669,#34D399); }
.kpi-o::after { background: linear-gradient(90deg,#D97706,#FCD34D); }
.kpi-l  { font-size: 11px; color: rgba(250,250,250,0.38); font-weight: 500; margin-bottom: 7px; }
.kpi-v  { font-size: 20px; font-weight: 700; color: #FAFAFA; }
.kpi-s  { font-size: 10px; color: rgba(250,250,250,0.25); margin-top: 3px; }

/* ── input section card ── */
.input-card {
    background: #1A1F2E;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
}

/* ── risk pills — rendered via st.radio but we style the container ── */
.risk-desc {
    font-size: 12px; color: rgba(250,250,250,0.4);
    margin-top: 4px; margin-bottom: 0;
}

/* ── disclaimer ── */
.disc {
    font-size: 11px; line-height: 1.7;
    color: rgba(250,250,250,0.25);
    background: rgba(124,92,252,0.06);
    border-left: 2px solid rgba(124,92,252,0.35);
    border-radius: 0 10px 10px 0;
    padding: 10px 14px; margin-top: 1rem;
}
.disc a { color: rgba(56,189,248,0.6); }

/* ── footer ── */
.wp-footer {
    text-align: center; font-size: 11px;
    color: rgba(250,250,250,0.15); margin-top: 3rem;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt(v):
    if v >= 1e7:  return f"₹{v/1e7:.2f} Cr"
    if v >= 1e5:  return f"₹{v/1e5:.2f} L"
    return f"₹{v:,.0f}"

RISK = {
    "🔴  Very Aggressive": {"ret": 15.0, "desc": "100% equity · small & mid-cap heavy · high volatility"},
    "🟠  Aggressive":       {"ret": 13.5, "desc": "Large & mid-cap dominant · moderate-high volatility"},
    "🔵  Balanced":         {"ret": 12.0, "desc": "60% equity / 40% debt · moderate volatility"},
    "🟢  Conservative":     {"ret": 10.0, "desc": "Debt-heavy · FD + liquid funds · low volatility"},
}

PLOT_THEME = dict(
    plot_bgcolor  = "rgba(0,0,0,0)",
    paper_bgcolor = "rgba(0,0,0,0)",
    font          = dict(family="Plus Jakarta Sans, sans-serif", color="rgba(250,250,250,0.5)"),
    margin        = dict(l=0, r=0, t=20, b=0),
    hovermode     = "x unified",
    hoverlabel    = dict(
        bgcolor     = "rgba(20,14,50,0.95)",
        bordercolor = "rgba(124,92,252,0.5)",
        font        = dict(size=13, color="#FAFAFA", family="Plus Jakarta Sans, sans-serif"),
    ),
)

def corpus_calc(sip, stepup, rate_pct, years):
    r = (rate_pct / 100) / 12
    c, inv = 0.0, 0.0
    yc, yi = [], []
    for y in range(1, years + 1):
        for _ in range(12):
            c = (c + sip) * (1 + r)
            inv += sip
        yc.append(c); yi.append(inv)
        if y < years: sip *= (1 + stepup / 100)
    return c, inv, yc, yi


# ─────────────────────────────────────────────────────────────────────────────
# STATE  —  import pre-fills session state
# ─────────────────────────────────────────────────────────────────────────────
if "imported" not in st.session_state:
    st.session_state.imported = {}

imp = st.session_state.imported
C   = imp.get("client", {})
R   = imp.get("custom_returns", {})

def ci(k, d): return C.get(k, d)
def ri(k, d): return R.get(k, d)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
left_h, right_h = st.columns([3, 1], gap="large")

with left_h:
    st.markdown("""
    <div class="wp-header">
      <div class="wp-logo">💜</div>
      <div>
        <div class="wp-title">WealthPath</div>
        <div class="wp-sub">Retirement corpus planner · India · For SEBI-registered advisors</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with right_h:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    imp_file = st.file_uploader("📂 Import plan", type="json", label_visibility="visible")
    if imp_file:
        try:
            st.session_state.imported = json.load(imp_file)
            st.toast("✅ Plan imported successfully!", icon="✅")
            st.rerun()
        except Exception:
            st.toast("⚠️ Could not read file.", icon="⚠️")

st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# INPUTS  —  two-column layout, inputs on left, results on right (live)
# ─────────────────────────────────────────────────────────────────────────────
in_col, out_col = st.columns([1, 1.55], gap="large")

with in_col:

    # ── Personal ──────────────────────────────────────────────────────────────
    st.markdown('<div class="chip">👤 Client details</div>', unsafe_allow_html=True)

    client_name = st.text_input("Client name", value=ci("name", "Arjun Sharma"))

    a1, a2 = st.columns(2)
    current_age = a1.number_input("Current age", 18, 70,  int(ci("age", 30)), 1)
    retire_age  = a2.number_input("Retirement age", 40, 80, int(ci("retirement_age", 60)), 1)
    years = int(retire_age - current_age)

    if years <= 0:
        st.error("Retirement age must be greater than current age.")
        st.stop()

    st.caption(f"**{years} years** to build your corpus")

    # ── Financials ────────────────────────────────────────────────────────────
    st.markdown('<div class="chip">💰 Monthly financials</div>', unsafe_allow_html=True)

    monthly_income   = st.number_input("Monthly income (₹)",   10_000, 10_000_000, int(ci("monthly_income",   150_000)), 5_000, format="%d")
    monthly_expenses = st.number_input("Monthly expenses (₹)", 5_000,   9_000_000, int(ci("monthly_expenses",  80_000)), 5_000, format="%d")
    monthly_sip      = st.number_input("Monthly SIP (₹)",         500,   5_000_000, int(ci("monthly_sip",       30_000)),   500, format="%d")

    surplus  = monthly_income - monthly_expenses
    sav_rate = (surplus / monthly_income * 100) if monthly_income else 0
    sip_pct  = (monthly_sip / monthly_income * 100) if monthly_income else 0

    st.markdown(f"""
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 4px">
      <span style="background:rgba(124,92,252,0.12);border:1px solid rgba(124,92,252,0.25);
                   border-radius:20px;padding:3px 10px;font-size:11px;color:#A78BFA;font-weight:600">
        Savings {sav_rate:.0f}%
      </span>
      <span style="background:rgba(56,189,248,0.10);border:1px solid rgba(56,189,248,0.22);
                   border-radius:20px;padding:3px 10px;font-size:11px;color:#7DD3FC;font-weight:600">
        SIP {sip_pct:.0f}% of income
      </span>
      <span style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.20);
                   border-radius:20px;padding:3px 10px;font-size:11px;color:#6EE7B7;font-weight:600">
        Surplus {fmt(surplus)}/mo
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Growth assumptions ────────────────────────────────────────────────────
    st.markdown('<div class="chip">📈 Growth assumptions</div>', unsafe_allow_html=True)

    annual_stepup = st.slider("SIP step-up per year (%)", 0.0, 25.0, float(ci("annual_stepup", 10.0)), 0.5,
                               format="%.1f%%")
    inflation     = st.slider("Expected inflation (%)",   2.0, 12.0, float(ci("inflation",      6.0)), 0.5,
                               format="%.1f%%")

    # ── Risk profile ──────────────────────────────────────────────────────────
    st.markdown('<div class="chip">⚡ Risk profile</div>', unsafe_allow_html=True)

    risk_keys    = list(RISK.keys())
    saved_risk   = ci("risk_profile", "🔵  Balanced")
    risk_idx     = risk_keys.index(saved_risk) if saved_risk in risk_keys else 2
    risk_profile = st.radio("Risk appetite", risk_keys, index=risk_idx, label_visibility="collapsed")
    st.caption(RISK[risk_profile]["desc"])

    with st.expander("⚙️  Customise assumed returns"):
        rc = st.columns(2)
        ret_va = rc[0].number_input("Very Aggressive %", 5.0, 30.0, float(ri("very_aggressive", 15.0)),  0.5, format="%.1f")
        ret_a  = rc[1].number_input("Aggressive %",      5.0, 25.0, float(ri("aggressive",      13.5)),  0.5, format="%.1f")
        rc2 = st.columns(2)
        ret_b  = rc2[0].number_input("Balanced %",       3.0, 20.0, float(ri("balanced",         12.0)), 0.5, format="%.1f")
        ret_c  = rc2[1].number_input("Conservative %",   2.0, 15.0, float(ri("conservative",     10.0)), 0.5, format="%.1f")

    custom_ret = {
        "🔴  Very Aggressive": ret_va,
        "🟠  Aggressive":      ret_a,
        "🔵  Balanced":        ret_b,
        "🟢  Conservative":    ret_c,
    }
    annual_return = custom_ret[risk_profile]


# ─────────────────────────────────────────────────────────────────────────────
# CALCULATIONS  (run before rendering right column)
# ─────────────────────────────────────────────────────────────────────────────
corpus, total_inv, yc_list, yi_list = corpus_calc(monthly_sip, annual_stepup, annual_return, years)

total_ret  = corpus - total_inv
real_val   = corpus / ((1 + inflation / 100) ** years)
monthly_swp = (corpus * 0.04) / 12
final_sip  = monthly_sip * ((1 + annual_stepup / 100) ** (years - 1))
ages_str   = [str(current_age + i + 1) for i in range(years)]
multiple   = corpus / total_inv


# ─────────────────────────────────────────────────────────────────────────────
# RIGHT COLUMN  —  results
# ─────────────────────────────────────────────────────────────────────────────
with out_col:

    # ── Hero card ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero">
      <div class="hero-eyebrow">Projected retirement corpus · Age {retire_age}</div>
      <div class="hero-amount">{fmt(corpus)}</div>
      <div class="hero-meta">{client_name} · {years}-year journey · {annual_return:.1f}% p.a. assumed return</div>
      <div class="hero-badges">
        <span class="badge badge-teal">💧 Real value {fmt(real_val)}</span>
        <span class="badge badge-green">✦ {multiple:.1f}× wealth multiple</span>
        <span class="badge badge-rose">📅 SWP {fmt(monthly_swp)}/mo</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI strip ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi kpi-p">
        <div class="kpi-l">Total invested</div>
        <div class="kpi-v">{fmt(total_inv)}</div>
        <div class="kpi-s">Principal over {years} yrs</div>
      </div>
      <div class="kpi kpi-t">
        <div class="kpi-l">Wealth created</div>
        <div class="kpi-v">{fmt(total_ret)}</div>
        <div class="kpi-s">{total_ret/total_inv*100:.0f}% gain on principal</div>
      </div>
      <div class="kpi kpi-g">
        <div class="kpi-l">Monthly SWP (4%)</div>
        <div class="kpi-v">{fmt(monthly_swp)}</div>
        <div class="kpi-s">Est. retirement income</div>
      </div>
      <div class="kpi kpi-o">
        <div class="kpi-l">Final monthly SIP</div>
        <div class="kpi-v">{fmt(final_sip)}</div>
        <div class="kpi-s">After {years} annual step-ups</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📊  Growth chart", "📋  Year-by-year", "⚖️  Scenarios"])

    gc = dict(color="rgba(250,250,250,0.07)")
    tc = dict(size=11, color="rgba(250,250,250,0.4)")

    with tab1:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=ages_str, y=yi_list, name="Amount invested",
            fill="tozeroy",
            fillcolor="rgba(56,189,248,0.07)",
            line=dict(color="rgba(56,189,248,0.4)", width=1.5, dash="dot"),
            customdata=[fmt(v) for v in yi_list],
            hovertemplate="Age %{x}<br>Invested: %{customdata}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=ages_str, y=yc_list, name="Corpus value",
            fill="tonexty",
            fillcolor="rgba(124,92,252,0.15)",
            line=dict(color="#A78BFA", width=2.5),
            customdata=[fmt(v) for v in yc_list],
            hovertemplate="Age %{x}<br>Corpus: %{customdata}<extra></extra>",
        ))

        # milestone annotations
        milestones = [(1e7,"₹1 Cr","#F472B6",30,-40), (5e7,"₹5 Cr","#34D399",-40,-40), (1e8,"₹10 Cr","#FBBF24",30,-50)]
        for thresh, label, col, ax, ay in milestones:
            for i, v in enumerate(yc_list):
                if v >= thresh:
                    fig.add_annotation(
                        x=ages_str[i], y=v, text=f"{label} @ {ages_str[i]}",
                        showarrow=True, arrowhead=2, arrowcolor=col,
                        font=dict(size=10, color=col),
                        bgcolor="rgba(14,17,23,0.9)", bordercolor=col,
                        borderwidth=1, borderpad=4, ax=ax, ay=ay,
                    )
                    break

        fig.update_layout(
            **PLOT_THEME, height=380,
            legend=dict(orientation="h", y=1.04, x=0,
                        font=dict(size=12, color="rgba(250,250,250,0.5)"),
                        bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(title="Age", showgrid=False, tickfont=tc,
                       title_font=dict(color="rgba(250,250,250,0.4)"),
                       linecolor="rgba(255,255,255,0.06)"),
            yaxis=dict(title="Portfolio value", showgrid=True, gridcolor=gc["color"],
                       tickformat=".2s", tickprefix="₹", tickfont=tc,
                       title_font=dict(color="rgba(250,250,250,0.4)")),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""<div class="disc">
        ⚠ Assumes constant annual return. Does not account for market volatility, TER, or LTCG taxation.
        Actual equity fund returns vary significantly. For illustration only —
        consult a <strong>SEBI-registered investment advisor</strong> before investing.
        Verify regulations at <a href="https://incometaxindia.gov.in" target="_blank">incometaxindia.gov.in</a>
        &amp; <a href="https://sebi.gov.in" target="_blank">sebi.gov.in</a>
        </div>""", unsafe_allow_html=True)

    with tab2:
        sip_now = monthly_sip
        rows = []
        for i in range(years):
            rows.append({
                "Yr": i + 1,
                "Age": current_age + i + 1,
                "Monthly SIP": fmt(sip_now),
                "Total invested": fmt(yi_list[i]),
                "Corpus": fmt(yc_list[i]),
                "Multiple": f"{yc_list[i]/yi_list[i]:.2f}×",
                "Real value": fmt(yc_list[i] / ((1 + inflation/100) ** (i+1))),
            })
            sip_now *= (1 + annual_stepup / 100)

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True, height=380)
        st.download_button("⬇️  Download CSV", df.to_csv(index=False),
                           f"{client_name.replace(' ','_')}_breakdown.csv", "text/csv")

    with tab3:
        fig2 = go.Figure()
        scen = []
        pal  = {
            "🔴  Very Aggressive": "#FB7185",
            "🟠  Aggressive":       "#FBBF24",
            "🔵  Balanced":         "#A78BFA",
            "🟢  Conservative":     "#34D399",
        }
        for profile, ret in custom_ret.items():
            c2, ti2, yc2, _ = corpus_calc(monthly_sip, annual_stepup, ret, years)
            scen.append({
                "Profile": profile.split("  ")[1],
                "Return": f"{ret:.1f}%",
                "Corpus": fmt(c2),
                "Real value": fmt(c2 / ((1 + inflation/100) ** years)),
                "SWP /mo": fmt((c2 * 0.04) / 12),
                "Multiple": f"{c2/ti2:.1f}×",
            })
            fig2.add_trace(go.Scatter(
                x=ages_str, y=yc2, name=f"{profile.split('  ')[1]} · {ret}%",
                line=dict(
                    color=pal[profile],
                    width=3 if profile == risk_profile else 1.5,
                    dash="solid" if profile == risk_profile else "dot",
                ),
                customdata=[fmt(v) for v in yc2],
                hovertemplate=f"{profile.split('  ')[1]} | Age %{{x}}: %{{customdata}}<extra></extra>",
            ))

        fig2.update_layout(
            **PLOT_THEME, height=320,
            legend=dict(orientation="h", y=1.05, x=0,
                        font=dict(size=11, color="rgba(250,250,250,0.5)"),
                        bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(title="Age", showgrid=False, tickfont=tc,
                       title_font=dict(color="rgba(250,250,250,0.4)")),
            yaxis=dict(title="Portfolio value", showgrid=True, gridcolor=gc["color"],
                       tickformat=".2s", tickprefix="₹", tickfont=tc,
                       title_font=dict(color="rgba(250,250,250,0.4)")),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(pd.DataFrame(scen), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT  —  always at bottom, after all values computed
# ─────────────────────────────────────────────────────────────────────────────
st.divider()

export_payload = {
    "version": "1.2",
    "exported_at": datetime.now().isoformat(),
    "client": {
        "name": client_name, "age": current_age,
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
    },
    "summary": {
        "corpus": round(corpus, 2),
        "total_invested": round(total_inv, 2),
        "real_value": round(real_val, 2),
        "monthly_swp": round(monthly_swp, 2),
        "wealth_multiple": round(multiple, 2),
    },
}

ex1, ex2, ex3 = st.columns([1, 1, 2])
ex1.download_button(
    "⬇️  Export plan (JSON)",
    data=json.dumps(export_payload, indent=2),
    file_name=f"{client_name.replace(' ','_')}_wealthpath_plan.json",
    mime="application/json",
    use_container_width=True,
)
ex2.download_button(
    "⬇️  Download table (CSV)",
    data=df.to_csv(index=False),
    file_name=f"{client_name.replace(' ','_')}_breakdown.csv",
    mime="text/csv",
    use_container_width=True,
)

st.markdown("""
<div class="wp-footer">
  WealthPath is a planning-support tool for SEBI-registered advisors. Not investment advice. Market returns are not guaranteed.<br>
  Verify regulations · <strong>incometaxindia.gov.in</strong> · <strong>sebi.gov.in</strong> · <strong>pfrda.org.in</strong>
</div>
""", unsafe_allow_html=True)
