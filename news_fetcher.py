"""
news_fetcher.py
Simple RSS news fetcher for market news
"""

import feedparser
from datetime import datetime, timedelta
import pytz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IST = pytz.timezone('Asia/Kolkata')

# RSS feeds
NEWS_FEEDS = [
    {
        "name": "Economic Times Markets",
        "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "weight": 1.0,
    },
    {
        "name": "Livemint Markets",
        "url": "https://www.livemint.com/rss/markets",
        "weight": 0.9,
    },
    {
        "name": "Business Standard Markets",
        "url": "https://www.business-standard.com/rss/markets-106.rss",
        "weight": 0.9,
    },
]


def is_recent_news(pub_date_str, hours=24):
    """
    Check if news article is from the last N hours
    
    Args:
        pub_date_str: Published date string from RSS feed
        hours: Number of hours to consider as "recent" (default 24)
    
    Returns:
        bool: True if recent, False if old
    """
    try:
        now = datetime.now(IST)
        cutoff = now - timedelta(hours=hours)
        
        # Try to parse the date string
        # RSS feeds use various formats, feedparser handles most
        parsed_date = feedparser._parse_date(pub_date_str)
        if parsed_date:
            pub_datetime = datetime(*parsed_date[:6])
            # Make timezone aware
            pub_datetime = IST.localize(pub_datetime)
            
            if pub_datetime < cutoff:
                return False
            return True
    except Exception as e:
        logger.debug(f"Date parse error: {e}")
        # If can't parse date, include it (benefit of doubt)
        return True
    
    return True


def get_all_news():
    """
    Fetch news from RSS feeds
    Only includes articles from the last 24 hours
    
    Returns:
        dict: {
            'articles': list of articles,
            'sentiment': overall sentiment
        }
    """
    articles = []
    total_fetched = 0
    filtered_out = 0
    
    for feed_config in NEWS_FEEDS:
        try:
            feed = feedparser.parse(feed_config['url'])
            
            for entry in feed.entries[:10]:  # Check up to 10 articles per feed
                total_fetched += 1
                pub_date = entry.get('published', '')
                
                # Filter: Only include articles from last 24 hours
                if not is_recent_news(pub_date, hours=24):
                    filtered_out += 1
                    logger.debug(f"Filtered old article: {entry.get('title', '')[:50]} ({pub_date})")
                    continue
                
                article = {
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'published': pub_date,
                    'source': feed_config['name'],
                    'weighted_score': 0  # Neutral
                }
                articles.append(article)
                
                # Stop after 5 recent articles per feed
                if len([a for a in articles if a['source'] == feed_config['name']]) >= 5:
                    break
                    
        except Exception as e:
            logger.error(f"Error fetching {feed_config['name']}: {e}")
    
    logger.info(f"Fetched {total_fetched} articles, filtered {filtered_out} old articles, kept {len(articles)} recent")
    
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
