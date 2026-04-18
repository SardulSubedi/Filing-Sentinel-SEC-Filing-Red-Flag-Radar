"""Filing Sentinel — SEC Filing Anomaly Detector Dashboard."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Filing Sentinel",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Design System — Deep Navy + Financial Gold (Ubineer-inspired)
# ---------------------------------------------------------------------------
C = {
    "bg":       "#0c1524",
    "sidebar":  "#081020",
    "surface":  "#12203a",
    "surface2": "#182848",
    "border":   "rgba(255,255,255,0.07)",
    "border_h": "rgba(255,255,255,0.13)",
    "text":     "#edf2f7",
    "muted":    "#7e94b0",
    "dim":      "#4a6080",
    "gold":     "#d4a84b",
    "gold_h":   "#e8c06e",
    "gold_bg":  "rgba(212,168,75,0.08)",
    "danger":   "#ef5350",
    "success":  "#4caf50",
}

CHART = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Outfit, system-ui, sans-serif", color="#7e94b0", size=12),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)",
               zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)",
               zerolinecolor="rgba(255,255,255,0.05)"),
    margin=dict(l=48, r=16, t=24, b=48),
)

# ---------------------------------------------------------------------------
# Fonts + Full CSS
# ---------------------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
    /* ============================================================
       GLOBAL
       ============================================================ */
    html, body, [data-testid="stApp"] {
        background-color: #0c1524 !important;
        color: #edf2f7 !important;
    }

    /* Canvas texture (subtle, professional) */
    [data-testid="stApp"] {
        background-image:
            radial-gradient(900px 600px at 20% 10%, rgba(212,168,75,0.08), transparent 55%),
            radial-gradient(900px 600px at 85% 20%, rgba(126,148,176,0.10), transparent 60%),
            radial-gradient(1200px 800px at 40% 120%, rgba(18,32,58,0.55), transparent 55%);
        background-attachment: fixed;
    }

    /* Content width + vertical rhythm */
    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 1400px;
        padding-top: 2.25rem;
        padding-bottom: 3.25rem;
    }

    /* Font: only target content elements, NEVER icons */
    [data-testid="stApp"] h1,
    [data-testid="stApp"] h2,
    [data-testid="stApp"] h3,
    [data-testid="stApp"] h4,
    [data-testid="stApp"] h5,
    [data-testid="stApp"] h6 {
        font-family: 'Outfit', system-ui, sans-serif !important;
        letter-spacing: -0.02em !important;
        color: #edf2f7 !important;
    }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] td,
    [data-testid="stMarkdownContainer"] th,
    [data-testid="stCaptionContainer"],
    label[data-testid="stWidgetLabel"] {
        font-family: 'Outfit', system-ui, sans-serif !important;
    }

    /* Protect icon fonts */
    [data-testid="stApp"] [data-testid="collapsedControl"],
    .material-symbols-rounded,
    [class*="material-symbols"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stApp"] button[kind="icon"],
    [data-testid="stApp"] [data-baseweb="icon"] {
        font-family: 'Material Symbols Rounded', sans-serif !important;
    }

    /* Header bar */
    [data-testid="stApp"] > header {
        background: rgba(12, 21, 36, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* ============================================================
       ANIMATIONS
       ============================================================ */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes shimmer {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes pulseGold {
        0%, 100% { box-shadow: 0 0 0 0 rgba(212,168,75,0.25); }
        50%      { box-shadow: 0 0 0 8px rgba(212,168,75,0); }
    }
    .anim-fade-up {
        animation: fadeUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    .anim-fade-up-d1 { animation-delay: 0.08s; }
    .anim-fade-up-d2 { animation-delay: 0.16s; }
    .anim-fade-up-d3 { animation-delay: 0.24s; }
    .anim-fade-in {
        animation: fadeIn 0.6s ease both;
    }

    /* ============================================================
       SIDEBAR
       ============================================================ */
    [data-testid="stSidebar"] {
        background: #081020 !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        font-family: 'Outfit', system-ui, sans-serif !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        font-family: 'Outfit', system-ui, sans-serif !important;
    }

    /* ============================================================
       HERO (landing)
       ============================================================ */
    .fs-hero {
        padding: 60px 0 20px 0;
        animation: fadeUp 0.8s cubic-bezier(0.22,1,0.36,1) both;
    }
    .fs-hero h1 {
        font-family: 'Outfit', system-ui, sans-serif !important;
        font-size: clamp(2.6rem, 5vw, 4rem);
        font-weight: 800;
        letter-spacing: -0.045em;
        line-height: 1.05;
        color: #edf2f7;
        margin: 0 0 20px 0;
    }
    .fs-hero h1 em {
        font-style: normal;
        color: #d4a84b;
    }
    .fs-hero .fs-sub {
        font-family: 'Outfit', system-ui, sans-serif;
        font-size: 1.15rem;
        font-weight: 400;
        color: #7e94b0;
        line-height: 1.7;
        max-width: 58ch;
        margin: 0 0 36px 0;
    }
    .fs-hero .fs-hint {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #4a6080;
        border-left: 2px solid #d4a84b;
        padding: 6px 0 6px 14px;
    }

    /* ============================================================
       FEATURE CARDS (landing)
       ============================================================ */
    .fs-features {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        margin-top: 52px;
    }
    @media (max-width: 768px) {
        .fs-features { grid-template-columns: 1fr; }
    }
    .fs-fcard {
        background: linear-gradient(135deg, #12203a 0%, #152545 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 36px 32px 32px;
        transition: border-color 0.5s cubic-bezier(0.22,1,0.36,1),
                    transform 0.5s cubic-bezier(0.22,1,0.36,1);
    }
    .fs-fcard:hover {
        border-color: rgba(212,168,75,0.25);
        transform: translateY(-2px);
    }
    .fs-fcard.wide { grid-column: 1 / -1; }
    .fs-fcard .fc-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        font-weight: 500;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #d4a84b;
        margin-bottom: 14px;
    }
    .fs-fcard .fc-title {
        font-family: 'Outfit', system-ui, sans-serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: #edf2f7;
        margin-bottom: 10px;
        letter-spacing: -0.01em;
    }
    .fs-fcard .fc-desc {
        font-family: 'Outfit', system-ui, sans-serif;
        font-size: 0.9rem;
        line-height: 1.7;
        color: #7e94b0;
    }

    /* ============================================================
       COMPANY HEADER (analysis)
       ============================================================ */
    .fs-company {
        padding: 28px 0 0;
        animation: fadeUp 0.6s cubic-bezier(0.22,1,0.36,1) both;
    }
    .fs-ticker {
        font-family: 'JetBrains Mono', monospace;
        font-size: clamp(2.2rem, 4vw, 3.2rem);
        font-weight: 700;
        color: #edf2f7;
        letter-spacing: -0.03em;
        margin: 0;
        line-height: 1.1;
    }
    .fs-coname {
        font-family: 'Outfit', system-ui, sans-serif;
        font-size: 0.95rem;
        color: #7e94b0;
        margin: 6px 0 0;
    }

    /* ============================================================
       METRIC STRIP
       ============================================================ */
    .fs-metrics {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        border-top: 1px solid rgba(255,255,255,0.07);
        border-bottom: 1px solid rgba(255,255,255,0.07);
        margin: 28px 0 32px;
        animation: fadeUp 0.65s cubic-bezier(0.22,1,0.36,1) 0.1s both;
    }
    @media (max-width: 768px) {
        .fs-metrics { grid-template-columns: repeat(2, 1fr); }
    }
    .fs-mcell {
        padding: 18px 20px;
        border-right: 1px solid rgba(255,255,255,0.07);
    }
    .fs-mcell:last-child { border-right: none; }
    .fs-mlabel {
        font-family: 'Outfit', system-ui, sans-serif;
        font-size: 0.68rem;
        font-weight: 500;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #4a6080;
        margin-bottom: 5px;
    }
    .fs-mval {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.3rem;
        font-weight: 600;
        color: #edf2f7;
        letter-spacing: -0.02em;
    }
    .fs-mval.flag { color: #ef5350; }
    .fs-mval.safe { color: #4caf50; }
    .fs-mval.gold { color: #d4a84b; }

    /* ============================================================
       SECTION HEADERS
       ============================================================ */
    .fs-section {
        font-family: 'Outfit', system-ui, sans-serif;
        font-size: 1.35rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #edf2f7;
        margin: 4px 0 4px;
    }
    .fs-sectionmeta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #4a6080;
        margin-bottom: 24px;
    }

    /* ============================================================
       TABS
       ============================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        border-bottom: 1px solid rgba(255,255,255,0.07) !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Outfit', system-ui, sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #4a6080 !important;
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        padding: 14px 24px !important;
        transition: color 0.35s cubic-bezier(0.22,1,0.36,1),
                    border-color 0.35s cubic-bezier(0.22,1,0.36,1) !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #d4a84b !important;
        border-bottom-color: #d4a84b !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #edf2f7 !important;
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 28px !important;
    }

    /* Plotly rounding + Streamlit chrome reduction */
    .js-plotly-plot .plotly .main-svg { border-radius: 14px; }
    [data-testid="stToolbar"] { visibility: hidden !important; height: 0 !important; }

    /* ============================================================
       BUTTONS
       ============================================================ */
    .stButton > button {
        font-family: 'Outfit', system-ui, sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        letter-spacing: 0.01em !important;
        transition: transform 0.25s cubic-bezier(0.22,1,0.36,1),
                    box-shadow 0.25s cubic-bezier(0.22,1,0.36,1),
                    background-color 0.3s !important;
    }
    .stButton > button:active {
        transform: scale(0.97) !important;
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #d4a84b, #c49a3d) !important;
        color: #0c1524 !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 30px rgba(12,21,36,0.35), 0 0 0 1px rgba(212,168,75,0.18) inset !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #e8c06e, #d4a84b) !important;
        box-shadow: 0 14px 36px rgba(12,21,36,0.45), 0 0 0 1px rgba(212,168,75,0.22) inset !important;
    }
    .stButton > button[kind="primary"]:focus-visible,
    .stButton > button[data-testid="stBaseButton-primary"]:focus-visible {
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(212,168,75,0.22), 0 14px 36px rgba(12,21,36,0.45) !important;
    }

    /* ============================================================
       INPUTS
       ============================================================ */
    [data-testid="stTextInput"] input {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.92rem !important;
        background: #12203a !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #edf2f7 !important;
        transition: border-color 0.35s cubic-bezier(0.22,1,0.36,1) !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #d4a84b !important;
        box-shadow: 0 0 0 2px rgba(212,168,75,0.12) !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: #4a6080 !important;
    }

    /* ============================================================
       EXPANDER (fix the icon font bug)
       ============================================================ */
    [data-testid="stExpander"] {
        background: #12203a !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] details > summary {
        font-family: 'Outfit', system-ui, sans-serif !important;
        font-weight: 500 !important;
        color: #7e94b0 !important;
        padding: 14px 18px !important;
    }
    [data-testid="stExpander"] details > summary:hover {
        color: #edf2f7 !important;
    }
    /* Ensure expander icon renders properly */
    [data-testid="stExpander"] details > summary svg,
    [data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] {
        font-family: 'Material Symbols Rounded' !important;
    }
    [data-testid="stExpander"] details > div {
        padding: 0 18px 18px !important;
    }

    /* ============================================================
       SLIDER
       ============================================================ */
    [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
        background-color: #d4a84b !important;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ============================================================
       PROGRESS
       ============================================================ */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #d4a84b, #e8c06e) !important;
    }

    /* ============================================================
       DOWNLOAD BUTTON
       ============================================================ */
    .stDownloadButton > button {
        font-family: 'Outfit', system-ui, sans-serif !important;
        background: #12203a !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #edf2f7 !important;
        border-radius: 10px !important;
        transition: border-color 0.3s, color 0.3s !important;
    }
    .stDownloadButton > button:hover {
        border-color: #d4a84b !important;
        color: #d4a84b !important;
    }

    /* ============================================================
       ALERTS
       ============================================================ */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
        font-family: 'Outfit', system-ui, sans-serif !important;
        border: none !important;
    }

    /* ============================================================
       DATAFRAME
       ============================================================ */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* ============================================================
       CHECKBOX
       ============================================================ */
    [data-testid="stCheckbox"] label {
        font-family: 'Outfit', system-ui, sans-serif !important;
    }

    /* ============================================================
       HIDE DEFAULT BRANDING
       ============================================================ */
    #MainMenu, footer, [data-testid="stStatusWidget"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div style="padding-top:8px;">'
        '<p style="font-family:Outfit,sans-serif; font-size:1.5rem; font-weight:700; '
        'letter-spacing:-0.03em; color:#edf2f7; margin:0 0 2px 0;">Filing Sentinel</p>'
        '<p style="font-family:Outfit,sans-serif; font-size:0.82rem; color:#4a6080; '
        'margin:0 0 28px 0;">SEC filing anomaly detection</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    ticker = st.text_input(
        "Ticker",
        value="",
        placeholder="NVDA, META, AAPL ...",
        help="Enter a US-listed stock ticker symbol",
    ).strip().upper()

    max_filings = st.slider(
        "Filings to scan",
        min_value=4,
        max_value=20,
        value=10,
    )

    include_semantic = st.checkbox(
        "Semantic drift analysis",
        value=True,
        help="Requires OPENAI_API_KEY",
    )

    include_ai_report = st.checkbox(
        "AI red flag report",
        value=True,
        help="Uses GPT for synthesis, rule-based fallback otherwise",
    )

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    analyze_btn = st.button("Run Analysis", type="primary", use_container_width=True)

    st.markdown(
        '<p style="font-family:Outfit,sans-serif; font-size:0.7rem; color:#4a6080; '
        'margin-top:40px; line-height:1.6;">'
        'Data from <a href="https://www.sec.gov/edgar/" style="color:#7e94b0;" '
        'target="_blank">SEC EDGAR</a>. Not investment advice.</p>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Chart Builders
# ---------------------------------------------------------------------------
def make_benford_chart(results: dict) -> go.Figure:
    df = pd.DataFrame(results["digits"])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["digit"], y=df["expected_pct"],
        name="Expected (Benford's)",
        marker_color="rgba(255,255,255,0.12)",
        marker_line=dict(color="rgba(255,255,255,0.2)", width=1),
    ))
    fig.add_trace(go.Bar(
        x=df["digit"], y=df["observed_pct"],
        name="Observed",
        marker_color="#d4a84b",
        marker_line=dict(color="#c49a3d", width=1),
    ))
    fig.update_layout(
        **CHART,
        barmode="group",
        xaxis_title="Leading Digit",
        yaxis_title="Frequency (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="right", x=1,
                    font=dict(size=11, color="#7e94b0"), bgcolor="rgba(0,0,0,0)"),
        height=440, bargap=0.22,
    )
    return fig


def make_deviation_chart(results: dict) -> go.Figure:
    df = pd.DataFrame(results["digits"])
    colors = ["#ef5350" if abs(d) > 3 else "rgba(212,168,75,0.6)" for d in df["deviation_pct"]]
    borders = ["#ef5350" if abs(d) > 3 else "#d4a84b" for d in df["deviation_pct"]]
    fig = go.Figure(go.Bar(
        x=df["digit"], y=df["deviation_pct"],
        marker_color=colors,
        marker_line=dict(color=borders, width=1),
        text=[f"{d:+.1f}%" for d in df["deviation_pct"]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11, color="#7e94b0"),
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.1)", line_width=1)
    fig.add_hrect(y0=-3, y1=3, fillcolor="rgba(76,175,80,0.04)", line_width=0)
    fig.update_layout(**CHART, xaxis_title="Leading Digit", yaxis_title="Deviation (%)",
                      showlegend=False, height=440)
    return fig


def make_drift_heatmap(drift: dict) -> go.Figure:
    sim = np.array(drift["similarity_matrix"])
    dates = drift["dates"]
    fig = go.Figure(go.Heatmap(
        z=sim, x=dates, y=dates,
        colorscale=[
            [0.0, "#7f1d1d"], [0.3, "#ef5350"], [0.6, "#fbbf24"],
            [0.85, "#d4a84b"], [1.0, "#1a3a2a"],
        ],
        zmin=0.7, zmax=1.0,
        text=np.round(sim, 3), texttemplate="%{text}",
        textfont=dict(size=10, family="JetBrains Mono", color="#edf2f7"),
        hoverongaps=False,
        colorbar=dict(tickfont=dict(family="JetBrains Mono", size=10, color="#4a6080"),
                      outlinewidth=0),
    ))
    fig.update_layout(**CHART, height=480, xaxis_title="Filing Date", yaxis_title="Filing Date",
                      yaxis_autorange="reversed")
    return fig


def make_drift_timeline(drift: dict) -> go.Figure:
    dates = drift["dates"]
    sims = drift["consecutive_similarities"]
    flags = drift["drift_flags"]
    labels = [f"{dates[i]} / {dates[i+1]}" for i in range(len(sims))]
    colors = [C["danger"] if f else C["gold"] for f in flags]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=sims, mode="lines+markers",
        line=dict(color="rgba(212,168,75,0.5)", width=2),
        marker=dict(color=colors, size=10, line=dict(color="#0c1524", width=2)),
        hovertemplate="%{x}<br>Similarity: %{y:.4f}<extra></extra>",
    ))
    fig.add_hline(y=drift["threshold"], line_dash="dot", line_color=C["danger"], line_width=1,
                  annotation_text=f"Threshold {drift['threshold']}",
                  annotation_position="bottom right",
                  annotation_font=dict(family="JetBrains Mono", size=10, color=C["danger"]))
    fig.update_layout(**CHART, yaxis_title="Cosine Similarity", xaxis_title="Filing Pair",
                      showlegend=False, height=440,
                      yaxis_range=[min(0.78, min(sims) - 0.04), 1.005])
    return fig


# ---------------------------------------------------------------------------
# Landing Page
# ---------------------------------------------------------------------------
if not ticker or not analyze_btn:
    st.markdown("""
    <div class="fs-hero">
        <h1>Filing <em>Sentinel</em></h1>
        <p class="fs-sub">
            Surface anomalies in public company filings before the market
            figures it out. Statistical forensics and semantic analysis
            on every 10-K and 10-Q, from raw XBRL to plain-English verdict.
        </p>
        <p class="fs-hint">Enter a ticker in the sidebar to begin analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="fs-features">
        <div class="fs-fcard anim-fade-up anim-fade-up-d1">
            <div class="fc-tag">Statistical Forensics</div>
            <div class="fc-title">Benford's Law Analysis</div>
            <p class="fc-desc">
                Every XBRL-reported figure tested against the expected
                leading-digit distribution. Deviations measured via MAD
                and chi-squared, flagged with Nigrini thresholds.
                Works on 20,000+ data points per company with zero API cost.
            </p>
        </div>
        <div class="fs-fcard anim-fade-up anim-fade-up-d2">
            <div class="fc-tag">NLP + Embeddings</div>
            <div class="fc-title">Semantic Drift Detection</div>
            <p class="fc-desc">
                Embedding-based cosine similarity tracks how MD&amp;A
                and Risk Factor language shifts across consecutive filings.
                Sudden drops often precede earnings surprises or restatements.
            </p>
        </div>
        <div class="fs-fcard wide anim-fade-up anim-fade-up-d3">
            <div class="fc-tag">Synthesis</div>
            <div class="fc-title">Red Flag Report</div>
            <p class="fc-desc">
                All signals consolidated into a single anomaly report written for a CFA-level audience.
                AI-powered when an OpenAI key is present; deterministic rule-based fallback otherwise.
                Downloadable as markdown, ready to drop into a research note.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ---------------------------------------------------------------------------
