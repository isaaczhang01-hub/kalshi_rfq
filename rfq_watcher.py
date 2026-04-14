import asyncio
import json
import os
import time
from collections import Counter
import requests

import websockets
from dotenv import load_dotenv

from auth import KalshiAuth
load_dotenv()

WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"

auth = KalshiAuth(
    api_key=os.environ["KALSHI_API_KEY_ID"],
    key_path=os.environ["KALSHI_API_PATH"],
)

# market_tickers = ["KXCS2GAME-26APR131400MOUZLGC-MOUZ"]

MIN_CONTRACTS = 50
TICKER_KEYWORDS = []

open_rfqs = {}
created_recent = []

market_cache = {}

def get_market_info(market_ticker):
    if market_ticker in market_cache:
        return market_cache[market_ticker]

    path = f"/trade-api/v2/markets/{market_ticker}"
    url = f"https://api.elections.kalshi.com{path}"
    headers = auth.request_headers("GET", path)

    data = requests.get(url, headers=headers).json()
    market = data["market"]
    market_cache[market_ticker] = market
    return market

def passes_filter(msg):
    contracts = float(msg.get("contracts_fp", 0) or 0)
    if contracts < MIN_CONTRACTS:
        return False

    if not TICKER_KEYWORDS:
        return True

    text = f"{msg.get('market_ticker', '')} {msg.get('event_ticker', '')}"
    return any(word in text for word in TICKER_KEYWORDS)    

def format_leg_human(leg):
    market_ticker = leg.get("market_ticker", "")
    side = leg.get("side", "").lower()
    market = get_market_info(market_ticker)

    title = market.get("title") or market_ticker

    if side == "yes":
        side_text = market.get("yes_sub_title") or "YES"
    else:
        side_text = market.get("no_sub_title") or "NO"

    subtitle = market.get("subtitle")
    if subtitle:
        return f"{title} -> {side_text} [{subtitle}]"
    return f"{title} -> {side_text}"

def format_parlay_human(rfq):
    legs = rfq.get("mve_selected_legs", [])
    if not legs:
        return "single market"

    return " | ".join(format_leg_human(leg) for leg in legs)

def rfq_sort_key(rfq):
    contracts = float(rfq.get("contracts_fp", 0) or 0)
    target_cost = float(rfq.get("target_cost_dollars", 0) or 0)
    return (contracts, target_cost)

async def printer():
    while True:
        await asyncio.sleep(2)

        now = time.time()
        recent = [x for x in created_recent if now - x["t"] <= 2]

        top_rfqs = sorted(
            open_rfqs.values(),
            key=rfq_sort_key,
            reverse=True
        )[:3]

        print(f"OPEN={len(open_rfqs)}  NEW_LAST_2S={len(recent)}")
        print("TOP 3 OPEN RFQS:")

        for i, rfq in enumerate(top_rfqs, 1):
            print(
                f"id={rfq.get('id')} | "
                f"contracts={rfq.get('contracts_fp')} | "
                f"target_cost=${rfq.get('target_cost_dollars')} | "
                f"parlay={format_parlay_human(rfq)}"
            )

            if i < len(top_rfqs):
                print("-" * 80)

async def main():
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

        asyncio.create_task(printer())

        while True:
            raw = await ws.recv()
            data = json.loads(raw)
            msg_type = data.get("type")
            msg = data.get("msg", {})

            if msg_type == "rfq_created":
                if passes_filter(msg):
                    rfq_id = msg.get("id")
                    open_rfqs[rfq_id] = msg
                    created_recent.append({
                        "t": time.time(),
                        "event_ticker": msg.get("event_ticker", "")
                    })

            elif msg_type == "rfq_deleted":
                rfq_id = msg.get("id")
                open_rfqs.pop(rfq_id, None)

            elif msg_type == "subscribed":
                print(f"Subscribed to {msg.get('channel')}")

            elif msg_type == "orderbook_snapshot":
                msg = data["msg"]
                print(f"Snapshot: {len(msg.get('yes', []))} yes levels, "
                      f"{len(msg.get('no', []))} no levels")

            elif msg_type == "orderbook_delta":
                msg = data["msg"]
                print(f"Delta: {msg['side']} @ {msg['price_dollars']}¢  {msg['delta_fp']}")

            elif msg_type == "error":
                print(f"Error: {data.get('msg')}")
                break

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stopped watcher.")