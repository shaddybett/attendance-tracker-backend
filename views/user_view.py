from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse
from flask_bcrypt import Bcrypt
from models import db, User, Role
from flask_jwt_extended import jwt_required, get_jwt_identity

bcrypt = Bcrypt()


class AddTeacher(Resource):
    @jwt_required()
    

    def post(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user.role_id !=1:
            return make_response(jsonify({'error': 'Permission denied'}), 403)

        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, required=True)
        parser.add_argument('last_name', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('department', type=str, required=True)
        parser.add_argument('course', type=str, required=True)
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('role_id', type=int, required=True)
        # parser.add_argument('avatar_url',type=str,required=False)
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
            role_id=data.role_id,
            # avatar_url=data.avatar_url
        )
        db.session.add(new_teacher)
        db.session.commit()
        return make_response(jsonify({'message': f'{data.first_name} added successfully  "department":{data.department}  "course":{data.course}'}), 200)


class AddStudent(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user.role_id !=1 and user.role_id !=2:
            return make_response(jsonify({'error': 'Permission denied'}), 403)
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, required=True)
        parser.add_argument('last_name', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('course', type=str, required=True)
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('role_id', type=int, required=True)
        # parser.add_argument('avatar_url',type=str,required=False)
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
            role_id=data.role_id,
            # avatar_url=data.avatar_url
        )

        db.session.add(new_student)
        db.session.commit()
        response = {
            "student_id":new_student.id, 
            "first_name":data.first_name,
            "last_name":data.last_name,
            "email":data.email,
            "course":data.course,

        }
        return make_response(jsonify(response), 201)
