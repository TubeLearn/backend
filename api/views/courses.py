from api.views import app_view
from models.courses import Courses
from flask import jsonify, request
from pytube import Playlist
from bson.objectid import ObjectId
from api.views.videos import add_videos
from models.videos import Videos



@app_view.route('/courses/<course_id>/video', methods=['GET'])
def get_video(course_id):
    try:
        video = Videos.objects(course_id=course_id).first()
        if video:
            return jsonify({'video_links': video.video})
        else:
            return add_videos(course_id)
    except Exception as e:
        return jsonify({'message': getattr(e, 'message', 'course does not exist')}), 404

@app_view.route('/courses', methods=['GET'])
def get_courses():
    courses = Courses.objects()
    return jsonify({'courses': courses}), 200

@app_view.route('/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    try:
        course = Courses.objects.get(id=course_id)
        if course:
            return jsonify({'course': course}), 200
        return jsonify({'message': 'Course not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Invalid course ID format'}), 400

@app_view.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        course = Courses.objects.get(id=course_id)
        if course:
            course.delete()
            return jsonify({'message': 'Course deleted'}), 200
        else:
            return jsonify({'message': 'Course not found'}), 404
    except Exception as e:
        return jsonify({'message': getattr(e, 'message', 'unable to delete course')}), 400

@app_view.route('/courses/add', methods=['POST'])
def add_course():
    data = request.get_json()
    url = data.get('link')
    if not url:
        return jsonify({'message': 'No link provided'}), 400
    p = Playlist(url)

    title = ""
    desc = ""
    try:
        desc = p.description
    except:
        pass
    try:
        title = p.title
    except:
        pass
    course = Courses.objects(title=title).first()
    if course:
        return jsonify({'message': 'Course already exists'}), 400
    try:
        course = Courses(title=title, description=desc, link=url)
        course.save()
        return jsonify({'message': 'Course added successfully'}), 201
    except Exception as e:
        print(e)
        return jsonify({'message': getattr(e, 'message', 'Could not create course')}), 400