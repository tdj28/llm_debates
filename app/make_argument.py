import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.llms.openai import OpenAI
from research import research  # Import the research function from the previous file
import logging

from pathlib import Path
from openai import OpenAI as OpenAI_RAW

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('../.env')

class OralArgument(BaseModel):
    """Represents an oral argument for a debate."""
    speech: str = Field(description="A conversational speech arguing for or against a topic")

def generate_oral_argument(topic: str, position: str, additional_context: str = None):
    # Step 1: Conduct research
    bullet_points = research(topic, position, additional_context)
    
    # Step 2: Generate an oral argument
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    llm = OpenAI(api_key=api_key, temperature=0.7, model="gpt-4o-mini")

    argument_prompt = f"""
    You are participating in an oral debate {position} {topic}. Your task is to create a 
    persuasive 1 minute or lessspeech that will be delivered in a conversational,
    back-and-forth format with your opponent.

    Use the following bullet points as the basis for your argument:

    {bullet_points}

    Additional context to consider: {additional_context or 'None provided'}

    Remember that you are trying to be pursuasive and that you are {position} {topic}.
    Your audience is well educated and will not fall for bullshit, tricks, fallacies,
    or fake data. Do not make anything up or they will throw rotten tomatoes at you.

    However, you are extremely passionate about your position and you will use your
    deep oratory skills to sway the audience to your side.

    Remember:
    - This is a spoken debate, so use language that sounds natural when spoken aloud.
    - Avoid formal section titles or numbering.
    - Use rhetorical devices and persuasive language appropriate for public speaking.
    - Keep the tone engaging and suitable for a live audience.
    - Limit the speech to about 1 minute when spoken.

    Ensure your argument is logical, persuasive, and delivered in a style suitable for an oral debate.
    You are passionate about being {position} {topic} and you have done your research. Now make
    your case to the live audience.
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

# def generate_debate(topic: str, additional_context: str = None):
#     logger.info(f"Generating debate on the topic: {topic}")
    
#     for_argument = generate_oral_argument(topic, "for", additional_context)
#     against_argument = generate_oral_argument(topic, "against", additional_context)

#     debate_script = f"""
# Moderator: Welcome to our debate on the topic of {topic}. We'll hear arguments from both sides. Let's begin with the argument in favor.

# Proponent: {for_argument}

# Moderator: Thank you for that argument. Now, let's hear from the opposition.

# Opponent: {against_argument}

# Moderator: Thank you both for your compelling arguments. This concludes our debate on {topic}.
# """
#     return debate_script.strip()

if __name__ == "__main__":
    topic = "veganism"
    position = "for"
    additional_context = ""  # You can modify this or set to None

    try:
        debate = generate_oral_argument(topic, position, additional_context)
        print(debate)
        client = OpenAI_RAW()
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
        model="tts-1-hd",
        voice="onyx",
        input=debate
        )

        response.stream_to_file(speech_file_path)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


