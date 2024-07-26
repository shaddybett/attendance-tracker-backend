import pandas as pd
import csv
import json
from io import StringIO, BytesIO
import csv
from flask import jsonify, Response, request, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from models import db, User, ClassStudent

class AddToClassFromFile(Resource):
    @jwt_required()
    def post(self, class_id):
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
                class_students, existing, not_found = self.parse_csv(file, class_id)
            elif filename.endswith('.xlsx'):
                # Read Excel data
                class_students, existing, not_found = self.parse_excel(file, class_id)
            else:
                return make_response(json.dumps({'error': 'Unsupported file type'}), 400)
             
            db.session.add_all(class_students)
            db.session.commit()
            
            data = {'msg': f'{len(class_students)} out of {len(class_students) + len(existing) + len(not_found)} students added successfully', 'emails_in_use':existing, 'not_found':not_found}
            response_data = json.dumps(data)
            
            return Response(response_data, status=200, mimetype='application/json')
        else:
            return make_response(json.dumps({'error': 'Invalid file type'}), 400)
    
    def parse_csv(self, file, id):
        # Read the CSV data from the file-like object           
        csv_data = file.stream.read().decode('utf-8')
        
        class_students = []
        existing = []
        not_found = []
        # Process CSV data
        csv_reader = csv.DictReader(StringIO(csv_data))
        
        for row in csv_reader:
            email = row['email']

            user = User.query.filter_by(email=email).first()
            if user:
                exists = ClassStudent.query.filter_by(class_id=id, user_id=user.id).first()

                if exists:
                    existing.append(email)
                else:
                    class_student = ClassStudent(
                        user_id = user.id,
                        class_id = id
                    )
                    class_students.append(class_student)
            else:
                not_found.append(email)
                
        return class_students, existing, not_found
    
    def parse_excel(self, file, id):
        # Read excel data using pandas
        file_contents = file.stream.read()
        excel_data = BytesIO(file_contents)
        df = pd.read_excel(excel_data)
        
        class_students = []
        existing = []
        not_found = []
        
        for index, row in df.iterrows():
            email = row['email']
            
            user = User.query.filter_by(email=email).first()
            if user:
                exists = ClassStudent.query.filter_by(class_id=id, user_id=user.id).first()

                
                if exists:
                    existing.append(email)
                else:
                    class_student = ClassStudent(
                        user_id = user.id,
                        class_id = id
                    )
                    class_students.append(class_student)
            else:
                not_found.append(email)
                
        return class_students, existing, not_found