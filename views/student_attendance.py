import json
from datetime import datetime, timedelta
from flask import jsonify, Response
from flask_restful import Resource
from models import db, Attendance, User
from flask_jwt_extended import jwt_required, get_jwt_identity

class StudentAttendanceReport(Resource):
    @jwt_required()
    def get(self):
        student_id = get_jwt_identity()
        student = User.query.filter_by(id=student_id).first()
        today = datetime.today().date()
        
        attendance = []
        
        for class_ in student.classes:
            # Query the database to retrieve attendance records for the specified student and class
            attendance_records = Attendance.query.filter_by(student_id=student_id, class_id=class_.id).all()
            
            if not attendance_records:
                present_days = 0
                late_days = 0

            # Initialize counters for present, absent, and late days
            present_days = 0
            late_days = 0
            absent_days = 0
            
            # Calculate the total number of days from class start date to today excluding weekends
            total_days = self.get_total_weekdays(class_.start_date.date(), class_.end_date.date() if class_.end_date.date() <= today else today)
            # Iterate through attendance records to calculate attendance stats
            for record in attendance_records:
                status = self.determine_attendance_status(record.created_at, class_.start_time, class_.end_time)
                if status == 'Present':
                    present_days += 1
                elif status == 'Late':
                    present_days += 1
                    late_days += 1
                elif status == 'Absent':
                    absent_days += 1
                    
            # Prepare the attendance report
            start_date = class_.start_date
            end_date = class_.end_date if class_.end_date.date() <= today else today
            start_time = class_.start_time.strftime('%H:%M')  # Convert to string
            end_time = class_.end_time.strftime('%H:%M') 
            
            attendance_report = {
                'class_id': class_.id,
                'class_name': class_.class_name,
                'class_start': start_time,
                'class_end': end_time,
                'student_id': student_id,
                'present_days': present_days,
                'absent_days': (total_days - present_days) ,
                'late_days': late_days,
                'days_remaining': (class_.end_date.date() - today).days
            }
            
            attendance.append(attendance_report)
            
        json_data = json.dumps(attendance)
        
        # Create a Response object with the JSON data
        response = Response(json_data, status=200, mimetype='application/json')
        
        return response
    
    def get_total_weekdays(self, start_date, end_date):
        total_days = (end_date - start_date).days + 1  # Add 1 to include the end date
        
        # Count the number of weekdays within the date range
        weekdays = sum(1 for single_date in range(total_days)
                       if (start_date + timedelta(days=single_date)).weekday() < 5)
        
        return weekdays
    
    
    def determine_attendance_status(self,attendance_datetime, class_start_time, class_end_time):
        # Check if the attendance date falls on a weekend
        if attendance_datetime.weekday() >= 5:  # Saturday (5) or Sunday (6)
            return 'Weekend'  # Ignore attendance on weekends
        # Calculate the expected start time for attendance based on the date of attendance and class start time
        expected_start_time = datetime.combine(attendance_datetime.date(), class_start_time)

        # Calculate the time difference between the recorded attendance time and the expected start time
        time_difference = abs(attendance_datetime - expected_start_time)

        if time_difference <= timedelta(minutes=15):
            # If the time difference is within 15 minutes, student is present
            attendance_status = 'Present'
        elif time_difference >= timedelta(minutes=15) and attendance_datetime.time() >= class_start_time and attendance_datetime.time() <= class_end_time:
            attendance_status = 'Late'
        else:
            attendance_status = 'Absent'

        return attendance_status
