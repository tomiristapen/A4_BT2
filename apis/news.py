import feedparser
import requests
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def embed_text(text: str) -> np.ndarray:
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    if response.status_code == 200:
        return np.array(response.json()["embedding"]).reshape(1, -1)
    else:
        return None

def get_latest_news_semantic(user_query: str, feed_url="https://cointelegraph.com/rss", max_items=5):
    feed = feedparser.parse(feed_url)
    all_news = []

    for entry in feed.entries:
        all_news.append({
            "title": entry.title.strip(),
            "summary": entry.summary[:300].strip().replace('\n', ' ') + "...",
            "link": entry.link,
            "published": entry.published
        })

    query_vec = embed_text(user_query)
    if query_vec is None:
        return []

    scored_news = []
    for item in all_news:
        news_text = item["title"] + " " + item["summary"]
        news_vec = embed_text(news_text)
        if news_vec is not None:
            score = cosine_similarity(query_vec, news_vec)[0][0]
            scored_news.append((score, item))

    scored_news.sort(reverse=True, key=lambda x: x[0])
    top_news = [item for _, item in scored_news[:max_items]]
    return top_news
