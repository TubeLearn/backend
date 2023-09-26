from api.views import app_view
from flask import request, jsonify
from models.users import Users
from flask_jwt_extended import create_access_token
from utils.crypto import encode_password, verify_password
from utils.validate import validate_dict
from bson.objectid import ObjectId
from datetime import datetime, timedelta



# sign up route tested and successful
@app_view.route('user/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    email = data['email']
    password = data['password']
    username = data['username']
    user_data = {"email":email,"username":username,"password":password}
    error = validate_dict(user_data)
    if(error):
        return jsonify(error), 400
    password = encode_password(password)
    try:
       user = Users(email=email, username=username, password=password).save()
    except Exception as e:
        return jsonify({"messsage": getattr(e, 'message', '')}), 400
    if user:
        return jsonify({'message': 'Registration successful'})
    return jsonify({'message': 'Registration failed'})

@app_view.route('user/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    data_to_validate = {"email": email, "password": password}
    error = validate_dict(data_to_validate)
    if(error):
        return jsonify(error), 400

    user = Users.objects(email=email).first()
    if user == None:
        return jsonify({'message': 'invalid email provided'}), 404
    if not verify_password(password, user['password']):
        return jsonify({'message': 'incorrect password provided'}), 400
    user_id = str(user.id)
    access_token = create_access_token(identity=user_id)
    response = jsonify({
        'message': 'Login successful'
    })
    expiresAt = datetime.now() + timedelta(days=1)
    response.set_cookie('access_token', access_token, httponly=True, samesite='None', expires=expiresAt)
    return response

@app_view.route('user/all', methods=['GET'])
def get_all():
    users = Users.objects().exclude('password')
    return jsonify({'users': users}), 200

@app_view.route('user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.objects.get(id=user_id)
    if user:
        user.delete()
        return jsonify({'message': 'user deleted'}), 200
    return jsonify({'message': 'user not found'}), 200
