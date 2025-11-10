from google.adk import Agent
import os
from google import genai
from google.genai.types import GenerateContentConfig, Part
from urllib.parse import urlparse

def create_images(script: dict, character_images: dict) -> dict:
    """Creates start and ending images for each scene using character references."""
    print("Creating images...")
    images_dir = "/usr/local/google/home/mlad/adk-demo/images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    PROJECT_ID = "mlad-argo"
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

    image_paths = []
    for scene in script["script"]:
        if scene["scene_number"] == 1:
            # For the first scene, use the base images directly
            start_image_path = urlparse(character_images["characters"][0]["image_url"]).path
            end_image_path = urlparse(character_images["characters"][1]["image_url"]).path
        else:
            base_prompt = scene["description"].replace("Narrator: ", "") # Remove narrator prefix for image prompt
            style_suffix = ", in the style of a vintage photograph, with a warm, sepia-toned palette, cinematic, photorealistic, the characters are looking away from the camera, their faces are not clearly visible, detailed environment."
            
            before_prompt = f"Before the action: {base_prompt}{style_suffix}"
            after_prompt = f"After the action: {base_prompt}{style_suffix}"

            if scene["scene_number"] == 4:
                after_prompt = f"A wedding picture of John and Jane{style_suffix}"

            character_parts = []
            if "characters" in character_images:
                for character in character_images["characters"]:
                    if character["name"] in base_prompt:
                        image_path = urlparse(character["image_url"]).path
                        with open(image_path, "rb") as f:
                            character_image_data = f.read()
                        character_parts.append(Part.from_bytes(data=character_image_data, mime_type="image/jpeg"))

            def generate_image(prompt, output_path):
                contents = character_parts + [prompt]
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-image-preview",
                        contents=contents,
                        config=GenerateContentConfig(
                            response_modalities=["TEXT", "IMAGE"],
                        ),
                    )
                    if response.candidates and response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if part.inline_data:
                                with open(output_path, "wb") as f:
                                    f.write(part.inline_data.data)
                                return True
                    raise Exception("No image data in response")
                except Exception as e:
                    print(f"Failed to generate image for prompt '{prompt}': {e}")
                    with open(output_path, "w") as f:
                        f.write("Placeholder: Image generation failed.")
                    return False

            start_image_path = os.path.join(images_dir, f"scene_{scene['scene_number']}_start.png")
            end_image_path = os.path.join(images_dir, f"scene_{scene['scene_number']}_end.png")

            generate_image(before_prompt, start_image_path)
            generate_image(after_prompt, end_image_path)

        image_paths.append(
            {
                "scene_number": scene["scene_number"],
                "start_image_path": start_image_path,
                "end_image_path": end_image_path
            }
        )
    return {"images": image_paths}

image_agent = Agent(
    name="ImageAgent",
    tools=[create_images],
)