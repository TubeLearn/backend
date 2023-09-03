from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from pymongo import MongoClient
from flask_limiter import Limiter
import openai
import json  

app = Flask(__name__)
limiter = Limiter(app)


open_ai_api = "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" # expired
mongoURL = "mongodb+srv://tubelearn:1234@cluster0.cbfe3cv.mongodb.net/?retryWrites=true&w=majority" #currently filled with junk
client = MongoClient(mongoURL)
db = client["HackTheClassRoom"]
users_collection = db["users"]
courses_collection = db["courses"]


app.config['SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)     

# sign up route tested and successful
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
    coursesDB = courses_collection.find()
    
    #Create a list to store course data in JSON format
    courses_json = []
    
    for course_data in coursesDB:
        # Convert each course data to a JSON-compatible format
        json_data = {
            "course_title": course_data["title"],
            "description": course_data["description"],
            # Add more data fields as needed
        }
        
        # Append the JSON data to the list
        courses_json.append(json_data)
    
    # Serialize the list of course data to JSON and return it
    return jsonify(courses_json)

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

# Couldn't fix or test [tokens finished on API key]. Every other route is working perfectly
@app.route('/courses/<course_id>/quiz', methods=['GET'])
@limiter.limit("5 per minute") # to reduce amount of tokens used
def get_course_quiz(course_id):
    from bson.objectid import ObjectId
    course_id = ObjectId(course_id)

    course = courses_collection.find_one({'_id': course_id})
    if course:
        description = course['description']
        
        json_format = {
            "question1": {
                "question": "",
                "option1": "",
                "option2": "",
                "option3": "",
                "option4": "",
                "correct_option": ""
            },
            "question2": {
                "question": "",
                "option1": "",
                "option2": "",
                "option3": "",
                "option4": "",
                "correct_option": ""
            },
            "question3": {
                "question": "",
                "option1": "",
                "option2": "",
                "option3": "",
                "option4": "",
                "correct_option": ""
            }
        }
        
        # Convert the JSON format to a string
        json_format_str = json.dumps(json_format)

        # prompt = f"""Here is the description of the course: {description}. Now, I want you to design three questions for this course in the following format:
        # {json_format_str}
        # Return only the JSON file, nothing else.
        # """

        # Need the prompt to be small and concise to save OpenAI credit tokens
        prompt = f"""Create four multiple-choice questions with answers from the course description: {description}, and return as JSON"""
        model = "gpt-3.5-turbo"
        openai.api_key = open_ai_api
        response = openai.Completion.create(engine=model, prompt=prompt, max_tokens=50) 

        generated_text = response.choices[0].text
        return jsonify(json.loads(generated_text))  # Parse the generated JSON response
    return jsonify({'message': 'Course not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