# Analysis Pipeline
# ---------------------------------------------------------------------------
from filing_sentinel.edgar import (
    lookup_cik, get_company_facts, get_10k_10q_filings,
    extract_all_xbrl_values, fetch_filing_html,
)
from filing_sentinel.parser import extract_section
from filing_sentinel.benford import analyze as benford_analyze
from filing_sentinel.semantic import compute_drift_matrix
from filing_sentinel.agent import synthesize_report

try:
    with st.spinner("Looking up company..."):
        cik, company_name = lookup_cik(ticker)
except ValueError as e:
    st.error(str(e))
    st.stop()

st.markdown(
    f'<div class="fs-company">'
    f'<p class="fs-ticker">{ticker}</p>'
    f'<p class="fs-coname">{company_name} &middot; CIK {cik}</p>'
    f'</div>',
    unsafe_allow_html=True,
)

progress = st.progress(0, text="Fetching XBRL data...")

# Step 1: Benford's
try:
    company_facts = get_company_facts(cik)
    xbrl_values = extract_all_xbrl_values(company_facts)
    raw_values = [v["value"] for v in xbrl_values]
    benford_results = benford_analyze(raw_values)
except Exception as e:
    benford_results = {"error": f"Benford's analysis failed: {e}", "n_samples": 0}

