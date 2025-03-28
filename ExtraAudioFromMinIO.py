from minio import Minio
import subprocess
from Configuration import Configuration

config = Configuration()

def stream_extract_audio(minio_client, bucket_name, object_name):
    # 创建一个子进程来运行 ffmpeg 命令
    ffmpeg_process = subprocess.Popen(
        ["ffmpeg", "-i", "pipe:", "-vn", "-ar", "44100", "-ac", "2", "-ab", "192k", "-f", "mp3", "D:/DinoStark/Temp/output_audio.mp3"],
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # 开始下载视频数据并发送到 ffmpeg 的标准输入
        for chunk in minio_client.get_object(bucket_name, object_name):
            ffmpeg_process.stdin.write(chunk)

        # 关闭 ffmpeg 的标准输入
        ffmpeg_process.stdin.close()

        # 等待 ffmpeg 子进程结束
        ffmpeg_process.wait()

        # 检查 ffmpeg 是否成功执行
        if ffmpeg_process.returncode != 0:
            stderr_output = ffmpeg_process.stderr.read()
            raise RuntimeError(
                f"ffmpeg failed with error code {ffmpeg_process.returncode}. Error: {stderr_output.decode('utf-8')}")

        print("Audio extraction completed successfully.")

    finally:
        # 确保 ffmpeg 子进程关闭
        ffmpeg_process.terminate()
        ffmpeg_process.wait()


if __name__ == "__main__":
    minioClient = Minio(
        config.minio_endpoint,
        access_key=config.minio_access_key,
        secret_key=config.minio_secret_key,
        secure=False  # 如果是HTTPS则设为True
    )

    bucket_name = config.minio_bucket_name_video_subtitles
    object_name = "videoUpload-2-1725461754385-2100b64f-96cd-4ab6-8b05-a342119edb10.mp4"

    stream_extract_audio(minioClient, bucket_name, object_name)