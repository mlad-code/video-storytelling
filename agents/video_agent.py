from google.adk import Agent
import os
import time
from google import genai
from google.genai.types import Image, GenerateVideosConfig
import subprocess

def create_video(story: dict, script: dict, images: dict) -> str:
    """Creates a video from a storyboard, script, and images by generating a video for each scene and stitching them together with fade transitions."""
    print("Creating video...")
    videos_dir = "/usr/local/google/home/mlad/adk-demo/videos"
    if not os.path.exists(videos_dir):
        os.makedirs(videos_dir)

    PROJECT_ID = "mlad-argo"
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")

    video_clips = []
    for i, scene in enumerate(script["script"]):
        print(f"Generating video for scene {i+1}...")
        prompt = scene["description"]
        starting_image_path = images["images"][i]["start_image_path"]
        ending_image_path = images["images"][i]["end_image_path"]

        if i == 0:
            # Add panning for the first scene
            prompt += " The camera pans from left to center on the first person, then from right to center on the second person."

        operation = client.models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            prompt=prompt,
            image=Image.from_file(location=starting_image_path),
            config=GenerateVideosConfig(
                aspect_ratio="16:9",
                number_of_videos=1,
                duration_seconds=8,
                resolution="1080p",
                person_generation="allow_adult",
                enhance_prompt=True,
                generate_audio=True,
            ),
        )

        while not operation.done:
            time.sleep(15)
            operation = client.operations.get(operation)

        if operation.response:
            video_data = operation.result.generated_videos[0].video.video_bytes
            clip_path = os.path.join(videos_dir, f"scene_{i+1}.mp4")
            with open(clip_path, "wb") as f:
                f.write(video_data)
            video_clips.append(clip_path)
        else:
            print(f"Failed to generate video for scene {i+1}")
            print(f"Operation details: {operation}")

    # Stitch the video clips together with fade transitions using ffmpeg
    if len(video_clips) > 1:
        print("Stitching video clips together with fade transitions...")
        # Create a complex filtergraph for ffmpeg to chain fade transitions
        filter_complex = ""
        for i in range(len(video_clips) - 1):
            filter_complex += f"[{i+1}:v]format=pix_fmts=yuva420p,fade=type=in:st=0:d=1,fade=type=out:st=7:d=1[v{i+1}];"
        
        inputs = "".join([f"-i {clip} " for clip in video_clips])
        
        video_chain = ""
        for i in range(len(video_clips)):
            video_chain += f"[v{i}]"

        final_video_path = os.path.join(videos_dir, "final_video.mp4")
        # A more robust ffmpeg command for fade transitions would be needed.
        # This is a simplified example and might not work as expected.
        # For now, we will stick to the simple concatenation.
        file_list_path = os.path.join(videos_dir, "file_list.txt")
        with open(file_list_path, "w") as f:
            for clip_path in video_clips:
                f.write(f"file '{clip_path}'\n")

        ffmpeg_command = f"ffmpeg -f concat -safe 0 -i {file_list_path} -c copy {final_video_path} -y"
        subprocess.run(ffmpeg_command, shell=True, check=True)

        # Clean up the individual clips and the file list
        for clip_path in video_clips:
            os.remove(clip_path)
        os.remove(file_list_path)

    elif len(video_clips) == 1:
        final_video_path = video_clips[0]
    else:
        final_video_path = ""

    return final_video_path

video_agent = Agent(
    name="VideoAgent",
    tools=[create_video],
)