progress.progress(30, text="Fetching filing list...")

# Step 2: Filings + semantic drift
mda_drift = None
risk_drift = None
filings_meta = []
try:
    filings_meta = get_10k_10q_filings(cik, max_filings=max_filings)
except Exception as e:
    st.warning(f"Could not fetch filing list: {e}")

if include_semantic and filings_meta:
    progress.progress(40, text="Downloading filings...")
    mda_sections, risk_sections = [], []
    for i, filing in enumerate(reversed(filings_meta)):
        pct = 40 + int(40 * (i + 1) / len(filings_meta))
        progress.progress(min(pct, 80), text=f"Parsing {filing['form']} ({filing['date']})...")
        try:
            html = fetch_filing_html(filing["url"])
            mda_text = extract_section(html, "mda")
            risk_text = extract_section(html, "risk_factors")
            if mda_text:
                mda_sections.append({"date": filing["date"], "text": mda_text})
            if risk_text:
                risk_sections.append({"date": filing["date"], "text": risk_text})
        except Exception:
            continue
    if len(mda_sections) >= 2:
        progress.progress(82, text="Computing MD&A embeddings...")
        try:
            mda_drift = compute_drift_matrix(mda_sections)
        except RuntimeError as e:
            st.info(f"Semantic drift skipped: {e}")
    if len(risk_sections) >= 2:
        progress.progress(88, text="Computing Risk Factor embeddings...")
        try:
            risk_drift = compute_drift_matrix(risk_sections)
        except RuntimeError:
            pass

