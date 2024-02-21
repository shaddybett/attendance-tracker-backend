
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

class User(db.Model,SerializerMixin):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String,nullable=False)
    last_name = db.Column(db.String,nullable=False)
    email = db.Column(db.String,nullable=False)
    department = db.Column(db.String,nullable=True)
    course = db.Column(db.String,nullable=True)
    password = db.Column(db.String,nullable=False)
    phone_number = db.Column(db.Integer,nullable=False)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'),nullable=False)


class Role(db.Model,SerializerMixin):
    __tablename__='roles'
    id = db.Column(db.Integer,primary_key=True)
    role_name=db.Column(db.String,nullable=False)


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
