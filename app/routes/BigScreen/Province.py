from sqlalchemy import text

from flask import Blueprint

from app.models.province_box import ProvinceBox

pb = Blueprint('pb', __name__)

@pb.route('/getProvinceBox', methods=['GET'])
def getProvinceBox():
    # 查询数据库
    box = ProvinceBox.query.all()
    box_list = []
    for item in box:
        box_list.append({
            'province': item.p_name,
            'box_count': item.box_count
        })
    return {'box': box_list}