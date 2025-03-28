import json
import logging
import uuid
from Configuration import Configuration
import warnings

from kafka.KafkaProducer import KafkaProducer

warnings.filterwarnings('ignore')
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import SubtitleGenerator
from minio import Minio
import subprocess

logger = logging.getLogger()
config = Configuration.get_instance()

def generate_unique_temp_filename(prefix: str = "", extension: str = ".txt") -> str:
    """生成一个唯一的临时文件名"""
    temp_dir: str = "D:/DinoStark/Temp/StellaTemp"
    unique_name: str = prefix + str(uuid.uuid4()) + extension
    return os.path.join(temp_dir, unique_name)

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

        # Members of Kafka.
        self.kafka_producer = KafkaProducer()
        self.kafka_producer_topic_summary_video_end = config.kafka_producer_topic_summary_video_end

    def __call__(self, *args, **kwargs):
        self.handle(kwargs["message"])

    def handle(self, message: str):
        # Get arguments from message.
        summary_video_start_message: dict = json.loads(message)
        video_id: int = summary_video_start_message["videoId"]
        video_object_name: str = summary_video_start_message["videoObjectName"]

        # Extract subtitle from video.
        audio_file_path: str = self.stream_extract_audio(video_object_name)
        logger.info("Begin extract subtitles.")
        sg: SubtitleGenerator = SubtitleGenerator(audio_file_path)
        subtitle_file_path: str = sg.run()
        logger.info("End extract subtitles.")

        # Upload subtitle to MinIO.
        subtitle_object_name: str = "Subtitle of video - " + str(video_id) + ".txt"
        logger.info("Uploading subtitle to minio.")
        self.minio_client.fput_object(self.bucket_name_video_subtitles, subtitle_object_name, subtitle_file_path)
        logger.info("Done uploading subtitle to minio.")

        # Clear temporary files.
        os.remove(audio_file_path)
        os.remove(subtitle_file_path)

        # Produce message of summary end.
        self.kafka_producer.produce(
            self.kafka_producer_topic_summary_video_end,
            None,
            {"videoId": video_id, "subtitleObjectName": subtitle_object_name},
        )

    def stream_extract_audio(self, object_name) -> str:
        audio_file_path: str = generate_unique_temp_filename(prefix="audio-", extension=".mp3")

        presigned_url: str = self.minio_client.presigned_get_object(self.bucket_name_videos, object_name)
        ffmpeg_command: list[str] = [
            "ffmpeg",
            "-i", presigned_url,  # 输入为presigned_url
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