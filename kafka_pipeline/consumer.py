import json

from kafka import KafkaConsumer


class SocialConsumer:

    def __init__(self, topic):

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers="kafka:9092",
            auto_offset_reset="earliest",
            value_deserializer=lambda x: json.loads(
                x.decode("utf-8")
            )
        )

    def read(self):

        for message in self.consumer:
            yield message.value