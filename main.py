from flask import Flask, render_template, session, redirect, url_for, flash
from app.models.user import db
from app.routes.auth import auth_bp
from app.routes.video import video_bp
from app.models.video import Video
import time
import atexit
from threading import Thread
from app.utils import check_gpu_status, video_processing

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
RUNNING = True
app.config.from_object('config.Config')

# 初始化数据库
db.init_app(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(video_bp, url_prefix='/video')

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        # 可以添加额外的逻辑，例如获取用户上传的视频列表等
        return redirect(url_for('video.management'))
    else:
        return redirect(url_for('auth.homepage'))

def video_task_manager():
    global RUNNING
    while RUNNING:
        # 如果 GPU 0 是空闲的
        # if check_gpu_status(0):
        if True:
            with app.app_context():
                # 查找状态为 "ready" 的视频，并按上传时间排序
                video = Video.query.filter_by(status="ready").order_by(Video.uploaded_at.asc()).first()

                if video:
                    # 调用您的视频处理函数
                    success, processed_path = video_processing(video.video_path)

                    if success:
                        video.processed_video_path = processed_path
                        video.status = "complete"
                    else:
                        video.status = "error"

                    db.session.commit()

        time.sleep(10)  # 可以根据需要调整检查间隔

def stop_task_manager():
    global RUNNING
    RUNNING = False

atexit.register(stop_task_manager)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    thread = Thread(target=video_task_manager)
    thread.start()

    app.run('0.0.0.0', 5000, debug=True)
