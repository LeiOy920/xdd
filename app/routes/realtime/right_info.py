from flask import Blueprint, request, make_response, jsonify
from sqlalchemy import func
from app.models.box_timely import BoxTimely
from app.config import db
from datetime import datetime, timedelta
import base64

import requests


rightinfo = Blueprint('rightinfo', __name__)


@rightinfo.route('/', methods=['POST','GET'])
def getRightTimelyBox():
    # 查询最新时间的票房数据，按票房金额降序排序
    data = BoxTimely.query. filter(BoxTimely.id == 1).all()
    total_box_timely = [
        {
            "box": item.today_box
        }
        for item in data
    ]
    return (jsonify(total_box_timely))

@rightinfo.route('/date', methods=['POST','GET'])
def getDate():
    # 查询最新时间的票房数据，按票房金额降序排序
    num_days = 4
    today = datetime.now().date()
    dates = [today.strftime("%m/%d")]
    for i in range(1, num_days + 1):
        dates.append((today - timedelta(days=i)).strftime("%m/%d"))
    # print(dates)
    return dates
