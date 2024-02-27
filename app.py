from flask import Flask, request, jsonify
from flask_restful import Api
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_cors import CORS
from models import db, TokenBlocklist
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import timedelta
from views import *
import os

load_dotenv()

# UPLOAD_FOLDER  = os.path.join(os.getcwd(), 'files') 

app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt()
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
jwt = JWTManager()
jwt.init_app(app)
db.init_app(app)
Migrate(app,db)


ADMIN_ROLE_ID = 1
TEACHER_ROLE_ID = 2
STUDENT_ROLE_ID = 3

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None

api.add_resource(Login,'/login')
api.add_resource(AuthenticatedUser, '/authenticated_user')
api.add_resource(Logout, '/logout')
api.add_resource(AddTeacher,'/addteacher')
api.add_resource(AddStudent,'/addstudent')
api.add_resource(AddStudentsFromFile,'/upload_students')

api.add_resource(ClassView, '/class', '/class/<int:class_id>')
api.add_resource(ClassStudentResource, '/class/<int:class_id>/student/<int:user_id>')
api.add_resource(AttendanceResource, '/class/<int:class_id>/attendance')
api.add_resource(ClassDetails, '/class/<int:class_id>/details')
api.add_resource(AllStudents, '/allstudents')
api.add_resource(AllTeachers,'/allteachers')
api.add_resource(DeleteUsers, '/deleteuser/teacher/<int:teacher_id>', '/deleteuser/student/<int:student_id>')
api.add_resource(UpdateUser, '/update/<int:user_id>')
api.add_resource(AttendanceDownloadAPI, '/download-attendance/<int:class_id>')
api.add_resource(StudentAttendanceReportPDF, '/generate-report')


if __name__=='__main__':
    app.run(debug=True,port=5000)






    