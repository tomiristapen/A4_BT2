import os
import requests
from dotenv import load_dotenv

load_dotenv()
CMC_API_KEY = os.getenv("CMC_API_KEY")

def get_top_cryptos(limit=50):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        "X-CMC_PRO_API_KEY": CMC_API_KEY
    }
    params = {
        "start": "1",
        "limit": limit,
        "convert": "USD"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if "data" not in data:
        raise Exception("Error from CoinMarketCap API: " + str(data))

    cryptos = []
    for coin in data["data"]:
        cryptos.append({
            "name": coin["name"],
            "symbol": coin["symbol"],
            "price": round(coin["quote"]["USD"]["price"], 2),
            "market_cap": round(coin["quote"]["USD"]["market_cap"], 2),
            "rank": coin["cmc_rank"]
        })

    return cryptos
