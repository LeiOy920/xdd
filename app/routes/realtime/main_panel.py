from flask import Blueprint, request, make_response, jsonify
from sqlalchemy.orm import aliased
from sqlalchemy import func, distinct
from app.models.box_timely import BoxTimely
from app.models.moviedetail import MovieDetail  # 导入MovieDetail模型
from app.config import db

mainpanel = Blueprint('mainpanel', __name__)

@mainpanel.route('/', methods=['POST','GET'])
def getPanelData():
    # 使用aliased给BoxTimely和MovieDetail创建别名，以防出现命名冲突
    box_alias = aliased(BoxTimely)
    movie_alias = aliased(MovieDetail)

    # 子查询：获取每个电影名称对应的唯一图片链接
    subquery = db.session.query(
        movie_alias.movie_name,
        movie_alias.movie_image,
        movie_alias.genre
    ).distinct().subquery()

    # 主查询：从BoxTimely表中获取票房数据，并通过movie_name字段与子查询结果连接
    query_result = db.session.query(
        box_alias.id,
        box_alias.movie_name,
        box_alias.today_box,
        box_alias.proportion,
        box_alias.slots_num,
        box_alias.slots_proportion,
        box_alias.average_person,
        box_alias.occupancy_rate,
        box_alias.release_days,
        box_alias.total_box,
        box_alias.day1_box,
        box_alias.day2_box,
        box_alias.day3_box,
        box_alias.day4_box,
        subquery.c.movie_image,
        subquery.c.genre
    ).\
        join(subquery, box_alias.movie_name == subquery.c.movie_name).\
        filter(box_alias.proportion.isnot(None)).\
        order_by(func.cast(box_alias.today_box, db.Float).desc()).\
        all()

    ranking_list = [
        {
            "id": item.id,
            "rank": item.id - 1,
            "movie_name": item.movie_name,
            "today_box": item.today_box,
            "proportion": item.proportion,
            "slots_num": item.slots_num,
            "slots_proportion": item.slots_proportion,
            "average_person": item.average_person,
            "occupancy_rate": item.occupancy_rate,
            "release_days": item.release_days,
            "total_box": item.total_box,
            "isStarred": False,
            "day1_box": item.day1_box,
            "day2_box": item.day2_box,
            "day3_box": item.day3_box,
            "day4_box": item.day4_box,
            "movie_image": item.movie_image,  # 现在可以直接访问image_url
            "genre": item.genre
        }
        for item in query_result
    ]

    return jsonify(ranking_list)