from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from pymongo import MongoClient

app = Flask(__name__)


client = MongoClient("mongodb://localhost:27017/")
db = client["HackTheClassRoom"]
users_collection = db["users"]
courses_collection = db["courses"]


app.config['SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.route('/user/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'message': 'Email already registered'}), 400
    user_data = {
        'email': data['email'],
        'password': data['password'],  
        'username': data['username']
    }
    users_collection.insert_one(user_data)
    return jsonify({'message': 'Registration successful'}), 201

@app.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email, 'password': password})
    if user:
        access_token = create_access_token(identity=str(user['_id']))
        response = jsonify({'message': 'Login successful'})
        response.set_cookie('access_token', access_token, httponly=True, samesite='None')
        return response

    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/user/current', methods=['GET'])
@jwt_required()
def current_user():
    current_user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': current_user_id})
    if user:
        return jsonify({
            'userId': str(user['_id']),
            'email': user['email'],
            'username': user['username']
        })

    return jsonify({'message': 'User not found'}), 404

@app.route('/courses', methods=['GET'])
def get_courses():
    courses = list(courses_collection.find({}, {'_id': False}))
    return jsonify(courses)

@app.route('/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    from bson.objectid import ObjectId

    try:
        # Convert the course_id from the URL to ObjectId
        course_id = ObjectId(course_id)
        course = courses_collection.find_one({'_id': course_id}, {'_id': False})

        if course:
            return jsonify(course)
        
        return jsonify({'message': 'Course not found'}), 404

    except Exception as e:
        return jsonify({'message': 'Invalid course ID format'}), 400


@app.route('/courses/add', methods=['POST'])
def add_course():
    data = request.get_json()
    
    # Generate a unique course ID (e.g., using ObjectId from pymongo)
    from bson.objectid import ObjectId
    course_id = ObjectId()
    
    # Add a new course to MongoDB with the generated course_id
    new_course = {
        '_id': course_id,
        'title': data['title'],
        'description': data['description'],
        'link': data['link']
    }

    # Check if a course with the same title already exists
    existing_course = courses_collection.find_one({'title': data['title']})
    if existing_course:
        return jsonify({'message': 'Course with the same title already exists'}), 400

    courses_collection.insert_one(new_course)
    return jsonify({'message': 'Course added successfully', 'course_id': str(course_id)}), 201



@app.route('/courses/<course_id>/quiz', methods=['GET'])
def get_course_quiz(course_id):
    #here the ai this can in to play to generate the question
    quiz_data = {'questions': ['Question 1', 'Question 2'], 'answers': ['Answer 1', 'Answer 2']}
    return jsonify(quiz_data)

if __name__ == '__main__':
    app.run(debug=True)
