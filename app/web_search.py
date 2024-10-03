from duckduckgo_search import DDGS
from playwright.sync_api import sync_playwright
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv('../.env')

client = OpenAI()

class SearchResultEval(BaseModel):
    title: str
    href: str
    body: str
    evaluation: int

def web_search(topic, for_against):
    sources = []

    search_system_prompt = f"""
    You are a helpful assistant whose job is craft a search engine query.
     """
    
    search_content_prompt = f"""
    You are a graduate student whose advisor is about to debate {topic}.

    Your advisor is {for_against} this topic. 

    Return a search query that will find powerful information relevant to the topic that will
    help your advisor make their case {for_against} {topic}.
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": search_system_prompt},
            {
                "role": "user",
                "content": search_content_prompt
            }
        ]
    )

    search_query = completion.choices[0].message.content.strip().replace('"', '')
    print(f"Generated search query: {search_query}")

    results = DDGS().text(
        search_query,
        safesearch='off',
        timelimit='y',
        max_results=10
    )
    
    print(results)

    for i in results:
        print(i['title'])
        # if "wikipedia.org" in i['href']:
        #     pass
        # else:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(60000) 
                page.goto(i['href'])
                text = page.text_content("body")  # Extracts all text within the body tag
                browser.close()
        except:
            text = None


        system_prompt = f"""
        You are a helpful assistant that evaluates search results. 
        
        The topic under consideration is {topic}.

        Your advisor is {for_against} this topic. 

        We are scanning the web for information to use in an argument. 

        You will be given a search result and asked to evaluate it.

        If you think your advisor would find the result useful, you should give it an evaluation value of 1

        If you think the result is not useful, you should give it an evaluation value of 0

        evaluation should be 0 or 1

        return the evaluation as a number

        """

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"title: {i['title']} \n href: {i['href']} \n Body: {text}"
                }
            ],
            response_format=SearchResultEval,
        )

        if completion.choices[0].message.parsed.evaluation == 1:
            sources.append(
                {
                    "title": i['title'],
                    "href": i['href'],
                    "body": text
                }
            )

    return sources

# topic = "veganism"
# for_against = "for"

# sources = web_search(topic, for_against)

# print(sources)