from flask import Blueprint, jsonify, request
from app.models import data_1905

datatest = Blueprint('datatest', __name__)

@datatest.route('/')
def index():
    # 查询所有用户
    datas = data_1905.Data1905.query.all()
    data_list = [{"id": data.id, "data_name": data.data_name, "chart_type": data.chart_type, "data_file_path": data.data_file_path} for data in datas]
    return jsonify(data_list)