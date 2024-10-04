import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.llms.openai import OpenAI
from app.research import research
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('../.env')

class OralArgument(BaseModel):
    """Represents an oral argument for a debate."""
    speech: str = Field(description="A concise, conversational speech arguing for or against a topic")

class ArgumentJudgement(BaseModel):
    """Represents a judgement of an argument's position."""
    position: str = Field(description="The judged position of the argument (for or against)")
    explanation: str = Field(description="Explanation of the judgement")


def generate_oral_argument(topic: str, position: str, round_num: int, total_rounds: int, opponent_argument: str = None):
    # Determine the type of round
    if round_num == 1:
        round_type = "opening"
    elif round_num == total_rounds:
        round_type = "conclusion"
    else:
        round_type = "rebuttal"

    # Step 1: Conduct research (only for opening and rebuttal rounds)
    bullet_points = research(topic, position, round_num) if round_type != "conclusion" else ""
    
    # Step 2: Generate an oral argument
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    llm = OpenAI(api_key=api_key, temperature=0.7, model="gpt-4-turbo-preview")

    argument_prompt = f"""
    You are participating in an oral debate. Your position is STRONGLY {position} the topic: "{topic}".
    This is the {round_type} round. Your task is to create a persuasive 30-45 second speech that will be 
    delivered in a conversational, back-and-forth format with your opponent.

    {"Here's your opponent's previous argument:" if opponent_argument else ""}
    {opponent_argument or ''}

    {"Use the following bullet points as the basis for your argument:" if round_type != "conclusion" else ""}
    {bullet_points}

    Remember:
    - You are STRONGLY {position} the topic. Do not argue for the other side under any circumstances.
    - Keep your argument concise, aiming for 30-45 seconds when spoken aloud.
    - This is a spoken debate, so use language that sounds natural when spoken.
    - Avoid formal section titles or numbering.
    - Use rhetorical devices and persuasive language appropriate for public speaking.
    - Keep the tone engaging and suitable for a live audience.
    - Ensure your argument is logical, persuasive, and delivered in a style suitable for an oral debate.
    - You are passionate about being {position} {topic} and you have done your research.

    {"For the opening statement, introduce your main arguments." if round_type == "opening" else ""}
    {"For the rebuttal, address the points made by your opponent and strengthen your position." if round_type == "rebuttal" else ""}
    {"For the conclusion, summarize your key points and make a final appeal to the audience." if round_type == "conclusion" else ""}

    Don't use "ladies and gentlemen" or "thank you" at the end of your argument.
    """

    argument_program = OpenAIPydanticProgram.from_defaults(
        output_cls=OralArgument,
        llm=llm,
        prompt_template_str=argument_prompt,
        verbose=True,
    )

    try:
        generated_argument = argument_program()
        return generated_argument.speech.strip()
    except Exception as e:
        logger.error(f"Error generating oral argument: {str(e)}")
        return "Failed to generate oral argument due to an error."

def revise_argument(original_argument: str, transcript: str, position: str, topic: str):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    llm = OpenAI(api_key=api_key, temperature=0.7, model="gpt-4-turbo-preview")

    revision_prompt = f"""
    You are participating in an oral debate. Your position is STRONGLY {position} the topic: "{topic}".
    You have just made the following argument:

    {original_argument}

    Here's the full transcript of the debate so far:

    {transcript}

    Your task is to revise your argument if necessary, ensuring that:
    1. You do not repeat points that have already been made in the debate.
    2. You maintain your position of being STRONGLY {position} the topic.
    3. You address any new points raised by your opponent that you haven't covered.
    4. Your argument remains concise, aiming for 30-45 seconds when spoken aloud.

    If no revision is necessary, return the original argument. Otherwise, provide a revised version.
    """

    revision_program = OpenAIPydanticProgram.from_defaults(
        output_cls=OralArgument,
        llm=llm,
        prompt_template_str=revision_prompt,
        verbose=True,
    )

    try:
        revised_argument = revision_program()
        return revised_argument.speech.strip()
    except Exception as e:
        logger.error(f"Error revising oral argument: {str(e)}")
        return original_argument
    
def judge_argument(argument: str, topic: str):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    llm = OpenAI(api_key=api_key, temperature=0.2, model="gpt-4-turbo-preview")

    judgement_prompt = f"""
    You are an impartial judge in a debate on the topic: "{topic}".
    Your task is to determine whether the following argument is for or against the topic:

    {argument}

    Analyze the argument carefully and decide if it is arguing for or against the topic.
    Provide your judgement along with a brief explanation of your reasoning.
    """

    judgement_program = OpenAIPydanticProgram.from_defaults(
        output_cls=ArgumentJudgement,
        llm=llm,
        prompt_template_str=judgement_prompt,
        verbose=True,
    )

    try:
        judgement = judgement_program()
        return judgement
    except Exception as e:
        logger.error(f"Error judging argument: {str(e)}")
        return ArgumentJudgement(position="unknown", explanation="Failed to judge the argument due to an error.")

def re_revise_argument(original_argument: str, transcript: str, position: str, topic: str, judgement: ArgumentJudgement, prior_arguments: list, sources: list):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    llm = OpenAI(api_key=api_key, temperature=0.7, model="gpt-4-turbo-preview")

    revision_prompt = f"""
    You are participating in an oral debate. Your position is STRONGLY {position} the topic: "{topic}".
    You have just made the following argument:

    {original_argument}

    However, your argument has been judged as being {judgement.position} the topic, which is incorrect.
    The judge's explanation is: {judgement.explanation}

    You MUST revise your argument to be STRONGLY {position} the topic. This is crucial.

    Here's the full transcript of the debate so far:

    {transcript}

    Your prior arguments in this debate:
    {' '.join(prior_arguments)}

    Sources you can use to support your argument:
    {' '.join(sources)}

    Your task is to revise your argument, ensuring that:
    1. You argue STRONGLY {position} the topic. This is non-negotiable.
    2. You do not repeat points that have already been made in the debate.
    3. You address any points raised by your opponent that you haven't covered.
    4. Your argument remains concise, aiming for 30-45 seconds when spoken aloud.
    5. You use the provided sources to support your argument if relevant.

    Remember, you are passionately {position} the topic "{topic}". Make sure your revised argument clearly reflects this position.
    """

    revision_program = OpenAIPydanticProgram.from_defaults(
        output_cls=OralArgument,
        llm=llm,
        prompt_template_str=revision_prompt,
        verbose=True,
    )

    try:
        revised_argument = revision_program()
        return revised_argument.speech.strip()
    except Exception as e:
        logger.error(f"Error re-revising oral argument: {str(e)}")
        return original_argument

def generate_and_validate_argument(topic: str, position: str, round_num: int, total_rounds: int, debate_transcript: str, opponent_argument: str = None, prior_arguments: list = None, sources: list = None):
    # Generate initial argument
    argument = generate_oral_argument(topic, position, round_num, total_rounds, opponent_argument)
    
    # Revise argument if not the first round
    if round_num > 1:
        argument = revise_argument(argument, debate_transcript, position, topic)
    
    # Judge the argument
    judgement = judge_argument(argument, topic)
    
    # If the judgement doesn't match the intended position, re-revise the argument
    if judgement.position.lower() != position.lower():
        logger.info(f"Argument judged as {judgement.position}, re-revising...")
        argument = re_revise_argument(argument, debate_transcript, position, topic, judgement, prior_arguments or [], sources or [])
        
        # Judge the re-revised argument (optional, for logging purposes)
        final_judgement = judge_argument(argument, topic)
        logger.info(f"Re-revised argument judged as {final_judgement.position}")
    
    return argument