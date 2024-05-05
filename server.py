from prometheus_client import Gauge, start_http_server
import random
import time
from cryptography.fernet import Fernet

# # 模拟指标更新
# while True:
#     # 生成随机值
#     value = random.randint(0, 100)
    
#     # 设置指标的值
#     gauge_metric.set(value)
    
#     # 等待一段时间
#     time.sleep(1)

import time 
import json
import os,sys
from flask import Flask, flash, request, redirect, url_for,abort
from werkzeug.utils import secure_filename
import subprocess
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

drawings_metric = Gauge('drawings', 'Drawings metric')
hentai_metric = Gauge('hentai', 'Hentai metric')
neutral_metric = Gauge('neutral', 'Neutral metric')
porn_metric = Gauge('porn', 'Porn metric')
sexy_metric = Gauge('sexy', 'Sexy metric')

# 启动一个HTTP服务器，导出指标
start_http_server(8080)

with open("key.txt","rb") as f:
        key=f.read()

fernet = Fernet(key)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        abort(400)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        abort(400)
    if file and allowed_file(file.filename):
        encrypted_image = file.read()  # Read the encrypted image data
        # Decrypt the image data
        decrypted_image_data = fernet.decrypt(encrypted_image)
        filename = secure_filename(file.filename)
        file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(file_path, 'wb') as f:
            f.write(decrypted_image_data)
        return process_image(file_path)
    else:
        abort(400)
    
def run_shell_print(args, try_num:int = 1, retry_interval: int = 3, continue_on_error: bool = False,return_result: bool = False):
    while try_num > 0:
        print(args)
        assert isinstance(args, list) == False
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        result = ""
        for line in iter(process.stdout.readline, b''):
            print(line.decode(), end='')
            result += line.decode()
        return_code = process.wait()
        process.stdout.close()
        print()
        sys.stdout.flush()
        if return_code:
            try_num -= 1
            if try_num == 0:
                break
            time.sleep(retry_interval)
            print("retry exec shell command:")
            continue
        else:
            break
    if return_code and not continue_on_error:
        print(f"shell command return error code: {return_code}")
        sys.exit(-1)
    if return_result:
        return result

def process_image(file_path:str):
    run_shell_print(f'nsfw-predict --saved_model_path /root/mobilenet_v2_140_224 --image_source {file_path} > out',)
    with open('out', 'r') as file:
        first_line = file.readline()
        json_data = file.read()

    key=first_line.split()[0]

    # size = first_line.split(' ')[-1].strip('\n')
    # width, height = size.strip('()').split(', ')
    # width = int(width)
    # height = int(height)

    # 解析 JSON 数据
    data = json.loads(json_data)

    # 获取各个值
    drawings = data[key]['drawings']
    hentai = data[key]['hentai']
    neutral = data[key]['neutral']
    porn = data[key]['porn']
    sexy = data[key]['sexy']
    drawings_metric.set(drawings)
    hentai_metric.set(hentai)
    neutral_metric.set(neutral)
    porn_metric.set(porn)
    sexy_metric.set(sexy)
    
    print("drawings:", drawings)
    print("hentai:", hentai)
    print("neutral:", neutral)
    print("porn:", porn)
    print("sexy:", sexy)

    # os.remove(file_path)
    return "ok"


if __name__ == '__main__':
    app.run(debug=False,port=12138,host="0.0.0.0")
    