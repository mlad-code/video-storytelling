from google.adk import Agent
import requests

def get_character_images(family_name: str) -> dict:
    """Fetches character image URLs and metadata from the MCP server."""
    print(f"Fetching character images and metadata for {family_name}...")
    response = requests.get(f"http://localhost:8000/mcp?family_name={family_name}")
    if response.status_code == 200:
        return {"characters": response.json()}
    else:
        return {"error": f"Failed to fetch character images: {response.status_code}"}

character_image_agent = Agent(
    name="CharacterImageAgent",
    tools=[get_character_images],
)