# title_finder_tool.py

from typing import Optional
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1

def arabic_to_devanagari(numstr):
    digits_map = str.maketrans("0123456789", "०१२३४५६७८९")
    return numstr.translate(digits_map)

def search_decision_title_by_number(
    decision_number: str,
    project_id: str,
    location: str,
    engine_id: str
) -> Optional[str]:
    nepali_number = arabic_to_devanagari(decision_number)
    print(f"Searching for decision_no: {nepali_number}")
    api_endpoint = f"{location}-discoveryengine.googleapis.com" if location != "global" else None
    client_options = ClientOptions(api_endpoint=api_endpoint) if api_endpoint else None
    client = discoveryengine_v1.SearchServiceClient(client_options=client_options)
    serving_config = (
        f"projects/{project_id}/locations/{location}/collections/default_collection/"
        f"engines/{engine_id}/servingConfigs/default_config"
    )
    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config,
        query=nepali_number,
        page_size=5,
    )
    response_iter = client.search(request)
    for resp in response_iter:
        data = resp.document.struct_data
        if "decision_no" in data and data["decision_no"] == nepali_number:
            print(f'Found: {data["title"]}')
            return data["title"]
    print("No exact match found.")
    return None

def title_finder_tool(
    case_number: str,
    project_id: str,
    location: str,
    engine_id: str,
    user_question: str
) -> str:
    """Answer a user question about a Nepali Supreme Court case using only the title."""
    title = search_decision_title_by_number(case_number, project_id, location, engine_id)
    if not title:
        return f"Case {case_number} not found."
    # NOTE: You can swap for Gemini, PaLM, OpenAI or any LLM here, just use the API directly
    try:
        from vertexai.preview.language_models import TextGenerationModel
        model = TextGenerationModel.from_pretrained("gemini-2.0-flash")
        prompt = (
            f"You are a legal expert. The title of the Supreme Court decision {case_number}: \n"
            f"{title}\n\n"
            f"Answer the following using only the title above:\n"
            f"{user_question}"
        )
        print("--- Tool: najir_expert_tool called ---")
        response = model.predict(prompt)
        return response.text.strip()
    except Exception as e:
        print("LLM error:", e)
        return "Sorry, an internal error occurred."
