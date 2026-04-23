import streamlit as st
import pandas as pd
import os
from supabase import create_client
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Remittance Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Design tokens ──────────────────────────────────────────────────────────────
BG_PAGE   = "#0d0d1f"
BG_CARD   = "#16162a"
BG_CARD2  = "#1e1e38"
BG_ROW    = "#1a1a30"
BG_THEAD  = "#252545"
BORDER    = "#2e2e52"
ACCENT    = "#00e5a0"      # green – positive values
ACCENT2   = "#4d9fff"      # blue  – info / links
WARN      = "#ffb347"      # amber – warnings
TEXT_PRI  = "#f0f0ff"
TEXT_SEC  = "#9898c0"
FONT      = "'Inter', 'Segoe UI', sans-serif"

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    plot_bgcolor=BG_CARD,
    paper_bgcolor=BG_CARD,
    font=dict(color=TEXT_PRI, family=FONT, size=13),
    xaxis=dict(gridcolor=BORDER, showgrid=True),
    yaxis=dict(gridcolor=BORDER, showgrid=True),
    margin=dict(l=10, r=10, t=40, b=10),
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, .stApp {{
    background-color: {BG_PAGE} !important;
    font-family: {FONT};
    color: {TEXT_PRI};
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 1.5rem 2rem 3rem !important; max-width: 1200px; margin: auto; }}

/* ── Typography ── */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    color: {TEXT_PRI} !important;
    font-family: {FONT} !important;
    letter-spacing: -0.01em;
}}
p, span, div, label {{ color: {TEXT_PRI} !important; font-family: {FONT} !important; }}
.stCaption, .caption-text {{ color: {TEXT_SEC} !important; font-size: 0.8rem !important; }}

/* ── Metric cards ── */
div[data-testid="stMetric"] {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
}}
div[data-testid="stMetricValue"] {{
    color: {ACCENT} !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    font-family: {FONT} !important;
}}
div[data-testid="stMetricLabel"] {{ color: {TEXT_SEC} !important; font-size: 0.82rem !important; }}
div[data-testid="stMetricDelta"] {{ font-size: 0.78rem !important; }}

