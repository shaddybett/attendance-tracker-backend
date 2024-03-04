import csv
import io
import pandas as pd
from datetime import datetime, timedelta
from flask import jsonify, Response
from flask_restful import Resource
from sqlalchemy import func
from models import db, Class as ClassModel, Attendance


class AttendanceDownloadAPI(Resource):
    def get(self, class_id, report_date):
        class_ = ClassModel.query.filter_by(id=class_id).first()
        if not class_:
            return jsonify({'error': 'Class not found'})

        return self.download_attendance(class_, report_date)

    def get_attendance_records(self, class_, report_date):
        class_start_time_str = class_.start_time.strftime("%H:%M:%S")
        class_start_time = datetime.strptime(class_start_time_str, '%H:%M:%S').time()

        attendance_records = []
        for student in class_.students:
            student_attendance = Attendance.query.filter(
                Attendance.class_id == class_.id,
                Attendance.student_id == student.id,
                func.DATE(Attendance.created_at) == report_date
            ).first()

            if student_attendance:
                attendance_datetime = student_attendance.created_at
                attendance_status = self.determine_attendance_status(attendance_datetime,class_start_time, class_.end_time)
                time_in = attendance_datetime.strftime("%H:%M:%S")
            else:
                # Check if it's a weekend
                if datetime.strptime(report_date, '%Y-%m-%d').weekday() >= 5:
                    attendance_status = 'Weekend'
                else:
                    attendance_status = 'Absent'
                time_in = '00:00'

            student_details = {
                'Student ID': student.id,
                'Name': student.first_name + ' ' + student.last_name,
                'Email': student.email,
                'Phone Number':student.phone_number,
                'Time In': time_in,
                'Attendance Status': attendance_status,
            }
            attendance_records.append(student_details)

        return attendance_records

    def determine_attendance_status(self, attendance_datetime,class_start_time, class_end_time):
        if attendance_datetime.weekday() >= 5:  # Check if it's Saturday or Sunday (Monday is 0)
            return 'Weekend'
        elif attendance_datetime.time() < class_end_time:
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
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    def download_attendance(self, class_, report_date, file_format='excel'):
        attendance_records = self.get_attendance_records(class_, report_date)
        if file_format == 'csv':
            data = self.generate_csv(attendance_records)
            mimetype = 'text/csv'
            filename_extension = '.csv'
        elif file_format == 'excel':
            data = self.generate_excel(attendance_records)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename_extension = '.xlsx'

        response = Response(data, mimetype=mimetype)
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_{report_date}{filename_extension}'
        return response
