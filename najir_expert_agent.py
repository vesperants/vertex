# najir_expert_agent.py

from google.adk.agents import LlmAgent
from title_finder_tool import title_finder_retriever
from vertexai.preview.language_models import TextGenerationModel

MODEL = "gemini-2.0-flash"

def najir_expert_tool(
    case_number: str,
    project_id: str,
    location: str,
    engine_id: str,
    user_question: str,
) -> str:
    # Step 1: Retrieve only the title
    title = title_finder_retriever(
        case_number=case_number,
        project_id=project_id,
        location=location,
        engine_id=engine_id
    )
    if not title:
        return f"Sorry, case {case_number} not found."

    # Step 2: Use LLM to answer based on the title
    prompt = (
        f"You are a legal expert. The title of the Supreme Court decision {case_number} is:\n"
        f"{title}\n\n"
        f"Using only the information in the title, answer the following question:\n"
        f"{user_question}"
    )

    try:
        model = TextGenerationModel.from_pretrained(MODEL)
        response = model.predict(prompt)
        return response.text.strip()
    except Exception as e:
        print("LLM error:", e)
        return "Sorry, an internal error occurred."

# Attach the above function as the agent's tool
najir_expert_agent = LlmAgent(
    name="najir_expert_agent",
    model=MODEL,
    instruction=(
        "You are the Najir Expert. "
        "You answer questions about Nepali Supreme Court cases using ONLY the retrieved case title "
        "from the 'title_finder_retriever' tool."
    ),
    description="Legal expert using only case title for answers.",
    tools=[najir_expert_tool],  # <-- This is your generation tool
)

print(f"✅ najir_expert_agent loaded.")
