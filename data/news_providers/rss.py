# data/news_providers/rss.py
from .base import NewsProvider, NewsItem
import feedparser
from typing import List

class RSSProvider(NewsProvider):
    def __init__(self):
        self.feeds = [
            "https://cointelegraph.com/rss",
            "https://www.coindesk.com/arc/outboundfeeds/rss/"
        ]

    def is_available(self) -> bool:
        return True

    def get_latest_news(self, limit=5) -> List[NewsItem]:
        items = []
        for url in self.feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:limit]:
                    items.append(NewsItem(
                        title=entry.title,
                        content=entry.summary[:500] if hasattr(entry, 'summary') else "",
                        url=entry.link,
                        published_at=entry.published if hasattr(entry, 'published') else "",
                        source="RSS"
                    ))
                if len(items) >= limit:
                    break
            except:
                continue
        return items[:limit]