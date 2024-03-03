from io import BytesIO
from flask import request, jsonify, Response
from flask_restful import Resource
from datetime import datetime, timedelta
from models import db, Attendance, User, Class as ClassModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.graph_objs as go


class StudentAttendanceReportPDF(Resource):
    def get(self,student_id, start_date, end_date):
        student = User.query.filter_by(id=student_id).first()

        # Convert the date strings to datetime objects
        start_date_time = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_time = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Validate the date range
        if end_date_time < start_date_time:
            return jsonify({'error': 'End date must be after start date'}), 400

        # Initialize counters for present, absent, and late days
        present_days = 0
        absent_days = 0
        late_days = 0

        # Calculate the number of days in the date range excluding weekends
        total_days = (end_date_time - start_date_time).days + 1
        weekends = set([5, 6])  # Saturday (5) and Sunday (6)
        weekdays = [start_date_time + timedelta(days=i) for i in range(total_days) if (start_date_time + timedelta(days=i)).weekday() not in weekends]

        # Iterate through each day in the date range
        for day in weekdays:
            # Query the database to check if attendance record exists for the student on the current day
            attendance_record = Attendance.query.filter_by(student_id=student_id).filter(db.func.date(Attendance.created_at) == day).first()

            if attendance_record:
                class_ = ClassModel.query.filter_by(id=attendance_record.class_id).first()
                status = self.determine_student_attendance(class_.start_time,class_.end_time, attendance_record.created_at)
                if status == 'Present':
                    present_days += 1
                elif status == 'Late':
                    late_days += 1
            else:
                absent_days += 1

        # Generate the PDF report
        pdf_buffer = self.generate_pdf_report(start_date_time, end_date_time, present_days, absent_days, late_days)

        # Return the PDF as a response
        return Response(pdf_buffer, mimetype='application/pdf', headers={'Content-Disposition': f'attachment; filename=attendance_report.pdf'})
    
    def determine_student_attendance(self,class_start_time, class_end_time, attendance_created_at):
        attendance_datetime = attendance_created_at
        # Combine the date part of attendance_datetime with class_start_time
        attendance_datetime_with_start_time = datetime.combine(attendance_datetime.date(), class_start_time)
        time_difference = abs(attendance_datetime - attendance_datetime_with_start_time)
        
        # Check if the time difference is within 15 minutes
        if time_difference <= timedelta(minutes=15):
            attendance_status = 'Present'
        elif time_difference >= timedelta(minutes=15) and attendance_datetime.time() >= class_start_time and attendance_datetime.time() <= class_end_time:
            attendance_status = 'Late'
        else:
            attendance_status = 'Absent'

        return attendance_status

    def generate_pdf_report(self, start_date_time, end_date_time, present_days, absent_days, late_days):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Add content to the PDF
        p.drawString(100, 750, "Attendance Report")
        p.drawString(100, 730, f"Date Range: {start_date_time} to {end_date_time}")
        p.drawString(100, 710, f"Present Days: {present_days}")
        p.drawString(100, 690, f"Absent Days: {absent_days}")
        p.drawString(100, 670, f"Late Days: {late_days}")

        # Draw a chart summarizing the information
        fig = go.Figure(data=[go.Pie(labels=['Present', 'Absent', 'Late'],
                                 values=[present_days, absent_days, late_days],
                                 hole=.3)])
    
        # Save the chart as an image
        fig.write_image("chart.png")

        # Add the chart image to the PDF
        p.drawImage("chart.png", 100, 450)

        p.showPage()
        p.save()

        buffer.seek(0)
        return buffer
