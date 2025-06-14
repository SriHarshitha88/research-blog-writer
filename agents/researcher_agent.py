from crewai import Agent
from tools.search_tool import search_tool
from tools.trend_analyzer import get_trending_topics

researcher = Agent(
    role="SEO Research Specialist",
    goal="Conduct comprehensive research and SEO analysis for blog topics",
    backstory="""You are an expert SEO researcher with years of experience in content strategy.
    You excel at identifying trending topics, analyzing search patterns, and understanding user intent.
    Your research helps create content that ranks well and resonates with readers.""",
    tools=[search_tool],
    verbose=True,
    allow_delegation=False
) 