"""
news_fetcher_scheduled.py
Scheduled news fetcher - fetches only 3 times per day (9 AM, 12 PM, 3 PM)
Caches news between scheduled times to avoid rate limits
"""

import os
import json
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import logging

# Import original fetchers
try:
    from news_fetcher_enhanced import get_newsapi_articles, score_sentiment
    USE_ENHANCED = True
except ImportError:
    USE_ENHANCED = False
    logger = logging.getLogger(__name__)
    logger.warning("news_fetcher_enhanced not available, using basic RSS only")

from news_fetcher import get_all_news as get_rss_news

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IST = pytz.timezone('Asia/Kolkata')

# Cache file location
CACHE_FILE = '.news_cache.json'

# Scheduled fetch times (IST)
FETCH_TIMES = [
    {'hour': 9, 'minute': 0},   # 9:00 AM
    {'hour': 12, 'minute': 0},  # 12:00 PM
    {'hour': 15, 'minute': 0}   # 3:00 PM
]

def should_fetch_news():
    """
    Check if we should fetch news now based on schedule
    Returns: (should_fetch: bool, reason: str)
    """
    now = datetime.now(IST)
    current_time = now.time()
    
    # Check if cache exists and is recent
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                last_fetch = datetime.fromisoformat(cache['last_fetch'])
                
                # If fetched within last 2.5 hours, use cache
                if (now - last_fetch).total_seconds() < 9000:  # 2.5 hours
                    time_since = (now - last_fetch).total_seconds() / 60
                    logger.info(f"Using cached news (fetched {time_since:.0f} minutes ago)")
                    return False, f"cached_{time_since:.0f}m_ago"
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
    
    # Check if current time is within 5 minutes of any scheduled time
    for fetch_time in FETCH_TIMES:
        scheduled = now.replace(hour=fetch_time['hour'], minute=fetch_time['minute'], second=0, microsecond=0)
        time_diff = abs((now - scheduled).total_seconds())
        
        # If within 5 minutes of scheduled time
        if time_diff < 300:  # 5 minutes = 300 seconds
            logger.info(f"Scheduled fetch time: {fetch_time['hour']}:{fetch_time['minute']:02d}")
            return True, f"scheduled_{fetch_time['hour']}:{fetch_time['minute']:02d}"
    
    # Not a scheduled time, use cache
    logger.info("Not a scheduled fetch time, using cache")
    return False, "not_scheduled"


def load_cached_news():
    """Load news from cache file"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                return cache.get('articles', []), cache.get('sentiment', {})
    except Exception as e:
        logger.error(f"Error loading cache: {e}")
    
    return [], {}


def save_news_cache(articles, sentiment):
    """Save news to cache file"""
    try:
        cache = {
            'last_fetch': datetime.now(IST).isoformat(),
            'articles': articles,
            'sentiment': sentiment
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
        logger.info(f"✓ Cached {len(articles)} articles")
    except Exception as e:
        logger.error(f"Error saving cache: {e}")


def get_all_news_scheduled():
    """
    Get news with scheduled fetching (9 AM, 12 PM, 3 PM only)
    Uses cache between scheduled times
    
    Returns:
        dict: {
            'articles': list of news articles,
            'sentiment': overall sentiment dict,
            'fetch_info': info about fetch/cache status
        }
    """
    should_fetch, reason = should_fetch_news()
    
    if should_fetch:
        # Scheduled fetch time - get fresh news
        logger.info("Fetching fresh news (scheduled time)...")
        
        articles = []
        
        # Try NewsAPI first if available
        if USE_ENHANCED:
            try:
                articles = get_newsapi_articles(max_articles=15)
            except Exception as e:
                logger.warning(f"NewsAPI error: {e}")
        
        # Fallback to RSS if NewsAPI fails or not available
        if not articles or len(articles) == 0:
            logger.info("Using RSS feeds for news")
            rss_data = get_rss_news()
            articles = rss_data.get('articles', [])
        
        # Calculate overall sentiment
        if articles:
            total_score = sum(a.get('weighted_score', 0) for a in articles)
            avg_score = total_score / len(articles) if articles else 0
            
            if avg_score > 0.1:
                sentiment_label = "BULLISH"
            elif avg_score < -0.1:
                sentiment_label = "BEARISH"
            else:
                sentiment_label = "NEUTRAL"
            
            sentiment = {
                'label': sentiment_label,
                'score': avg_score,
                'article_count': len(articles)
            }
        else:
            sentiment = {'label': 'NEUTRAL', 'score': 0, 'article_count': 0}
        
        # Save to cache
        save_news_cache(articles, sentiment)
        
        return {
            'articles': articles,
            'sentiment': sentiment,
            'fetch_info': {
                'status': 'fresh',
                'reason': reason,
                'time': datetime.now(IST).strftime('%H:%M:%S')
            }
        }
    
    else:
        # Use cached news
        articles, sentiment = load_cached_news()
        
        if not articles:
            # No cache available, use RSS as fallback
            logger.info("No cache available, using RSS feeds")
            rss_data = get_rss_news()
            articles = rss_data.get('articles', [])
            sentiment = rss_data.get('sentiment', {})
        
        return {
            'articles': articles,
            'sentiment': sentiment,
            'fetch_info': {
                'status': 'cached',
                'reason': reason,
                'next_fetch': get_next_fetch_time()
            }
        }


def get_next_fetch_time():
    """Get the next scheduled fetch time"""
    now = datetime.now(IST)
    
    for fetch_time in FETCH_TIMES:
        scheduled = now.replace(hour=fetch_time['hour'], minute=fetch_time['minute'], second=0, microsecond=0)
        
        if scheduled > now:
            return scheduled.strftime('%H:%M')
    
    # If all times passed today, return first time tomorrow
    return f"{FETCH_TIMES[0]['hour']}:{FETCH_TIMES[0]['minute']:02d} (tomorrow)"


# Alias for compatibility
get_all_news = get_all_news_scheduled


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING SCHEDULED NEWS FETCHER")
    print("="*70 + "\n")
    
    print(f"Current time: {datetime.now(IST).strftime('%H:%M:%S')}")
    print(f"Scheduled times: 9:00 AM, 12:00 PM, 3:00 PM\n")
    
    should_fetch, reason = should_fetch_news()
    print(f"Should fetch now: {should_fetch}")
    print(f"Reason: {reason}\n")
    
    if not should_fetch:
        print(f"Next fetch: {get_next_fetch_time()}\n")
    
    print("Fetching news...")
    news_data = get_all_news_scheduled()
    
    print(f"\nArticles: {len(news_data['articles'])}")
    print(f"Sentiment: {news_data['sentiment'].get('label', 'N/A')}")
    print(f"Fetch status: {news_data['fetch_info']['status']}")
    print(f"Reason: {news_data['fetch_info']['reason']}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")
