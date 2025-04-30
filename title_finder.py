from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1
from typing import Optional

# -- helpers --

def arabic_to_devanagari(numstr):
    # "10693" => "१०६९३"
    digits_map = str.maketrans("0123456789", "०१२३४५६७८९")
    return numstr.translate(digits_map)

def search_decision_title_by_number(
    decision_number: str,
    project_id: str,
    location: str,
    engine_id: str
) -> Optional[str]:
    # Convert to Devanagari numerals
    nepali_number = arabic_to_devanagari(decision_number)
    print(f"Searching for decision_no: {nepali_number}")

    # Set up client
    api_endpoint = f"{location}-discoveryengine.googleapis.com" if location != "global" else None
    client_options = ClientOptions(api_endpoint=api_endpoint) if api_endpoint else None
    client = discoveryengine_v1.SearchServiceClient(client_options=client_options)

    # Build serving config path
    serving_config = (
        f"projects/{project_id}/locations/{location}/collections/default_collection/"
        f"engines/{engine_id}/servingConfigs/default_config"
    )

    # Build the query (searches for the Devanagari number)
    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config,
        query=nepali_number,
        page_size=5,
    )

    response_iter = client.search(request)
    for resp in response_iter:
        # Each result is a SearchResponse.SearchResult
        # Your structData is stored in resp.document.struct_data
        data = resp.document.struct_data
        # Compare the decision_no field (as string)
        if "decision_no" in data and data["decision_no"] == nepali_number:
            print(f'Found: {data["title"]}')
            return data["title"]  # Or, if you want full record, return 'data'
    print("No exact match found.")
    return None

# ---- Example usage ----
if __name__ == "__main__":
    PROJECT_ID = "vesp-a581d"
    LOCATION = "global"  # "global", "us", "eu", etc
    ENGINE_ID = "najir-search_1745733029866"

    user_input = input("Enter decision number (Arabic numerals): ").strip()
    title = search_decision_title_by_number(
        user_input, PROJECT_ID, LOCATION, ENGINE_ID
    )
    if title:
        print("\nTITLE:", title)
    else:
        print("No result found for your input.")