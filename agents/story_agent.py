from google.adk import Agent

def create_story(family_history: dict) -> dict:
    """Creates a story from family history data."""
    print("Creating story...")
    # This is a placeholder. In a real implementation, this would
    # make a request to a large language model (e.g., Gemini).
    return {
        "scenes": [
            {
                "scene_number": 1,
                "description": f"Narrator: Meet {family_history['records'][0]['name']}, born in {family_history['records'][0]['birth_place']}, a man of strength and skill. And this is {family_history['records'][1]['name']}, born in {family_history['records'][1]['birth_place']}, a woman of knowledge and grace."
            },
            {
                "scene_number": 2,
                "description": f"Narrator: {family_history['records'][0]['name']} was a blacksmith, his days filled with the clang of the hammer and the heat of the forge."
            },
            {
                "scene_number": 3,
                "description": f"Narrator: {family_history['records'][1]['name']} was a teacher, her days spent in a library, surrounded by books and knowledge."
            },
            {
                "scene_number": 4,
                "description": "Narrator: They met in a library, a place of quiet and books, where their love story began. Their journey together led them to a beautiful wedding, a celebration of their love."
            }
        ]
    }

story_agent = Agent(
    name="StoryAgent",
    tools=[create_story],
)
