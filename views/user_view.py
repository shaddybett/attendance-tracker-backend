
# from flask import Flask, request, jsonify,Blueprint,make_response
# from flask_restful import Api,Resource
# from flask_bcrypt import Bcrypt
# from dotenv import load_dotenv
# from flask_cors import CORS
# from models import db, User, Role
# from flask_migrate import Migrate

# user_bp = Blueprint('user_bp', __name__)
# bcrypt = Bcrypt()

# class Login(Resource):

#     def post(self):
#         data = request.get_json()
#         email = data.get('email')
#         password = data.get('password')

#         user = User.query.filter_by(email=email).first()
#         if user and bcrypt.check_password_hash(user.password, password):
#             role = Role.query.filter_by(id=user.role_id).first()
#             user_dict = {
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#                 'email': user.email,
#                 'department': user.department,
#                 'course': user.course,
#                 'phone_number': user.phone_number,
#                 'role': role.role_name
#             }
#             return make_response(jsonify(user_dict), 200)
#         else:
#             return make_response(jsonify({'error': 'Invalid email or password'}), 401)

  


# class AddTeacher(Resource):
#     def post(self):
#         data = request.get_json()
#         email = data.get('email')

#         exists = User.query.filter_by(email=email).first()
#         if exists:
#             return make_response(jsonify({'message': 'Email already in use'}), 403)
#         else:
#             new_teacher = User(
#                 first_name=data['first_name'],
#                 last_name=data['last_name'],
#                 email=email,
#                 department=data['department'],
#                 course=data['course'],
#                 password=bcrypt.generate_password_hash(data['email']).decode('utf-8'),
#                 phone_number=data['phone_number'],
#                 role_id=data['role_id']
#             )
#             db.session.add(new_teacher)
#             db.session.commit()
#             print(new_teacher.role_id)
#             return jsonify({'message': f'{data["first_name"]} added successfully'})

# class AddStudent(Resource):
#     def post(self):
#         data = request.get_json()
#         email = data.get('email')

#         exists = User.query.filter_by(email=email).first()
#         if exists:
#             return make_response(jsonify({'message': 'Email already in use'}), 403)
#         else:
#             new_student = User(
#                 first_name=data['first_name'],
#                 last_name=data['last_name'],
#                 email=email,
#                 course=data['course'],
#                 password=bcrypt.generate_password_hash(data['email']).decode('utf-8'),
#                 phone_number=data['phone_number'],
#                 role_id=data['role_id']
#             )
#             db.session.add(new_student)
#             db.session.commit()
#             return make_response(jsonify({'message': f' {data["first_name"]} added successfully'}))




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

        if not email or not password:
            return make_response(jsonify({'error': 'Email and password are required'}), 400)

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
            return make_response(jsonify({'error': 'Invalid email or password'}), 401)


class AddTeacher(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, required=True)
        parser.add_argument('last_name', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('department', type=str, required=True)
        parser.add_argument('course', type=str, required=True)
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('role_id', type=int, required=True)
        data = parser.parse_args(strict=True)  # strict=True will raise an error if a required field is missing

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
            password=bcrypt.generate_password_hash(data['email']).decode('utf-8'),
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
            password=bcrypt.generate_password_hash(data.email).decode('utf-8'),
            phone_number=data.phone_number,
            role_id=data.role_id
        )
        db.session.add(new_student)
        db.session.commit()
        return make_response(jsonify({'message': f'{data.first_name} added successfully  "course":{data.course} '}), 200)
