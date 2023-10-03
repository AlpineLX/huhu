from flask import Blueprint, request, send_from_directory, jsonify, flash, render_template, session, redirect, url_for, abort
from app.models.video import db, Video
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from dateutil.parser import parse
import os
import uuid
from app.utils import SaveFirstFrame
from datetime import datetime
from app.models.user import User

video_bp = Blueprint('video', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")
# UPLOAD_FOLDER = "app/static/uploads"
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'flv', 'mov', 'wmv', 'webm', 'mkv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@video_bp.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file part"})

        file = request.files['file']

        if file.filename == '':
            return jsonify({"success": False, "message": "No selected file"})

        # 从session中获取用户ID
        current_user_id = session.get('user_id', None)
        if not current_user_id:
            return jsonify({"success": False, "message": "User not logged in"})

        # 根据user_id从数据库中获取用户
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"success": False, "message": "User not found"})

        if file and allowed_file(file.filename):
            unique_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            videopath = os.path.join(UPLOAD_FOLDER, unique_id + os.path.splitext(filename)[1])
            file.save(videopath)

            # 获取用户的当地时间
            user_time_str = request.form.get('userLocalTime', "")
            user_local_time = parse(user_time_str)

            # 获取视频文件的大小
            file_size_mb = os.path.getsize(videopath) / (1024 * 1024)  # Convert bytes to MB

            # 获取视频时长
            with VideoFileClip(videopath) as clip:
                video_duration = int(clip.duration)  # in seconds

            video = Video(unique_id=unique_id,
                          user_id=current_user.username,
                          video_path=videopath,
                          filename=filename,
                          status="waiting",
                          file_size=file_size_mb,
                          duration=video_duration,
                          uploaded_at=user_local_time)
            db.session.add(video)
            db.session.commit()

            image_path = os.path.join(UPLOAD_FOLDER, unique_id + ".jpg")

            SaveFirstFrame(videopath, image_path)  # Assume this function will be executed in another thread or process

            return jsonify({"success": True, "message": "Upload successful", "video_id": unique_id, "image_url": url_for('static', filename='uploads/' + unique_id + ".jpg")})

        return jsonify({"success": False, "message": "Invalid file type"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@video_bp.route('/download/<int:video_id>', methods=['GET'])
def download_video(video_id):
    video = Video.query.get(video_id)
    if not video:
        abort(404)  # 视频未找到
    if video.status != 'complete':
        abort(403)  # 如果视频不是完成状态，拒绝下载请求
    return send_from_directory(directory=os.path.dirname(video.processed_video_path),
                               path=os.path.basename(video.processed_video_path))


@video_bp.route('/preview/<string:video_id>', methods=['GET'])
def preview_video(video_id):
    # Similar to download, but perhaps you'd return the video in a streaming format
    # For simplicity, I'll assume they're the same
    return download_video(video_id)

@video_bp.route('/management', methods=['GET'])
def management():
    # 检查session中是否有user_id
    if 'user_id' not in session:
        flash("请先登录！", "warning")
        return redirect(url_for('auth.login'))
    return render_template('management.html')

@video_bp.route('/MyVideos', methods=['GET'])
def MyVideos():
    # 检查session中是否有user_id
    if 'user_id' not in session:
        flash("请先登录！", "warning")
        return redirect(url_for('auth.login'))

    # 获取用户的所有视频
    current_user_id = session.get('user_id', None)
    current_user = User.query.get(current_user_id)
    videos = Video.query.filter_by(user_id=current_user.username).all()
    return render_template('MyVideos.html', videos=videos)

@video_bp.route('/save_selection', methods=['POST'])
def save_selection():
    data = request.get_json()

    video_id = data.get('video_id')
    xini = data.get('xini')
    yini = data.get('yini')
    xend = data.get('xend')
    yend = data.get('yend')

    # 使用unique_id字段查询Video
    video = Video.query.filter_by(unique_id=video_id).first()
    if video:
        video.xini = xini
        video.yini = yini
        video.xend = xend
        video.yend = yend
        video.status = 'ready'
        db.session.commit()
        return jsonify({"success": True, "message": "Selection saved successfully"})
    else:
        return jsonify({"success": False, "message": "Video not found"}), 404

@video_bp.route('/UploadSuccess', methods=['GET'])
def UploadSuccess():
    # 检查session中是否有user_id
    if 'user_id' not in session:
        flash("请先登录！", "warning")
        return redirect(url_for('auth.login'))
    return render_template('UpLoadSuccess.html')


