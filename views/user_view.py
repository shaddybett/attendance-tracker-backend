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

class AllStudents(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user.role_id !=1 and user.role_id !=2:
            return make_response(jsonify({'error': 'Permission denied'}), 403)
        students = User.query.filter_by(role_id=3).all()
        
        response = []
        for student in students:
                student_data = {
                    "student_id": student.id, 
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "email": student.email,
                    "course": student.course
                }
                response.append(student_data)

        return make_response(jsonify(response), 200)


class AllTeachers(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user.role_id !=1:
            return make_response(jsonify({'error': 'Permission denied'}), 403)

        teachers = User.query.filter_by(role_id = 2).all()
        response = []
        for teacher in teachers:
            teacher_data = {
                "teacher_id":teacher.id,
                "first_name": teacher.first_name,
                "last_name":teacher.last_name,
                "email":teacher.email,
                "department":teacher.department,
                "course":teacher.course,
                "phone_number":teacher.phone_number,
                "role_id":teacher.role_id
            }
            response.append(teacher_data)
        return make_response(jsonify(response),200)


class DeleteUsers(Resource):
    @jwt_required()
    def delete(self, teacher_id=None, student_id=None):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user.role_id != 1:
            return make_response(jsonify({'error': 'Permission denied'}), 403)
        
        if teacher_id:
            teacher = User.query.filter_by(id=teacher_id, role_id=2).first()
            if teacher:
                db.session.delete(teacher)
                db.session.commit()
                return make_response(jsonify({'message': f'Teacher {teacher.first_name} successfully deleted'}), 200)
            else:
                return make_response(jsonify({'error': 'Teacher not found'}), 404)

        if student_id:
            student = User.query.filter_by(id=student_id, role_id=3).first()
            if student:
                db.session.delete(student)
                db.session.commit()
                return make_response(jsonify({'message': f'Student {student.first_name} successfully deleted'}), 200)
            else:
                return make_response(jsonify({'error': 'Student not found'}), 404)

        return make_response(jsonify({'error': 'No user ID provided'}), 400)


class UpdateUser(Resource):
    @jwt_required()
    def patch(self,user_id):
        id = get_jwt_identity()
        user_to_update = User.query.filter_by(id=user_id).first()
        current_user = User.query.filter_by(id=id).first()

        if user_to_update is None:
            return make_response(jsonify({'error': 'User not found'}), 404)
        
        data = request.get_json()
        exists = User.query.filter_by(email=data['email']).first()
        if exists and exists.id != user_to_update.id:
            return make_response(jsonify({'error': 'Email exists'}), 401)
        if current_user.role_id == 1 and user_to_update.role_id != 1:
            
            for attr in data:
                setattr(user_to_update,attr,data[attr])
            db.session.commit()
            response_data = {
                key: value for key, value in user_to_update.to_dict().items() if key != 'password'
            }    
            return make_response(jsonify(response_data), 202)


        if (user_to_update.role_id == 2 and current_user.role_id == 2 and current_user.id == user_to_update.id) or (user_to_update.role_id == 3 and current_user.role_id == 2 ): 
            for attr in data:
                setattr(user_to_update,attr,data[attr])
            db.session.commit()
            response_data = {
                key: value for key, value in user_to_update.to_dict().items() if key != 'password'
            }    
            return make_response(jsonify(response_data), 202)
    
        if(user_to_update.id == current_user.id):
            for attr in data:
                setattr(user_to_update,attr,data[attr])
            db.session.commit()
            response_data = {
                key: value for key, value in user_to_update.to_dict().items() if key != 'password'
            }    
            return make_response(jsonify(response_data), 202)

        return make_response(jsonify({'error': 'Permission denied'}), 403)