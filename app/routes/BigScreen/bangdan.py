from flask import Blueprint, request, make_response

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
