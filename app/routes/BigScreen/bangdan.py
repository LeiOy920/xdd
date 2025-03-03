from flask import Blueprint, request

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
