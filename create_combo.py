import os
import time
import requests
from dotenv import load_dotenv
from auth import KalshiAuth

load_dotenv()

BASE_URL = "https://api.elections.kalshi.com"

auth = KalshiAuth(
    api_key=os.environ["KALSHI_API_KEY_ID"],
    key_path=os.environ["KALSHI_API_PATH"],
)

def create_combo_market(collection_ticker, selected_markets):
    path = f"/trade-api/v2/multivariate_event_collections/{collection_ticker}"
    url = BASE_URL + path
    headers = auth.request_headers("POST", path)

    payload = {
        "selected_markets": selected_markets,
        "with_market_payload": True,
    }

    resp = requests.post(url, headers=headers, json=payload)
    print("CREATE COMBO status:", resp.status_code)
    print(resp.text)
    resp.raise_for_status()
    return resp.json()

def get_orderbook(market_ticker):
    url = f"{BASE_URL}/trade-api/v2/markets/{market_ticker}/orderbook"
    resp = requests.get(url)
    print("ORDERBOOK status:", resp.status_code)
    resp.raise_for_status()
    return resp.json()

def watch_orderbook(market_ticker, seconds=30, poll_every=2):
    print("=" * 100)
    print("WATCHING ORDERBOOK FOR:", market_ticker)
    print("=" * 100)

    for _ in range(max(1, seconds // poll_every)):
        ob = get_orderbook(market_ticker)
        yes = ob.get("orderbook", {}).get("yes", [])
        no = ob.get("orderbook", {}).get("no", [])

        print("-" * 100)
        print("YES bids:", yes[:5])
        print("NO bids:", no[:5])

        time.sleep(poll_every)

if __name__ == "__main__":
    collection_ticker = "KXMVENBASINGLEGAME-26APR15ORLPHI"

    selected_markets = [
        {
            "event_ticker": "KXNBAGAME-26APR15ORLPHI",
            "market_ticker": "KXNBAGAME-26APR15ORLPHI-PHI",
            "side": "yes",
        },
        {
            "event_ticker": "KXNBA3PT-26APR15ORLPHI",
            "market_ticker": "KXNBA3PT-26APR15ORLPHI-PHITMAXEY0-2",
            "side": "yes",
        },
        {
            "event_ticker": "KXNBASTL-26APR15ORLPHI",
            "market_ticker": "KXNBASTL-26APR15ORLPHI-ORLJSUGGS4-1",
            "side": "yes",
        },
    ]

    combo = create_combo_market(collection_ticker, selected_markets)

    combo_market_ticker = combo.get("market_ticker") or combo.get("market", {}).get("ticker")
    print("=" * 100)
    print("COMBO MARKET TICKER:", combo_market_ticker)
    print("=" * 100)

    watch_orderbook(combo_market_ticker, seconds=30, poll_every=2)