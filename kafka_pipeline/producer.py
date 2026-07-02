import json

from kafka import KafkaProducer


class SocialProducer:

    def __init__(self):

        self.producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    def send(self, topic, message):

        self.producer.send(topic, message)
        self.producer.flush()