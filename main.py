import subprocess
import time
from agents.agent import generate_family_story_video

def main():
    # Start the MCP server in the background
    mcp_server_process = subprocess.Popen(["python", "/usr/local/google/home/mlad/adk-demo/mcp_server.py"])
    time.sleep(2)  # Give the server a moment to start

    family_name = "Doe"

    # Run the main agent
    video_path = generate_family_story_video(family_name)

    print(f"Video created: {video_path}")

    # Stop the MCP server
    mcp_server_process.terminate()


if __name__ == "__main__":
    main()