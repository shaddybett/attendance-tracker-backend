from flask import Flask, request, jsonify
from flask_restful import Api
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_cors import CORS
from models import db, User, Role
from flask_migrate import Migrate
from views import *

load_dotenv()
import os

app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt()
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
Migrate(app,db)


ADMIN_ROLE_ID = 1
TEACHER_ROLE_ID = 2
STUDENT_ROLE_ID = 3

api.add_resource(Login,'/login')
api.add_resource(AddTeacher,'/addteacher')
api.add_resource(AddStudent,'/addstudent')

if __name__=='__main__':
    app.run(debug=True,port=5000)