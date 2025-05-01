# najir_expert_agent.py

from vertexai.preview.agent.runtime import Agent

from title_finder_tool import title_finder_tool

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"  # Or whatever model string your platform expects

najir_expert_agent = Agent(
    model=MODEL_GEMINI_2_0_FLASH,   # Configure as your agent infra expects
    name="najir_expert_agent",
    instruction=(
        "You are the Najir Expert sub-agent. "
        "Your task is to answer questions about Nepali Supreme Court cases, "
        "using only the retrieved case title via the 'najir_expert_tool'."
    ),
    description="Handles legal questions about Supreme Court cases using only their title.",
    tools=[najir_expert_tool],
)

print(f"✅ Agent '{najir_expert_agent.name}' created using model '{MODEL_GEMINI_2_0_FLASH}'.")
