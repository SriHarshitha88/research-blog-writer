from duckduckgo_search import DDGS
from typing import List

def get_trending_topics() -> List[str]:
    """
    Get trending topics using DuckDuckGo search.
    Returns a list of trending topics.
    """
    try:
        with DDGS() as ddgs:
            # Get trending topics
            trends = list(ddgs.news(
                keywords="technology AI innovation",
                region="wt-wt",
                safesearch="off",
                time="d"
            ))
            
            # Extract and format trending topics
            trending_topics = [
                f"{item['title']} - {item['source']}"
                for item in trends[:5]  # Get top 5 trends
            ]
            
            return trending_topics
    except Exception as e:
        print(f"Error fetching trends: {e}")
        return [
            "The Future of AI in Education",
            "Latest Developments in Machine Learning",
            "Impact of AI on Healthcare",
            "Ethical Considerations in AI Development",
            "AI and the Future of Work"
        ]  # Fallback topics 