from google.adk import Agent

def create_script(story: dict) -> dict:
    """Creates a script from a story."""
    print("Creating script...")
    # This is a placeholder. In a real implementation, this would
    # make a request to a large language model (e.g., Gemini).
    script_scenes = []
    for scene in story["scenes"]:
        script_scenes.append(
            {
                "scene_number": scene["scene_number"],
                "description": scene["description"],
                "dialogue": "This is a placeholder dialogue."
            }
        )
    return {"script": script_scenes}

script_agent = Agent(
    name="ScriptAgent",
    tools=[create_script],
)