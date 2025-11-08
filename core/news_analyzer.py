# core/news_analyzer.py
from data.news_providers import get_news
from data.llm_providers import get_llm_chain

def analyze_news_sentiment() -> dict:
    """
    Анализирует новости с помощью LLM.
    Гарантирует совместимость с верхним регистром.
    """
    news = get_news(limit=3)
    if not news:
        return {
            "sentiment": "NEUTRAL",
            "confidence": 0.0,
            "source": "none",
            "news_count": 0
        }

    llm_chain = get_llm_chain()
    if not llm_chain:
        return {
            "sentiment": "NEUTRAL",
            "confidence": 0.0,
            "source": "no_llm",
            "news_count": len(news)
        }

    llm = llm_chain[0]  # Первый доступный
    texts = [f"{n.title} {n.content}" for n in news]
    sentiments = []

    for text in texts:
        result = llm.analyze_sentiment(text)
        # Приводим к верхнему регистру
        sentiment_upper = result["sentiment"].upper()
        # Защита от неизвестных значений
        if sentiment_upper not in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            sentiment_upper = "NEUTRAL"
        sentiments.append({
            "sentiment": sentiment_upper,
            "confidence": result["confidence"]
        })

    # Подсчёт
    avg_conf = sum(s["confidence"] for s in sentiments) / len(sentiments)
    counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    for s in sentiments:
        counts[s["sentiment"]] += 1

    final_sentiment = max(counts, key=counts.get)

    return {
        "sentiment": final_sentiment,
        "confidence": round(avg_conf, 2),
        "source": llm.__class__.__name__.replace("Provider", ""),
        "news_count": len(news)
    }