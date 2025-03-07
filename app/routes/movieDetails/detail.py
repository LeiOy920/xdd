import base64

import requests
from flask import Blueprint, request

from app.config import minio_storage
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
        print(movie_name)
        movie_basic = MovieDetail.query.filter(MovieDetail.movie_name == movie_name).first()

    if movie_basic is None:
        return {'msg': '电影不存在'}

    sentiment_score = SentimentScore.query.filter_by(m_id=movie_basic.id).first()

    return {
            'id': movie_basic.id,
            'movie_name': movie_basic.movie_name,
            'movie_image': movie_basic.movie_image,
            'director': movie_basic.director,
            'screenwriter': movie_basic.screenwriter,
            'release_date': movie_basic.release_date,
            'runtime': movie_basic.runtime,
            'production_country_region': movie_basic.production_country_region,
            'douban_rating': movie_basic.douban_rating,
            'also_known_as': movie_basic.also_known_as,
            'genre': movie_basic.genre.split(),
            'starring': movie_basic.starring.split() if movie_basic.starring else [],
            'ciyun_image': 'b.png',
            'sentiment_score': {'average_score': sentiment_score.average_score,
                              'total_references': sentiment_score.total_references,
                              'very_like': sentiment_score.very_like,
                              's_like': sentiment_score.s_like,
                              'normal': sentiment_score.normal,
                              'dislike': sentiment_score.dislike,
                              'very_dislike': sentiment_score.very_dislike}
        }








@detail.route('/downloadImage', methods=['POST'])
def download_image():
    url = request.json.get('url')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }
    response = requests.get(url, headers=headers)  # 这个是请求图片
    image_base64 = base64.b64encode(response.content).decode('utf-8')
    return {'image': image_base64}


@detail.route('/getWordCloud', methods=['GET'])
def getWordCloud():
    id = request.args.get('id')
    file = minio_storage.get_file(object_name=f'word_cloud_gold{id}.png', bucket_name='movie-wordclouds')
    if file is not None:
        image_base64 = base64.b64encode(file.read()).decode('utf-8')
    else:
        image_base64 = ''
    return {'image': image_base64}