import time
from app.models.video import db, Video
import cv2
import GPUtil

def SaveFirstFrame(videopath, image_path):
    # 读取视频文件
    cap = cv2.VideoCapture(videopath)

    # 检查是否成功打开视频
    if not cap.isOpened():
        print("Error: Couldn't open the video file.")
        return

    # 读取第一帧
    ret, frame = cap.read()

    # 如果读取成功，保存该帧
    if ret:
        cv2.imwrite(image_path, frame)

    # 释放视频资源
    cap.release()


def check_gpu_status(gpu_id):
    """
    使用GPUtil检查特定GPU是否空闲。
    :param gpu_id: 要检查的GPU的ID。
    返回True，如果指定的GPU空闲并且没有进程在使用它。
    否则，返回False。
    """
    # 获取所有GPU设备的列表
    gpus = GPUtil.getGPUs()

    # 检查GPU ID是否在有效范围内
    if gpu_id >= len(gpus):
        raise ValueError(f"Invalid GPU ID. Only {len(gpus)} GPUs detected.")

    # 获取指定的GPU
    gpu = gpus[gpu_id]

    # 检查该GPU的使用率和内存使用
    if gpu.load < 0.1 and gpu.memoryUtil < 0.1:
        return True  # GPU空闲

    return False  # GPU正在被使用

def video_processing(video_path):
    # 这里是您的视频处理逻辑
    # 如果成功, 返回处理完成的视频路径，否则返回None




    return True, video_path

if __name__ == '__main__':
    video_path = '/home/liuxi/Projects/huhu/app/static/uploads/40d2dc48-5dcd-4a0a-af5d-85aa5ff30cba.mov'