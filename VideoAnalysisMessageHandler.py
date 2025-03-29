import json
import logging
import uuid
from Configuration import Configuration
import warnings

from VideoMarker import VideoMarker
from kafka.KafkaProducer import KafkaProducer

warnings.filterwarnings('ignore')
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import SubtitleGenerator
from minio import Minio
import subprocess

VIDEO_ID: str = "videoId"
SUBTITLE_OBJECT_NAME: str = "subtitleObjectName"
MARKED_VIDEO_OBJECT_NAME: str = "markedVideoObjectName"

logger = logging.getLogger()
config = Configuration.get_instance()

def generate_unique_temp_file_name(prefix: str = "", extension: str = ".txt") -> str:
    """生成一个唯一的临时文件名"""
    temp_dir: str = config.temp_dir
    unique_name: str = prefix + str(uuid.uuid4()) + extension
    return os.path.join(temp_dir, unique_name)

def get_file_extension(file_name: str) -> str:
    """
    Returns the file extension from the file name, including the "."
    :param file_name: File name.
    :return: File extension.
    """
    index_of_extension: int = file_name.rfind(".")
    return file_name[index_of_extension:]

class VideoAnalysisMessageHandler:
    def __init__(self):
        # Members of MinIO.
        self.minio_client = Minio(
            config.minio_endpoint,
            access_key=config.minio_access_key,
            secret_key=config.minio_secret_key,
            secure=False  # 如果是HTTPS则设为True
        )
        self.bucket_name_videos = config.minio_bucket_name_videos
        self.bucket_name_video_subtitles = config.minio_bucket_name_video_subtitles
        self.minio_bucket_name_analyzed_videos = config.minio_bucket_name_analyzed_videos

        # Members of Kafka.
        self.kafka_producer = KafkaProducer()
        self.kafka_producer_topic_summary_video_end = config.kafka_producer_topic_summary_video_end

    def __call__(self, *args, **kwargs):
        self.handle(kwargs["message"])

    def handle(self, message: str):
        # Get arguments from message.
        summary_video_start_message: dict = json.loads(message)
        video_id: int = summary_video_start_message[VIDEO_ID]
        video_object_name: str = summary_video_start_message["videoObjectName"]

        # Download video file to local drive.
        video_file_extension: str = get_file_extension(video_object_name)
        video_file_path: str = generate_unique_temp_file_name(prefix="video", extension=video_file_extension)
        self.minio_client.fget_object(self.bucket_name_videos, video_object_name, video_file_path)

        # Extract subtitle from video.
        audio_file_path: str = self.extract_audio(video_file_path)
        logger.info("Begin extract subtitles.")
        sg: SubtitleGenerator = SubtitleGenerator(audio_file_path)
        subtitle_file_path: str = sg.run()
        logger.info("End extract subtitles.")

        # Upload subtitle to MinIO.
        subtitle_object_name: str = "Subtitle of video - " + str(video_id) + ".txt"
        logger.info("Uploading subtitle to minio.")
        self.minio_client.fput_object(self.bucket_name_video_subtitles, subtitle_object_name, subtitle_file_path)
        logger.info("Done uploading subtitle to minio.")

        # Action recognition of students.
        # Mark frames, save into new file, then upload to MinIO.
        marked_video_file_path: str = generate_unique_temp_file_name(prefix="marked-video-", extension=video_file_extension)
        video_marker: VideoMarker = VideoMarker(video_file_path, marked_video_file_path)
        logger.info("Begin marking video.")
        video_marker.mark()
        logger.info("Done marking video. Uploading to minio.")
        marked_video_object_name: str = "Marked video - " + str(video_id) + video_file_extension
        self.minio_client.fput_object(self.minio_bucket_name_analyzed_videos, marked_video_object_name, marked_video_file_path)

        # Clear temporary files.
        os.remove(audio_file_path)
        os.remove(subtitle_file_path)
        os.remove(video_file_path)
        os.remove(marked_video_file_path)

        # Produce message of summary end.
        self.kafka_producer.produce(
            self.kafka_producer_topic_summary_video_end,
            None,
            {VIDEO_ID: video_id, SUBTITLE_OBJECT_NAME: subtitle_object_name, MARKED_VIDEO_OBJECT_NAME: marked_video_object_name},
        )

    def extract_audio(self, video_file_path: str) -> str:
        audio_file_path: str = generate_unique_temp_file_name(prefix="audio-", extension=".mp3")

        ffmpeg_command: list[str] = [
            "ffmpeg",
            "-i", video_file_path,
            "-q:a", "0",  # 音频质量设置
            "-map", "a",  # 只提取音频流
            audio_file_path  # 输出文件
        ]

        logger.info("Running ffmpeg audio extraction command, output audio file path = " + audio_file_path)

        try:
            subprocess.run(ffmpeg_command, check=True)
            logger.info("Audio extraction completed successfully.")

        except subprocess.CalledProcessError as e:
            logger.error("Error occurred while extracting audio:", e)

        return audio_file_path