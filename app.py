import streamlit as st
from apis.coinmarketcap import get_top_cryptos
from ai.response_gen import generate_response
from apis.news import get_latest_news_semantic

# Заголовок и меню
st.set_page_config(page_title="AI Crypto Assistant", layout="wide")
st.title("💡 AI Crypto Dashboard")

page = st.sidebar.radio("Навигация", ["📈 Цены в реальном времени", "📰 Крипто-новости", "🤖 AI-помощник"])

# Вкладка 1: Цены
if page == "📈 Цены в реальном времени":
    st.header("📈 Топ 50 Криптовалют")
    try:
        cryptos = get_top_cryptos()
        for coin in cryptos:
            st.write(f"{coin['rank']}. {coin['name']} ({coin['symbol']}) — ${coin['price']} | Market Cap: ${coin['market_cap']:,}")
    except Exception as e:
        st.error(f"Ошибка при получении данных: {e}")

# Вкладка 2: Новости

elif page == "📰 Крипто-новости":
    st.header("📰 Последние крипто-новости (Cointelegraph)")

    try:
        news_items = get_latest_news_semantic("crypto")

        for item in news_items:
            st.markdown(f"### [{item['title']}]({item['link']})")
            st.caption(f"🕒 {item['published']}")
            st.markdown("---")
    except Exception as e:
        st.error(f"Ошибка при загрузке новостей: {e}")

# Вкладка 3: AI
elif page == "🤖 AI-помощник":
    st.header("🤖 Задай вопрос крипто-помощнику")
    query = st.text_input("💬 Пример: Tell me about Bitcoin")

    if query:
        try:
            # Извлекаем название токена из запроса (очень просто, для примера)
            token = query.split()[-1] if len(query.split()) > 2 else "Bitcoin"
            cryptos = get_top_cryptos()
            # Получаем новости, цену и рыночные данные
            news = get_latest_news_semantic(token)
            # Поиск информации о токене в топ-50
            token_info = next((c for c in cryptos if token.lower() in (c['name'].lower(), c['symbol'].lower())), None)
            # Формируем данные для генерации ответа
            with st.spinner("⚙️ Генерация ответа..."):
                reply = generate_response(query, cryptos, news=news, token_info=token_info)
                st.markdown("### 📜 Ответ:")
                st.write(reply)
        except Exception as e:
            st.error(f"Ошибка: {e}")
