import pandas as pd
import csv
import json
from io import StringIO, BytesIO
import csv
from flask import jsonify, Response, request, make_response
from flask_restful import Resource
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from models import db, User

bcrypt = Bcrypt()
# ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
# UPLOAD_FOLDER  = '/files'


# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class AddStudentsFromFile(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        
        if user.role_id !=1 and user.role_id !=2:
            return make_response(json.dumps({'error': 'Permission denied'}), 403)
        
        if 'file-upload' not in request.files:
            print(request.files)
            return make_response(json.dumps({'error': 'No file part'}), 404)
        
        file = request.files['file-upload']
     
        if file.filename == '':
             return make_response(json.dumps({'error': 'No selected file'}), 404)

        if file:
            filename = secure_filename(file.filename)

            if filename.endswith('.csv'):
                # Read CSV data
                students, existing = self.parse_csv(file)
            elif filename.endswith('.xlsx'):
                # Read Excel data
                students, existing = self.parse_excel(file)
            else:
                return make_response(json.dumps({'error': 'Unsupported file type'}), 400)
             
            db.session.add_all(students)
            db.session.commit()
            
            data = {'msg': f'{len(students)} out of {len(students) + len(existing)} students created successfully', 'emails_in_use':existing}
            response_data = json.dumps(data)
            return Response(response_data, status=200, mimetype='application/json')
        else:
            return make_response(json.dumps({'error': 'Invalid file type'}), 400)
    
    def parse_csv(self, file):
        # Read the CSV data from the file-like object           
        csv_data = file.stream.read().decode('utf-8')
        
        students = []
        existing = []
        # Process CSV data
        csv_reader = csv.DictReader(StringIO(csv_data))
        
        for row in csv_reader:
            first_name = row['first_name']
            last_name = row['last_name']
            email = row['email']
            phone_number = row['phone_number']
            course = row['course']
            
            user = User.query.filter_by(email=email).first()
            
            if user:
                existing.append(email)
            else:
                student = User(
                    first_name=first_name,
                    last_name=last_name,
                    email = email,
                    phone_number=phone_number,
                    password=bcrypt.generate_password_hash(email).decode('utf-8'),
                    course=course,
                    role_id=3,
                )
                students.append(student)
                
        return students, existing
    
    def parse_excel(self, file):
        # Read excel data using pandas
        file_contents = file.stream.read()
        excel_data = BytesIO(file_contents)
        df = pd.read_excel(excel_data)
        
        students = []
        existing = []
        
        for index, row in df.iterrows():
            first_name = row['first_name']
            last_name = row['last_name']
            email = row['email']
            phone_number = row['phone_number']
            course = row['course']
            
            user = User.query.filter_by(email=email).first()
            
            if user:
                existing.append(email)
            else:
                student = User(
                    first_name=first_name,
                    last_name=last_name,
                    email = email,
                    phone_number=phone_number,
                    password=bcrypt.generate_password_hash(email).decode('utf-8'),
                    course=course,
                    role_id=3,
                )
                students.append(student)
                
        return students, existing