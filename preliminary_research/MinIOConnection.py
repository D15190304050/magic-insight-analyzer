from minio import Minio
from Configuration import Configuration

config = Configuration()

def list_objects(minio_client: Minio, bucket_name: str):
    # 列出bucket中的所有对象
    objects = minio_client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        print(obj.object_name)

if __name__ == "__main__":
    # 创建一个MinIO客户端实例
    minio_client: Minio = Minio(
        config.minio_endpoint,
        access_key=config.minio_access_key,
        secret_key=config.minio_secret_key,
        secure=False  # 如果MinIO服务器是HTTPS，则设置为True
    )

    # 指定需要列出对象的bucket名称
    bucket_name: str = config.minio_bucket_name_video_subtitles

    # 调用函数列出bucket中的对象
    list_objects(minio_client, bucket_name)

    object_name: str = "Subtitle of video-1.txt"
    file_path: str = r"D:/DinoStark/Temp/" + object_name
    minio_client.fget_object(bucket_name, object_name, file_path)