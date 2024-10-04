import json
import os
from typing import List, Dict, Any
from pydantic import BaseModel

class Source(BaseModel):
    title: str
    href: str

class DebateRound(BaseModel):
    round: int
    position: str
    topic: str
    sources: List[Source]
    bullet_points: List[str]
    argument: str = ""

class DebateData(BaseModel):
    rounds: List[DebateRound] = []

class DebateDataManager:
    def __init__(self, file_path: str = "../debate_data.json"):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self) -> DebateData:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return DebateData(**data)
        return DebateData()

    def _save_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data.dict(), f, indent=2)

    def add_round(self, round_num: int, position: str, topic: str, sources: List[Dict[str, str]], bullet_points: List[str]):
        new_round = DebateRound(
            round=round_num,
            position=position,
            topic=topic,
            sources=[Source(**source) for source in sources],
            bullet_points=bullet_points
        )
        self.data.rounds.append(new_round)
        self._save_data()

    def add_argument(self, round_num: int, position: str, topic: str, argument: str):
        for round_data in self.data.rounds:
            if round_data.round == round_num and round_data.position == position and round_data.topic == topic:
                round_data.argument = argument
                self._save_data()
                return
        # If the round doesn't exist, create a new one with the argument
        new_round = DebateRound(
            round=round_num,
            position=position,
            topic=topic,
            sources=[],
            bullet_points=[],
            argument=argument
        )
        self.data.rounds.append(new_round)
        self._save_data()

    def get_round(self, round_num: int, position: str) -> Dict[str, Any]:
        for round_data in self.data.rounds:
            if round_data.round == round_num and round_data.position == position:
                return round_data.dict()
        return {}
    
    def save_full_transcript(self, topic: str, transcript: str):
        # You might want to create a new attribute in your data structure for this
        self.data.full_transcript = {
            "topic": topic,
            "transcript": transcript
        }
        self._save_data()

    def get_full_transcript(self, topic: str) -> str:
        if hasattr(self.data, 'full_transcript') and self.data.full_transcript['topic'] == topic:
            return self.data.full_transcript['transcript']
        return ""

    def get_argument(self, round_num: int, position: str) -> str:
        for round_data in self.data.rounds:
            if round_data.round == round_num and round_data.position == position:
                return round_data.argument
        return ""

    def get_all_rounds(self) -> List[Dict[str, Any]]:
        return [round_data.dict() for round_data in self.data.rounds]

    def clear_data(self):
        self.data = DebateData()
        self._save_data()

# Example usage
if __name__ == "__main__":
    manager = DebateDataManager()
    
    # Adding sample data
    manager.add_round(
        round_num=1,
        position="for",
        topic="veganism",
        sources=[
            {"title": "Health Benefits of Veganism", "href": "https://example.com/vegan-health"},
            {"title": "Environmental Impact of Veganism", "href": "https://example.com/vegan-environment"}
        ],
        bullet_points=[
            "Veganism reduces the risk of heart disease",
            "Plant-based diets have a lower environmental impact",
            "Ethical considerations for animal welfare"
        ]
    )

    # Adding an argument
    manager.add_argument(1, "for", "veganism", "Veganism is beneficial for health and the environment...")

    # Retrieving data
    round_data = manager.get_round(1, "for")
    print(json.dumps(round_data, indent=2))

    # Getting the argument
    argument = manager.get_argument(1, "for")
    print("Argument:", argument)