from flask import Blueprint
from sqlalchemy import func

from app.config import db
from app.models.map_data import MapData


map = Blueprint('map', __name__)


@map.route('/', methods=['POST'])
def getMapData():
    # 查询每个地区的平均评分
    avg_ratings = db.session.query(
        MapData.region,
        func.avg(MapData.rating).label('avg_rating')
    ).group_by(MapData.region).all()

    # 创建地区平均评分的字典
    region_avg_ratings = {region: round(float(avg_rating), 1) for region, avg_rating in avg_ratings}

    # 按rank升序获取所有数据，并按地区分组
    all_data = MapData.query.order_by(MapData.m_rank.asc()).all()

    # 按地区组织数据
    result = []
    region_movies = {}

    # 首先将电影按地区分组
    for data in all_data:
        if data.region not in region_movies:
            region_movies[data.region] = []

        # 添加该地区的电影信息
        movie_info = {
            'title': data.movie_name,  # 假设有title字段
            'rating': data.rating,
            'rank': data.m_rank,
            # 可以添加其他电影相关信息
        }
        region_movies[data.region].append(movie_info)

    # 构建最终结果
    for region, movies in region_movies.items():
        entry = {
            'name': region,
            'value': region_avg_ratings[region],  # 使用该地区的平均评分
            'movies': movies  # 包含该地区的所有电影信息
        }
        result.append(entry)
    return {'data': result}

