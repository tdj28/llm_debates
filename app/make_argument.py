import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.llms.openai import OpenAI
from research import research
import logging
from debate_data_manager import DebateDataManager
from pathlib import Path
from openai import OpenAI as OpenAI_RAW

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('../.env')

class OralArgument(BaseModel):
    """Represents an oral argument for a debate."""
    speech: str = Field(description="A conversational speech arguing for or against a topic")

def generate_oral_argument(topic: str, position: str, round_num: int, total_rounds: int, debate_transcript: str, additional_context: str = None):
    # Determine the type of round
    if round_num == 1:
        round_type = "opening"
    elif round_num == total_rounds:
        round_type = "conclusion"
    else:
        round_type = "rebuttal"

    # Step 1: Conduct research (only for opening and rebuttal rounds)
    bullet_points = research(topic, position, round_num, additional_context) if round_type != "conclusion" else ""
    
    # Step 2: Generate an oral argument
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    llm = OpenAI(api_key=api_key, temperature=0.7, model="gpt-4o-mini")

    argument_prompt = f"""
    You are participating in an oral debate {position} {topic}. This is the {round_type} round.
    Your task is to create a persuasive 1-2 minute speech that will be delivered in a conversational,
    back-and-forth format with your opponent.

    Here's the transcript of the debate so far:
    {debate_transcript}

    {"Use the following bullet points as the basis for your argument:" if round_type != "conclusion" else ""}
    {bullet_points}

    You may use these points to make your argument, but remember this is your 
    opinion and these bullet points are just useful to help you make your case,
    not shape your argument.

    {"Additional context to consider:" if additional_context else ""}
    {additional_context or ''}

    Remember that you are trying to be persuasive and that you are {position} {topic}.
    Your audience is well educated and will not fall for bullshit, tricks, fallacies,
    or fake data. Do not make anything up or they will throw rotten tomatoes at you.

    However, you are extremely passionate about your position and you will use your
    deep oratory skills to sway the audience to your side.

    {"For the opening statement, introduce your main arguments." if round_type == "opening" else ""}
    {"For the rebuttal, address the points made by your opponent and strengthen your position." if round_type == "rebuttal" else ""}
    {"For the conclusion, summarize your key points and make a final appeal to the audience." if round_type == "conclusion" else ""}

    Remember:
    - This is a spoken debate, so use language that sounds natural when spoken aloud.
    - Avoid formal section titles or numbering.
    - Use rhetorical devices and persuasive language appropriate for public speaking.
    - Keep the tone engaging and suitable for a live audience.
    - Limit the speech to about 1-2 minutes when spoken.
    - DO NOT REPEAT ARGUMENTS THAT HAVE ALREADY BEEN MADE. Bring new perspectives or deeper analysis to the debate.

    Ensure your argument is logical, persuasive, and delivered in a style suitable for an oral debate.
    You are passionate about being {position} {topic} and you have done your research. Now make
    your case to the live audience.

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
        argument_text = generated_argument.speech.strip()

        # Save the generated argument to the DebateDataManager
        manager = DebateDataManager()
        manager.add_argument(round_num, position, topic, argument_text)

        return argument_text

    except Exception as e:
        logger.error(f"Error generating oral argument: {str(e)}")
        return "Failed to generate oral argument due to an error."

def generate_moderator_speech(round_num: int, total_rounds: int, topic: str):
    if round_num == 1:
        return f"Welcome to our debate on the topic of {topic}. We'll begin with opening statements from both sides."
    elif round_num == total_rounds:
        return f"We've now reached the conclusion of our debate on {topic}. Both sides will present their closing arguments."
    elif round_num == total_rounds + 1:
        return f"This concludes our debate on {topic}. Thank you to both sides for their compelling arguments."
    else:
        return f"We'll now proceed to round {round_num} of our debate on {topic}."

def generate_and_save_speech(topic: str, position: str, round_num: int, total_rounds: int, debate_transcript: str, additional_context: str = None):
    if position == "moderator":
        debate_text = generate_moderator_speech(round_num, total_rounds, topic)
    else:
        debate_text = generate_oral_argument(topic, position, round_num, total_rounds, debate_transcript, additional_context)
    
    print(f"{position.capitalize()} - Round {round_num}:")
    print(debate_text)

    client = OpenAI_RAW()
    if position == "moderator":
        speech_file_path = Path(__file__).parent / f"speech_{round_num}_aaa.mp3"
    else:
        speech_file_path = Path(__file__).parent / f"speech_{round_num}_{position}.mp3"
    match position:
        case "for":
            voice = "fable"
        case "against":
            voice = "onyx"
        case "moderator":
            voice = "shimmer"
        case _:
            raise ValueError("Invalid position")

    with client.audio.speech.with_streaming_response.create(
        model="tts-1-hd",
        voice=voice,
        input=debate_text
    ) as response:
        response.stream_to_file(speech_file_path)

    logger.info(f"Speech for {position} position in round {round_num} saved to {speech_file_path}")
    return debate_text

def run_debate(topic: str, total_rounds: int = 5):
    manager = DebateDataManager()
    debate_transcript = ""

    for round_num in range(1, total_rounds + 1):
        # Moderator introduces the round
        moderator_text = generate_and_save_speech(topic, "moderator", round_num, total_rounds, debate_transcript)
        debate_transcript += f"\nModerator (Round {round_num}): {moderator_text}\n"

        # Generate and save arguments for both positions
        for_context = manager.get_argument(round_num - 1, "against") if round_num > 1 else None
        against_context = manager.get_argument(round_num - 1, "for") if round_num > 1 else None

        additional_context = """
        The opposing side made this claim in the previous round. Be skeptical of it and argue against it.
        Use facts and data to back up your argument: {}
        """ if round_num > 1 else None

        for_text = generate_and_save_speech(topic, "for", round_num, total_rounds, debate_transcript,
                                 additional_context.format(for_context) if additional_context else None)
        debate_transcript += f"\nFor (Round {round_num}): {for_text}\n"

        against_text = generate_and_save_speech(topic, "against", round_num, total_rounds, debate_transcript,
                                 additional_context.format(against_context) if additional_context else None)
        debate_transcript += f"\nAgainst (Round {round_num}): {against_text}\n"

    # Moderator concludes the debate
    final_moderator_text = generate_and_save_speech(topic, "moderator", total_rounds + 1, total_rounds, debate_transcript)
    debate_transcript += f"\nModerator (Conclusion): {final_moderator_text}\n"

    # Save the full debate transcript
    manager.save_full_transcript(topic, debate_transcript)

topic = "nonduality is not enlightenment"
total_rounds = 4

try:
    run_debate(topic, total_rounds)
except Exception as e:
    logger.error(f"An error occurred: {str(e)}")