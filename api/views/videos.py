from api.views import app_view
from flask import jsonify
from bson.objectid import ObjectId
from models.courses import Courses
from pytube import Playlist
from models.videos import Videos

def try_catch_exception(fnc, video_id):
    def wrapper(*args, **kwargs):
        try:
            fnc(video_id)
        except Exception as e:
            return jsonify({'message':getattr(e, 'message', 'course not deleted')}), 404
    return wrapper

@app_view.route('/videos', methods=['GET'])
def get_videos():
    videos = Videos.objects()
    return jsonify({'videos': videos}), 200

@app_view.route('/videos/<course_id>', methods=['POST'])
def add_videos(course_id):
    course = Courses.objects.get(id=course_id)
    if course:
        video_links = []
        link = course.link
        playlist = Playlist(link)
        v = playlist.videos

        for video in v:
            title = video.title
            desc = video.description
            thumbnail = video.thumbnail_url
            length = video.length
            data = {"title":title,"description":desc,"thumbnail":thumbnail,"length":length,'link':link}
            video_links.append(data)
        Videos(video=video_links, course_id=course.id).save()
        return jsonify({'message':'Added videos to course','video_links':video_links}), 200
    return jsonify({'message':'course not found'}), 404

@app_view.route('/videos/<video_id>', methods=['DELETE'])
def delete_videos(video_id):
    try:
        video = Videos.objects.get(id=video_id)
        if video:
           video.delete()
           return jsonify({'message': 'deleted video'}), 200
        return jsonify({'message':'video not found'}), 404
    except Exception as e:
        return jsonify({'message':getattr(e, 'message', 'video not deleted')}), 404


@app_view.route('/videos/<video_id>', methods=['GET'])
def get_single_video(video_id):
    try:
        video = Videos.objects.get(id=video_id)
        if video:
           return jsonify({'video': video}), 200
        return jsonify({'message':'video not found'}), 404
    except Exception as e:
        return jsonify({'message':getattr(e,'message', 'video not found')}), 404


