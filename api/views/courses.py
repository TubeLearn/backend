from api.views import app_view
from api.models.base import courses_collection
from flask import jsonify, request
from pytube import Playlist
from bson.objectid import ObjectId
from api.views.videos import add_videos



@app_view.route('/courses/<course_id>/video', methods=['GET'])
def get_video(course_id):
    course_id = ObjectId(course_id)

    course = courses_collection.find_one({'_id': course_id})
    if course:
        video_id = course['video']
        print(video_id)
        return jsonify({'video_links': []})
 
    return jsonify({'message': 'Course not found'}), 404

@app_view.route('/courses', methods=['GET'])
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
            "link": course_data["link"],
            "video": str(course_data["video"])
        }
        
        # Append the JSON data to the list
        courses_json.append(json_data)
    
    # Serialize the list of course data to JSON and return it
    return jsonify(courses_json)

@app_view.route('/courses/<course_id>', methods=['GET'])
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

@app_view.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    from bson.objectid import ObjectId

    try:
        # Convert the course_id from the URL to ObjectId
        course_id = ObjectId(course_id)
        courses_collection.delete_one({'_id': course_id})
        return jsonify({'message': 'Course deleted'}), 200

    except Exception as e:
        return jsonify({'message': 'Invalid course ID format'}), 400

@app_view.route('/course/add', methods=['POST'])
def add_course():
    data = request.get_json()
    url = ""
    try:
        url = data['link']
    except KeyError:
        return jsonify({'message': 'No link provided'}), 400
    # Generate a unique course ID (e.g., using ObjectId from pymongo)
    course_id = ObjectId()
    p = Playlist(url)
    # Add a new course to MongoDB with the generated 
    title = ''
    desc = ''
    try:
        title = p.title
    except:
        pass
    try:
        desc = p.description
    except:
        pass

    new_course = {
        '_id': course_id,
        'title': title ,
        'description': desc,
        'link': url
    }

    # Check if a course with the same title already exists
    existing_course = courses_collection.find_one({'title': new_course['title']})
    if existing_course:
        return jsonify({'message': 'Course with the same title already exists'}), 400

    courses_collection.insert_one(new_course)
    return jsonify({'message': 'Course added successfully'}), 201