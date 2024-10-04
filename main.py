from pathlib import Path
import logging
from openai import OpenAI as OpenAI_RAW
from app.make_argument import (
    generate_oral_argument,
    revise_argument,

)
from app.debate_data_manager import DebateDataManager
from dotenv import load_dotenv
import os

load_dotenv('.env')
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_moderator_speech(round_num: int, total_rounds: int, topic: str):
    if round_num == 1:
        return f"Welcome to our debate on the topic of {topic}. We'll begin with opening statements from both sides."
    elif round_num == total_rounds:
        return f"We've now reached the conclusion of our debate on the topic {topic}. Both sides will present their closing arguments."
    elif round_num == total_rounds + 1:
        return f"This concludes our debate on the topic {topic}. Thank you to both sides for their compelling arguments. We hope you the audience learned something today and will take it with you and make up your own minds on this topic."
    else:
        return f"We'll now proceed to round {round_num} of our debate on the topic {topic}."

def generate_and_save_speech(topic: str, position: str, round_num: int, total_rounds: int, debate_transcript: str, opponent_argument: str = None):
    if position == "moderator":
        debate_text = generate_moderator_speech(round_num, total_rounds, topic)
    else:
        debate_text = generate_oral_argument(topic, position, round_num, total_rounds, opponent_argument)
        if round_num > 1:
            debate_text = revise_argument(debate_text, debate_transcript, position, topic)
    
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

        for_text = generate_and_save_speech(topic, "for", round_num, total_rounds, debate_transcript, for_context)
        debate_transcript += f"\nFor (Round {round_num}): {for_text}\n"

        against_text = generate_and_save_speech(topic, "against", round_num, total_rounds, debate_transcript, against_context)
        debate_transcript += f"\nAgainst (Round {round_num}): {against_text}\n"

        # Save arguments
        manager.add_argument(round_num, "for", topic, for_text)
        manager.add_argument(round_num, "against", topic, against_text)

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