/* ── Alerts ── */
div[data-testid="stAlert"] {{
    border-radius: 10px !important;
    border: 1px solid {BORDER} !important;
}}
div[data-testid="stAlert"] p {{ color: {TEXT_PRI} !important; font-size: 0.92rem !important; }}
.stSuccess {{ background: #0a2e1e !important; border-left: 3px solid {ACCENT} !important; }}
.stInfo    {{ background: #0a1a3a !important; border-left: 3px solid {ACCENT2} !important; }}
.stWarning {{ background: #2e1e0a !important; border-left: 3px solid {WARN} !important; }}

/* ── Inputs ── */
.stSelectbox > div > div,
.stNumberInput > div > div > input,
input[type="number"] {{
    background: {BG_CARD2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT_PRI} !important;
    font-family: {FONT} !important;
}}
.stSelectbox label, .stNumberInput label, .stSlider label, .stRadio label {{
    color: {TEXT_SEC} !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}}

/* ── Slider ── */
.stSlider > div > div > div {{ background: {ACCENT} !important; }}

/* ── Divider ── */
hr {{ border-color: {BORDER} !important; margin: 28px 0 !important; }}

/* ── Buttons ── */
.stButton button {{
    background: {BG_CARD2} !important;
    color: {TEXT_PRI} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    font-family: {FONT} !important;
    font-size: 0.88rem !important;
    padding: 6px 18px !important;
    transition: all 0.2s;
}}
.stButton button:hover {{
    background: {ACCENT} !important;
    color: #0d0d1f !important;
    border-color: {ACCENT} !important;
}}

/* ── HTML tables (used everywhere instead of st.dataframe) ── */
.dark-table-wrap {{
    overflow-x: auto;
    border-radius: 12px;
    border: 1px solid {BORDER};
    margin-bottom: 12px;
}}
.dark-table {{
    width: 100%;
    border-collapse: collapse;
    font-family: {FONT};
    font-size: 0.88rem;
    background: {BG_ROW};
}}
.dark-table thead tr {{
    background: {BG_THEAD} !important;
}}
.dark-table thead th {{
    color: {TEXT_SEC} !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    padding: 12px 16px !important;
    border-bottom: 1px solid {BORDER} !important;
    text-align: left !important;
}}
.dark-table tbody tr {{
    border-bottom: 1px solid {BORDER};
    transition: background 0.15s;
}}
.dark-table tbody tr:last-child {{ border-bottom: none; }}
.dark-table tbody tr:hover {{ background: {BG_CARD2} !important; }}
.dark-table tbody td {{
    color: {TEXT_PRI} !important;
    padding: 11px 16px !important;
    background: transparent !important;
}}
.dark-table tbody td.accent  {{ color: {ACCENT}  !important; font-weight: 600; }}
.dark-table tbody td.accent2 {{ color: {ACCENT2} !important; font-weight: 600; }}
.dark-table tbody td.warn    {{ color: {WARN}    !important; font-weight: 600; }}
.dark-table tbody td.best    {{
    color: {ACCENT} !important;
    font-weight: 700;
    position: relative;
}}
.dark-table tbody td.best::before {{
    content: "★ ";
    font-size: 0.75rem;
}}

/* ── Section card wrapper ── */
.section-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
}}
.section-label {{
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {TEXT_SEC};
    margin-bottom: 4px;
}}
.section-title {{
    font-size: 1.15rem;
    font-weight: 600;
    color: {TEXT_PRI};
    margin-bottom: 16px;
}}
.hero-title {{
    font-size: 2rem;
    font-weight: 700;
    color: {TEXT_PRI};
    margin-bottom: 6px;
    letter-spacing: -0.02em;
}}
.hero-sub {{
    font-size: 0.95rem;
    color: {TEXT_SEC};
    margin-bottom: 4px;
}}
.badge {{
    display: inline-block;
    background: {BG_CARD2};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    color: {TEXT_SEC};
    margin-right: 6px;
    margin-top: 8px;
}}
.badge-green {{
    background: #0a2e1e;
    border-color: {ACCENT};
    color: {ACCENT};
}}
.result-box {{
    background: #0a2e1e;
    border: 1px solid {ACCENT};
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
}}
.result-box .amount {{
    font-size: 1.8rem;
    font-weight: 700;
    color: {ACCENT};
    line-height: 1.1;
}}
.result-box .label {{
    font-size: 0.8rem;
    color: {TEXT_SEC};
    margin-top: 2px;
}}
.result-box .after-fee {{
    font-size: 0.85rem;
    color: {TEXT_SEC};
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid {BORDER};
}}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def dark_table(rows: list[dict], highlight_col: str = "", best_key: str = "") -> None:
    """Render a list of dicts as a styled dark HTML table."""
    if not rows:
        return
    headers = list(rows[0].keys())
    
    # Find best value index if requested
    best_idx = -1
    if best_key and rows:
        try:
            vals = [float(str(r.get(best_key, "0")).replace(",", "").replace("$", "").replace("KES", "").strip())
                    for r in rows]
            best_idx = vals.index(max(vals))
        except Exception:
            pass

    th_cells = "".join(f"<th>{h}</th>" for h in headers)
    body_rows = []
    for i, row in enumerate(rows):
        cells = []
        for h in headers:
            val = row.get(h, "")
            cls = ""
            if i == best_idx and h == best_key:
                cls = " class='best'"
            elif highlight_col and h == highlight_col:
                cls = " class='accent'"
            cells.append(f"<td{cls}>{val}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    html = f"""
    <div class="dark-table-wrap">
      <table class="dark-table">
        <thead><tr>{th_cells}</tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
      </table>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


def section(label: str, title: str) -> None:
    st.markdown(f"""
    <div class="section-label">{label}</div>
    <div class="section-title">{title}</div>
    """, unsafe_allow_html=True)


def plotly_chart(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)


# ── Data ───────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("🔐 Database credentials not configured. Set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")
    st.stop()

@st.cache_data(ttl=300)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = (supabase.table("exchange_rates")
                        .select("*")
                        .order("fetched_at", desc=False)
                        .execute())
    df = pd.DataFrame(response.data)
    if not df.empty:
        df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    return df

df = load_data()

if df.empty:
    st.warning("⏳ No data yet. The automated fetcher will start collecting data soon.")
    st.stop()

latest = df.groupby(["base_currency", "target_currency"]).last().reset_index()
seven_days_ago = datetime.now() - timedelta(days=7)
df_recent = df[df["fetched_at"] >= seven_days_ago]

def get_rate(base, target):
    vals = latest[(latest["base_currency"] == base) & (latest["target_currency"] == target)]["rate"].values
    return float(vals[0]) if len(vals) > 0 else None


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="padding: 12px 0 8px;">
  <div class="hero-title">🌍 Global Remittance Tracker</div>
  <div class="hero-sub">Live mid-market exchange rates · USA, UK & Europe → Africa</div>
  <span class="badge badge-green">● Live</span>
  <span class="badge">Updates every hour</span>
  <span class="badge">Mid-market rates</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# TOP METRICS
# ══════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)
pairs_meta = [
    (c1, "🇺🇸 USD → 🇰🇪 KES", "USD", "KES"),
    (c2, "🇬🇧 GBP → 🇰🇪 KES", "GBP", "KES"),
    (c3, "🇪🇺 EUR → 🇰🇪 KES", "EUR", "KES"),
    (c4, "🇺🇸 USD → 🇳🇬 NGN", "USD", "NGN"),
]
for col, label, base, tgt in pairs_meta:
    rate = get_rate(base, tgt)
    if rate:
        # Calculate 24h change if enough history
        yesterday = datetime.now() - timedelta(hours=24)
        hist = df[(df["base_currency"] == base) & (df["target_currency"] == tgt) & (df["fetched_at"] >= yesterday)]
        delta_str = None
        if len(hist) >= 2:
            old = hist.iloc[0]["rate"]
            change_pct = ((rate - old) / old) * 100
            delta_str = f"{change_pct:+.2f}% (24h)"
        col.metric(label, f"{rate:,.2f}", delta=delta_str)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 1. CURRENCY CONVERTER
# ══════════════════════════════════════════════════════════════════════════════
section("Feature 01", "💸 Currency Converter")

col_a, col_b, col_c = st.columns([1.5, 1, 1])
with col_a:
    amount = st.number_input("Amount to send", min_value=1, value=100, step=10)
with col_b:
    from_currency = st.selectbox("From", ["USD", "GBP", "EUR"])
with col_c:
    to_currency = st.selectbox("To", ["KES", "NGN", "GHS", "ZAR", "UGX", "TZS"])

conv_rate = get_rate(from_currency, to_currency)

if conv_rate:
    converted = amount * conv_rate
    fee_pct = st.slider("Estimated provider fee (%)", 0.0, 5.0, 2.0, 0.5)
    fee_usd = amount * (fee_pct / 100)
    recipient_gets = (amount - fee_usd) * conv_rate

    st.markdown(f"""
    <div class="result-box">
      <div class="label">{amount} {from_currency} at mid-market rate</div>
      <div class="amount">{converted:,.2f} {to_currency}</div>
      <div class="after-fee">
        After {fee_pct:.1f}% fee (≈ {from_currency} {fee_usd:.2f}) → 
        recipient gets <strong style="color:#f0f0ff">{recipient_gets:,.2f} {to_currency}</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("💡 Mid-market rate shown. Your actual provider rate will differ.")
else:
    st.warning(f"No rate data available for {from_currency} → {to_currency}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 2. BEST TIME ALERT
# ══════════════════════════════════════════════════════════════════════════════
section("Feature 02", "📊 Best Time to Send")

PAIR_MAP = {
    "USD → KES": ("USD", "KES"),
    "USD → NGN": ("USD", "NGN"),
    "GBP → KES": ("GBP", "KES"),
    "EUR → KES": ("EUR", "KES"),
}
alert_pair = st.selectbox("Currency pair", list(PAIR_MAP.keys()))
base, target = PAIR_MAP[alert_pair]
pair_data = df[(df["base_currency"] == base) & (df["target_currency"] == target) & (df["fetched_at"] >= seven_days_ago)]

if not pair_data.empty:
    cur = pair_data.iloc[-1]["rate"]
    best = pair_data["rate"].max()
    avg  = pair_data["rate"].mean()
    low  = pair_data["rate"].min()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current Rate",  f"{cur:.2f}")
    m2.metric("7-Day High",    f"{best:.2f}")
    m3.metric("7-Day Average", f"{avg:.2f}")
    m4.metric("7-Day Low",     f"{low:.2f}")

    pct_from_best = ((best - cur) / cur) * 100
    if cur >= best * 0.99:
        st.success(f"✅ **Great time to send!** You're within 1% of the 7-day high.")
    elif cur <= best * 0.95:
        st.info(f"⏳ **Consider waiting.** Rate is {pct_from_best:.1f}% below the 7-day high.")
    else:
        st.warning(f"📊 **Moderate rate.** {pct_from_best:.1f}% below this week's best.")

    fig = px.line(pair_data, x="fetched_at", y="rate",
                  title=f"{base} → {target} · Last 7 Days")
    fig.add_hline(y=best, line_dash="dot", line_color=ACCENT,
                  annotation_text="7-day high", annotation_font_color=ACCENT)
    fig.add_hline(y=avg,  line_dash="dot", line_color=ACCENT2,
                  annotation_text="average", annotation_font_color=ACCENT2)
    fig.update_traces(line_color=ACCENT2, line_width=2)
    plotly_chart(fig)
else:
    st.warning("Not enough historical data for this pair yet.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 3. SEND MONEY COST CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
section("Feature 03", "🏦 Send Money Cost Calculator")

col_s1, col_s2 = st.columns([2, 1])
with col_s1:
    send_amount = st.number_input("Amount to send (USD)", min_value=10, value=500, step=50, key="send_calc")
with col_s2:
    dest_currency = st.selectbox("Destination currency", ["KES", "NGN", "GHS", "ZAR", "UGX", "TZS"], key="dest_curr")

dest_rate = get_rate("USD", dest_currency)

SERVICES = {
    "Sendwave / M-Pesa":  1.0,
    "WorldRemit":         2.0,
    "Bank Transfer":      3.0,
    "Western Union":      4.0,
    "PayPal":             4.5,
}

if dest_rate:
    rows = []
    for svc, fee_pct in SERVICES.items():
        fee_usd   = send_amount * (fee_pct / 100)
        after_fee = send_amount - fee_usd
        rcv       = after_fee * dest_rate
        rows.append({
            "Service":            svc,
            "Fee":                f"{fee_pct}%",
            "Fee (USD)":          f"${fee_usd:.2f}",
            f"Recipient ({dest_currency})": f"{rcv:,.0f}",
        })

    best_col = f"Recipient ({dest_currency})"
    dark_table(rows, highlight_col=f"Recipient ({dest_currency})", best_key=best_col)

    best_row = min(rows, key=lambda r: float(r["Fee (USD)"].replace("$", "")))
    st.success(f"💰 **Lowest fee:** {best_row['Service']} → {best_row[best_col]} {dest_currency} received")

    # Bar chart comparison
    fig_bar = go.Figure(go.Bar(
        x=[r["Service"] for r in rows],
        y=[float(r[best_col].replace(",", "")) for r in rows],
        marker_color=[ACCENT if r["Service"] == best_row["Service"] else ACCENT2 for r in rows],
        text=[r[best_col] for r in rows],
        textposition="outside",
        textfont=dict(color=TEXT_PRI, size=11),
    ))
    fig_bar.update_layout(
        title=f"What recipient gets out of ${send_amount} (USD → {dest_currency})",
        xaxis_title="", yaxis_title=f"Amount ({dest_currency})",
        showlegend=False, **PLOTLY_LAYOUT
    )
    plotly_chart(fig_bar)
else:
    st.warning(f"USD → {dest_currency} rate not available")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 4. RATE ALERT CHECKER
# ══════════════════════════════════════════════════════════════════════════════
section("Feature 04", "🔔 Rate Alert Checker")

st.caption("Set a target rate and check if it's been reached this week.")

col_r1, col_r2 = st.columns([1, 1])
with col_r1:
    alert_pair2 = st.selectbox("Currency pair", list(PAIR_MAP.keys()), key="alert_pair2")
alert_base, alert_tgt = PAIR_MAP[alert_pair2]
cur_alert = get_rate(alert_base, alert_tgt)

if cur_alert:
    with col_r2:
        target_rate = st.number_input("Your target rate", min_value=0.01,
                                      value=round(cur_alert + 2, 2), step=0.5)

    c_r1, c_r2, c_r3 = st.columns(3)
    c_r1.metric("Current Rate",  f"{cur_alert:.2f}")
    c_r2.metric("Your Target",   f"{target_rate:.2f}")

    pair_hist = df[(df["base_currency"] == alert_base) & (df["target_currency"] == alert_tgt)]
    max_ever  = pair_hist["rate"].max() if not pair_hist.empty else cur_alert
    c_r3.metric("All-Time High (stored)", f"{max_ever:.2f}")

    if target_rate <= cur_alert:
        st.success(f"🎯 **TARGET REACHED!** Current rate {cur_alert:.2f} meets your target of {target_rate:.2f}")
    else:
        gap = ((target_rate - cur_alert) / cur_alert) * 100
        st.info(f"⏳ Not yet reached. Need +{gap:.1f}% ({target_rate - cur_alert:.2f} pts) to hit {target_rate:.2f}")

    if not pair_hist.empty:
        if max_ever >= target_rate:
            st.caption(f"📈 Your target was previously reached (historical high: {max_ever:.2f})")
        else:
            st.caption(f"📉 Target not yet reached in stored history (high so far: {max_ever:.2f})")
else:
    st.warning("Rate data not available for selected pair.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 5. MULTI-CURRENCY SOURCE COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
section("Feature 05", "🌍 Best Sending Country Comparison")

compare_amount = st.number_input("USD equivalent to compare", min_value=10, value=100, step=10, key="compare_amt")
compare_dest   = st.selectbox("Destination", ["KES", "NGN", "GHS", "ZAR"], key="compare_dest")

SOURCES = {
    "🇺🇸 USA (USD)": ("USD", None),
    "🇬🇧 UK  (GBP)": ("GBP", "USD"),
    "🇪🇺 EUR (EUR)": ("EUR", "USD"),
}

comp_rows = []
for label, (src_cur, pivot) in SOURCES.items():
    dest_r = get_rate(src_cur, compare_dest)
    if not dest_r:
        continue
    if pivot:
        # Convert USD amount → source currency first
        usd_to_src = get_rate("USD", src_cur)
        src_amount  = compare_amount * usd_to_src if usd_to_src else compare_amount
    else:
        src_amount = compare_amount
    received = src_amount * dest_r
    comp_rows.append({
        "Sending From":         label,
        f"Received ({compare_dest})": f"{received:,.0f}",
    })

if comp_rows:
    dark_table(comp_rows, best_key=f"Received ({compare_dest})")
    best_comp = max(comp_rows, key=lambda r: float(r[f"Received ({compare_dest})"].replace(",", "")))
    st.success(f"🏆 **Best value:** Sending from {best_comp['Sending From']} gives most {compare_dest}")
else:
    st.warning("Comparison data not available.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 6. HISTORICAL TRENDS
# ══════════════════════════════════════════════════════════════════════════════
section("Feature 06", "📈 Exchange Rate Trends")

chart_pair = st.selectbox("Currency pair", list(PAIR_MAP.keys()), key="chart_pair")
chart_base, chart_tgt = PAIR_MAP[chart_pair]
chart_data = df_recent[(df_recent["base_currency"] == chart_base) & (df_recent["target_currency"] == chart_tgt)]

if not chart_data.empty:
    fig_hist = px.area(chart_data, x="fetched_at", y="rate",
                       title=f"{chart_base} → {chart_tgt} · Last 7 Days")
    fig_hist.update_traces(
        line_color=ACCENT2, line_width=2,
        fillcolor="rgba(77,159,255,0.12)"
    )
    plotly_chart(fig_hist)
else:
    st.warning("Not enough data for this pair in the last 7 days.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 7. RECENT RAW RATES TABLE
# ══════════════════════════════════════════════════════════════════════════════
section("Data", "📋 Recent Rates Log")

recent = (df.tail(20)[["base_currency", "target_currency", "rate", "fetched_at"]]
            .sort_values("fetched_at", ascending=False)
            .copy())
recent["fetched_at"] = recent["fetched_at"].dt.strftime("%Y-%m-%d %H:%M")
recent["rate"] = recent["rate"].apply(lambda x: f"{x:,.4f}")
recent.columns = ["From", "To", "Rate", "Fetched At"]

dark_table(recent.to_dict("records"), highlight_col="Rate")
st.caption(f"📡 Last updated: {df['fetched_at'].max().strftime('%Y-%m-%d %H:%M UTC')} · Refreshes every hour")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER / TRUST SIGNALS
# ══════════════════════════════════════════════════════════════════════════════
section("Trust", "⚡ About This Data")

f1, f2, f3 = st.columns(3)
f1.metric("🕐 Update Frequency", "Every Hour",    delta="Automated via GitHub Actions")
f2.metric("📊 Data Points",      f"{len(df):,}",  delta="And growing")
f3.metric("🔗 Source",           "ExchangeRate API", delta="Live mid-market rates")

st.markdown(f"""
<div style="text-align:center; margin-top:28px; padding-bottom:20px;">
  <p style="color:{TEXT_SEC}; font-size:0.82rem; margin-bottom:12px;">
    Rates are mid-market and for reference only. Always check your provider's actual rate before sending.
  </p>
  <a href="https://github.com/petermusila/global-remittance-tracker" target="_blank"
     style="text-decoration:none;">
    <span style="background:{BG_CARD2}; color:{TEXT_PRI}; border:1px solid {BORDER};
                 border-radius:8px; padding:8px 20px; font-size:0.88rem; font-family:{FONT};">
      📁 View Source on GitHub
    </span>
  </a>
</div>
""", unsafe_allow_html=True)
