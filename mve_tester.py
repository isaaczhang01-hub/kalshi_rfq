import os
import requests
from dotenv import load_dotenv
from auth import KalshiAuth

load_dotenv()

BASE_URL = "https://api.elections.kalshi.com"   # use demo-api.kalshi.co for demo

auth = KalshiAuth(
    api_key=os.environ["KALSHI_API_KEY_ID"],
    key_path=os.environ["KALSHI_API_PATH"],
)

session = requests.Session()

def get_mve_collections(status=None, series_ticker=None, associated_event_ticker=None, limit=20):
    path = "/trade-api/v2/multivariate_event_collections"
    url = BASE_URL + path
    headers = auth.request_headers("GET", path)

    params = {"limit": limit}
    if status is not None:
        params["status"] = status
    if series_ticker is not None:
        params["series_ticker"] = series_ticker
    if associated_event_ticker is not None:
        params["associated_event_ticker"] = associated_event_ticker

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

def get_mve_collection(collection_ticker):
    path = f"/trade-api/v2/multivariate_event_collections/{collection_ticker}"
    url = BASE_URL + path
    headers = auth.request_headers("GET", path)

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    data = get_mve_collections(status="open", limit=3)

    for c in data["multivariate_contracts"]:
        print("=" * 80)
        print("collection_ticker:", c["collection_ticker"])
        print("title:", c["title"])
        print("description:", c.get("description"))
        print("size_min:", c.get("size_min"), "size_max:", c.get("size_max"))
        print("associated events:")
        for e in c["associated_events"]:
            print(
                "  ",
                e["ticker"],
                "| yes_only =", e.get("is_yes_only"),
                "| size_max =", e.get("size_max"),
            )

    # example once you know a collection ticker:
    # one = get_mve_collection("YOUR_COLLECTION_TICKER")
    # print(one)