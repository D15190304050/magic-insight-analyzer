import cv2
import moviepy
from ultralytics import YOLO

class VideoMarker:
    def __init__(self, video_path: str, final_output_path: str):
        self.video_path: str = video_path
        self.final_output_path: str = final_output_path

    def mark(self):
        model = YOLO("yolo/best.pt")

        video = cv2.VideoCapture(self.video_path)
        if (not video.isOpened()):
            print("Error opening video stream or file.")
            exit(1)

        # 获取视频的基本信息
        frame_width: int = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height: int = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps: float = video.get(cv2.CAP_PROP_FPS)

        # 提取原始音频
        try:
            video_clip = moviepy.VideoFileClip(self.video_path)
            audio = video_clip.audio
        except Exception as e:
            print(f"音频提取失败: {e}")
            exit()

        # 存储处理后的帧
        frames = []

        while True:
            has_next, frame = video.read()
            if not has_next:
                break

            results = model(frame)
            for box in results[0].boxes.xyxy:
                x1, y1, x2, y2 = map(int, box[:4])  # 获取边界框坐标
                class_id = int(results[0].boxes.cls[0])  # 识别的类别ID
                class_name = model.names[class_id]  # 获取类别名称

                # 画框
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            frames.append(frame)

        video.release()

        # 使用ImageSequenceClip创建视频剪辑
        try:
            processed_clip = moviepy.ImageSequenceClip(frames, fps=fps)

            # 合并音频到处理后的视频
            processed_clip.audio = audio
            processed_clip.write_videofile(self.final_output_path, codec="libx264", audio_codec="aac")

            print(f"带音频的最终视频已保存到: {self.final_output_path}")
        except Exception as e:
            print(f"视频合并失败: {e}")
        finally:
            # 释放资源
            video_clip.close()

if __name__ == '__main__':
    video_path: str = r"E:\Downloads\课堂视频\1.mp4"
    output_video_path: str = r"D:\DinoStark\Temp\out.mp4"
    video_marker: VideoMarker = VideoMarker(video_path, output_video_path)
    video_marker.mark()

    print("Done...")