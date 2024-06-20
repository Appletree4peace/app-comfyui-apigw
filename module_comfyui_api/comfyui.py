import websocket
import uuid
import json
import random
import urllib.request
import urllib.parse
from module_python_l10n_logger.logger_config import setup_logger

class ComfyUI:
    def __init__(self, api_server_url):
        self.api_server_url = api_server_url
        self.client_id = str(uuid.uuid4())
        self.logger = setup_logger(__name__)

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(self.api_server_url), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(self.api_server_url, url_values)) as response:
            return response.read()

    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self.api_server_url, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(self, ws, prompt, hand_picked_nids=[]):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        # Jeff: my refined version
        history = self.get_history(prompt_id)[prompt_id]

        # if a hand picked nids are passed, we only return those
        if len(hand_picked_nids):
            for nid in hand_picked_nids:
                node_output = history['outputs'][nid]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                output_images[nid] = images_output
        # Original version
        else:
            for o in history['outputs']:
                for node_id in history['outputs']:
                    node_output = history['outputs'][node_id]
                    if 'images' in node_output:
                        images_output = []
                        for image in node_output['images']:
                            image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                            images_output.append(image_data)
                    output_images[node_id] = images_output

        return output_images

    def call(self, prompt, hand_picked_nids=[]):
        ws = websocket.WebSocket()
        try:
            ws.connect("ws://{}/ws?clientId={}".format(self.api_server_url, self.client_id))
            images = self.get_images(ws, prompt, hand_picked_nids)
            output_images_data = []

            for node_id in images:
                for image_data in images[node_id]:
                    output_images_data.append(image_data)

            ws.close()
            return output_images_data

        except Exception as e:
            print("An error occurred:", e)

        finally:
            ws.close()

def generate_random_seed(length = 14):
    min_value = 10 ** (length - 1)
    max_value = (10 ** length) - 1
    return random.randint(min_value, max_value)