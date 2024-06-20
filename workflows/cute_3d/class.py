from module_comfyui_api.comfyui import ComfyUI, generate_random_seed
from module_python_l10n_logger.logger_config import setup_logger
import json
import os
import random
import yaml
from flask import request, jsonify, send_file, make_response
from io import BytesIO

class cute_3d:
    def __init__(self, workflow, code):
        self.workflow = workflow
        self.code = code
        self.api_file = os.path.join('workflows', code, workflow['workflow_api_file'])
        self.logger = setup_logger(__name__)
        self.config = self.load_config()
    
    def load_config(self):
        path = os.path.join('workflows', self.code, 'config.yaml')
        with open(path, 'r') as file:
            return yaml.safe_load(file)
    
    def send_prompt(self):
        logo_overlay = True

        pre_set = request.form.get('pre_set')
        face = request.form.get('face').replace('images/', '')
        if pre_set != None and pre_set != "":
            config = self.config['poses'][pre_set]
            if 'pose_image' in config:
                pose = f'{config["pose_image"]}'
            else:
                pose = face
            prompt_positive = config['prompt_positive']
        else:
            config = self.config['poses'][pre_set]
            pose = request.form.get('pose').replace('images/', '')
            prompt_positive = request.form.get('prompt_positive')
        
        with open(self.api_file) as f:
            prompt = json.load(f)
        prompt["331"]["inputs"]["image"] = pose
        prompt["432"]["inputs"]["image"] = face
        prompt["447"]["inputs"]["text"] = prompt_positive
        prompt["647"]["inputs"]["seed"] = generate_random_seed()
        if logo_overlay == False:
            del prompt["620"]
            prompt["444"]["inputs"]["images"][0] = "425"
            prompt["444"]["inputs"]["images"][1] = 5
            prompt["456"]["inputs"]["images"][0] = "425"
            prompt["456"]["inputs"]["images"][1] = 5

        comfyui = ComfyUI(os.getenv('API_SERVER_URL'))

        try:
            self.logger.info("Calling ComfyUI API Server")
            response = comfyui.call(prompt, self.config['poses'][pre_set]['return_node_ids'])
            image = response[0]
        except Exception as e:
            self.logger.error(f"Error in comfyui.call(): {e}")
            return jsonify({"message": f"Error processing the file: {e}"}), 500

        if image is None:
            self.logger.error("comfyui.call() returned None")
            return jsonify({"message": "No image generated"}), 500

        # Convert images to byte streams for HTTP response
        img_io = BytesIO(image)
        img_io.seek(0)

        response = make_response(send_file(img_io, mimetype='image/png'))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response
