import json
from kafka import KafkaConsumer


class SocialConsumer:

    def __init__(self, topic: str):

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers="kafka:9092",
            group_id="social-cleaning-test",

            # IMPORTANT FIXES
            auto_offset_reset="earliest",
            enable_auto_commit=False,

            # give enough time for DAG execution
            consumer_timeout_ms=15000,

            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )

    def read(self):
        self.consumer.poll(timeout_ms=1000)

        count = 0

        for message in self.consumer:
            yield message.value

            count += 1

            # IMPORTANT: prevent infinite/long execution
            if count >= 500:
                break

    def close(self):
        self.consumer.close()