from duckduckgo_search import DDGS
from playwright.sync_api import sync_playwright
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import os
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.llms.openai import OpenAI
import logging

load_dotenv('../.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    """Represents a single search result."""
    title: str = Field(description="The title of the search result")
    href: str = Field(description="The URL of the search result")
    body: str = Field(description="The main content or body of the search result")

class SearchResultEval(BaseModel):
    """Evaluation of a search result."""
    evaluation: int = Field(description="Evaluation score: 1 for useful, 0 for not useful")

class SearchQuery(BaseModel):
    """Represents a search query."""
    query: str = Field(description="The generated search query")

def web_search(topic: str, for_against: str, additional_context: str = None):
    sources = []

    # LLM setup
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    llm = OpenAI(api_key=api_key, temperature=0.7, model="gpt-4o-mini")

    # Search query generation
    search_query_prompt = f"""
    You are a graduate student whose advisor is about to debate {topic}.
    Your advisor is {for_against} this topic. 
    Return a search query that will find powerful information relevant to the topic that will
    help your advisor make their case {for_against} {topic}.
    {additional_context or ''}
    """

    search_query_program = OpenAIPydanticProgram.from_defaults(
        output_cls=SearchQuery,
        llm=llm,
        prompt_template_str=search_query_prompt,
        verbose=True,
    )

    try:
        search_query_result = search_query_program()
        search_query = search_query_result.query
        logger.info(f"Generated search query: {search_query}")
    except Exception as e:
        logger.error(f"Error generating search query: {str(e)}")
        return sources

    # Perform search
    try:
        results = DDGS().text(
            search_query,
            safesearch='off',
            timelimit='y',
            max_results=10
        )
    except Exception as e:
        logger.error(f"Error performing DuckDuckGo search: {str(e)}")
        return sources

    # Process search results
    for result in results:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(60000)
                page.goto(result['href'])
                text = page.text_content("body")
                browser.close()
        except Exception as e:
            logger.warning(f"Skipping {result['href']}: Unable to fetch content")
            continue  # Skip to the next result if content can't be fetched

        # Evaluate search result
        eval_prompt = f"""
        You are a helpful assistant that evaluates search results. 
        The topic under consideration is {topic}.
        Your advisor is {for_against} this topic. 
        We are scanning the web for information to use in an argument. 
        {additional_context or ''}
        You will be given a search result and asked to evaluate it.
        If you think your advisor would find the result useful, you should give it an evaluation value of 1
        If you think the result is not useful, you should give it an evaluation value of 0
        evaluation should be 0 or 1
        You must return the evaluation as a number in the 'evaluation' field.

        Title: {result['title']}
        URL: {result['href']}
        Content: {text[:1000]}  # Limit content to first 1000 characters to avoid token limits
        """

        logger.info(f"Evaluating search result: {result['href']}")

        eval_program = OpenAIPydanticProgram.from_defaults(
            output_cls=SearchResultEval,
            llm=llm,
            prompt_template_str=eval_prompt,
            verbose=True,
        )

        try:
            eval_result = eval_program()

            if eval_result.evaluation == 1:
                sources.append(SearchResult(
                    title=result['title'],
                    href=result['href'],
                    body=text
                ))
        except Exception as e:
            logger.error(f"Error evaluating search result: {str(e)}")

    return sources

# # Example usage
# topic = "veganism"
# for_against = "for"

# try:
#     sources = web_search(topic, for_against)
#     print(sources)
# except Exception as e:
#     logger.error(f"An error occurred during web search: {str(e)}")