from flask import Blueprint

import app

dm = Blueprint('dm', __name__)
@dm.route('/', methods=['POST'])
def index():
    try:
        with open('./static/comments1.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # 提取偶数行内容（索引从 0 开始，所以索引为奇数的行是偶数行）
            even_lines = [line.strip() for i, line in enumerate(lines) if i % 2 != 0]
            # 将偶数行内容合并成一个字符串
            text = '_,_'.join(even_lines)
            words = text.split('_,_')  # 按行分割
    except FileNotFoundError:
        words = []
    return {'data': words}

if __name__ == '__main__':
    app.run(debug=True)