
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model,SerializerMixin):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String,nullable=False)
    last_name = db.Column(db.String,nullable=False)
    email = db.Column(db.String,nullable=False,unique=True)
    department = db.Column(db.String,nullable=True)
    course = db.Column(db.String,nullable=True)
    avatar_url = db.Column(db.String,nullable=True)
    password = db.Column(db.String,nullable=False)
    phone_number = db.Column(db.String,nullable=False)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'),nullable=False)




class Role(db.Model,SerializerMixin):
    __tablename__='roles'
    id = db.Column(db.Integer,primary_key=True)
    role_name=db.Column(db.String,nullable=False)


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

class Class(db.Model, SerializerMixin):
    __tablename__ = 'classes'
    serialize_rules = ('-students',)
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    students = db.relationship('User', secondary='class_students', backref=db.backref('classes'))

class ClassStudent(db.Model):
    __tablename__ = 'class_students'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id',ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete='CASCADE'), nullable=False)

class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id',ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String, nullable=False)  # 'Present' or 'Absent'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
