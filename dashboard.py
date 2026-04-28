import streamlit as st
import pandas as pd
import os
from supabase import create_client
import plotly.express as px
from datetime import datetime, timedelta

# Page config - MUST be first
st.set_page_config(
    page_title="Global Remittance Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3a 100%);
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* All text white */
    .stMarkdown, .stText, .stCaption, .stSubheader, .stHeader,
    p, span, div, label, .stSelectbox label, .stNumberInput label {
        color: #ffffff !important;
    }
    h1, h2, h3, h4, h5 { color: #ffffff !important; }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #1e1e3a !important;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #334155;
    }
    div[data-testid="stMetricValue"] {
        color: #00ff88 !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetricLabel"] { color: #ffffff !important; }
    div[data-testid="stMetricDelta"] svg { display: none !important; }
    div[data-testid="stMetricDelta"] > div { color: #7a8499 !important; font-size: 0.75rem !important; }

    /* ── HTML tables (replacing st.dataframe) ── */
    .rt-table-wrap {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #2a2a4a;
        margin-bottom: 12px;
    }
    .rt-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #1a1a2e;
        font-size: 0.9rem;
    }
    .rt-table thead tr { background-color: #2a2a4a; }
    .rt-table thead th {
        color: #ffffff !important;
        font-weight: bold !important;
        padding: 10px 14px !important;
        border-bottom: 1px solid #3a3a5a !important;
        text-align: left;
    }
    .rt-table tbody tr {
        border-bottom: 1px solid #2a2a4a;
        transition: background 0.15s;
    }
    .rt-table tbody tr:last-child { border-bottom: none; }
    .rt-table tbody tr:hover { background-color: #2a2a4a !important; }
    .rt-table tbody td {
        color: #ffffff !important;
        padding: 9px 14px !important;
        background: transparent !important;
    }
    .rt-table tbody tr.best-row { background-color: #0a2e1a !important; }
    .rt-table tbody td.highlight { color: #00ff88 !important; font-weight: 600; }

    /* Alert boxes */
    .stAlert { background-color: #1e1e3a !important; border-radius: 10px; }
    .stAlert p { color: #ffffff !important; }
    .stSuccess { background-color: #0a2e1a !important; border-left: 4px solid #00ff88 !important; }
    .stInfo    { background-color: #0a1a3e !important; border-left: 4px solid #3388ff !important; }
    .stWarning { background-color: #3e2e0a !important; border-left: 4px solid #ffaa00 !important; }

    /* Inputs */
    .stSelectbox > div > div {
        background-color: #2a2a4a !important;
        border: 1px solid #4a4a6a !important;
        border-radius: 8px !important;
    }
    .stSelectbox label, .stNumberInput label { color: #ffffff !important; }
    select, input, .stNumberInput input {
        background-color: #2a2a4a !important;
        color: #ffffff !important;
        border: 1px solid #4a4a6a !important;
        border-radius: 8px !important;
    }

    /* Misc */
    hr { border-color: #334155 !important; margin: 20px 0 !important; }
    .stRadio > div { background-color: transparent !important; }
    .stRadio label, .stSlider label { color: #ffffff !important; }
    .stCaption, caption { color: #a0a0c0 !important; }
    .stButton button {
        background-color: #4a4a6a !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    .stButton button:hover { background-color: #5a5a7a !important; }
    .stPlotlyChart { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Credentials ────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Database credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")
    st.stop()

# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table("exchange_rates").select("*").order("fetched_at", desc=False).execute()
    df = pd.DataFrame(response.data)
    if not df.empty:
        df['fetched_at'] = pd.to_datetime(df['fetched_at'])
    return df

df = load_data()

# ── HTML table helper (fixes dark background issue with st.dataframe) ──────────
def render_table(rows: list, highlight_col: str = "", best_key: str = ""):
    """Render a list of dicts as a dark-themed HTML table."""
    if not rows:
        return
    headers = list(rows[0].keys())

    # Find best row index
    best_idx = -1
    if best_key:
        try:
            vals = [float(str(r.get(best_key, "0"))
                    .replace(",", "").replace("$", "")) for r in rows]
            best_idx = vals.index(max(vals))
        except Exception:
            pass

    ths   = "".join(f"<th>{h}</th>" for h in headers)
    tbody = []
    for i, row in enumerate(rows):
        row_cls = " class='best-row'" if i == best_idx else ""
        cells = []
        for h in headers:
            v   = row.get(h, "")
            cls = " class='highlight'" if (i == best_idx and h == highlight_col) else ""
            cells.append(f"<td{cls}>{v}</td>")
        tbody.append(f"<tr{row_cls}>{''.join(cells)}</tr>")

    st.markdown(f"""
    <div class="rt-table-wrap">
      <table class="rt-table">
        <thead><tr>{ths}</tr></thead>
        <tbody>{''.join(tbody)}</tbody>
      </table>
    </div>""", unsafe_allow_html=True)


# ── Plotly dark theme helper ───────────────────────────────────────────────────
def dark_chart(fig, height=350):
    fig.update_layout(
        height=height,
        xaxis_title="Time",
        yaxis_title="Rate",
        template="plotly_dark",
        plot_bgcolor="#1a1a2e",
        paper_bgcolor="#1a1a2e",
        font=dict(color="white"),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
if not df.empty:
    latest = df.groupby(['base_currency', 'target_currency']).last().reset_index()

    # ── Header ────────────────────────────────────────────────────────────────
    st.title("🌍 Global Remittance Tracker")
    st.markdown("**Live exchange rates for money transfers from USA, UK, and Europe to Africa**")
    st.caption("📊 Using mid-market rates. Actual transfer rates may include fees from your provider.")

    # ── Top metrics ───────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    HERO_PAIRS = [
        (col1, "🇺🇸 USD → 🇰🇪 KES", "USD", "KES"),
        (col2, "🇬🇧 GBP → 🇰🇪 KES", "GBP", "KES"),
        (col3, "🇪🇺 EUR → 🇰🇪 KES", "EUR", "KES"),
        (col4, "🇺🇸 USD → 🇳🇬 NGN", "USD", "NGN"),
    ]
    for col, label, base, tgt in HERO_PAIRS:
        vals = latest[(latest['base_currency'] == base) &
                      (latest['target_currency'] == tgt)]['rate'].values
        if len(vals):
            rate = vals[0]
            # 24 h delta
            yest = datetime.now() - timedelta(hours=24)
            hist = df[(df['base_currency'] == base) & (df['target_currency'] == tgt) &
                      (df['fetched_at'] >= yest)]
            delta = None
            if len(hist) >= 2:
                chg   = ((rate - hist.iloc[0]['rate']) / hist.iloc[0]['rate']) * 100
                delta = f"{chg:+.2f}% (24 h)"
            col.metric(label, f"{rate:.2f}", delta=delta)

    st.divider()

    # ── Feature 1: Currency Converter ─────────────────────────────────────────
    st.subheader("💸 Currency Converter")
    st.caption("💡 Mid-market rate shown. Your provider may add fees.")

    col_a, col_b, col_c = st.columns(3)
    with col_a: amount        = st.number_input("Amount to send", min_value=1, value=100, step=10)
    with col_b: from_currency = st.selectbox("From", ["USD", "GBP", "EUR"])
    with col_c: to_currency   = st.selectbox("To",   ["KES", "NGN", "GHS", "ZAR", "UGX", "TZS"])

    converter_rate = latest[(latest['base_currency'] == from_currency) &
                            (latest['target_currency'] == to_currency)]['rate'].values

    if len(converter_rate) > 0:
        converted_amount = amount * converter_rate[0]
        st.success(f"💰 {amount} {from_currency} = **{converted_amount:,.2f} {to_currency}**")

        fee_percent    = st.slider("Estimated fee (%)", min_value=0.0, max_value=5.0, value=2.0, step=0.5)
        fee            = amount * (fee_percent / 100)
        recipient_gets = converted_amount - (fee * converter_rate[0])
        st.caption(f"After {fee_percent}% fee: ~{recipient_gets:,.2f} {to_currency}")
    else:
        st.warning(f"No data available for {from_currency} to {to_currency}")

    st.divider()

    # ── Feature 2: Best Time Alert ────────────────────────────────────────────
    st.subheader("📊 Best Time Alert")

    alert_pair = st.selectbox("Select currency pair", ["USD to KES", "USD to NGN", "GBP to KES", "EUR to KES"])
    alert_map  = {
        "USD to KES": ("USD", "KES"),
        "USD to NGN": ("USD", "NGN"),
        "GBP to KES": ("GBP", "KES"),
        "EUR to KES": ("EUR", "KES"),
    }
    base, target      = alert_map[alert_pair]
    seven_days_ago    = datetime.now() - timedelta(days=7)
    pair_data         = df[(df['base_currency'] == base) & (df['target_currency'] == target) &
                           (df['fetched_at'] >= seven_days_ago)]

    if not pair_data.empty:
        current_rate = pair_data.iloc[-1]['rate']
        best_rate    = pair_data['rate'].max()
        avg_rate     = pair_data['rate'].mean()

        col_alert1, col_alert2, col_alert3 = st.columns(3)
        col_alert1.metric("Current Rate",      f"{current_rate:.2f}")
        col_alert2.metric("Best Rate (7 days)", f"{best_rate:.2f}")
        col_alert3.metric("Average Rate",       f"{avg_rate:.2f}")

        improvement_needed = ((best_rate - current_rate) / current_rate) * 100
        if current_rate >= best_rate * 0.99:
            st.success("✅ **Great time to send!** Rate is within 1% of the 7-day high.")
        elif current_rate <= best_rate * 0.95:
            st.info(f"⏳ **Consider waiting.** Rate is {improvement_needed:.1f}% below the 7-day high.")
        else:
            st.warning(f"📊 **Moderate rate.** {improvement_needed:.1f}% below best rate this week.")

        fig_small = px.line(pair_data, x='fetched_at', y='rate',
                            title=f"{base} to {target} — Last 7 Days")
        dark_chart(fig_small, height=300)
    else:
        st.warning("Not enough historical data for this pair yet.")

    st.divider()

    # ── Feature 3: Send Money Cost Calculator ────────────────────────────────
    st.subheader("🏦 Send Money Cost Calculator")

    send_amount = st.number_input("Amount to send (USD)", min_value=10, value=500, step=50, key="send_calc")

    services = {
        "M-Pesa (Sendwave)": 1.5,
        "WorldRemit":        2.0,
        "Bank Transfer":     3.0,
        "Western Union":     4.0,
        "PayPal":            4.5,
    }

    usd_kes_current = latest[(latest['base_currency'] == 'USD') &
                              (latest['target_currency'] == 'KES')]['rate'].values
    if len(usd_kes_current) > 0:
        rate    = usd_kes_current[0]
        results = []
        for service, fee_percent in services.items():
            fee_amount    = send_amount * (fee_percent / 100)
            recipient_kes = (send_amount - fee_amount) * rate
            results.append({
                "Service":              service,
                "Fee (%)":              f"{fee_percent}%",
                "Fee (USD)":            f"${fee_amount:.2f}",
                "Recipient Gets (KES)": f"{recipient_kes:,.0f}",
            })

        best = min(results, key=lambda x: float(x["Fee (USD)"].replace("$", "")))
        render_table(results, highlight_col="Recipient Gets (KES)", best_key="Recipient Gets (KES)")
        st.success(f"💰 **Best option:** {best['Service']} → {best['Recipient Gets (KES)']} KES")
    else:
        st.warning("USD to KES rate not available")

    st.divider()

    # ── Feature 4: Rate Alert ─────────────────────────────────────────────────
    st.subheader("🔔 Rate Alert")
    st.markdown("Set your target rate and see if it's been reached")

    target_pair = st.selectbox("Select currency pair for alert",
                               ["USD to KES", "USD to NGN", "GBP to KES", "EUR to KES"],
                               key="alert_pair")
    target_map = {
        "USD to KES": ("USD", "KES"),
        "USD to NGN": ("USD", "NGN"),
        "GBP to KES": ("GBP", "KES"),
        "EUR to KES": ("EUR", "KES"),
    }
    target_base, target_targ = target_map[target_pair]
    current_target_rate = latest[(latest['base_currency'] == target_base) &
                                  (latest['target_currency'] == target_targ)]['rate'].values

    if len(current_target_rate) > 0:
        current_val = current_target_rate[0]
        target_rate = st.number_input("Your target rate", min_value=0.0,
                                      value=float(current_val) + 2.0, step=0.5)

        col_alert_a, col_alert_b = st.columns(2)
        col_alert_a.metric("Current Rate", f"{current_val:.2f}")
        col_alert_b.metric("Your Target",  f"{target_rate:.2f}")

        if target_rate <= current_val:
            st.success(f"🎯 **TARGET REACHED!** Current rate ({current_val:.2f}) meets your target ({target_rate:.2f})")
        else:
            difference = ((target_rate - current_val) / current_val) * 100
            st.info(f"⏳ Target not reached yet. Need {difference:.1f}% increase to reach {target_rate:.2f}")

        pair_history = df[(df['base_currency'] == target_base) & (df['target_currency'] == target_targ)]
        if not pair_history.empty:
            max_rate = pair_history['rate'].max()
            if max_rate >= target_rate:
                st.caption(f"📈 Target rate of {target_rate} was reached (max: {max_rate:.2f})")
            else:
                st.caption(f"📉 Target rate not yet reached (max so far: {max_rate:.2f})")
    else:
        st.warning("Rate data not available")

    st.divider()

    # ── Feature 5: Multi-Currency Comparison ─────────────────────────────────
    st.subheader("🌍 Multi-Currency Comparison")
    st.markdown("Best place to send $100 to Kenya")

    compare_amount     = 100
    compare_currencies = {
        "🇺🇸 USA (USD)":    ("USD", "KES"),
        "🇬🇧 UK (GBP)":     ("GBP", "KES"),
        "🇪🇺 Europe (EUR)": ("EUR", "KES"),
    }
    compare_results = []
    for label, (base_curr, target_curr) in compare_currencies.items():
        rate_val = latest[(latest['base_currency'] == base_curr) &
                          (latest['target_currency'] == target_curr)]['rate'].values
        if not len(rate_val):
            continue
        if base_curr == "USD":
            converted = compare_amount * rate_val[0]
        elif base_curr == "GBP":
            u2g = latest[(latest['base_currency'] == 'USD') &
                         (latest['target_currency'] == 'GBP')]['rate'].values
            converted = (compare_amount / u2g[0]) * rate_val[0] if len(u2g) else compare_amount * rate_val[0] * 1.25
        elif base_curr == "EUR":
            u2e = latest[(latest['base_currency'] == 'USD') &
                         (latest['target_currency'] == 'EUR')]['rate'].values
            converted = (compare_amount / u2e[0]) * rate_val[0] if len(u2e) else compare_amount * rate_val[0] * 1.08
        else:
            converted = compare_amount * rate_val[0]
        compare_results.append({"From": label, "Recipient Gets (KES)": f"{converted:,.0f}"})

    if compare_results:
        render_table(compare_results, highlight_col="Recipient Gets (KES)",
                     best_key="Recipient Gets (KES)")
        best_val   = max(float(r["Recipient Gets (KES)"].replace(",", "")) for r in compare_results)
        best_label = next(r["From"] for r in compare_results
                          if float(r["Recipient Gets (KES)"].replace(",", "")) == best_val)
        st.success(f"🏆 **Best option:** Send from {best_label} → {best_val:,.0f} KES")
    else:
        st.warning("Comparison data not available")

    st.divider()

    # ── Historical Chart ──────────────────────────────────────────────────────
    st.subheader("📈 Exchange Rate Trends (Last 7 Days)")

    df_recent  = df[df['fetched_at'] >= seven_days_ago]
    chart_pair = st.selectbox("Select currency pair for chart",
                              ["USD to KES", "USD to NGN", "GBP to KES", "EUR to KES"],
                              key="chart_pair")
    chart_map = {
        "USD to KES": ("USD", "KES"),
        "USD to NGN": ("USD", "NGN"),
        "GBP to KES": ("GBP", "KES"),
        "EUR to KES": ("EUR", "KES"),
    }
    chart_base, chart_target = chart_map[chart_pair]
    chart_data = df_recent[(df_recent['base_currency'] == chart_base) &
                            (df_recent['target_currency'] == chart_target)]

    if not chart_data.empty:
        fig = px.line(chart_data, x='fetched_at', y='rate',
                      title=f'{chart_base} to {chart_target} — Last 7 Days')
        dark_chart(fig, height=380)

    # ── Recent Rates table ────────────────────────────────────────────────────
    st.subheader("📋 Recent Rates")
    recent = (df.tail(10)[['base_currency', 'target_currency', 'rate', 'fetched_at']]
                .sort_values('fetched_at', ascending=False)
                .copy())
    recent['fetched_at'] = recent['fetched_at'].dt.strftime("%d %b  %H:%M")
    recent['rate']       = recent['rate'].apply(lambda x: f"{x:,.4f}")
    recent.columns       = ['From', 'To', 'Rate', 'Time']
    render_table(recent.to_dict("records"))

    st.caption(f"📡 Last updated: {df['fetched_at'].max().strftime('%d %b %Y %H:%M UTC')} | Data refreshes every hour")

    # ── Social Proof ──────────────────────────────────────────────────────────
    st.divider()
    st.subheader("⚡ Why Trust This Data?")

    col_proof1, col_proof2, col_proof3 = st.columns(3)
    col_proof1.metric("🕐 Update Frequency", "Every Hour",       delta="Automated")
    col_proof2.metric("📊 Data Points",      f"{len(df):,}",     delta="And growing")
    col_proof3.metric("🔗 Data Source",      "ExchangeRate API", delta="Live")

    st.caption("📈 Data fetched automatically via GitHub Actions. No manual intervention. Fully open source.")

    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <a href="https://github.com/petermusila/global-remittance-tracker" target="_blank"
           style="text-decoration: none;">
            <button style="background:#2a2a4a; color:white; border:1px solid #4a4a6a;
                           padding:8px 16px; border-radius:8px; cursor:pointer;">
                📁 View Source Code on GitHub
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("No data yet. The automated fetcher will start collecting data soon.")
