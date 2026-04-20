import streamlit as st
import pandas as pd
import os
from supabase import create_client
import plotly.express as px
from datetime import datetime, timedelta

# Read from environment variables (Streamlit Cloud will inject these)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Check if credentials are available
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Database credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")
    st.stop()

@st.cache_data(ttl=300)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table("exchange_rates").select("*").order("fetched_at", desc=False).execute()
    df = pd.DataFrame(response.data)
    if not df.empty:
        df['fetched_at'] = pd.to_datetime(df['fetched_at'])
    return df

st.set_page_config(page_title="Global Remittance Tracker", layout="wide")

st.title("🌍 Global Remittance Tracker")
st.markdown("Live exchange rates for money transfers from USA, UK, and Europe to Africa")

# Load data
df = load_data()

if not df.empty:
    # Latest rates
    latest = df.groupby(['base_currency', 'target_currency']).last().reset_index()
    
    col1, col2, col3, col4 = st.columns(4)
    
    # USD to KES
    usd_kes = latest[(latest['base_currency']=='USD') & (latest['target_currency']=='KES')]['rate'].values
    if len(usd_kes) > 0:
        col1.metric("🇺🇸 USD → 🇰🇪 KES", f"{usd_kes[0]:.2f}")
    
    # GBP to KES
    gbp_kes = latest[(latest['base_currency']=='GBP') & (latest['target_currency']=='KES')]['rate'].values
    if len(gbp_kes) > 0:
        col2.metric("🇬🇧 GBP → 🇰🇪 KES", f"{gbp_kes[0]:.2f}")
    
    # EUR to KES
    eur_kes = latest[(latest['base_currency']=='EUR') & (latest['target_currency']=='KES')]['rate'].values
    if len(eur_kes) > 0:
        col3.metric("🇪🇺 EUR → 🇰🇪 KES", f"{eur_kes[0]:.2f}")
    
    # USD to NGN
    usd_ngn = latest[(latest['base_currency']=='USD') & (latest['target_currency']=='NGN')]['rate'].values
    if len(usd_ngn) > 0:
        col4.metric("🇺🇸 USD → 🇳🇬 NGN", f"{usd_ngn[0]:.2f}")
    
    st.divider()
    
    # Historical chart
    st.subheader("📈 Exchange Rate Trends (Last 7 Days)")
    
    seven_days_ago = datetime.now() - timedelta(days=7)
    df_recent = df[df['fetched_at'] >= seven_days_ago]
    
    usd_data = df_recent[df_recent['base_currency']=='USD'][df_recent['target_currency']=='KES']
    if not usd_data.empty:
        fig = px.line(usd_data, x='fetched_at', y='rate', title='USD to KES - Last 7 Days')
        fig.update_layout(xaxis_title="Time", yaxis_title="Exchange Rate (KES)")
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Recent Rates")
    recent = df.tail(10)[['base_currency', 'target_currency', 'rate', 'fetched_at']]
    recent = recent.sort_values('fetched_at', ascending=False)
    st.dataframe(recent, use_container_width=True)
    
    st.caption(f"Last updated: {df['fetched_at'].max()} | Data updates every hour")
else:
    st.warning("No data yet. The automated fetcher will start collecting data soon.")
