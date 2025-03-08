import pandas as pd
from flask import Blueprint, request, make_response

from app.config import minio_storage
from app.models.moviedetail import MovieDetail
from app.models.rankings import Rankings

bd = Blueprint('bd', __name__)


@bd.route('/', methods=['POST'])
def getMapData():
    bangdan = request.get_json().get('bangdan')

    data = Rankings.query.filter_by(ranking_type=bangdan).order_by(Rankings.r_rank.asc()).all()

    ranking_list = []
    for item in data:
        ranking_list.append(f'''<li>
                    <span>{item.r_rank}</span>
                    <span>{item.movie_name}</span>
                    <span>{item.quantity}</span>
                    
            </li>''')

    return {'ranking': ''.join(ranking_list)}



@bd.route('/outputExcel', methods=['GET'])
def outputExcel():
    bangdan = request.args.get('bangdan')
    data = Rankings.query.filter_by(ranking_type=bangdan).order_by(Rankings.r_rank.asc()).all()


    columns = ['排名', '电影名', '评分' if bangdan == '豆瓣Top250' or bangdan == '猫眼电影Top100' else '票房(国内单位为万元；全球单位为亿元)']
    data_list = []

    for item in data:
        data_list.append((item.r_rank, item.movie_name, item.quantity))

    from app.utils.ExcelUtils import export_to_excel
    excel = export_to_excel( 'Sheet1', columns, data_list)

    response = make_response(excel.getvalue())

    # 设置Content-Type和Content-Disposition头信息
    response.headers['Content-Type'] = 'application/vnd.ms-excel'
    filename = f'{bangdan}.xlsx'
    response.headers['Content-Disposition'] = f'attachment; filename={filename.encode("utf-8").decode("latin-1")}'

    return response

@bd.route('/getTypeChart', methods=['POST'])
def getTypeChart():
    file = minio_storage.get_file(object_name='coming_tyep.xlsx',
                                  bucket_name='movie-analytics')  # 包含文件内容的BytesIO对象，或None（如果文件不存在）
    if file is not None:
        excel_data = pd.read_excel(file, sheet_name='Sheet1')
        type = excel_data.iloc[:, 0].str.strip().tolist()
        num = excel_data.iloc[:, 1].astype(int).tolist()
        return {'type': type,
                'num': num}
    else:
        return {}


@bd.route('/getRadarChart', methods=['POST'])
def getRadarChart():
    file = minio_storage.get_file(object_name='1905type_average_scores.xlsx',
                                  bucket_name='movie-analytics')  # 包含文件内容的BytesIO对象，或None（如果文件不存在）
    if file is not None:
        excel_data = pd.read_excel(file, sheet_name='Sheet1')
        type = excel_data.iloc[:, 0].str.strip().tolist()
        num = excel_data.iloc[:, 1].round(2).tolist()



        return {'SixMovie':
                    {
                        'type': type,
                        'num': num
                    },
                'DBmovie': getDBData(),
                'MYmovie': getMYData()
                }
    else:
        return {}


@bd.route('/getPrivilege', methods=['POST'])
def getPrivilege():
    movie_name = request.get_json().get('movie_name')
    data = Rankings.query.filter_by(movie_name = movie_name).all()
    return {'privileges': [item.ranking_type for item in data]}


def getDBData():
    data = Rankings.query.filter_by(ranking_type='豆瓣Top250').all()
    movie_names = [item.movie_name for item in data]
    movie_details = MovieDetail.query.filter(MovieDetail.movie_name.in_(movie_names)).all()
    from collections import defaultdict
    type_ratings = defaultdict(list)
    for movie in movie_details:
        genres = movie.genre.split()
        for genre in genres:
            type_ratings[genre].append(movie.douban_rating)
    average_ratings = {genre: round(sum(ratings) / len(ratings), 2) for genre, ratings in type_ratings.items()}
    return {'type': list(average_ratings.keys()),
            'num': list(average_ratings.values())}

def getMYData():
    data = Rankings.query.filter_by(ranking_type='猫眼电影Top100').all()
    movie_names = [item.movie_name for item in data]
    movie_details = MovieDetail.query.filter(MovieDetail.movie_name.in_(movie_names)).all()
    from collections import defaultdict
    type_ratings = defaultdict(list)
    for movie in movie_details:
        genres = movie.genre.split()
        for genre in genres:
            type_ratings[genre].append(next(item.quantity for item in data if item.movie_name == movie.movie_name))
    average_ratings = {genre: round(sum(map(float, ratings)) / len(ratings), 2) for genre, ratings in type_ratings.items()}
    return {'type': list(average_ratings.keys()),
            'num': list(average_ratings.values())}