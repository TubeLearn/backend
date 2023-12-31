from flask import Flask, jsonify, request
from api.views import app_view
from models.base import open_ai_api
from models.users import Users
from models.courses import Courses
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from flask_mongoengine import MongoEngine
from bson.objectid import ObjectId

from flask_limiter import Limiter
import openai
import json
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(app_view)
app.config['MONGODB_SETTINGS'] = [{
    'host': 'mongodb+srv://kevinkbet:b9mnc2W6OJYjv4PA@cluster0.ci8q496.mongodb.net/HackTheClassRoom',
}]
db = MongoEngine(app)
limiter = Limiter(app)

CORS(app)

app.config['SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route('/user/current', methods=['GET'])
@jwt_required()
def current_user():
    user_id = get_jwt_identity()
    user_id = ObjectId(user_id)
    user = Users.objects.get(id=user_id)
    if user:
        return jsonify({
            'user_id': str(user.id),
            'email': user['email'],
            'username': user['username']
        })
    return jsonify({'message': 'User not found'}), 404



# Couldn't fix or test [tokens finished on API key]. Every other route is working perfectly
@app.route('/courses/<course_id>/quiz', methods=['GET'])
@limiter.limit("5 per minute") # to reduce amount of tokens used
def get_course_quiz(course_id):
    course_id = ObjectId(course_id)

    course = Courses.objects.get(id=course_id)
    if course:
        description = course.description

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
