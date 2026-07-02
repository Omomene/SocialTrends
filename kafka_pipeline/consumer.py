import json

from kafka import KafkaConsumer


class SocialConsumer:

    def __init__(self, topic):

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers="kafka:9092",
            group_id="social-cleaning",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=3000,
            value_deserializer=lambda x: json.loads(
                x.decode("utf-8")
            )
        )

    def read(self):

        for message in self.consumer:
            yield message.value