import requests
import os
from supabase import create_client
from datetime import datetime

# Read from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Check if credentials are loaded
if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_KEY environment variables")
    exit(1)

print(f"Loaded SUPABASE_URL: {SUPABASE_URL[:20]}...")  # Print first 20 chars only
print(f"Loaded SUPABASE_KEY: {SUPABASE_KEY[:20]}...")  # Print first 20 chars only

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# List of currency pairs to track
CURRENCY_PAIRS = [
    ("USD", "KES"),
    ("USD", "NGN"),
    ("USD", "GHS"),
    ("USD", "ZAR"),
    ("GBP", "KES"),
    ("EUR", "KES"),
    ("USD", "UGX"),
    ("USD", "TZS"),
]

def fetch_exchange_rate(base, target):
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
        print(f"❌ Error: {e}")
        return None

def save_to_supabase(base, target, rate):
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
        print(f"❌ Database error: {e}")
        return False

def main():
    print(f"\n{'='*50}")
    print(f"Global Remittance Tracker")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    success = 0
    for base, target in CURRENCY_PAIRS:
        rate = fetch_exchange_rate(base, target)
        if rate and save_to_supabase(base, target, rate):
            success += 1
    
    print(f"\n{'='*50}")
    print(f"Saved {success}/{len(CURRENCY_PAIRS)} rates")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
