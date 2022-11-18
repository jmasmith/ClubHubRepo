from flask_login import UserMixin
from . import db

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    memberCount = db.Column(db.Integer)
    type = db.Column(db.String(100))
    members = db.Column(db.String(500))

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(200))
    membership = db.Column(db.String(500))