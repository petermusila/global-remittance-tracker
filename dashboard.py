import streamlit as st
import pandas as pd
import os
from supabase import create_client
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RemitTrack · Global Remittance Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Midnight Finance Design Tokens ─────────────────────────────────────────────
BG_PAGE    = "#060612"
BG_CARD    = "#0d1117"
BG_CARD2   = "#0f172a"
BG_INPUT   = "#1e293b"
BORDER     = "#1e293b"
BORDER2    = "#334155"
ACCENT     = "#6ee7b7"       # emerald green
ACCENT_DIM = "#059669"       # muted green
ACCENT2    = "#38bdf8"       # sky blue
WARN       = "#fbbf24"
TEXT_PRI   = "#f1f5f9"
TEXT_SEC   = "#94a3b8"
TEXT_HINT  = "#475569"
FONT       = "'Inter', 'Segoe UI', sans-serif"

PLOTLY_BASE = dict(
    template="plotly_dark",
    plot_bgcolor=BG_CARD2,
    paper_bgcolor=BG_CARD,
    font=dict(color=TEXT_SEC, family=FONT, size=12),
    xaxis=dict(gridcolor=BORDER, showgrid=True, zeroline=False,
               tickfont=dict(color=TEXT_HINT, size=11)),
    yaxis=dict(gridcolor=BORDER, showgrid=True, zeroline=False,
               tickfont=dict(color=TEXT_HINT, size=11)),
    margin=dict(l=8, r=8, t=44, b=8),
    title_font=dict(color=TEXT_SEC, size=13, family=FONT),
    hoverlabel=dict(bgcolor=BG_CARD2, bordercolor=BORDER2,
                    font=dict(color=TEXT_PRI, size=12, family=FONT)),
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {{
    background-color: {BG_PAGE} !important;
    font-family: {FONT} !important;
    color: {TEXT_PRI} !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1280px !important;
    margin: 0 auto !important;
}}
h1,h2,h3,h4,h5,h6,p,span,div,label {{
    color: {TEXT_PRI} !important;
    font-family: {FONT} !important;
}}
.stCaption {{ color: {TEXT_HINT} !important; font-size: 0.78rem !important; }}

div[data-testid="stMetric"] {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-top: 2px solid {ACCENT_DIM} !important;
    border-radius: 12px !important;
    padding: 20px 22px !important;
}}
div[data-testid="stMetricValue"] {{
    color: {ACCENT} !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}}
div[data-testid="stMetricLabel"] {{
    color: {TEXT_SEC} !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}}
div[data-testid="stMetricDelta"] > div {{
    font-size: 0.73rem !important;
    color: {TEXT_HINT} !important;
}}
div[data-testid="stMetricDelta"] svg {{ display: none !important; }}

