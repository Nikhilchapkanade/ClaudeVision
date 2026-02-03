import json
import random
import time
import requests
import os
from mcp.server.fastmcp import FastMCP

# --- CONFIGURATION ---
# PASTE THE URL FROM YOUR SCREENSHOT HERE (Keep the quotes!)
COMFY_URL = "https://unexcursive-reprovable-christi.ngrok-free.dev"
WORKFLOW_FILE = "workflow_api.json"
OUTPUT_DIR = os.path.abspath("./output")

mcp = FastMCP("ComfyUI-Cloud")

@mcp.tool()
def generate_image(prompt: str) -> str:
    """Generates an image using the Cloud ComfyUI server."""
    
    # 1. Load Workflow
    if not os.path.exists(WORKFLOW_FILE):
        return "Error: workflow_api.json not found in this folder."
        
    with open(WORKFLOW_FILE, "r") as f:
        workflow = json.load(f)

    # 2. Inject Prompt
    # Note: These IDs (6 and 3) are standard, but if it fails, we check your JSON.
    workflow["6"]["inputs"]["text"] = prompt
    workflow["3"]["inputs"]["seed"] = random.randint(1, 1000000000)

    # 3. Send to Cloud
    print(f"Sending prompt to Cloud...")
    try:
        p = {"prompt": workflow}
        response = requests.post(f"{COMFY_URL}/prompt", json=p)
        prompt_id = response.json().get('prompt_id')
    except Exception as e:
        return f"Connection Error: {str(e)}. Is Colab still running?"
    
    # 4. Wait for it to finish
    print("Waiting for generation...")
    while True:
        try:
            res = requests.get(f"{COMFY_URL}/history/{prompt_id}")
            if prompt_id in res.json():
                history_data = res.json()[prompt_id]
                break
        except:
            pass
        time.sleep(1)

    # 5. Download the Image
    try:
        # Find the image filename in the response
        outputs = history_data.get('outputs', {})
        for node_id in outputs:
            if 'images' in outputs[node_id]:
                image_info = outputs[node_id]['images'][0]
                filename = image_info['filename']
                
                # Download
                img_data = requests.get(f"{COMFY_URL}/view?filename={filename}").content
                
                if not os.path.exists(OUTPUT_DIR):
                    os.makedirs(OUTPUT_DIR)
                
                filepath = os.path.join(OUTPUT_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(img_data)
                    
                return f"Success! Image saved to: {filepath}"
    except Exception as e:
        return f"Error downloading image: {str(e)}"

if __name__ == "__main__":
    mcp.run()