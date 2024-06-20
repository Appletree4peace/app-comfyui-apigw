from module_comfyui_api.comfyui import ComfyUI, generate_random_seed
from module_python_l10n_logger.logger_config import setup_logger
import json
import os
import random
import yaml
from flask import request, jsonify, send_file, make_response
from io import BytesIO

class instantid:
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
        face = request.form.get('face').replace('images/', '')

        pre_set = request.form.get('pre_set')
        pre_set_applylogo = True

        if pre_set != None and pre_set != "":
            config = self.config['art_styles'][pre_set]
            pose = config['pose_image']
            logo = config['logo_image']
            style = config['style_name']
            prompt_positive = config['prompt_positive']
            prompt_negative = config['prompt_negative']
            apply_logo = pre_set_applylogo
        else:
            pose = request.form.get('pose').replace('images/', '')
            logo = request.form.get('logo').replace('images/', '')
            style = request.form.get('style_name')
            prompt_positive = request.form.get('prompt_positive')
            prompt_negative = request.form.get('prompt_negative')
            apply_logo = request.form.get('apply_logo')

        #self.logger.info(f"pose is {pose}")
        #self.logger.info(f"logo is {logo}")
        #self.logger.info(f"style is {style}")
        #self.logger.info(f"prompt_positive is {prompt_positive}")
        #self.logger.info(f"prompt_negative is {prompt_negative}")
        #self.logger.info(f"apply_logo is {apply_logo}")

        with open(self.api_file) as f:
            prompt = json.load(f)
        prompt["28"]["inputs"]["seed"] = generate_random_seed()
        prompt["49"]["inputs"]["string"] = prompt_positive
        prompt["50"]["inputs"]["string"] = prompt_negative
        prompt["7"]["inputs"]["image"] = face
        prompt["8"]["inputs"]["image"] = pose
        prompt["5"]["inputs"]["style_name"] = style
        prompt["54"]["inputs"]["image"] = logo

        if apply_logo:
            pass
        else:
            del prompt["53"]
            prompt["9"]["inputs"]["images"][0] = "6"

        comfyui = ComfyUI(os.getenv('API_SERVER_URL'))

        try:
            self.logger.info("Calling ComfyUI API Server")
            if pre_set == None or pre_set == "":
                for key,config in self.config['art_styles'].items():
                    if config['style_name'] == style:
                        astyle = key
                        break
            else:
                astyle = pre_set

            response = comfyui.call(prompt, self.config['art_styles'][astyle]['return_node_ids'])
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
