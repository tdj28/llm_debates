import random
import time
import os
from dotenv import load_dotenv
from app.pro import pro_ai
from app.con import con_ai
from app.research import research

from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

topic = "veganism"

# First round of research
research_results = research(topic)

debate_prep_for = debate_prep(research_results["for"], "for")
debate_prep_against = debate_prep(research_results["against"], "against")


# def debate(topic, duration=300):
#     print(f"Debate topic: {topic}")
    
#     # Initial research
#     pro_research = research(pro_ai, f"{topic} benefits")
#     con_research = research(con_ai, f"{topic} drawbacks")
    
#     # Determine who goes first
#     first_side = random.choice(["pro", "con"])
#     current_side = first_side
    
#     start_time = time.time()
#     while time.time() - start_time < duration:
#         if current_side == "pro":
#             response = pro_ai([
#                 SystemMessage(content=f"You are debating in favor of {topic}. Use the following research to support your argument: {pro_research}"),
#                 HumanMessage(content=f"Make your case for {topic}.")
#             ])
#             print(f"Pro: {response.content}")
#         else:
#             response = con_ai([
#                 SystemMessage(content=f"You are debating against {topic}. Use the following research to support your argument: {con_research}"),
#                 HumanMessage(content=f"Make your case against {topic}.")
#             ])
#             print(f"Con: {response.content}")
        
#         # Switch sides
#         current_side = "con" if current_side == "pro" else "pro"
        
#         # Optional additional research
#         if random.choice([True, False]):
#             if current_side == "pro":
#                 pro_research += "\n" + research(pro_ai, f"{topic} additional benefits")
#             else:
#                 con_research += "\n" + research(con_ai, f"{topic} additional drawbacks")
        
#         time.sleep(2)  # Add a small delay between responses

#     print("Debate concluded.")

# if __name__ == "__main__":
#     debate("veganism", duration=300)