import logging
from Configuration import Configuration
from confluent_kafka import Consumer, KafkaException, KafkaError

logger = logging.getLogger(__name__)
config = Configuration.get_instance()

kafka_config = {
    'bootstrap.servers': config.kafka_bootstrap_servers,  # Kafka集群的地址
    'group.id': config.kafka_consumer_group_id,  # 消费者组ID
    'auto.offset.reset': config.kafka_consumer_auto_offset_reset,  # 从最早的偏移量开始读取
    'enable.auto.commit': config.kafka_consumer_enable_auto_commit,  # 禁用自动提交
    'session.timeout.ms': config.kafka_consumer_session_timeout_ms,  # 会话超时时间
    'max.poll.interval.ms': config.kafka_consumer_max_poll_interval_ms,  # 最大提交时间间隔
    'heartbeat.interval.ms': config.kafka_consumer_heartbeat_interval_ms,  # 心跳间隔
}

class KafkaConsumer:
    def __init__(self):
        self.consumer = Consumer(kafka_config)

    def consume_messages(self, topic: str, handler):
        try:
            self.consumer.subscribe([topic])

            while True:
                msg = self.consumer.poll(timeout=1.0)  # 拉取消息，设置超时时间
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.info('End of partition reached')
                    else:
                        raise KafkaException(msg.error())
                else:
                    message_value = msg.value().decode("utf-8")
                    logger.info(f'Received message: {message_value}')
                    handler(message = message_value)
                    self.consumer.commit()

        except Exception as e:
            logger.error(f"Error occurred: {e}")

        finally:
            self.consumer.close()