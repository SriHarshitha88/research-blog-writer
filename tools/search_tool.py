from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from typing import Optional

class SearchTool(BaseTool):
    name: str = "Web Search"
    description: str = "Search the web for up-to-date information using DuckDuckGo"

    def _run(self, query: str, num_results: Optional[int] = 5) -> str:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: The search query
            num_results: Number of results to return (default: 5)
        
        Returns:
            Formatted search results as a string
        """
        try:
            with DDGS() as ddgs:
                # Perform the search
                results = list(ddgs.text(
                    query,
                    region="wt-wt",
                    safesearch="off",
                    max_results=num_results
                ))
                
                # Format results
                formatted_results = []
                for result in results:
                    formatted_results.append(
                        f"Title: {result['title']}\n"
                        f"Link: {result['link']}\n"
                        f"Description: {result['body']}\n"
                    )
                
                return "\n\n".join(formatted_results)
                
        except Exception as e:
            return f"Error performing search: {str(e)}"

search_tool = SearchTool() 