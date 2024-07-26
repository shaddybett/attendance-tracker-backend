import json
from flask import Flask, request, jsonify,Blueprint,make_response, Response
from flask_restful import Api,Resource,reqparse
from flask_bcrypt import Bcrypt
from sqlalchemy import func, cast, DATE
from models import db, User, Role, ClassStudent, Class as ClassModel, Attendance
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity


bcrypt = Bcrypt()

class ClassView(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user.role_id !=2:
            return make_response(jsonify({'error': 'Permission denied'}), 403)
        parser = reqparse.RequestParser()
        parser.add_argument('class_name',type=str,required = True)
        parser.add_argument('user_id',type=int,required=True)
        parser.add_argument('start_time',type=str,required=True)
        parser.add_argument('end_time',type=str,required=True)
        parser.add_argument('start_date',type=str,required=True)
        parser.add_argument('end_date',type=str,required=True)
        data = parser.parse_args(strict=True)

        exists = ClassModel.query.filter_by(class_name=data.class_name).first()
        if exists:
            return make_response(jsonify({'error':'Class already exists'}),403)
        if any(value == '' or value is None for value in data.values()):
            return make_response(jsonify({'error': 'Fill in all forms'}),400)

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
        
        return jsonify(new_class.to_dict())

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        classes = ClassModel.query.filter_by(user_id=user_id).all()
        classes_data = [class_.to_dict() for class_ in classes]
        return jsonify(classes_data)
    @jwt_required()
    def patch(self, class_id):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user.role_id !=2 and user.role_id !=1:   
            return make_response(jsonify({'error': 'Permission denied'}), 403)
        data = request.get_json()
        
        class_ = ClassModel.query.filter_by(id=class_id).first()
        
        if class_:
            for attr in data:
                setattr(class_, attr, data[attr])
                
                db.session.add(class_)
                db.session.commit()
                
            return make_response(class_.to_dict(), 200)
        else:
            return jsonify({'error': 'Class not found'})

    @jwt_required()
    def delete(self, class_id):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user.role_id !=2 and user.role_id !=1:   
            return make_response(jsonify({'error': 'Permission denied'}), 403)
        user_id = get_jwt_identity()
        class_id = int(class_id)  # Convert class_id to integer

        class_ = ClassModel.query.get(class_id)
        if class_ and class_.user_id==user_id:
            db.session.delete(class_)
            db.session.commit()
            return jsonify({'message': f'Class deleted successfully'})
        else:
            return jsonify({'error': 'Class not found'})

class ClassStudentResource(Resource):
    @jwt_required()
    def post(self, class_id):
            id = get_jwt_identity()
            user = User.query.filter_by(id=id).first()
            
            if user.role_id !=2 and user.role_id !=1:   
                return make_response(jsonify({'error': 'Permission denied'}), 403)
            
            data = request.get_json()
            student = User.query.filter_by(email=data['email']).first()
            
            if not student:
                return make_response(jsonify({'error': 'Student not found'}), 404)

            exists = ClassStudent.query.filter_by(class_id=class_id, user_id=student.id).first()
            if exists:
                return make_response(jsonify({'error': 'Student already exists in class'}), 401)

            class_student = ClassStudent(class_id=class_id, user_id=student.id)
            db.session.add(class_student)
            db.session.commit()
            return make_response(jsonify({'message': f'{student.first_name} added successfully'}), 201)

    @jwt_required()
    def delete(self, class_id):    
        id = get_jwt_identity()
        user = User.query.filter_by(id=id).first()
        if user.role_id !=2 and user.role_id !=1:   
            return make_response(jsonify({'error': 'Permission denied'}), 403)
        
        data = request.get_json()
        student_id = data['student_id']
        class_student = ClassStudent.query.filter_by(class_id=class_id, user_id=student_id).first()

        if class_student:
            db.session.delete(class_student)
            db.session.commit()
            return jsonify({'message': 'Student removed from class successfully'})
        else:
            return make_response(jsonify({'error': 'Student not found in class'}), 404)

class AttendanceResource(Resource):
    @jwt_required()
    def post(self, class_id):
        # data = request.get_json()
        student_id = get_jwt_identity()
        # status = data.get('status')  # 'Present', 'Absent' or 'Late'
        # date = data.get('date')

        # Check if the class exists
        class_exists = ClassModel.query.filter_by(id=class_id).first()
        if not class_exists:
            return jsonify({'error': 'Class does not exist!'})
        
        # Check if the student exists in the school
        student_exists = User.query.filter_by(id=student_id).first()
        if not student_exists:
            return jsonify({'error' : 'Student does not exist in the school!'})
        
        # Check if student is enrolled in the class
        student_in_class = ClassStudent.query.filter_by(
            class_id=class_id,
            user_id=student_id
        ).first()

        if not student_in_class:
            return jsonify({'error': 'Student not enrolled in this class!'})

        today = datetime.today().date()
        # Check for existing attendance recored for the same day
        existing_attendance = Attendance.query.filter(
            Attendance.class_id==class_id,
            Attendance.student_id==student_id,
            cast(Attendance.created_at, DATE) == today
        ).first()
        
        print(existing_attendance)

        if existing_attendance:
            response_data = {'error': 'Attendance already marked for this student in this class!'}
            return json.dumps(response_data), 409

        attendance = Attendance(class_id=class_id, student_id=student_id, status="present")
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({'message': 'Attendance marked successfully'})

class ClassDetails(Resource):
    def get(self, class_id, details_date):
        class_ = ClassModel.query.filter_by(id=class_id).first()
        
        if not class_:
            return jsonify({'error': 'Class not found'})
        
        class_start_time_str = class_.start_time.strftime("%H:%M:%S")
        class_start_time = datetime.strptime(class_start_time_str, '%H:%M:%S').time()

        students = []
        for student in class_.students:     
            student_attendance = Attendance.query.filter(
                Attendance.class_id == class_id,
                Attendance.student_id == student.id,
                func.DATE(Attendance.created_at) == details_date  # Comparing only the dates
            ).first()
            if student_attendance:
                attendance_datetime = student_attendance.created_at
                # Combine the date part of attendance_datetime with class_start_time
                attendance_datetime_with_start_time = datetime.combine(attendance_datetime.date(), class_start_time)
                time_difference = abs(attendance_datetime - attendance_datetime_with_start_time)
                
                # Check if the time difference is within 15 minutes
                if time_difference <= timedelta(minutes=15):
                    attendance_status = 'Present' if attendance_datetime.weekday() <= 5 else 'Weekend'
                    time_in = student_attendance.created_at.strftime("%H:%M")
                elif attendance_datetime.time() >= class_.end_time:
                    attendance_status = 'Absent' if attendance_datetime.weekday() <= 5 else 'Weekend'
                    time_in = student_attendance.created_at.strftime("%H:%M")
                else:
                    attendance_status = 'Late' if attendance_datetime.weekday() <= 5 else 'Weekend'
                    time_in = student_attendance.created_at.strftime("%H:%M")
            else:
                # Check if it's a weekend
                if datetime.strptime(details_date, '%Y-%m-%d').weekday() >= 5:
                    attendance_status = 'Weekend'
                else:
                    attendance_status = 'Absent'
                time_in = '00:00'  

            student_details = {
                'id': student.id,
                'first_name': student.first_name, 
                'last_name': student.last_name, 
                'attendance_status': attendance_status,
                'time_in': time_in,
                'phone_number': student.phone_number,
                'email':student.email
            }
            students.append(student_details)
            
        present_students = sum(1 for student in students if student['attendance_status'] == 'Present')
        absent_students = sum(1 for student in students if student['attendance_status'] == 'Absent')
        late_students = sum(1 for student in students if student['attendance_status'] == 'Late')

        class_details = {
            'class_name': class_.class_name,
            'students': students,
            'present_students': present_students,
            'absent_students': absent_students,
            'late_students': late_students,
            'total_students': len(class_.students)
        }

        return Response(json.dumps(class_details), status=200, mimetype='application/json')

    