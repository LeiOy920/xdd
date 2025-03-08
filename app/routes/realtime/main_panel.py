from flask import Blueprint, request, make_response, jsonify
from sqlalchemy import func
from app.models.box_timely import BoxTimely
from app.config import db

mainpanel = Blueprint('mainpanel', __name__)


@mainpanel.route('/', methods=['POST','GET'])
def getPanelData():
    # 查询最新时间的票房数据，按票房金额降序排序
    data = BoxTimely.query. filter(BoxTimely.proportion.isnot(None)) \
        .order_by(func.cast(BoxTimely.today_box, db.Float).desc()) \
        .all()
    ranking_list = [
        {
            "id": item.id,
            "rank": item.id-1,
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
            "day4_box": item.day4_box

        }
        for item in data
    ]
    return jsonify(ranking_list)

