import websocket
import uuid
import json
import urllib.request
import urllib.parse
import requests
import random
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_ADDRESS = os.getenv("COMFY_URL", "http://127.0.0.1:8188")
CLIENT_ID = str(uuid.uuid4())

# !!! IMPORTANT: MATCH THESE IDs TO YOUR JSON WORKFLOW !!!
# Open text_to_image.json and find the node with "class_type": "CLIPTextEncode"
PROMPT_NODE_ID = "6" 
# Find the node with "class_type": "KSampler"
SEED_NODE_ID = "3"

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{SERVER_ADDRESS}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{SERVER_ADDRESS}/view?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen(f"{SERVER_ADDRESS}/history/{prompt_id}") as response:
        return json.loads(response.read())

def generate_image_task(positive_prompt, output_dir):
    # 1. Load Workflow JSON
    with open(os.getenv("WORKFLOW_FILE"), "r") as f:
        workflow = json.load(f)

    # 2. Modify Workflow (Inject Prompt & Random Seed)
    # Note: Structure depends on your specific JSON. Adjust keys if needed.
    workflow[PROMPT_NODE_ID]["inputs"]["text"] = positive_prompt
    workflow[SEED_NODE_ID]["inputs"]["seed"] = random.randint(1, 1000000000)

    # 3. Connect to WebSocket
    ws = websocket.WebSocket()
    ws.connect(f"ws://{SERVER_ADDRESS.split('//')[1]}/ws?clientId={CLIENT_ID}")

    # 4. Send to Queue
    prompt_response = queue_prompt(workflow)
    prompt_id = prompt_response['prompt_id']
    
    # 5. Wait for Completion
    print(f"Generating image for prompt: {positive_prompt}...")
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break # Execution finished
        else:
            continue

    # 6. Retrieve Image Filename
    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            for image in node_output['images']:
                filename = image['filename']
                subfolder = image['subfolder']
                folder_type = image['type']
                
                # Download image data
                image_data = get_image(filename, subfolder, folder_type)
                
                # Save locally
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(image_data)
                
                return os.path.abspath(filepath)
    
    return None