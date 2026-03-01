"""
news_fetcher.py
Simple RSS news fetcher for market news
"""

import feedparser
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RSS feeds
NEWS_FEEDS = [
    {
        "name": "Economic Times Markets",
        "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "weight": 1.0,
    },
    {
        "name": "MoneyControl News",
        "url": "https://www.moneycontrol.com/rss/MCtopnews.xml",
        "weight": 0.9,
    },
]


def get_all_news():
    """
    Fetch news from RSS feeds
    
    Returns:
        dict: {
            'articles': list of articles,
            'sentiment': overall sentiment
        }
    """
    articles = []
    
    for feed_config in NEWS_FEEDS:
        try:
            feed = feedparser.parse(feed_config['url'])
            
            for entry in feed.entries[:5]:  # Get 5 articles per feed
                article = {
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': feed_config['name'],
                    'weighted_score': 0  # Neutral
                }
                articles.append(article)
        except Exception as e:
            logger.error(f"Error fetching {feed_config['name']}: {e}")
    
    # Simple sentiment (neutral by default)
    sentiment = {
        'label': 'NEUTRAL',
        'score': 0,
        'article_count': len(articles)
    }
    
    return {
        'articles': articles,
        'sentiment': sentiment
    }


if __name__ == "__main__":
    news = get_all_news()
    print(f"Fetched {len(news['articles'])} articles")
    print(f"Sentiment: {news['sentiment']['label']}")
