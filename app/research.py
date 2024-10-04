from web_search import web_search
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import os
import logging

load_dotenv('../.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BulletPoint(BaseModel):
    """Represents a single bullet point."""
    point: str = Field(description="A concise bullet point summarizing a key piece of information")

class ResearchSummary(BaseModel):
    """Represents a summary of research results."""
    bullet_points: List[BulletPoint] = Field(description="A list of bullet points summarizing the research")

def research(topic: str, position: str, additional_context: str = None):
    search_results = web_search(topic, position, additional_context)

    # LLM setup
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    llm = OpenAI(api_key=api_key, temperature=0.7, model="gpt-4o-mini")

    all_bullet_points = []

    for result in search_results:
        condense_prompt = f"""
        You are a graduate student whose advisor is about to debate {topic}.

        Your advisor is {position} this topic. 

        An undergraduate student has researched the topic and found the following information:

        Title: {result.title}
        URL: {result.href}
        Content: {result.body[:1000]}  # Limiting to first 1000 characters

        Return a list of 2-3 bullet points that will help your advisor make their case {position} {topic}.

        {additional_context or ''}

        Each bullet point should be a concise summary of a key piece of information.
        """

        research_program = OpenAIPydanticProgram.from_defaults(
            output_cls=ResearchSummary,
            llm=llm,
            prompt_template_str=condense_prompt,
            verbose=True,
        )

        try:
            research_summary = research_program()
            all_bullet_points.extend(research_summary.bullet_points)
        except Exception as e:
            logger.error(f"Error condensing research result: {str(e)}")

    # Merge and deduplicate bullet points
    unique_points = list(set(point.point for point in all_bullet_points))
    
    # If there are too many points, we can summarize them further
    if len(unique_points) > 10:
        summarize_prompt = f"""
        You are a graduate student preparing a summary for your advisor's debate on {topic}.
        Your advisor is {position} this topic.

        You have compiled the following bullet points from your research:

        {' '.join([f"• {point}" for point in unique_points])}

        Please condense these into a final list of 7-10 most important and unique bullet points 
        that will help your advisor make their case {position} {topic}. In addition to providing
        the pithy points, try to include factual information such as statistics, quotes, relative 
        numbers, etc.

        {additional_context or ''}
        """

        final_summary_program = OpenAIPydanticProgram.from_defaults(
            output_cls=ResearchSummary,
            llm=llm,
            prompt_template_str=summarize_prompt,
            verbose=True,
        )

        try:
            final_summary = final_summary_program()
            unique_points = [point.point for point in final_summary.bullet_points]
        except Exception as e:
            logger.error(f"Error creating final summary: {str(e)}")

    # Convert the final list of points to a string of bullet points
    results = "\n".join([f"• {point}" for point in unique_points])
    
    return results

# Example usage
# if __name__ == "__main__":
#     topic = "veganism"
#     position = "against"

#     try:
#         condensed_research = research(topic, position)
#         print(condensed_research)
#     except Exception as e:
#         logger.error(f"An error occurred during research: {str(e)}")