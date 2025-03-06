import base64

import requests
from flask import Blueprint, request

detail = Blueprint('detail', __name__)


@detail.route('/downloadImage', methods=['POST'])
def download_image():
    url = request.json.get('url')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }
    response = requests.get(url, headers=headers)  # 这个是请求图片
    image_base64 = base64.b64encode(response.content).decode('utf-8')
    return {'image': image_base64}


