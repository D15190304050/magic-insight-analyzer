import yaml
import threading

class Configuration:
    _lock = threading.Lock()
    _local = threading.local()

    def __init__(self):
        with open("application.yaml", "r", encoding="utf-8") as stream:
            config = yaml.safe_load(stream)

        # Redis.
        self.redis_host = config['redis']['host']
        self.redis_port = config['redis']['port']
        self.redis_db = config['redis']['db']

        # MinIO.
        self.minio_endpoint = config['minio']['endpoint']
        self.minio_access_key = config['minio']['access-key']
        self.minio_secret_key = config['minio']['secret-key']
        self.minio_bucket_name_videos = config['minio']['bucket-name-videos']
        self.minio_bucket_name_video_subtitles = config['minio']['bucket-name-video-subtitles']

        # Kafka.
        self.kafka_bootstrap_servers = config['kafka']['bootstrap-servers']
        self.kafka_producer_topic_summary_video_end = config['kafka']["producer"]['topic-summary-video-end']
        self.kafka_producer_acks = config['kafka']["producer"]['acks']
        self.kafka_producer_retries = config['kafka']["producer"]['retries']
        self.kafka_producer_buffer_memory = config['kafka']["producer"]['buffer-memory']
        self.kafka_producer_batch_size = config['kafka']["producer"]['batch-size']
        self.kafka_producer_client_id = config['kafka']["producer"]['client-id']
        self.kafka_producer_compression_type = config['kafka']["producer"]['compression-type']
        self.kafka_producer_linger_ms = config['kafka']["producer"]['linger-ms']
        self.kafka_consumer_topic_summary_video_start = config['kafka']["consumer"]['topic-summary-video-start']
        self.kafka_consumer_group_id = config['kafka']["consumer"]['group-id']
        self.kafka_consumer_auto_offset_reset = config['kafka']["consumer"]['auto-offset-reset']
        self.kafka_consumer_enable_auto_commit = config['kafka']["consumer"]['enable-auto-commit']
        self.kafka_consumer_session_timeout_ms = config['kafka']["consumer"]['session-timeout-ms']
        self.kafka_consumer_max_poll_interval_ms = config['kafka']["consumer"]['max-poll-interval-ms']
        self.kafka_consumer_heartbeat_interval_ms = config['kafka']["consumer"]['heartbeat-interval-ms']


    @classmethod
    def get_instance(cls):
        with cls._lock:
            if not hasattr(cls._local, 'instance'):
                cls._local.instance = cls()
        return cls._local.instance