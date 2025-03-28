import logging
from confluent_kafka import Producer
import json
from Configuration import Configuration

logger = logging.getLogger()
config = Configuration.get_instance()

# 键值序列化器示例：这里使用 JSON 序列化器作为示例
def key_serializer(key):
    return json.dumps(key).encode("utf-8")  # 假设 key 是一个字典类型

def value_serializer(value):
    return json.dumps(value).encode("utf-8")  # 假设 value 也是一个字典类型

# Kafka 配置
conf = {
    "bootstrap.servers": config.kafka_bootstrap_servers,  # Kafka broker 地址
    "compression.type": config.kafka_producer_compression_type,  # 禁用压缩
    "client.id": config.kafka_producer_client_id,  # 客户端 ID
    "buffer.memory": config.kafka_producer_buffer_memory,  # 缓冲区大小：32MB
    "retries": config.kafka_producer_retries,  # 重试次数
    "acks": config.kafka_producer_acks,  # ack 应答级别：all (确保所有副本都接收到消息)
    "batch.size": config.kafka_producer_batch_size,  # 批次大小：16KB
    "linger.ms": config.kafka_producer_linger_ms,  # 设置 linger.ms 为 1000ms
}

# 创建一个生产者实例
producer = Producer(conf)

# 发送消息的回调函数
def delivery_report(err, msg):
    """消息发送后的回调函数"""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# 要发送的消息
topic = "my_topic"
key = {"id": 123}
value = {"message": "Hello Kafka!"}

# 发送消息
producer.produce(
    topic,
    key=key_serializer(key),
    value=value_serializer(value),
    callback=delivery_report
)

# 确保消息已发送（将所有排队的消息发送出去）
producer.flush()
