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


def create_rfq(market_ticker, contracts, rest_remainder=False, target_cost_dollars=None):
    path = "/trade-api/v2/communications/rfqs"
    url = BASE_URL + path
    headers = auth.request_headers("POST", path)

    payload = {
        "market_ticker": market_ticker,
        "rest_remainder": rest_remainder,
        "contracts_fp": f"{contracts:.2f}",
    }

    if target_cost_dollars is not None:
        payload["target_cost_dollars"] = f"{target_cost_dollars:.4f}"

    resp = requests.post(url, headers=headers, json=payload)
    print("CREATE status:", resp.status_code)
    print(resp.text)

    resp.raise_for_status()
    rfq_id = resp.json()["id"]
    print("Created RFQ:", rfq_id)
    return rfq_id


def delete_rfq(rfq_id):
    path = f"/trade-api/v2/communications/rfqs/{rfq_id}"
    url = BASE_URL + path
    headers = auth.request_headers("DELETE", path)

    resp = requests.delete(url, headers=headers)
    print("DELETE status:", resp.status_code)

    if resp.status_code == 204:
        print(f"Deleted RFQ: {rfq_id}")
    else:
        print(resp.text)

    resp.raise_for_status()

if __name__ == "__main__":
    mode = input("Type 'c' to create or 'd' to delete: ").strip().lower()

    if mode == "c":
        market_ticker = "KXMLBGAME-26APR132210NYMLAD-NYM"

        rfq_id = create_rfq(
            market_ticker=market_ticker,
            contracts=10,
            rest_remainder=False,
            target_cost_dollars=None,
        )
        print("Saved RFQ ID:", rfq_id)

    elif mode == "d":
        rfq_id = input("Enter RFQ ID to delete: ").strip()
        delete_rfq(rfq_id)