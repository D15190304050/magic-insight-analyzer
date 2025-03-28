import time
from confluent_kafka import Consumer, KafkaException, KafkaError

conf = {
    'bootstrap.servers': 'localhost:29092,localhost:39092,localhost:49092',  # Kafka集群的地址
    'group.id': 'kafkaRunner2Px',  # 消费者组ID
    'auto.offset.reset': 'earliest',  # 从最早的偏移量开始读取
    'enable.auto.commit': False,  # 禁用自动提交
    'session.timeout.ms': 10000,  # 会话超时时间
    'max.poll.interval.ms': 300000,  # 最大提交时间间隔
    'heartbeat.interval.ms': 3000,  # 心跳间隔
}

consumer = Consumer(conf)


def consume_messages(topic):
    try:
        consumer.subscribe([topic])

        while True:
            msg = consumer.poll(timeout=1.0)  # 拉取消息，设置超时时间
            if msg is None:
                time.sleep(1)
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('End of partition reached')
                else:
                    raise KafkaException(msg.error())
            else:
                print(f'Received message: {msg.value().decode("utf-8")}')

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        consumer.close()


# 调用函数，指定要消费的topic
consume_messages('test-topic')
