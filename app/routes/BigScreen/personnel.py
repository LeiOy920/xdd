import pandas as pd
from flask import Blueprint

from app.models.person import Person

personnel = Blueprint('personnel', __name__)


@personnel.route('/totalAndaverage', methods=['POST'])
def getTrend():
    data = Person.query.all()
    total_and_average = []
    for person in data:
        average = person.box_office_amount / person.movie_count
        total_and_average.append({'name': person.name, 'total': person.box_office_amount, 'average': average})
    return total_and_average


