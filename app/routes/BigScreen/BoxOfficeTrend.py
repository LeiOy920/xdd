import pandas as pd
from flask import Blueprint

trend = Blueprint('trend', __name__)

from app.config import minio_storage

@trend.route('/box-office', methods=['POST'])
def getTrend():
    file = minio_storage.get_file(object_name='历年票房及2025预测.xlsx',
                                  bucket_name='movie-analytics')  # 包含文件内容的BytesIO对象，或None（如果文件不存在）
    if file is not None:
        excel_data = pd.read_excel(file, sheet_name='Sheet1')
        years = excel_data.iloc[:, 0].tolist()
        box_office = excel_data.iloc[:, 1].tolist()
        GDP = excel_data.iloc[:-1, 2].tolist()
        CPI = excel_data.iloc[:-1, 3].tolist()
        return {'year': years,
                'box_office': box_office,
                'GDP': GDP,
                'CPI': CPI}
    else:
        return {}


