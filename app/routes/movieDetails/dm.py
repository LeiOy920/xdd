from flask import Blueprint, request

from app.utils.minIOUtils import MinIOStorage

dm = Blueprint('dm', __name__)

from app.config import minio_storage

@dm.route('/', methods=['POST'])
def index():
    try:
        id = request.json.get('id')
        file = minio_storage.get_file(object_name=f'comments{id}.txt', bucket_name = 'movie-reviews')  # 包含文件内容的BytesIO对象，或None（如果文件不存在）
        if file is not None:
            lines = [line.decode('utf-8') for line in file.readlines()]
            # 提取偶数行内容（索引从 0 开始，所以索引为奇数的行是偶数行）
            even_lines = [line.strip() for i, line in enumerate(lines) if i % 2 != 0]
            # 将偶数行内容合并成一个字符串
            text = '_,_'.join(even_lines)
            words = text.split('_,_')  # 按行分割
        else:
            words = []
    except (FileNotFoundError, AttributeError):
        words = []
    return {'data': words}

