from api.views import app_view
from api.models.videos import videos as Video
from flask import jsonify, request

# examples of CRUD methods

@app_view.route('/test', methods=['GET'])
def get_all_test():
    videos = Video.objects()
    return jsonify({"videos": videos}), 200

@app_view.route('/test/<test_id>', methods=['GET'])
def get_single_test(test_id):
    video = Video.objects.get(id=test_id)
    return jsonify({"video": video}), 200

@app_view.route('/test/<test_id>', methods=['DELETE'])
def delete_single_test(test_id):
    video = Video.objects.get(id=test_id)
    if video:
        video.delete()
        return jsonify({"messsage": "video deleted"}), 200
    return jsonify({"messsage": "video not found"}), 404

@app_view.route('/test', methods=['POST'])
def create_single_test():
    data = request.get_json()
    new_video = data['video']
    try:
        video = Video(video=new_video).save()
    except Exception as e:
        return jsonify({"messsage": e.message}), 400
    if video:
        return jsonify({"messsage": "video created"}), 200
    return jsonify({"messsage":"video not created"}), 400

@app_view.route('/test/<test_id>', methods=['PATCH'])
def update_single_test(test_id):
    video = Video.objects.get(id=test_id)
    if video:
        video.update(video=[{"title":"hello"}])
        return jsonify({"messsage": "video updated"}), 200
    return jsonify({"messsage":"video not found"}), 404