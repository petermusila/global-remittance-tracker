import streamlit as st
import pandas as pd
import os
from supabase import create_client
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Global Remittance Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Reduce padding and spacing
st.markdown("""
<style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
    }
    hr {
        margin: 0.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for complete dark mode - all text visible
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #1a1a3e, #24243e);
    }
    
    /* Force all text to be white */
    .stApp, .main, .stMarkdown, .stText, .stCaption, .stSubheader, .stHeader,
    p, span, div, label, .stSelectbox label, .stNumberInput label,
    .stRadio label, .stRadio span, .stCheckbox label, .stTextInput label {
        color: #ffffff !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, .stTitle {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Metric cards - fix for "Current Rate", "Top Gainer", "Top Loser" */
    div[data-testid="stMetric"] {
        background-color: rgba(30,30,60,0.8) !important;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #444;
    }
    
    div[data-testid="stMetricValue"] {
        color: #00ff88 !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-size: 1rem !important;
    }
    
    div[data-testid="stMetricDelta"] {
        color: #ffaa00 !important;
    }
    
    /* Fix for dataframe/table - dark background */
    .stDataFrame, .stDataFrame table, .dataframe, table {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
    }
    
    .stDataFrame th, .dataframe th, table th {
        background-color: #2a2a4a !important;
        color: #ffffff !important;
        font-weight: bold !important;
        padding: 8px !important;
    }
    
    .stDataFrame td, .dataframe td, table td {
        background-color: #1a1a2e !important;
        color: #ffffff !important;
        padding: 8px !important;
    }
    
    /* Fix for any white backgrounds in tables */
    div[data-testid="stDataFrame"] div[data-testid="StyledTable"] {
        background-color: #1e1e2e !important;
    }
    
    /* Select boxes and inputs */
    .stSelectbox > div > div {
        background-color: #333 !important;
        color: white !important;
    }
    
    select, input, .stSelectbox select {
        background-color: #333 !important;
        color: white !important;
        border: 1px solid #555 !important;
    }
    
    /* Alert boxes */
    .stAlert {
        background-color: #1e1e2e !important;
        border-left: 4px solid #00ff88 !important;
        color: #ffffff !important;
    }
    
    .stAlert p, .stAlert div {
        color: #ffffff !important;
    }
    
    .stSuccess {
        background-color: #0a2e1a !important;
        border-left-color: #00ff88 !important;
    }
    
    .stInfo {
        background-color: #0a1a3e !important;
        border-left-color: #3388ff !important;
    }
    
    .stWarning {
        background-color: #3e2e0a !important;
        border-left-color: #ffaa00 !important;
    }
    
    /* Divider */
    hr {
        border-color: #444 !important;
        margin: 15px 0 !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: transparent !important;
    }
    
    .stRadio label {
        color: #ffffff !important;
    }
    
    /* Number input */
    .stNumberInput input {
        background-color: #333 !important;
        color: white !important;
    }
    
    /* Caption */
    .stCaption, caption {
        color: #aaa !important;
    }
    
    /* Fix for any remaining white elements */
    .css-1y4p8pa, .css-1v3fvcr, .css-16idsys {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Read from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Database credentials not configured.")
    st.stop()

@st.cache_data(ttl=300)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table("exchange_rates").select("*").order("fetched_at", desc=False).execute()
    df = pd.DataFrame(response.data)
    if not df.empty:
        df['fetched_at'] = pd.to_datetime(df['fetched_at'])
    return df

# Load data
df = load_data()

if not df.empty:
    latest = df.groupby(['base_currency', 'target_currency']).last().reset_index()
    
    # Header
    st.title("🌍 Global Remittance Tracker")
    st.markdown("**Live exchange rates for money transfers from USA, UK, and Europe to Africa**")
    st.caption("📊 Using mid-market rates. Actual transfer rates may include fees from your provider.")
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    usd_kes = latest[(latest['base_currency']=='USD') & (latest['target_currency']=='KES')]['rate'].values
    if len(usd_kes) > 0:
        col1.metric("🇺🇸 USD → 🇰🇪 KES", f"{usd_kes[0]:.2f}", delta=None)
    
    gbp_kes = latest[(latest['base_currency']=='GBP') & (latest['target_currency']=='KES')]['rate'].values
    if len(gbp_kes) > 0:
        col2.metric("🇬🇧 GBP → 🇰🇪 KES", f"{gbp_kes[0]:.2f}", delta=None)
    
    eur_kes = latest[(latest['base_currency']=='EUR') & (latest['target_currency']=='KES')]['rate'].values
    if len(eur_kes) > 0:
        col3.metric("🇪🇺 EUR → 🇰🇪 KES", f"{eur_kes[0]:.2f}", delta=None)
    
    usd_ngn = latest[(latest['base_currency']=='USD') & (latest['target_currency']=='NGN')]['rate'].values
    if len(usd_ngn) > 0:
        col4.metric("🇺🇸 USD → 🇳🇬 NGN", f"{usd_ngn[0]:.2f}", delta=None)
    
    st.divider()
    
    # ============ TOP GAINERS / LOSERS SECTION ============
    st.subheader("📈 Top Movers (Last 24 Hours)")
    
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    df_24h = df[df['fetched_at'] >= twenty_four_hours_ago]
    
    movers = []
    for (base, target), group in df_24h.groupby(['base_currency', 'target_currency']):
        if len(group) >= 2:
            oldest = group.iloc[0]['rate']
            newest = group.iloc[-1]['rate']
            change = ((newest - oldest) / oldest) * 100
            movers.append({
                "Pair": f"{base}/{target}",
                "Current": newest,
                "24h Change %": round(change, 2),
                "Trend": "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            })
    
    if movers:
        movers_df = pd.DataFrame(movers)
        top_gainer = movers_df.loc[movers_df['24h Change %'].idxmax()]
        top_loser = movers_df.loc[movers_df['24h Change %'].idxmin()]
        
        gain_col, lose_col = st.columns(2)
        with gain_col:
            st.metric("🚀 Top Gainer", f"{top_gainer['Pair']}", f"+{top_gainer['24h Change %']}%")
        with lose_col:
            st.metric("📉 Top Loser", f"{top_loser['Pair']}", f"{top_loser['24h Change %']}%")
        
        st.dataframe(movers_df[['Pair', 'Current', '24h Change %']], use_container_width=True)
    else:
        st.info("More data needed for 24-hour trends. Check back soon.")
    
    st.divider()
    
    # ============ CURRENCY CONVERTER ============
    st.subheader("💸 Currency Converter")
    st.caption("💡 Mid-market rate shown. Your provider may add fees.")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        amount = st.number_input("Amount to send", min_value=1, value=100, step=10)
    
    with col_b:
        from_currency = st.selectbox("From", ["USD", "GBP", "EUR"])
    
    with col_c:
        to_currency = st.selectbox("To", ["KES", "NGN", "GHS", "ZAR", "UGX", "TZS"])
    
    converter_rate = latest[(latest['base_currency']==from_currency) & 
                              (latest['target_currency']==to_currency)]['rate'].values
    
    if len(converter_rate) > 0:
        converted_amount = amount * converter_rate[0]
        st.success(f"💰 {amount} {from_currency} = **{converted_amount:,.2f} {to_currency}**")
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; margin-top: 10px;">
            <p style="margin: 0; color: white;">✈️ <strong>Ready to send?</strong> Compare rates at:</p>
            <a href="https://wise.com/us/currency-converter/{from_currency}-to-{to_currency}-rate?sourceAmount={amount}" target="_blank">
                <button style="background: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 5px; margin-top: 5px; cursor: pointer;">
                    💸 Send with Wise →
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"No data available for {from_currency} to {to_currency}")
    
    st.divider()
    
    # ============ BEST TIME ALERT ============
    st.subheader("📊 Best Time to Send")
    
    alert_pair = st.selectbox("Select currency pair", ["USD to KES", "USD to NGN", "GBP to KES", "EUR to KES"])
    alert_map = {
        "USD to KES": ("USD", "KES"),
        "USD to NGN": ("USD", "NGN"),
        "GBP to KES": ("GBP", "KES"),
        "EUR to KES": ("EUR", "KES")
    }
    base, target = alert_map[alert_pair]
    
    seven_days_ago = datetime.now() - timedelta(days=7)
    pair_data = df[(df['base_currency']==base) & (df['target_currency']==target) & (df['fetched_at'] >= seven_days_ago)]
    
    if not pair_data.empty:
        current_rate = pair_data.iloc[-1]['rate']
        best_rate = pair_data['rate'].max()
        
        if current_rate >= best_rate * 0.99:
            st.success(f"✅ **Great time to send!** Rate is within 1% of the 7-day high ({best_rate:.2f})")
        elif current_rate <= best_rate * 0.95:
            st.info(f"⏳ **Consider waiting.** Current rate is {((best_rate - current_rate)/current_rate)*100:.1f}% below the 7-day high")
        else:
            st.warning(f"📊 **Moderate rate.** {((best_rate - current_rate)/current_rate)*100:.1f}% below best rate this week")
    else:
        st.warning("Not enough data yet.")
    
    st.divider()
    
    # ============ RATE ALERTS (Target) ============
    st.subheader("🔔 Rate Alert")
    st.caption("Set your target rate. We'll show you when it's reached.")
    
    target_pair = st.selectbox("Select currency pair", ["USD to KES", "USD to NGN", "GBP to KES", "EUR to KES"], key="alert_pair2")
    target_map = {
        "USD to KES": ("USD", "KES"),
        "USD to NGN": ("USD", "NGN"),
        "GBP to KES": ("GBP", "KES"),
        "EUR to KES": ("EUR", "KES")
    }
    target_base, target_targ = target_map[target_pair]
    
    current_target_rate = latest[(latest['base_currency']==target_base) & (latest['target_currency']==target_targ)]['rate'].values
    
    if len(current_target_rate) > 0:
        current_val = current_target_rate[0]
        target_rate = st.number_input("Your target rate", min_value=0.0, value=float(current_val) + 2.0, step=0.5)
        
        col_alert_a, col_alert_b = st.columns(2)
        col_alert_a.metric("Current Rate", f"{current_val:.2f}")
        col_alert_b.metric("Your Target", f"{target_rate:.2f}")
        
        if target_rate <= current_val:
            st.success(f"🎯 **TARGET REACHED!** Current rate ({current_val}) meets or exceeds your target ({target_rate})")
        else:
            st.info(f"⏳ Target not reached yet. Need {((target_rate - current_val)/current_val)*100:.1f}% increase")
    else:
        st.warning("Rate data not available")
    
    st.divider()
    
    # ============ INTERACTIVE CHART (24H / 7D selector) ============
    st.subheader("📈 Exchange Rate Trends")
    
    chart_pair = st.selectbox("Select currency pair", ["USD to KES", "USD to NGN", "GBP to KES", "EUR to KES"], key="chart_pair")
    chart_map = {
        "USD to KES": ("USD", "KES"),
        "USD to NGN": ("USD", "NGN"),
        "GBP to KES": ("GBP", "KES"),
        "EUR to KES": ("EUR", "KES")
    }
    chart_base, chart_target = chart_map[chart_pair]
    
    time_range = st.radio("Select time range", ["Last 24 Hours", "Last 7 Days"], horizontal=True)
    
    if time_range == "Last 24 Hours":
        time_filter = datetime.now() - timedelta(hours=24)
        chart_title = f"{chart_base} to {chart_target} - Last 24 Hours"
    else:
        time_filter = datetime.now() - timedelta(days=7)
        chart_title = f"{chart_base} to {chart_target} - Last 7 Days"
    
    chart_data = df[(df['base_currency']==chart_base) & (df['target_currency']==chart_target) & (df['fetched_at'] >= time_filter)]
    
    if not chart_data.empty:
        fig = px.line(chart_data, x='fetched_at', y='rate', title=chart_title)
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title=f"Rate ({chart_target})",
            template="plotly_dark",
            plot_bgcolor="rgba(255,255,255,0.05)",
            paper_bgcolor="rgba(255,255,255,0)",
            font=dict(color="white")
        )
        fig.update_traces(line=dict(color="#00ff88", width=2))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough data for selected time range")
    
    st.divider()
    
    # ============ RECENT RATES WITH 24H CHANGE ============
    st.subheader("📋 Recent Rates with 24-Hour Change")
    
    recent = df.tail(15)[['base_currency', 'target_currency', 'rate', 'fetched_at']].copy()
    recent = recent.sort_values('fetched_at', ascending=False)
    
    changes_24h = []
    for idx, row in recent.iterrows():
        pair_24h = df[(df['base_currency']==row['base_currency']) & 
                      (df['target_currency']==row['target_currency']) &
                      (df['fetched_at'] >= row['fetched_at'] - timedelta(hours=24))]
        if len(pair_24h) >= 2:
            old_rate = pair_24h.iloc[0]['rate']
            change = ((row['rate'] - old_rate) / old_rate) * 100
            changes_24h.append(f"{change:+.2f}%")
        else:
            changes_24h.append("N/A")
    
    recent['24h Change'] = changes_24h
    
    recent_display = recent[['base_currency', 'target_currency', 'rate', '24h Change', 'fetched_at']].copy()
    recent_display.columns = ['From', 'To', 'Rate', '24h Change', 'Time']
    recent_display['Rate'] = recent_display['Rate'].round(2)
    
    st.dataframe(recent_display, use_container_width=True)
    
    st.caption(f"📡 Last updated: {df['fetched_at'].max().strftime('%Y-%m-%d %H:%M:%S')} | Data refreshes every hour")
    
    # ============ SOCIAL PROOF SECTION ============
    st.divider()
    st.subheader("⚡ Why Trust This Data?")
    
    col_proof1, col_proof2, col_proof3 = st.columns(3)
    with col_proof1:
        st.metric("🕐 Update Frequency", "Every Hour", delta="Automated")
    with col_proof2:
        st.metric("📊 Data Points", f"{len(df):,}", delta="And growing")
    with col_proof3:
        st.metric("🔗 Data Source", "ExchangeRate API", delta="Live")
    
    st.caption("📈 Data fetched automatically via GitHub Actions. No manual intervention. Fully open source.")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <a href="https://github.com/petermusila/global-remittance-tracker" target="_blank">
            <button style="background: #333; color: white; border: 1px solid #555; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                📁 View Source Code on GitHub
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("No data yet. The automated fetcher will start collecting data soon.")
