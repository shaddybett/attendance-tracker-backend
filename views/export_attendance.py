import csv
import io
from datetime import datetime, timedelta
from flask import jsonify, Response
from flask_restful import Resource
from sqlalchemy import func
from models import db, Class as ClassModel, Attendance


class AttendanceDownloadAPI(Resource):
    def get(self, class_id):
        class_ = ClassModel.query.filter_by(id=class_id).first()
        if not class_:
            return jsonify({'error': 'Class not found'})

        # Assuming attendance is recorded on the same day as the request
        today = datetime.today().date()
        return self.download_attendance(class_, today)

    def get_attendance_records(self, class_, today):
        class_start_time_str = class_.start_time.strftime("%H:%M:%S")
        class_start_time = datetime.strptime(class_start_time_str, '%H:%M:%S').time()

        attendance_records = []
        for student in class_.students:
            student_attendance = Attendance.query.filter(
                Attendance.class_id == class_.id,
                Attendance.student_id == student.id,
                func.DATE(Attendance.created_at) == today
            ).first()

            if student_attendance:
                attendance_datetime = student_attendance.created_at
                attendance_status = self.determine_attendance_status(attendance_datetime,class_start_time, class_.end_time)
                attendance_date = attendance_datetime.strftime("%Y-%m-%d %H:%M:%S")
            else:
                attendance_status = 'Absent'
                attendance_date = None

            student_details = {
                'Student ID': student.id,
                'First Name': student.first_name,
                'Last Name': student.last_name,
                'Attendance Status': attendance_status,
                'Attendance Date': attendance_date
            }
            attendance_records.append(student_details)

        return attendance_records

    def determine_attendance_status(self, attendance_datetime,class_start_time, class_end_time):
        if attendance_datetime.time() < class_end_time:
            if attendance_datetime.time() >= class_start_time:
                return 'Present' if (attendance_datetime - datetime.combine(attendance_datetime.date(), class_start_time)) <= timedelta(minutes=15) else 'Late'
            else:
                return 'Absent'
        else:
            return 'Absent'

    def generate_csv(self, data):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def generate_excel(self, data):
        # code to generate Excel format
        pass

    def download_attendance(self, class_, today, file_format='csv'):
        attendance_records = self.get_attendance_records(class_, today)
        if file_format == 'csv':
            data = self.generate_csv(attendance_records)
            mimetype = 'text/csv'
            filename_extension = '.csv'
        elif file_format == 'excel':
            data = self.generate_excel(attendance_records)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename_extension = '.xlsx'

        response = Response(data, mimetype=mimetype)
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_{today}{filename_extension}'
        return response
