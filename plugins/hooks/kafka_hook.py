from kafka import KafkaProducer
from kafka import KafkaConsumer

import json


class KafkaHook:

    def get_producer(self):

        return KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v:
            json.dumps(v).encode("utf-8")
        )

    def get_consumer(self, topic):

        return KafkaConsumer(
            topic,
            bootstrap_servers="kafka:9092",
            auto_offset_reset="earliest",
            value_deserializer=lambda x:
            json.loads(x.decode("utf-8"))
        )