import os
import sys
from dotenv import load_dotenv
load_dotenv()
# Import your search function from title_finder.py
from title_finder import search_decision_title_by_number

import google.generativeai as genai

# --- Gemini API Setup ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Make sure to set this in your environment
if not GEMINI_API_KEY:
    print("Please set GEMINI_API_KEY environment variable.")
    sys.exit(1)
genai.configure(api_key=GEMINI_API_KEY)

class NajirExpertAgent:
    def __init__(self, case_number, project_id, location, engine_id):
        self.case_number = case_number
        self.project_id = project_id
        self.location = location
        self.engine_id = engine_id

        self.case_title = search_decision_title_by_number(
            case_number, project_id, location, engine_id
        )
        if self.case_title is None:
            raise ValueError(f"Case {case_number} not found.")

        self.system_prompt = (
            f"You are a legal expert. The title of the Supreme Court decision "
            f"{self.case_number} is:\n\n"
            f"{self.case_title}\n\n"
            f"Answer the user's questions about this case as best as you can, using only the information in the title above."
        )
        self.history = [
            {"role": "user", "parts": [self.system_prompt]}
        ]

        model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")
        self.chat = model.start_chat(history=self.history)

    def ask(self, user_message):
        self.history.append({"role": "user", "parts": [user_message]})
        response = self.chat.send_message(user_message)
        assistant_text = response.text.strip()
        self.history.append({"role": "model", "parts": [assistant_text]})
        return assistant_text

class NajirSessionManager:
    def __init__(self, project_id, location, engine_id):
        self.project_id = project_id
        self.location = location
        self.engine_id = engine_id
        self.agents = {}

    def get_agent(self, case_number):
        if case_number not in self.agents:
            try:
                agent = NajirExpertAgent(
                    case_number, self.project_id, self.location, self.engine_id
                )
                self.agents[case_number] = agent
            except ValueError as err:
                print(err)
                return None
        return self.agents[case_number]

if __name__ == "__main__":
    PROJECT_ID = "vesp-a581d"  # change as needed
    LOCATION = "global"
    ENGINE_ID = "najir-search_1745733029866"

    session = NajirSessionManager(PROJECT_ID, LOCATION, ENGINE_ID)

    print("Welcome to Najir Expert Agent (Gemini Edition)")
    print("Type 'exit' at any prompt to quit.\n")

    while True:
        case_number = input("Enter case number: ").strip()
        if case_number.lower() == "exit":
            break
        agent = session.get_agent(case_number)
        if not agent:
            continue
        while True:
            user_question = input(f"Your question about case {case_number}: ").strip()
            if user_question.lower() == "exit":
                break
            answer = agent.ask(user_question)
            print(f"NajirExpertAgent: {answer}\n")
        print()