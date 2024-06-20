from flask import Flask, render_template, abort, request, jsonify#,  send_file, send_from_directory, safe_join, abort
from werkzeug.utils import secure_filename
from module_python_l10n_logger.logger_config import setup_logger
from io import BytesIO
import os
import subprocess
from workflow import Workflow
import shutil
import importlib
from PIL import Image

## App config
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic', 'webp'}
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE_MB', 20)) * 1024 * 1024

app = Flask(__name__)
GW_UPLOAD_FOLDER = os.getenv('GW_UPLOAD_FOLDER', 'uploads')
app.config['GW_UPLOAD_FOLDER'] = GW_UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['SHORTCUTS_FOLDER'] = os.getenv('SHORTCUTS_FOLDER', 'shortcuts')
app.config['WORKFLOWS'] = Workflow.load_config(open('workflows.yaml', 'r'))

## Logger
logger = setup_logger(__name__)

## Functions
def allowed_file(filename):
    result = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    logger.info(f"File '{filename}' allowed: {result}")
    return result

def convert_heic_to_png(heic_path):
    png_path = heic_path.rsplit('.', 1)[0] + '.png'
    convert_command = ["convert", heic_path, png_path]
    logger.info(f"Converting '{heic_path}' to PNG.")

    try:
        logger.info(f"Converting '{heic_path}' to '{png_path}'.")
        subprocess.run(convert_command, check=True)
        with open(png_path, 'rb') as f:
            output = BytesIO(f.read())
        return output
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during conversion: {e}")
        return None

def convert_webp_to_png(webp_path):
    png_path = webp_path.rsplit('.', 1)[0] + '.png'
    logger.info(f"Converting '{webp_path}' to PNG.")

    try:
        logger.info(f"Converting '{webp_path}' to '{png_path}'.")
        with Image.open(webp_path) as image:
            image.save(png_path, 'PNG')

        with open(png_path, 'rb') as f:
            output = BytesIO(f.read())
        return output
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        return None

def copy_default_files(source_folder, destination_folder):
    # Ensure the destination directory exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        logger.info(f"Created destination folder: {destination_folder}")

    # List all files in the source directory
    for file in os.listdir(source_folder):
        source_file_path = os.path.join(source_folder, file)
        
        # Check if the current item is a file (skip directories)
        if os.path.isfile(source_file_path):
            destination_file_path = os.path.join(destination_folder, file)
            
            # Copy file if it does not exist in the destination directory
            if not os.path.exists(destination_file_path):
                logger.info(f"Copying default file: {source_file_path} to {destination_file_path}")
                shutil.copyfile(source_file_path, destination_file_path)
            else:
                logger.info(f"File already exists: {destination_file_path}")
        else:
            logger.info(f"Skipped non-file item: {source_file_path}")

## @/wfs
@app.route('/wfs', methods=['GET'])
def list_workflows():
    workflows = app.config['WORKFLOWS']
    lists = []
    for code in workflows:
        workflow = workflows[code]
        lists.append({
            'name': workflow['name'],
            'code': code
        })
    return render_template('workflows.html.j2', workflow_list=lists)

## @/wf/<workflow>
@app.route('/wf/<code>', methods=['GET'])
def show_workflow_form(code):
    workflows = app.config['WORKFLOWS']
    # Check if the workflow_code exists in the workflows dictionary
    if code not in workflows:
        abort(404)  # Not found, return 404 error

    return render_template('workflow.html.j2', workflow=workflows[code], code=code)

## @/upload
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        logger.error("No file part")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['GW_UPLOAD_FOLDER'], filename) 
        file.save(file_path)
        logger.info("File uploaded: " + filename)

        if filename.rsplit('.', 1)[1].lower() == 'heic':
            convert_heic_to_png(file_path)
            filename = filename.rsplit('.', 1)[0] + '.png'
        elif filename.rsplit('.', 1)[1].lower() == 'webp':
            convert_webp_to_png(file_path)
            filename = filename.rsplit('.', 1)[0] + '.png'

        return filename, 200
    else:
        logger.error("File type not allowed")
        return jsonify({'error': 'File type not allowed'}), 400


## @/wf/<workflow>/submit
@app.route('/wf/<code>/submit', methods=['POST'])
def submit_workflow(code):
    workflows = app.config['WORKFLOWS']
    # Check if the workflow_code exists in the workflows dictionary
    if code not in workflows:
        logger.error(f"Workflow {code} does not exist.")
        abort(404)  # Not found, return 404 error

    # Copy default files over
    source_dir = os.path.join('workflows', code, 'images')
    dest_dir = app.config['GW_UPLOAD_FOLDER']
    copy_default_files(source_dir, dest_dir)

#    for file in workflows[code]['files']:
#        filename = os.path.basename(file['default'])
#        if not os.path.exists(os.path.join(app.config['GW_UPLOAD_FOLDER'], filename)):
#            logger.info('Copying default image file: ' + file['default'] + ' to ' + os.path.join(app.config['GW_UPLOAD_FOLDER'], filename))
#            shutil.copyfile(os.path.join('workflows', code, file['default']), os.path.join(app.config['GW_UPLOAD_FOLDER'], filename))

    module = importlib.import_module('.'.join(['workflows', code, 'class']))
    cls_name = code
    WorkFlowClass = getattr(module, cls_name)
    instance = WorkFlowClass(workflows[code], code)

    return instance.send_prompt()
    

## main()
if __name__ == '__main__':
    port = int(os.getenv('GW_PORT', 5000))
    logger.info(f"Starting server on port {port}.")
    app.run(debug=True, port=port)