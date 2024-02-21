import json
from datetime import datetime
from datetime import timezone
from flask import jsonify, request, Blueprint, Response,make_response
from flask_restful import Resource
from flask_bcrypt import Bcrypt
from models import User, Role, TokenBlocklist, db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

bcrypt = Bcrypt()

auth_bp = Blueprint('auth_bp', __name__)

# login user
class Login(Resource):

    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if email is None or password is None:
            if email is None:
                return make_response(jsonify({'error': 'Email is required'}), 400)
            elif password is None:
                return make_response(jsonify({'error': 'Password is required'}), 400)
            return Response(json.dumps(response_data), status=400, mimetype='application/json')
        if password == '':
            return make_response(jsonify({'error': 'Enter Your Password'}),400)
        if email == '':
            return make_response(jsonify({'error': 'Enter Your Email'}),400)
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            role = Role.query.filter_by(id=user.role_id).first()
            
            access_token = create_access_token(identity=user.id)
            response_data = {
                'role': role.role_name,
                'access_token': access_token
            }
            return Response(json.dumps(response_data), status=200, mimetype='application/json')
        else:
            response_data = {'error': 'Invalid email or password'}
            return Response(json.dumps(response_data), status=401, mimetype='application/json')

# get logged in user
class AuthenticatedUser(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()
        
        if user:
            user_data = {
                'user_id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'department': user.department,
                'course': user.course,
                'phone_number': user.phone_number
            }
            response_data = json.dumps(user_data)
            return Response(response_data, status=200, mimetype='application/json')
        else:
            error_data = {'error': 'User not found'}
            response_data = json.dumps(error_data)
            return Response(response_data, status=404, mimetype='application/json')
        
# logout user
class Logout(Resource):
    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()
        return jsonify(msg="JWT revoked")