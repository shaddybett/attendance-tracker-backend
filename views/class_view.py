from flask import Flask, request, jsonify,Blueprint,make_response
from flask_restful import Api,Resource
from flask_bcrypt import Bcrypt
from models import db, User, Role, ClassStudent, Class as ClassModel, Attendance
from datetime import datetime

class_bp = Blueprint('class_bp', __name__)


class ClassView(Resource):
    def post(self):
        data = request.get_json()

        new_class = ClassModel(
            class_name=data.get('class_name'), 
            user_id=data.get('user_id'),
            start_time = data.get('start_time'),
            end_time = data.get('end_time'),
            start_date = data.get('start_date'),
            end_date = data.get('end_date')
            )
        
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify({'message': f'Class {data.get("class_name")} created successfully'})

    def get(self):
        classes = Class.query.all()
        classes_data = [class_.to_dict() for class_ in classes]
        return jsonify(classes_data)

    def put(self, class_id):
        data = request.get_json()
        new_class_name = data.get('new_class_name')

        class_ = Class.query.get(class_id)
        if class_:
            class_.class_name = new_class_name
            db.session.commit()
            return jsonify({'message': f'Class name updated successfully'})
        else:
            return jsonify({'error': 'Class not found'})

    def delete(self, class_id):
        class_ = Class.query.get(class_id)
        if class_:
            db.session.delete(class_)
            db.session.commit()
            return jsonify({'message': f'Class deleted successfully'})
        else:
            return jsonify({'error': 'Class not found'})

class ClassStudent(Resource):
    def post(self, class_id):
        data = request.get_json()
        student_id = data.get('student_id')

        class_student = ClassStudent(class_id=class_id, student_id=student_id)
        db.session.add(class_student)
        db.session.commit()
        
        return jsonify({'message': 'Student added to class successfully'})

    def delete(self, class_id, student_id):
        class_student = ClassStudent.query.filter_by(class_id=class_id, student_id=student_id).first()
        if class_student:
            db.session.delete(class_student)
            db.session.commit()
            return jsonify({'message': 'Student removed from class successfully'})
        else:
            return jsonify({'error': 'Student not found in class'})

class Attendance(Resource):
    def post(self, class_id):
        data = request.get_json()
        student_id = data.get('student_id')
        status = data.get('status')  # 'Present' or 'Absent'
        date = data.get('date')

        attendance = Attendance(class_id=class_id, student_id=student_id, status=status, date=date)
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({'message': 'Attendance marked successfully'})

class ClassDetails(Resource):
    def get(self, class_id):
        class_ = Class.query.get(class_id)
        if not class_:
            return jsonify({'error': 'Class not found'})

        total_students = len(class_.students)

        # Assuming attendance is recorded on the same day as the request
        today = datetime.today().date()

        present_students = Attendance.query.filter_by(
            class_id=class_id, date=today, status='Present'
        ).count()

        absent_students = Attendance.query.filter_by(
            class_id=class_id, date=today, status='Absent'
        ).count()

        class_details = {
            'class_name': class_.class_name,
            'total_students': total_students,
            'present_students': present_students,
            'absent_students': absent_students,
        }

        return jsonify(class_details)