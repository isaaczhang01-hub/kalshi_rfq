import asyncio
import json
import os
import requests
import websockets
from dotenv import load_dotenv

from auth import KalshiAuth

load_dotenv()

BASE_URL = "https://api.elections.kalshi.com"   # switch to demo if needed
WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"

auth = KalshiAuth(
    api_key=os.environ["KALSHI_API_KEY_ID"],
    key_path=os.environ["KALSHI_API_PATH"],
)

# paste your RFQ id here
RFQ_ID = "b7347bed-8cb1-4637-8458-448aba0dc5b9"


def get_rfq(rfq_id):
    path = f"/trade-api/v2/communications/rfqs/{rfq_id}"
    url = BASE_URL + path
    headers = auth.request_headers("GET", path)

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def accept_quote(quote_id, accepted_side):
    path = f"/trade-api/v2/communications/quotes/{quote_id}/accept"
    url = BASE_URL + path
    headers = auth.request_headers("PUT", path)

    payload = {
        "accepted_side": accepted_side  # "yes" or "no"
    }

    resp = requests.put(url, headers=headers, json=payload)
    print("ACCEPT status:", resp.status_code)
    print(resp.text)
    resp.raise_for_status()


def print_starting_snapshot(rfq_id):
    try:
        data = get_rfq(rfq_id)
        # docs say this endpoint returns a single RFQ by id; depending on wrapper shape,
        # the RFQ may be under "rfq" or the top level.
        rfq = data.get("rfq", data)

        print("=" * 80)
        print("STARTING RFQ SNAPSHOT")
        print(f"id={rfq.get('id')}")
        print(f"market={rfq.get('market_ticker')}")
        print(f"event={rfq.get('event_ticker')}")
        print(f"contracts={rfq.get('contracts_fp')}")
        print(f"target_cost={rfq.get('target_cost_dollars')}")
        print(f"status={rfq.get('status')}")
        print("=" * 80)
    except Exception as e:
        print(f"Could not fetch RFQ snapshot: {e}")


def print_quote_created(msg):
    print("-" * 80)
    print("QUOTE CREATED")
    print(f"quote_id={msg.get('quote_id') or msg.get('id')}")
    print(f"rfq_id={msg.get('rfq_id')}")
    print(f"yes_bid={msg.get('yes_bid_dollars')}")
    print(f"no_bid={msg.get('no_bid_dollars')}")
    print(f"contracts={msg.get('contracts_fp')}")
    print(f"yes_size={msg.get('yes_contracts_offered_fp')}")
    print(f"no_size={msg.get('no_contracts_offered_fp')}")
    print(f"creator={msg.get('creator_id')}")
    print(f"status={msg.get('status')}")
    print(f"created_ts={msg.get('created_ts')}")


def print_quote_accepted(msg):
    print("-" * 80)
    print("QUOTE ACCEPTED")
    print(f"quote_id={msg.get('quote_id') or msg.get('id')}")
    print(f"rfq_id={msg.get('rfq_id')}")
    print(f"accepted_side={msg.get('accepted_side')}")
    print(f"contracts_accepted={msg.get('contracts_accepted_fp') or msg.get('contracts_fp')}")
    print(f"accepted_ts={msg.get('accepted_ts')}")
    print(f"status={msg.get('status')}")


def print_quote_executed(msg):
    print("-" * 80)
    print("QUOTE EXECUTED")
    print(f"quote_id={msg.get('quote_id') or msg.get('id')}")
    print(f"rfq_id={msg.get('rfq_id')}")
    print(f"order_id={msg.get('order_id')}")
    print(f"executed_ts={msg.get('executed_ts')}")
    print(f"status={msg.get('status')}")


def print_rfq_deleted(msg):
    print("-" * 80)
    print("RFQ DELETED / CLOSED")
    print(f"id={msg.get('id')}")
    print(f"rfq_id={msg.get('rfq_id')}")
    print(f"deleted_ts={msg.get('deleted_ts')}")
    print(f"status={msg.get('status')}")


async def main():
    print_starting_snapshot(RFQ_ID)

    headers = auth.ws_headers()

    async with websockets.connect(WS_URL, additional_headers=headers) as ws:
        subscribe_msg = {
            "id": 1,
            "cmd": "subscribe",
            "params": {
                "channels": ["communications"]
            },
        }
        await ws.send(json.dumps(subscribe_msg))
        print(f"Watching RFQ {RFQ_ID} ...")

        while True:
            raw = await ws.recv()
            data = json.loads(raw)

            msg_type = data.get("type")
            msg = data.get("msg", {})

            if msg_type == "subscribed":
                print("Subscribed to communications.")
                continue

            if msg_type == "error":
                print(f"Error: {msg}")
                break

            # RFQ events sometimes use "id" for the RFQ id
            event_rfq_id = msg.get("rfq_id") or msg.get("id")

            if event_rfq_id != RFQ_ID:
                continue

            if msg_type == "quote_created":
                print_quote_created(msg)

                quote_id = msg.get("quote_id") or msg.get("id")
                action = input("Type yes / no / skip: ").strip().lower()

                if action in {"yes", "no"}:
                    accept_quote(quote_id, action)
                else:
                    print("Skipped.")
            elif msg_type == "quote_accepted":
                print_quote_accepted(msg)
            elif msg_type == "quote_executed":
                print_quote_executed(msg)
            elif msg_type == "rfq_deleted":
                print_rfq_deleted(msg)
            else:
                print("-" * 80)
                print(f"OTHER EVENT: {msg_type}")
                print(json.dumps(msg, indent=2))


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stopped watcher.")