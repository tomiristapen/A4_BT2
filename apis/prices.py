import requests

# Преобразуем название в ID CoinGecko
def map_token_to_id(name):
    name_map = {
        "Bitcoin": "bitcoin",
        "Ethereum": "ethereum",
        "Solana": "solana",
        "Cardano": "cardano",
        "Dogecoin": "dogecoin",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "TRON": "tron"
        # Добавь больше при необходимости
    }
    return name_map.get(name, "bitcoin")

def get_token_price(token_name):
    token_id = map_token_to_id(token_name)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
    try:
        res = requests.get(url).json()
        return res.get(token_id, {}).get("usd")
    except:
        return None

def get_price_history(token_id, days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days={days}"
    try:
        res = requests.get(url).json()
        prices = res.get("prices", [])
        market_caps = res.get("market_caps", [])
        if not prices:
            return "No historical data found."
        summary = []
        for i in [0, len(prices)//2, -1]:
            if i == -1:
                i = len(prices)-1
            price = prices[i][1]
            cap = market_caps[i][1] if market_caps else 'N/A'
            date = prices[i][0]
            summary.append(f"Date: {date}, Price: ${round(price,2)}, Market Cap: ${round(cap,2) if cap != 'N/A' else 'N/A'}")
        return "\n".join(summary)
    except Exception as e:
        return f"Error fetching history: {e}"
