from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from pymongo import MongoClient
from flask_limiter import Limiter
import openai
import json  
from flask_cors import CORS,cross_origin
from pytube import Playlist

app = Flask(__name__)
limiter = Limiter(app)

CORS(app)

open_ai_api = "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" # expired
mongoURL = "mongodb+srv://tubelearn:1234@cluster0.s19nica.mongodb.net/?retryWrites=true&w=majority" #currently filled with junk
client = MongoClient(mongoURL)
db = client["HackTheClassRoom"]
users_collection = db["users"]
courses_collection = db["courses"]

app.config['SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)     

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173/'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


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
    return jsonify({'message': 'Registration successful'})

@app.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email, 'password': password})
    if user:
        access_token = create_access_token(identity=str(user['_id']))
        response = jsonify({
            'message': 'Login successful',
            'access_token': access_token 
        })
        response.set_cookie('access_token', access_token, httponly=True, samesite='None')
        return response

    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/courses/<course_id>/video', methods=['GET'])
def get_video(course_id):
    from bson.objectid import ObjectId
    course_id = ObjectId(course_id)

    course = courses_collection.find_one({'_id': course_id})
    if course:
        video_links = []
        link = course['link']
        playlist = Playlist(link)
        v = playlist.videos
        
        for video in v:
            title = video.title
            desc = video.description
            thumbnail = video.thumbnail_url
            length = video.length
            data = {"title":title,"description":desc,"thumbnail":thumbnail,"length":length}
            video_links.append(data)
        return jsonify({'video_links': video_links})
 

    return jsonify({'message': 'Course not found'}), 404
    


@app.route('/user/current', methods=['GET'])
@jwt_required()
def current_user():
    current_user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': current_user_id})
    if user:
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            'userId': str(user['_id']),
            'email': user['email'],
            'username': user['username'],
            'access_token': access_token  
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
            "course_id": str(course_data["_id"]),
            "course_title": course_data["title"],
            "description": course_data["description"],
            "link": course_data["link"]
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

@app.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    from bson.objectid import ObjectId

    try:
        # Convert the course_id from the URL to ObjectId
        course_id = ObjectId(course_id)
        courses_collection.delete_one({'_id': course_id})
        return jsonify({'message': 'Course deleted'}), 200

    except Exception as e:
        return jsonify({'message': 'Invalid course ID format'}), 400

@app.route('/course/add', methods=['POST'])
def add_course():
    data = request.get_json()
    url = ""
    try:
        url = data['link']
    except KeyError:
        return jsonify({'message': 'No link provided'}), 400
    # Generate a unique course ID (e.g., using ObjectId from pymongo)
    from bson.objectid import ObjectId
    course_id = ObjectId()
    p = Playlist(url)
    # Add a new course to MongoDB with the generated 
    title = ""
    desc = ""
    try:
        title = p.title
    except:
        title = ""
    try:
        desc = p.description
    except:
        desc = ""

    new_course = {
        '_id': course_id,
        'title': title ,
        'description': desc,
        'link': url
    }

    # Check if a course with the same title already exists
    existing_course = courses_collection.find_one({'title': new_course['title']})
    if existing_course:
        existing_course_id = existing_course['_id']
        return jsonify({'message': 'Course with the same title already exists', 'course_id': str(existing_course_id)}), 400

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
