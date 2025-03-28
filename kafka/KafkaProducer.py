import logging
from confluent_kafka import Producer
import json
from Configuration import Configuration

logger = logging.getLogger(__name__)
config = Configuration.get_instance()

# Kafka 配置
kafka_config: dict = {
    "bootstrap.servers": config.kafka_bootstrap_servers,  # Kafka broker 地址
    "compression.type": config.kafka_producer_compression_type,  # 禁用压缩
    "client.id": config.kafka_producer_client_id,  # 客户端 ID
    # "buffer.memory": config.kafka_producer_buffer_memory,  # 缓冲区大小：32MB
    "retries": config.kafka_producer_retries,  # 重试次数
    "acks": config.kafka_producer_acks,  # ack 应答级别：all (确保所有副本都接收到消息)
    "batch.size": config.kafka_producer_batch_size,  # 批次大小：16KB
    "linger.ms": config.kafka_producer_linger_ms,  # 设置 linger.ms 为 1000ms
}

# 键值序列化器示例：这里使用 JSON 序列化器作为示例
def key_serializer(key):
    if (key is None):
        return None
    return json.dumps(key).encode("utf-8")  # 假设 key 是一个字典类型

def value_serializer(value):
    return json.dumps(value).encode("utf-8")  # 假设 value 也是一个字典类型

# 发送消息的回调函数
def delivery_report(err, msg):
    """消息发送后的回调函数"""
    if err is not None:
        logger.info(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

class KafkaProducer:
    def __init__(self):
        # 创建一个生产者实例
        self.producer = Producer(kafka_config)

    def produce(self, topic: str, key: object, value: object):
        """
        发送消息
        :param topic:
        :param key:
        :param value:
        :return:
        """

        key = key_serializer(key)
        message_value = value_serializer(value)

        logger.info(f"Sending message: {message_value}, key = {key}, topic = {topic}")

        self.producer.produce(
            topic,
            key=key,
            value=message_value,
            callback=delivery_report
        )

        logger.info(f"Done sending message: {message_value}, key = {key}, topic = {topic}")

        # 确保消息已发送（将所有排队的消息发送出去）
        # self.producer.flush()
