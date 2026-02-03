from mcp.server.fastmcp import FastMCP
from client import generate_image_task
from utils import convert_image_to_webp
import os

# Initialize the MCP Server
mcp = FastMCP("ComfyUI-Agent")

@mcp.tool()
def generate_image(prompt: str) -> str:
    """
    Generates an image using a local ComfyUI instance based on a text prompt.
    Returns the absolute path to the generated image file.
    Use this when you need to create visual assets for a website or presentation.
    """
    output_folder = os.path.abspath("./output")
    try:
        image_path = generate_image_task(prompt, output_folder)
        if image_path:
            return f"Success! Image saved at: {image_path}"
        else:
            return "Error: Image generation failed or no output file found."
    except Exception as e:
        return f"Critical Error: {str(e)}"

@mcp.tool()
def optimize_image(file_path: str) -> str:
    """
    Converts an existing image file (PNG/JPG) to WebP format for better web performance.
    Args:
        file_path: The absolute path to the source image.
    """
    result = convert_image_to_webp(file_path)
    return f"Optimization complete. New file: {result}"

if __name__ == "__main__":
    mcp.run()