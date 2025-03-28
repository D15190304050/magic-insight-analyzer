import logging
import logging.config
import yaml
from VideoAnalysisMessageHandler import VideoAnalysisMessageHandler
from kafka.KafkaConsumer import KafkaConsumer
from Configuration import Configuration

config = Configuration.get_instance()

def load_logging_config():
    with open('./logging_config.yaml', 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

if __name__ == '__main__':
    load_logging_config()
    summary_handler = VideoAnalysisMessageHandler()

    kafka_consumer = KafkaConsumer()
    kafka_consumer.consume_messages(config.kafka_consumer_topic_summary_video_start, summary_handler)
