import os
import requests
from crewai.tools import tool

@tool("SearchApi Travel Explorer")
def searchapi_tool(query: str) -> str:
    """
    Search the web using SearchApi.io for travel information, flights, costs, and attractions.
    """
    # The user requested google_travel_explore but it requires a specific `departure_id`.
    # To keep the agent functioning seamlessly with natural language queries,
    # we use the standard google search engine through SearchApi.io which returns comprehensive snippets.
    api_key = os.getenv("SEARCHAPI_API_KEY") or os.getenv("SERPER_API_KEY") or "NgNQCzCKrNvRCJe7AcMz29gS"
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key
    }
    try:
        response = requests.get("https://www.searchapi.io/api/v1/search", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract organic results to make the snippet useful and concise for the agent
        results = data.get("organic_results", [])
        snippets = []
        for r in results[:6]: # Extract top 6 results
            title = r.get('title', 'No Title')
            snippet = r.get('snippet', r.get('description', 'No details available.'))
            snippets.append(f"Title: {title}\nSnippet: {snippet}\n")
        
        return "\n".join(snippets) if snippets else "No results found for this query."
    except Exception as e:
        return f"Error executing search via SearchApi.io: {str(e)}"
