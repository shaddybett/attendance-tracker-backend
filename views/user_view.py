
from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse
from flask_bcrypt import Bcrypt
from models import db, User, Role

bcrypt = Bcrypt()

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if email is None or password is None:
            if email is None:
                return make_response(jsonify({'error': 'Email is required'}), 400)
            elif password is None:
                return make_response(jsonify({'error': 'Password is required'}), 400)

        if password == '': 
            return make_response(jsonify({'error': 'Enter you password'}), 400)
        if email == '':
            return make_response(jsonify({'error': 'Enter your email'}), 400)

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            role = Role.query.filter_by(id=user.role_id).first()
            user_dict = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'department': user.department,
                'course': user.course,
                'phone_number': user.phone_number,
                'role': role.role_name
            }
            return make_response(jsonify(user_dict), 200)
        else:
            return make_response(jsonify({'error': 'Incorrect email or password'}), 401)



class AddTeacher(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, required=True)
        parser.add_argument('last_name', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('department', type=str, required=True)
        parser.add_argument('course', type=str, required=True)
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('role_id', type=int, required=True)
        data = parser.parse_args(strict=True) 

        exists = User.query.filter_by(email=data.email).first()
        if exists:
            return make_response(jsonify({'error': 'Email already in use'}), 403)
        if any(value == '' or value is None for value in data.values()):
            return make_response(jsonify({'error': 'Fill in all the forms'}), 400)
        new_teacher = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            department=data.department,
            course=data.course,
            password=bcrypt.generate_password_hash(data.email).decode('utf-8'),
            phone_number=data.phone_number,
            role_id=data.role_id
        )
        db.session.add(new_teacher)
        db.session.commit()
        return make_response(jsonify({'message': f'{data.first_name} added successfully  "department":{data.department}  "course":{data.course}'}), 200)


class AddStudent(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, required=True)
        parser.add_argument('last_name', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('course', type=str, required=True)
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('role_id', type=int, required=True)
        data = parser.parse_args(strict=True)

        exists = User.query.filter_by(email=data.email).first()
        if exists:
            return make_response(jsonify({'error': 'Email already in use'}), 403)

        new_student = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            course=data.course,
            password=bcrypt.generate_password_hash(data.password).decode('utf-8'),
            phone_number=data.phone_number,
            role_id=data.role_id
        )
        db.session.add(new_student)
        db.session.commit()
        return make_response(jsonify({'message': f'{data.first_name} added successfully  "course":{data.course} '}), 200)


# class GetStudents (Resource):
#     def get(self):
#         data = request.get_json()
#         exists = User.query.get_all(User.student).all()
#         if exists:
#             return data,200
#         else:
#             return jsonify ({'message':'Students currently un available'}),404
        

# class GetTeachers (Resource):
#     def get(self):
#         data = request.get_json()
#         exists = User.query.get_all(User.student).all()
#         if exists:
#             return data,200
#         else:
#             return jsonify ({'message':'Teachers currently unavailable'}),404   

# class GetAdmin (Resource):
#     def get(self):
#         data = request.get_json()
#         exists = User.query.get_all(User.student).all()
#         if exists:
#             return data,200
#         else:
#             return jsonify ({'message':'Stu currently un available'}),404             