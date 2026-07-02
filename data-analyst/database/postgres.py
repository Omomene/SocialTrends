import psycopg2

from config import *

class PostgresManager:

    def __init__(self):

        self.conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )

        self.cursor = self.conn.cursor()

    def execute(self, query, params=None):

        self.cursor.execute(query, params)

        self.conn.commit()

    def fetchall(self):

        return self.cursor.fetchall()

    def insert_sentiment_hourly(
        self,
        hour_ts,
        match_id,
        post_count,
        positive_count,
        neutral_count,
        negative_count,
        avg_sentiment
    ):

        query = """
        INSERT INTO sentiment_hourly
        (
            hour_ts,
            match_id,
            post_count,
            positive_count,
            neutral_count,
            negative_count,
            avg_sentiment
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)

        ON CONFLICT (hour_ts, match_id)

        DO UPDATE SET

        post_count = EXCLUDED.post_count,
        positive_count = EXCLUDED.positive_count,
        neutral_count = EXCLUDED.neutral_count,
        negative_count = EXCLUDED.negative_count,
        avg_sentiment = EXCLUDED.avg_sentiment;
        """

        self.execute(
            query,
            (
                hour_ts,
                match_id,
                post_count,
                positive_count,
                neutral_count,
                negative_count,
                avg_sentiment
            )
        )

    def insert_topic_hourly(
        self,
        hour_ts,
        match_id,
        topic,
        occurrences
    ):

        query = """
        INSERT INTO topic_hourly
        (
            hour_ts,
            match_id,
            topic,
            occurrences
        )
        VALUES (%s,%s,%s,%s);
        """

        self.execute(
            query,
            (
                hour_ts,
                match_id,
                topic,
                occurrences
            )
        )

    def close(self):

        self.cursor.close()

        self.conn.close()