from api.views import app_view
from flask import request, jsonify
from api.models.base import users_collection
from flask_jwt_extended import create_access_token
from api.utils.crypto import encode_password, verify_password
from api.utils.validate import validate_dict
from bson.objectid import ObjectId


    
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
    user_data['password'] = encode_password(password)
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'message': 'Email already registered'}), 400
    users_collection.insert_one(user_data)
    return jsonify({'message': 'Registration successful'})

@app_view.route('user/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    data_to_validate = {"email": email, "password": password}
    error = validate_dict(data_to_validate)
    if(error):
        return jsonify(error), 400

    user = users_collection.find_one({'email': email})
    if user == None:
        return jsonify({'message': 'Invalid credentials'}), 401
    if not verify_password(password, user['password']):
        return jsonify({'message': 'incorrect password'}), 400
    access_token = create_access_token(identity=str(user['_id']))
    response = jsonify({
        'message': 'Login successful'
    })
    response.set_cookie('access_token', access_token, httponly=True, samesite='None')
    return response

    

@app_view.route('user/all', methods=['GET'])
def get_all():
    users = users_collection.find()
    users_json = []
    
    for user in users:
        
        json_data = {
            "course_id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "password": user["password"]
        }

        users_json.append(json_data)
    return jsonify({'users': users_json}), 200

@app_view.route('user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user_id = ObjectId(user_id)
    user = users_collection.delete_one({'_id': user_id})
    if user:
        return jsonify({'message': 'user deleted'}), 200
    return jsonify({'message': 'user not found'}), 200
