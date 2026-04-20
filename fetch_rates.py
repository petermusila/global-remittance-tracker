import requests
import os
from supabase import create_client
from datetime import datetime

# Supabase configuration - reads from environment variables (GitHub Secrets)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# List of currency pairs to track (sending country -> receiving country)
CURRENCY_PAIRS = [
    ("USD", "KES"),  # USA to Kenya
    ("USD", "NGN"),  # USA to Nigeria
    ("USD", "GHS"),  # USA to Ghana
    ("USD", "ZAR"),  # USA to South Africa
    ("GBP", "KES"),  # UK to Kenya
    ("EUR", "KES"),  # Europe to Kenya
    ("USD", "UGX"),  # USA to Uganda
    ("USD", "TZS"),  # USA to Tanzania
]

def fetch_exchange_rate(base, target):
    """Fetch live exchange rate from API"""
    url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    
    try:
        response = requests.get(url)
        data = response.json()
        rate = data["rates"].get(target)
        
        if rate:
            print(f"✅ {base} -> {target}: {rate}")
            return rate
        else:
            print(f"❌ Rate not found for {base} -> {target}")
            return None
    except Exception as e:
        print(f"❌ Error fetching {base}->{target}: {e}")
        return None

def save_to_supabase(base, target, rate):
    """Save exchange rate to Supabase"""
    data = {
        "base_currency": base,
        "target_currency": target,
        "rate": rate,
        "fetched_at": datetime.now().isoformat()
    }
    
    try:
        supabase.table("exchange_rates").insert(data).execute()
        return True
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        return False

def main():
    print(f"\n{'='*50}")
    print(f"Global Remittance Tracker - Live Rate Fetch")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    success_count = 0
    
    for base, target in CURRENCY_PAIRS:
        rate = fetch_exchange_rate(base, target)
        if rate:
            if save_to_supabase(base, target, rate):
                success_count += 1
    
    print(f"\n{'='*50}")
    print(f"Summary: {success_count}/{len(CURRENCY_PAIRS)} rates saved")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
