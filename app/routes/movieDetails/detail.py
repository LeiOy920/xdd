import base64

import requests
from flask import Blueprint, request
from sqlalchemy import or_

from app.models.moviedetail import MovieDetail
from app.models.sentiment_score import SentimentScore

detail = Blueprint('detail', __name__)


@detail.route('/getMovieDetails', methods=['GET'])
def getMovieDetails():
    id = request.args.get('id')
    movie_name = request.args.get('movie_name')



    if id is not None:
        movie_basic = MovieDetail.query.filter_by(id=id).first()
    else:
        movie_basic = MovieDetail.query.filter(or_(movie_name == movie_name)).first()

    if movie_basic is None:
        return {'msg': '电影不存在'}

    sentiment_score = SentimentScore.query.filter_by(m_id=movie_basic.id)




    




@detail.route('/downloadImage', methods=['POST'])
def download_image():
    url = request.json.get('url')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }
    response = requests.get(url, headers=headers)  # 这个是请求图片
    image_base64 = base64.b64encode(response.content).decode('utf-8')
    return {'image': image_base64}