div[data-testid="stAlert"] {{
    border-radius: 8px !important;
    font-size: 0.88rem !important;
}}
div[data-testid="stAlert"] p {{ color: {TEXT_PRI} !important; }}
.stSuccess {{ background: #022c22 !important; border-left: 3px solid {ACCENT} !important; border-color: {ACCENT_DIM} !important; }}
.stInfo    {{ background: #0c1f3a !important; border-left: 3px solid {ACCENT2} !important; border-color: #0369a1 !important; }}
.stWarning {{ background: #1c1208 !important; border-left: 3px solid {WARN} !important; border-color: #92400e !important; }}

.stSelectbox > div > div,
.stNumberInput > div > div > input {{
    background: {BG_INPUT} !important;
    border: 1px solid {BORDER2} !important;
    border-radius: 8px !important;
    color: {TEXT_PRI} !important;
}}
.stSelectbox label, .stNumberInput label, .stSlider label {{
    color: {TEXT_HINT} !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}}
.stSlider > div > div > div > div {{
    background: {ACCENT_DIM} !important;
}}
hr {{ border: none !important; border-top: 1px solid {BORDER} !important; margin: 32px 0 !important; }}
.stPlotlyChart {{
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}}

/* Topbar */
.mf-topbar {{
    display:flex; align-items:center; justify-content:space-between;
    padding: 12px 0 26px; border-bottom: 1px solid {BORDER}; margin-bottom: 28px;
}}
.mf-logo {{ font-size:1.3rem; font-weight:700; letter-spacing:-.01em; color:{TEXT_PRI}; }}
.mf-logo span {{ color:{ACCENT}; }}
.mf-right {{ display:flex; align-items:center; gap:14px; }}
.mf-live {{
    display:inline-flex; align-items:center; gap:5px;
    background:#022c22; border:1px solid {ACCENT_DIM};
    border-radius:20px; padding:4px 11px;
    font-size:0.7rem; font-weight:700; color:{ACCENT}; letter-spacing:.05em;
}}
.mf-live-dot {{
    width:6px; height:6px; border-radius:50%; background:{ACCENT};
    animation: blink 2s infinite;
}}
.mf-stale {{
    background:#1c1208; border-color:#92400e; color:{WARN};
}}
.mf-stale .mf-live-dot {{ background:{WARN}; }}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}
.mf-ts {{ font-size:0.72rem; color:{TEXT_HINT}; }}

/* Section headers */
.mf-sec {{
    display:flex; align-items:baseline; gap:10px;
    margin:28px 0 16px; padding-bottom:10px; border-bottom:1px solid {BORDER};
}}
.mf-sec-n {{ font-size:0.68rem; font-weight:700; letter-spacing:.1em; color:{ACCENT_DIM}; }}
.mf-sec-t {{ font-size:1rem; font-weight:600; color:{TEXT_PRI}; letter-spacing:-.01em; }}

/* Converter result */
.mf-result {{
    background:{BG_CARD}; border:1px solid {ACCENT_DIM};
    border-radius:12px; padding:20px 24px; margin:14px 0 6px;
    display:flex; align-items:center; justify-content:space-between; gap:16px;
    flex-wrap: wrap;
}}
.mf-r-label {{ font-size:0.7rem; text-transform:uppercase; letter-spacing:.07em; color:{TEXT_HINT}; margin-bottom:4px; }}
.mf-r-amount {{
    font-size:2.2rem; font-weight:700; color:{ACCENT};
    letter-spacing:-.03em; line-height:1;
}}
.mf-r-cur {{ font-size:1rem; color:{TEXT_SEC}; font-weight:400; margin-left:4px; }}
.mf-r-right {{ text-align:right; }}
.mf-r-fee-label {{ font-size:0.7rem; color:{TEXT_HINT}; text-transform:uppercase; letter-spacing:.06em; margin-bottom:3px; }}
.mf-r-fee-val {{ font-size:1.1rem; font-weight:600; color:{TEXT_SEC}; }}

/* Tables */
.mf-tw {{ border:1px solid {BORDER}; border-radius:12px; overflow:hidden; margin:10px 0; }}
.mf-t  {{ width:100%; border-collapse:collapse; font-family:{FONT}; font-size:0.87rem; background:{BG_CARD2}; }}
.mf-t thead tr  {{ background:{BG_INPUT}; }}
.mf-t thead th  {{
    padding:11px 16px; text-align:left;
    font-size:0.68rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.08em; color:{TEXT_HINT}; border-bottom:1px solid {BORDER};
}}
.mf-t tbody tr  {{ border-bottom:1px solid {BORDER}; transition:background .15s; }}
.mf-t tbody tr:last-child {{ border-bottom:none; }}
.mf-t tbody tr:hover  {{ background:#1e293b; }}
.mf-t tbody tr.best-row {{ background:#022c22 !important; }}
.mf-t tbody td  {{ padding:12px 16px; color:{TEXT_PRI}; background:transparent; }}
.mf-t td.green  {{ color:{ACCENT};  font-weight:600; }}
.mf-t td.blue   {{ color:{ACCENT2}; font-weight:500; }}
.mf-t td.muted  {{ color:{TEXT_SEC}; font-size:0.82rem; }}
.mf-t td.best   {{ color:{ACCENT}; font-weight:700; }}
.mf-t td.best::before {{ content:"▲ "; font-size:.65rem; opacity:.7; }}

/* Footer */
.mf-foot {{
    margin-top:40px; padding-top:22px; border-top:1px solid {BORDER};
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;
}}
.mf-foot-txt {{ font-size:0.75rem; color:{TEXT_HINT}; line-height:1.7; }}
.mf-foot-link {{
    display:inline-flex; align-items:center; gap:6px;
    background:{BG_INPUT}; border:1px solid {BORDER2};
    border-radius:8px; padding:7px 16px;
    font-size:0.82rem; color:{TEXT_SEC}; text-decoration:none;
}}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def mf_sec(num, title):
    st.markdown(f"""
    <div class="mf-sec">
      <span class="mf-sec-n">{num}</span>
      <span class="mf-sec-t">{title}</span>
    </div>""", unsafe_allow_html=True)


def mf_table(rows, best_key="", green_col="", blue_col="", muted_col=""):
    if not rows:
        return
    headers = list(rows[0].keys())
    best_idx = -1
    if best_key:
        try:
            vals = [float(str(r.get(best_key, "0"))
                    .replace(",", "").replace("$", "")) for r in rows]
            best_idx = vals.index(max(vals))
        except Exception:
            pass
    ths  = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for i, row in enumerate(rows):
        row_cls = " class='best-row'" if i == best_idx else ""
        cells = []
        for h in headers:
            v   = row.get(h, "")
            cls = ""
            if   i == best_idx and h == best_key: cls = " class='best'"
            elif h == green_col:                  cls = " class='green'"
            elif h == blue_col:                   cls = " class='blue'"
            elif h == muted_col:                  cls = " class='muted'"
            cells.append(f"<td{cls}>{v}</td>")
        body.append(f"<tr{row_cls}>{''.join(cells)}</tr>")
    st.markdown(f"""
    <div class="mf-tw"><table class="mf-t">
      <thead><tr>{ths}</tr></thead>
      <tbody>{''.join(body)}</tbody>
    </table></div>""", unsafe_allow_html=True)


def mf_chart(fig):
    fig.update_layout(**PLOTLY_BASE)
    st.plotly_chart(fig, use_container_width=True)


# ── Data ───────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("🔐 Set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")
    st.stop()

@st.cache_data(ttl=300)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    res = (supabase.table("exchange_rates")
                   .select("*")
                   .order("fetched_at", desc=False)
                   .execute())
    df = pd.DataFrame(res.data)
    if not df.empty:
        df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    return df

df = load_data()
if df.empty:
    st.warning("⏳ Pipeline warming up — data will appear shortly.")
    st.stop()

latest         = df.groupby(["base_currency", "target_currency"]).last().reset_index()
seven_days_ago = datetime.now() - timedelta(days=7)
df_recent      = df[df["fetched_at"] >= seven_days_ago]

def get_rate(base, tgt):
    v = latest[(latest["base_currency"] == base) &
               (latest["target_currency"] == tgt)]["rate"].values
    return float(v[0]) if len(v) else None

PAIR_MAP = {
    "USD → KES": ("USD", "KES"),
    "USD → NGN": ("USD", "NGN"),
    "GBP → KES": ("GBP", "KES"),
    "EUR → KES": ("EUR", "KES"),
}


# ══════════════════════════════════════════════════════════════════════════════
# TOPBAR
# ══════════════════════════════════════════════════════════════════════════════
last_ts   = df["fetched_at"].max()
is_stale  = (datetime.now() - last_ts.replace(tzinfo=None)).total_seconds() > 7200
live_cls  = "mf-live mf-stale" if is_stale else "mf-live"
live_text = "STALE" if is_stale else "LIVE"

st.markdown(f"""
<div class="mf-topbar">
  <div class="mf-logo">🌍 Remit<span>Track</span></div>
  <div class="mf-right">
    <span class="{live_cls}">
      <span class="mf-live-dot"></span>{live_text}
    </span>
    <span class="mf-ts">Updated {last_ts.strftime("%-d %b, %H:%M UTC")}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HERO METRICS
# ══════════════════════════════════════════════════════════════════════════════
cols = st.columns(4)
HERO = [
    ("🇺🇸 USD → 🇰🇪 KES", "USD", "KES"),
    ("🇬🇧 GBP → 🇰🇪 KES", "GBP", "KES"),
    ("🇪🇺 EUR → 🇰🇪 KES", "EUR", "KES"),
    ("🇺🇸 USD → 🇳🇬 NGN", "USD", "NGN"),
]
for col, (lbl, base, tgt) in zip(cols, HERO):
    rate = get_rate(base, tgt)
    if rate:
        hist = df[(df["base_currency"] == base) & (df["target_currency"] == tgt) &
                  (df["fetched_at"] >= datetime.now() - timedelta(hours=24))]
        delta = None
        if len(hist) >= 2:
            chg   = ((rate - hist.iloc[0]["rate"]) / hist.iloc[0]["rate"]) * 100
            delta = f"{chg:+.2f}% (24 h)"
        col.metric(lbl, f"{rate:,.2f}", delta=delta)

st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 01 · CURRENCY CONVERTER
# ══════════════════════════════════════════════════════════════════════════════
mf_sec("01", "Currency Converter")
ca, cb, cc = st.columns([1.6, 1, 1])
with ca: amount  = st.number_input("Amount", min_value=1, value=100, step=10)
with cb: from_c  = st.selectbox("From", ["USD", "GBP", "EUR"])
with cc: to_c    = st.selectbox("To", ["KES", "NGN", "GHS", "ZAR", "UGX", "TZS"])

cr = get_rate(from_c, to_c)
if cr:
    converted = amount * cr
    fee_pct   = st.slider("Provider fee estimate (%)", 0.0, 5.0, 2.0, 0.5)
    after_fee = (amount * (1 - fee_pct / 100)) * cr
    fee_usd   = amount * fee_pct / 100
    st.markdown(f"""
    <div class="mf-result">
      <div>
        <div class="mf-r-label">Mid-market · {from_c} → {to_c}</div>
        <div class="mf-r-amount">{converted:,.2f}<span class="mf-r-cur">{to_c}</span></div>
      </div>
      <div class="mf-r-right">
        <div class="mf-r-fee-label">After {fee_pct:.1f}% fee (≈ {from_c} {fee_usd:.2f})</div>
        <div class="mf-r-fee-val">{after_fee:,.2f} {to_c}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Mid-market reference only. Your provider's actual rate includes a spread.")
else:
    st.warning(f"No rate data for {from_c} → {to_c}")


# ══════════════════════════════════════════════════════════════════════════════
# 02 · BEST TIME TO SEND
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
mf_sec("02", "Best Time to Send")

pair2 = st.selectbox("Currency pair", list(PAIR_MAP.keys()), key="p2")
b2, t2 = PAIR_MAP[pair2]
pd2 = df[(df["base_currency"] == b2) & (df["target_currency"] == t2) &
         (df["fetched_at"] >= seven_days_ago)]

if not pd2.empty:
    cur2  = pd2.iloc[-1]["rate"]
    best2 = pd2["rate"].max()
    avg2  = pd2["rate"].mean()
    low2  = pd2["rate"].min()

    mc = st.columns(4)
    mc[0].metric("Current",    f"{cur2:.2f}")
    mc[1].metric("7-Day High", f"{best2:.2f}")
    mc[2].metric("7-Day Avg",  f"{avg2:.2f}")
    mc[3].metric("7-Day Low",  f"{low2:.2f}")

    gap2 = ((best2 - cur2) / cur2) * 100
    if cur2 >= best2 * 0.99:
        st.success("✦ Great time to send — within 1% of the 7-day high.")
    elif cur2 <= best2 * 0.95:
        st.info(f"◌ Consider waiting — {gap2:.1f}% below the 7-day high.")
    else:
        st.warning(f"◈ Moderate — {gap2:.1f}% below this week's best rate.")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=pd2["fetched_at"], y=pd2["rate"], mode="lines", name="Rate",
        line=dict(color=ACCENT2, width=2),
        fill="tozeroy", fillcolor="rgba(56,189,248,0.06)"
    ))
    fig2.add_hline(y=best2, line_dash="dot", line_color=ACCENT,
                   annotation_text="7-day high",
                   annotation_font=dict(color=ACCENT, size=11))
    fig2.add_hline(y=avg2, line_dash="dot", line_color=TEXT_HINT,
                   annotation_text="avg",
                   annotation_font=dict(color=TEXT_HINT, size=11))
    fig2.update_layout(title=f"{b2} → {t2}  ·  Last 7 days", showlegend=False)
    mf_chart(fig2)
else:
    st.warning("Not enough historical data for this pair yet.")


# ══════════════════════════════════════════════════════════════════════════════
# 03 · SEND MONEY COST CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
mf_sec("03", "Send Money Cost Calculator")

cs1, cs2 = st.columns([2, 1])
with cs1: send_amt = st.number_input("Amount to send (USD)", min_value=10, value=500, step=50)
with cs2: dest_c   = st.selectbox("Destination", ["KES", "NGN", "GHS", "ZAR", "UGX", "TZS"])

dr3 = get_rate("USD", dest_c)
SERVICES = {
    "Sendwave / M-Pesa": 1.0,
    "WorldRemit":        2.0,
    "Bank Transfer":     3.0,
    "Western Union":     4.0,
    "PayPal":            4.5,
}
if dr3:
    rows3 = []
    for svc, fp in SERVICES.items():
        fee = send_amt * fp / 100
        rcv = (send_amt - fee) * dr3
        rows3.append({
            "Service":              svc,
            "Fee":                  f"{fp}%",
            "Fee (USD)":            f"${fee:.2f}",
            f"Received ({dest_c})": f"{rcv:,.0f}",
        })
    rcv_col = f"Received ({dest_c})"
    best3 = min(rows3, key=lambda r: float(r["Fee (USD)"].replace("$", "")))
    st.success(f"▲ Lowest fees via {best3['Service']} → {best3[rcv_col]} {dest_c} received")

    clrs = [ACCENT if r["Service"] == best3["Service"] else ACCENT_DIM for r in rows3]
    fig3 = go.Figure(go.Bar(
        x=[r["Service"] for r in rows3],
        y=[float(r[rcv_col].replace(",", "")) for r in rows3],
        marker_color=clrs, marker_line_width=0,
        text=[r[rcv_col] for r in rows3],
        textposition="outside", textfont=dict(color=TEXT_SEC, size=11),
    ))
    fig3.update_layout(title=f"${send_amt} USD → {dest_c} by provider",
                       xaxis_title="", yaxis_title=f"{dest_c} received",
                       showlegend=False)
    mf_chart(fig3)
else:
    st.warning(f"USD → {dest_c} rate not available.")


# ══════════════════════════════════════════════════════════════════════════════
# 04 · RATE ALERT CHECKER
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
mf_sec("04", "Rate Alert Checker")

ar1, ar2 = st.columns(2)
with ar1: apair = st.selectbox("Currency pair", list(PAIR_MAP.keys()), key="p4")
ab4, at4 = PAIR_MAP[apair]
cur4 = get_rate(ab4, at4)

if cur4:
    with ar2:
        tgt4 = st.number_input("Your target rate", min_value=0.01,
                               value=round(cur4 + 2, 2), step=0.5)
    am1, am2, am3 = st.columns(3)
    am1.metric("Current Rate", f"{cur4:.2f}")
    am2.metric("Your Target",  f"{tgt4:.2f}")
    ah4 = df[(df["base_currency"] == ab4) & (df["target_currency"] == at4)]
    mx4 = ah4["rate"].max() if not ah4.empty else cur4
    am3.metric("All-Time High", f"{mx4:.2f}")

    if tgt4 <= cur4:
        st.success(f"✦ Target reached — {cur4:.2f} meets your target of {tgt4:.2f}")
    else:
        g4 = ((tgt4 - cur4) / cur4) * 100
        st.info(f"◌ Need +{g4:.1f}% ({tgt4 - cur4:.2f} pts) to reach {tgt4:.2f}")
    if not ah4.empty:
        st.caption("✦ Target previously reached in history." if mx4 >= tgt4
                   else f"Historical high so far: {mx4:.2f}")
else:
    st.warning("Rate data unavailable.")


# ══════════════════════════════════════════════════════════════════════════════
# 05 · MULTI-CURRENCY SOURCE COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
mf_sec("05", "Best Sending Country Comparison")

cv1, cv2 = st.columns([1.5, 1])
with cv1: cmp_amt  = st.number_input("USD equivalent", min_value=10, value=100, step=10)
with cv2: cmp_dest = st.selectbox("Destination", ["KES", "NGN", "GHS", "ZAR"], key="p5")

SOURCES = {
    "🇺🇸 USA (USD)": ("USD", None),
    "🇬🇧 UK  (GBP)": ("GBP", "USD"),
    "🇪🇺 EU  (EUR)": ("EUR", "USD"),
}
crows = []
for lbl, (src, pivot) in SOURCES.items():
    dr5 = get_rate(src, cmp_dest)
    if not dr5:
        continue
    sa  = cmp_amt * get_rate("USD", src) if pivot and get_rate("USD", src) else cmp_amt
    rcv = sa * dr5
    crows.append({"label": lbl, "rcv": rcv})

if crows:
    best_rcv = max(crows, key=lambda r: r["rcv"])
    mc5 = st.columns(len(crows))
    for col, row in zip(mc5, crows):
        is_best = row["rcv"] == best_rcv["rcv"]
        delta   = "▲ Best value" if is_best else None
        col.metric(row["label"], f"{row['rcv']:,.0f} {cmp_dest}", delta=delta)
    st.success(f"▲ Best value from {best_rcv['label']} — most {cmp_dest} per USD equivalent")
else:
    st.warning("Comparison data unavailable.")


# ══════════════════════════════════════════════════════════════════════════════
# 06 · EXCHANGE RATE TRENDS
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
mf_sec("06", "Exchange Rate Trends")

pair6 = st.selectbox("Currency pair", list(PAIR_MAP.keys()), key="p6")
b6, t6 = PAIR_MAP[pair6]
cd6 = df_recent[(df_recent["base_currency"] == b6) & (df_recent["target_currency"] == t6)]

if not cd6.empty:
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=cd6["fetched_at"], y=cd6["rate"], mode="lines", name="Rate",
        line=dict(color=ACCENT, width=2.5),
        fill="tozeroy", fillcolor="rgba(110,231,183,0.06)"
    ))
    xs = np.arange(len(cd6))
    if len(xs) > 2:
        m, c = np.polyfit(xs, cd6["rate"].values, 1)
        fig6.add_trace(go.Scatter(
            x=cd6["fetched_at"], y=m * xs + c, mode="lines", name="Trend",
            line=dict(color=TEXT_HINT, width=1.5, dash="dot")
        ))
    fig6.update_layout(
        title=f"{b6} → {t6}  ·  Last 7 days with trend", showlegend=True,
        legend=dict(font=dict(color=TEXT_SEC, size=11), bgcolor="rgba(0,0,0,0)")
    )
    mf_chart(fig6)
else:
    st.warning("Not enough data for this pair in the last 7 days.")


# ══════════════════════════════════════════════════════════════════════════════
# 07 · RECENT RATES LOG  (collapsed — for power users / pipeline debugging)
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("🔬 Raw data log — last 20 records", expanded=False):
    recent = (df.tail(20)[["base_currency", "target_currency", "rate", "fetched_at"]]
                .sort_values("fetched_at", ascending=False).copy())
    recent["fetched_at"] = recent["fetched_at"].dt.strftime("%d %b  %H:%M")
    recent["rate"]       = recent["rate"].apply(lambda x: f"{x:,.4f}")
    recent.columns       = ["From", "To", "Rate", "Fetched At"]
    mf_table(recent.to_dict("records"), green_col="Rate", blue_col="From",
             muted_col="Fetched At")
    st.caption("Pipeline refreshes every hour via GitHub Actions")


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE STATS + FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
mf_sec("●", "Pipeline Status")

pf1, pf2, pf3 = st.columns(3)
pf1.metric("Update Cadence",   "Hourly",           delta="GitHub Actions")
pf2.metric("Total Datapoints", f"{len(df):,}",      delta="Growing")
pf3.metric("Data Source",      "ExchangeRate API",  delta="Mid-market rates")

st.markdown(f"""
<div class="mf-foot">
  <div class="mf-foot-txt">
    Rates shown are mid-market reference values only.<br>
    Always verify your provider's actual rate before sending money.
  </div>
  <a class="mf-foot-link"
     href="https://github.com/petermusila/global-remittance-tracker"
     target="_blank">↗ View source on GitHub</a>
</div>
""", unsafe_allow_html=True)
