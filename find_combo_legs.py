import requests

BASE_URL = "https://api.elections.kalshi.com"

def get_markets_for_event(event_ticker):
    url = f"{BASE_URL}/trade-api/v2/markets"
    resp = requests.get(url, params={"event_ticker": event_ticker})
    resp.raise_for_status()
    return resp.json()["markets"]

def print_markets_for_event(event_ticker):
    print("=" * 100)
    print("EVENT:", event_ticker)

    markets = get_markets_for_event(event_ticker)
    for m in markets:
        print(
            f"{m['ticker']} | "
            f"{m.get('title')} | "
            f"YES -> {m.get('yes_sub_title')} | "
            f"NO -> {m.get('no_sub_title')}"
        )

if __name__ == "__main__":
    event_tickers = [
        "KXNBAGAME-26APR15ORLPHI",
        "KXNBASPREAD-26APR15ORLPHI",
        "KXNBATOTAL-26APR15ORLPHI",
        "KXNBAPTS-26APR15ORLPHI",
        "KXNBAAST-26APR15ORLPHI",
        "KXNBAREB-26APR15ORLPHI",
        "KXNBA3PT-26APR15ORLPHI",
        "KXNBASTL-26APR15ORLPHI",
        "KXNBABLK-26APR15ORLPHI",
    ]

    for event_ticker in event_tickers:
        print_markets_for_event(event_ticker)