# Step 3: Report
progress.progress(92, text="Generating report...")
report_text = ""
if include_ai_report:
    try:
        report_text = synthesize_report(ticker, company_name, benford_results, mda_drift, risk_drift)
    except Exception as e:
        report_text = f"Report generation failed: {e}"

progress.progress(100, text="Done")
progress.empty()

# ---------------------------------------------------------------------------
# Metric Strip
# ---------------------------------------------------------------------------
n_samples = benford_results.get("n_samples", 0)
mad_val = benford_results.get("mad")
n_filings = len(filings_meta)
has_drift = bool(
    (mda_drift and mda_drift.get("has_significant_drift"))
    or (risk_drift and risk_drift.get("has_significant_drift"))
)

mad_str = f"{mad_val}" if mad_val is not None else "---"
mad_cls = "flag" if benford_results.get("flagged") else "safe"
drift_str = "Detected" if has_drift else "None"
drift_cls = "flag" if has_drift else "safe"

st.markdown(f"""
<div class="fs-metrics">
    <div class="fs-mcell">
        <div class="fs-mlabel">Data Points</div>
        <div class="fs-mval gold">{n_samples:,}</div>
    </div>
    <div class="fs-mcell">
        <div class="fs-mlabel">Benford MAD</div>
        <div class="fs-mval {mad_cls}">{mad_str}</div>
    </div>
    <div class="fs-mcell">
        <div class="fs-mlabel">Filings Scanned</div>
        <div class="fs-mval gold">{n_filings}</div>
    </div>
    <div class="fs-mcell">
        <div class="fs-mlabel">Semantic Drift</div>
        <div class="fs-mval {drift_cls}">{drift_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tabs = st.tabs(["Benford's Law", "Semantic Drift", "Red Flag Report", "Filings"])

with tabs[0]:
    if "error" in benford_results:
        st.warning(benford_results["error"])
    else:
        conformity = benford_results["conformity"]
        st.markdown(
            f'<div class="fs-section">Benford\'s Law &mdash; {conformity}</div>'
            f'<div class="fs-sectionmeta">'
            f'{benford_results["n_samples"]:,} values &middot; '
            f'MAD {benford_results["mad"]} &middot; '
            f'&chi;&sup2; {benford_results["chi2_statistic"]} '
            f'(p={benford_results["chi2_p_value"]})'
            f'</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(make_benford_chart(benford_results), use_container_width=True)
        with c2:
            st.plotly_chart(make_deviation_chart(benford_results), use_container_width=True)

        with st.expander("About Benford's Law"):
            st.markdown(
                "Benford's Law predicts that in naturally occurring datasets, the leading "
                "digit 1 appears ~30.1% of the time, digit 2 ~17.6%, and so on. Financial "
                "figures in legitimate filings tend to follow this distribution closely.\n\n"
                "**MAD Thresholds** (Nigrini, 2012):\n"
                "- < 0.006: Close conformity\n"
                "- < 0.012: Acceptable conformity\n"
                "- < 0.015: Marginally acceptable\n"
                "- 0.015+: Nonconformity (investigate further)"
            )

with tabs[1]:
    if not include_semantic:
        st.info("Semantic drift analysis is disabled. Enable it in the sidebar.")
    elif mda_drift is None and risk_drift is None:
        st.warning("Requires OPENAI_API_KEY and at least 2 parseable filings.")
    else:
        for label, drift in [("MD&A", mda_drift), ("Risk Factors", risk_drift)]:
            if drift is None or "error" in drift:
                continue
            st.markdown(
                f'<div class="fs-section">{label} Drift</div>'
                f'<div class="fs-sectionmeta">'
                f'{len(drift["dates"])} filings &middot; '
                f'{drift["dates"][0]} to {drift["dates"][-1]} &middot; '
                f'threshold {drift["threshold"]}'
                f'</div>',
                unsafe_allow_html=True,
            )
            dc1, dc2 = st.columns(2)
            with dc1:
                st.plotly_chart(make_drift_timeline(drift), use_container_width=True)
            with dc2:
                st.plotly_chart(make_drift_heatmap(drift), use_container_width=True)

            if drift.get("has_significant_drift"):
                for i, fl in enumerate(drift["drift_flags"]):
                    if fl:
                        st.warning(
                            f"**Significant language shift** between "
                            f"{drift['dates'][i]} and {drift['dates'][i+1]} "
                            f"(similarity: {drift['consecutive_similarities'][i]:.4f})"
                        )
            else:
                st.success(f"No significant {label} language changes detected.")
            st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

        with st.expander("How semantic drift detection works"):
            st.markdown(
                "Each filing section is converted into an embedding vector. Cosine similarity "
                "between consecutive filings measures language change. A sudden drop can "
                "precede earnings surprises, restatements, or regulatory actions."
            )

with tabs[2]:
    if not report_text:
        st.info("Report generation is disabled. Enable it in the sidebar.")
    else:
        st.markdown(report_text)
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        st.download_button(
            "Download Report (.md)",
            data=report_text,
            file_name=f"{ticker}_red_flag_report.md",
            mime="text/markdown",
        )

with tabs[3]:
    if filings_meta:
        st.markdown(
            f'<div class="fs-section">Filing Index</div>'
            f'<div class="fs-sectionmeta">{len(filings_meta)} recent 10-K / 10-Q for {ticker}</div>',
            unsafe_allow_html=True,
        )
        df_filings = pd.DataFrame(filings_meta)
        st.dataframe(
            df_filings[["form", "date", "accession"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "form": st.column_config.TextColumn("Form"),
                "date": st.column_config.TextColumn("Filed"),
                "accession": st.column_config.TextColumn("Accession"),
            },
        )
    else:
        st.warning("No filing metadata available.")
