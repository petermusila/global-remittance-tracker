# 🌍 Global Remittance Tracker

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://global-remittance-tracker.streamlit.app)
[![GitHub Actions](https://img.shields.io/badge/Automated-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/petermusila/global-remittance-tracker/actions)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

## 📌 Overview

**Global Remittance Tracker** is a live, fully automated data pipeline that fetches real-time exchange rates every hour and displays them on a public dashboard. This project demonstrates the full data stack:

- **Data Engineering:** Automated pipelines, API integration, cloud database, scheduled workflows
- **Data Science:** Pattern detection, anomaly detection, correlation analysis
- **Data Analysis:** Interactive dashboards, time series visualization, business insights

🔗 **Live Demo:** [global-remittance-tracker.streamlit.app](https://global-remittance-tracker.streamlit.app)

---

## 🏗️ Architecture
[ExchangeRate API] ──(every hour)──→ [GitHub Actions] ──→ [Supabase Database] ──→ [Streamlit Dashboard]
│ │ │ │
│ Automated fetch Historical data Public HTTPS link
│ No manual work Cloud storage Shareable dashboard

text

---

## 📊 Features

| Feature | Description |
|---------|-------------|
| **Live Exchange Rates** | Real-time rates for USD, GBP, EUR to African currencies |
| **Automated Pipeline** | Fetches new data every hour via GitHub Actions |
| **Cloud Database** | All historical data stored in Supabase (PostgreSQL) |
| **Public Dashboard** | Interactive Streamlit dashboard with live charts |
| **Historical Trends** | 7-day trend analysis for each currency pair |
| **Zero Manual Intervention** | Runs 24/7 completely automatically |

---

## 📈 Currency Pairs Tracked

| Base Currency | Target Currencies |
|---------------|-------------------|
| 🇺🇸 USD | Kenyan Shilling (KES), Nigerian Naira (NGN), Ghanaian Cedi (GHS), South African Rand (ZAR), Ugandan Shilling (UGX), Tanzanian Shilling (TZS) |
| 🇬🇧 GBP | Kenyan Shilling (KES) |
| 🇪🇺 EUR | Kenyan Shilling (KES) |

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Data Pipeline** | Python, Requests API, GitHub Actions (cron scheduling) |
| **Database** | Supabase (PostgreSQL) |
| **Dashboard** | Streamlit, Plotly, Pandas |
| **Version Control** | Git, GitHub |
| **Deployment** | Streamlit Cloud (HTTPS) |

---

## 📁 Repository Structure
global-remittance-tracker/
├── .github/workflows/
│ └── fetch_rates.yml # Scheduled workflow (runs hourly)
├── fetch_rates.py # API fetcher and database loader
├── dashboard.py # Streamlit dashboard
├── requirements.txt # Python dependencies
└── README.md # Project documentation

text

---

## 🚀 How It Works

### 1. Data Fetching (GitHub Actions)
- Runs automatically at minute 0 of every hour
- Calls ExchangeRate API for all currency pairs
- Saves results to Supabase database

### 2. Data Storage (Supabase)
- PostgreSQL database stores all historical rates
- Each record includes: base currency, target currency, rate, timestamp

### 3. Dashboard (Streamlit)
- Reads live data from Supabase
- Displays current rates in real-time
- Shows 7-day trend charts
- Updates automatically every 5 minutes

---

## 🔧 Local Development

### Prerequisites
- Python 3.12+
- Supabase account (free)

### Setup

```bash
# Clone the repository
git clone https://github.com/petermusila/global-remittance-tracker.git
cd global-remittance-tracker

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"

# Run the fetcher manually
python fetch_rates.py

# Run the dashboard locally
streamlit run dashboard.py

👤 Author
Peter Musila
GitHub: @petermusila
Project Link: https://github.com/petermusila/global-remittance-tracker
Live Demo: https://global-remittance-tracker.streamlit.app
