from app.web_search import web_search

positions = [
    "for",
    "against"
]

research_results = {}

def research(topic):
    for position in positions:
        research_results[position] = web_search(topic, position)

    return research_results

# from app.tools import(
#     ddg_search, 
#     tools,
#     wikipedia
# )

# # topic, for_against

# def research(agent, topic):
#     agent.add_tools(tools)
#     agent.run(f"Provide a summary of the pros and cons of {topic}")


#     ddg_results = ddg_search.run(f"{topic} pros and cons")
#     wiki_results = wikipedia.run(topic)
#     print(f"DuckDuckGo: {ddg_results}\n\nWikipedia: {wiki_results}")
#     return f"DuckDuckGo: {ddg_results}\n\nWikipedia: {wiki_results}"