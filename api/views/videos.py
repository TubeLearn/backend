from api.views import app_view
from flask import jsonify
from bson.objectid import ObjectId
from api.models.base import videos_collection,courses_collection
from pytube import Playlist
from api.models.videos import videos as Video

@app_view.route('/videos', methods=['GET'])
def get_videos():
    videos = videos_collection.find()
    video_data = []
    if videos:
        for video in videos:
            v = {
                "video_id": str(video['_id']),
                "videos": video['videos']
                }
            video_data.append(v)
    return jsonify({'videos': video_data}), 200

@app_view.route('/videos/<course_id>', methods=['POST'])
def add_videos(course_id):
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
            data = {"title":title,"description":desc,"thumbnail":thumbnail,"length":length,'link':link}
            video_links.append(data)
        video_id = ObjectId()
        videos_collection.insert_one({'_id': video_id,'videos':video_links})
        courses_collection.update_one({'_id': course_id},{'$set': {'video':video_id}},upsert=True,update=True)
        return jsonify({'message':'Added videos to course','video_links':video_links}), 200
    return jsonify({'message':'course not found'}), 404

@app_view.route('/videos/<video_id>', methods=['DELETE'])
def delete_videos(video_id):
    video_id = ObjectId(video_id)
    video = videos_collection.delete_one({'_id': video_id})
    if video:
       return jsonify({'message': 'deleted video'}), 200
    return jsonify({'message':'video not found'}), 404

@app_view.route('/videos/<video_id>', methods=['GET'])
def get_single_video(video_id):
    video_id = ObjectId(video_id)
    video = videos_collection.find_one({'_id': video_id})
    if video:
       data = {'video_id': str(video['_id']), 'videos': video['videos']}
       return jsonify({'video': data}), 200
    return jsonify({'message':'video not found'}), 404


