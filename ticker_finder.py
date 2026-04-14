import requests

market_ticker = "KXMLBGAME-26APR132210NYMLAD-NYM"
url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{market_ticker}"

data = requests.get(url).json()
market = data["market"]

print("ticker:", market["ticker"])
print("title:", market.get("title"))
print("subtitle:", market.get("subtitle"))
print("yes side:", market.get("yes_sub_title"))
print("no side:", market.get("no_sub_title"))