from module_comfyui_api.comfyui import ComfyUI, generate_random_seed
from module_python_l10n_logger.logger_config import setup_logger
import json
import os
from flask import request, jsonify, send_file, make_response
from io import BytesIO

class you_and_me:
    def __init__(self, workflow, code):
        self.workflow = workflow
        self.code = code
        self.api_file = os.path.join('workflows', code, workflow['workflow_api_file'])
        self.logger = setup_logger(__name__)
    
    def send_prompt(self):
        you = request.form.get('you').replace('images/', '')
        me = request.form.get('me').replace('images/', '')
        prompt_positive = request.form.get('prompt_positive')
        prompt_negative = request.form.get('prompt_negative')

        with open(self.api_file) as f:
            prompt = json.load(f)
        prompt["12"]["inputs"]["image"] = you
        prompt["27"]["inputs"]["image"] = me
        prompt["113"]["inputs"]["text"] = prompt_positive
        prompt["196"]["inputs"]["text"] = prompt_negative
        prompt["209"]["inputs"]["seed"] = generate_random_seed()

        comfyui = ComfyUI(os.getenv('API_SERVER_URL'))

        try:
            self.logger.info("Calling ComfyUI API Server")
            image = comfyui.call(prompt, ["135"])[0]
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
