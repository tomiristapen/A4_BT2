import requests
import re
from apis.prices import get_token_price
from apis.news import get_latest_news_semantic

def extract_token_name(user_query, crypto_data):
    query_lower = user_query.lower()
    for coin in crypto_data:
        if coin["name"].lower() in query_lower or coin["symbol"].lower() in query_lower:
            return coin["name"]
    return "Bitcoin"

def extract_two_tokens(user_query, crypto_data):
    query_lower = user_query.lower()
    found = []
    for coin in crypto_data:
        if coin["name"].lower() in query_lower or coin["symbol"].lower() in query_lower:
            found.append(coin["name"])
        if len(found) == 2:
            break
    return found if len(found) == 2 else None

def is_price_or_marketcap_query(user_query):
    q = user_query.lower()
    return any(x in q for x in ["price", "market cap", "капитализац", "цена"])

def is_compare_query(user_query):
    q = user_query.lower()
    return "compare" in q or "vs" in q or "сравн" in q

def is_about_query(user_query):
    q = user_query.lower()
    return any(x in q for x in ["about", "что такое", "расскажи", "info"])

def is_news_only_query(user_query):
    q = user_query.lower()
    return any(x in q for x in ["latest news", "recent news", "news about"])

def is_investment_query(user_query):
    q = user_query.lower()
    return any(x in q for x in ["should i invest", "buy now", "влож", "покупать", "инвест"])

def extract_news_count(query: str, default=5) -> int:
    match = re.search(r"\b(\d{1,2})\b", query)
    return int(match.group(1)) if match else default

def generate_response(user_query, crypto_data, news=None, token_info=None):
    token_name = extract_token_name(user_query, crypto_data)
    token = token_info if token_info else next((c for c in crypto_data if c["name"] == token_name), None)
    price = get_token_price(token_name)

    # Инвест-вопрос
    if is_investment_query(user_query):
        news_items = get_latest_news_semantic(token_name, max_items=5)
        filtered_news = [
            item for item in news_items if item.get("title") and item.get("summary")
        ]
        news_text = "\n\n".join([
            f"{i+1}. **{item['title']}**\nSummary: {item['summary']}\n[Read more]({item['link']})"
            for i, item in enumerate(filtered_news)
        ]) if filtered_news else "No recent news found."

        prompt = f"""
User is considering investing in **{token_name}**.

**💵 Price:** ${price}
**📊 Market Cap:** ${token['market_cap'] if token else 'N/A'}
**🏆 Rank:** {token['rank'] if token else 'N/A'}

**📰 Relevant News:**
{news_text}

Based on this data, provide an honest and thoughtful investment evaluation of {token_name}.
"""
        return call_llama(prompt)

    # Только новости
    if is_news_only_query(user_query):
        count = extract_news_count(user_query)
        news_items = get_latest_news_semantic(user_query, max_items=count)
        filtered_news = [
            item for item in news_items if item.get("title") and item.get("summary")
        ][:count]
        news_text = "\n\n".join([
            f"{i+1}. **{item['title']}**\nSummary: {item['summary']}\n[Source]({item['link']})"
            for i, item in enumerate(filtered_news)
        ]) if filtered_news else "No relevant news found."

        prompt = f"""
User asked for the {count} latest news about **{token_name}**.

{news_text}

Do NOT include price or market cap. Just present clearly formatted news.
"""
        return call_llama(prompt)

    # Сравнение
    if is_compare_query(user_query):
        tokens = extract_two_tokens(user_query, crypto_data)
        if tokens:
            info = []
            for t in tokens:
                p = get_token_price(t)
                tk = next((c for c in crypto_data if c["name"] == t), None)
                info.append(f"{t}: Price ${p}, Cap ${tk['market_cap']}, Rank {tk['rank']}")
            prompt = f"""
Compare the following tokens based on price, market cap and rank:

- {info[0]}
- {info[1]}

Which one looks stronger? Present clearly.
"""
            return call_llama(prompt)

    # Описание токена
    if is_about_query(user_query):
        from apis.prices import get_token_description
        desc = get_token_description(token_name.lower())
        news_items = get_latest_news_semantic(token_name, max_items=3)
        filtered_news = [
            item for item in news_items if item.get("title") and item.get("summary")
        ]
        news_text = "\n\n".join([
            f"{i+1}. **{item['title']}**\n{item['summary']}\n[Source]({item['link']})"
            for i, item in enumerate(filtered_news)
        ]) if filtered_news else "No news found."

        prompt = f"""
User asked about **{token_name}**.

**💵 Price:** ${price}
**📊 Market Cap:** ${token['market_cap']}
**🏆 Rank:** {token['rank']}

**What is it:** {desc}

**📰 Recent News:**
{news_text}

Summarize clearly.
"""
        return call_llama(prompt)

    # Обычный режим
    count = extract_news_count(user_query)
    news_items = news if news else get_latest_news_semantic(user_query, max_items=count)
    filtered_news = [
        item for item in news_items if item.get("title") and item.get("summary")
    ][:count]

    news_text = "\n\n".join([
        f"{i+1}. **{item['title']}**\n{item['summary']}\n[Source]({item['link']})"
        for i, item in enumerate(filtered_news)
    ]) if filtered_news else "No relevant news found."

    market_text = f"**Market Cap:** ${token['market_cap']} | **Rank:** {token['rank']}" if token else ""

    prompt = f"""
User asked: "{user_query}"

**Token:** {token_name}
**Price:** ${price}
{market_text}

**Recent News:**
{news_text}

Provide a helpful, readable response combining this info.
"""
    return call_llama(prompt)

def call_llama(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.2", "prompt": prompt, "stream": False}
    )
    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")
    return response.json().get("response", "No response from Ollama.")
