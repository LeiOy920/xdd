from app.config import db
from sqlalchemy import Enum


class Person (db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(255))
    box_office_amount = db.Column(db.DECIMAL)
    movie_count = db.Column(db.Integer)
    age = db.Column(db.Integer)
    gender = db.Column(Enum("Male", "Female"))
    constellation = db.Column(db.String(255))
    graduate_school = db.Column(db.String(255))
    career = db.Column(db.Text)