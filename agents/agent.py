from google.adk.apps import App
from google.adk.agents import Agent
from agents.history_agent import get_character_images
from agents.story_agent import create_story
from agents.script_agent import create_script
from agents.image_agent import create_images
from agents.video_agent import create_video

def generate_family_story_video(family_name: str) -> str:
    """Generates a family story video for the given family name."""
    print(f"Starting video generation for the {family_name} family...")

    # Run agents
    character_data = get_character_images(family_name)
    story = create_story({"records": character_data["characters"]})
    script = create_script(story)
    images = create_images(script, character_data)
    video_path = create_video(story, script, images)

    return video_path

root_agent = Agent(
    name="MainAgent",
    tools=[generate_family_story_video],
)

app = App(name="adk-demo", root_agent=root_agent)
