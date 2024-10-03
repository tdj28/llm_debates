from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import Tool

ddg_search = DuckDuckGoSearchAPIWrapper()
wikipedia = WikipediaAPIWrapper()

tools = [
    Tool(
        name="DuckDuckGo Search",
        func=ddg_search.run,
        description="Useful for searching the internet for current information."
    ),
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description="Useful for getting detailed information on a topic."
    )
]