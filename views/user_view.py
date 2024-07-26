import os
from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse
from flask_bcrypt import Bcrypt
from models import db, User, Role
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png','jpg','jpeg','webp'}
UPLOAD_FOLDER  = '/files'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        # parser.add_argument('course', type=str, required=True)
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
            password=bcrypt.generate_password_hash(data['email']).decode('utf-8'),
            phone_number=data.phone_number,
            role_id=2,
            # avatar_url=data.avatar_url
        )
        db.session.add(new_teacher)
        db.session.commit()
        return make_response(jsonify({'message': f'{data.first_name} added successfully'}), 200)

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
            role_id=3,
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
                    "phone_number": student.phone_number,
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
    def delete(self, id):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user.role_id != 1 and user.role_id != 2:
            return make_response(jsonify({'error': 'Permission denied'}), 403)
        
        user_to_delete = User.query.filter_by(id=id).first()
        
        if not user_to_delete:
            return make_response(jsonify({'error': 'User not found'}), 404)
        
        if user.role_id == 1 :
            db.session.delete(user_to_delete)
            db.session.commit()
            return make_response(jsonify({'message': f'{user_to_delete.first_name} successfully deleted'}), 200)

        if (user.role_id == 2 and user.id == user_to_delete.id) or (user_to_delete.role_id == 3 and user.role_id == 2 ): 
            db.session.delete(user_to_delete)
            db.session.commit()
            return make_response(jsonify({'message': f'{user_to_delete.first_name} successfully deleted'}), 200)

class UpdateUser(Resource):
    @jwt_required()
    def patch(self,user_id):
        id = get_jwt_identity()
        user_to_update = User.query.filter_by(id=user_id).first()
        current_user = User.query.filter_by(id=id).first()

        if user_to_update is None:
            return make_response(jsonify({'error': 'User not found'}), 404)
        
        data = request.form
        file = request.files.get('file-upload')
        
        if file:  # If file exists in request
            filename = secure_filename(file.filename)
            base_dir = os.path.abspath(os.path.dirname(__file__))
            upload_folder = 'media'  # Set the upload folder
            os.makedirs(upload_folder, exist_ok=True) 
            file.save(os.path.join(upload_folder, filename))  # Save file to file system
            file_url = os.path.join(upload_folder, filename)  # URL relative to the media folder
            user_to_update.avatar_url = file_url 

        exists = User.query.filter_by(email=data['email']).first()
        if exists and exists.id != user_to_update.id:
            return make_response(jsonify({'error': 'Email already exists'}), 401)
        
        if current_user.role_id == 1 and user_to_update.role_id != 1:
            self.update_user_attributes(user_to_update, data)  
            return make_response(jsonify(self.filter_user_data(user_to_update)), 202)

        if (user_to_update.role_id == 2 and current_user.role_id == 2 and current_user.id == user_to_update.id) or (user_to_update.role_id == 3 and current_user.role_id == 2 ): 
            self.update_user_attributes(user_to_update, data)
            return make_response(jsonify(self.filter_user_data(user_to_update)), 202)
    
        if(user_to_update.id == current_user.id):
            self.update_user_attributes(user_to_update, data)    
            return make_response(jsonify(self.filter_user_data(user_to_update)), 202)

        return make_response(jsonify({'error': 'Permission denied'}), 403)
    
    def update_user_attributes(self,user, data):
        for attr in data:
            if attr == 'password':
                setattr(user, attr, bcrypt.generate_password_hash(data[attr]).decode('utf-8'))
            else:
                setattr(user,attr,data[attr])

        db.session.commit()
    
    def filter_user_data(self,user):
        return {key: value for key, value in user.to_dict().items() if key != 'password'}
