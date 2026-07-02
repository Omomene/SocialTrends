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
        VALUES (%s,%s,%s,%s)

        ON CONFLICT (hour_ts, match_id, topic)
        DO UPDATE SET
        occurrences = EXCLUDED.occurrences;
        
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

    def insert_sentiment_timeline(
        self,
        hour_ts,
        match_id,
        sentiment_index,
        dominant_sentiment,
        total_posts
    ):


        query = """
        INSERT INTO sentiment_timeline
        (
            hour_ts,
            match_id,
            sentiment_index,
            dominant_sentiment,
            total_posts
        )
        VALUES (%s,%s,%s,%s,%s)

        ON CONFLICT (hour_ts, match_id)

        DO UPDATE SET

        sentiment_index = EXCLUDED.sentiment_index,
        dominant_sentiment = EXCLUDED.dominant_sentiment,
        total_posts = EXCLUDED.total_posts;
        """

        self.execute(
            query,
            (
                hour_ts,
                match_id,
                sentiment_index,
                dominant_sentiment,
                total_posts
            )
        )

    def insert_event_correlation(
        self,
        event_id,
        match_id,
        event_time,
        event_type,
        volume_delta,
        sentiment_delta,
        dominant_topic_after,
        correlation_strength,
        explanation
    ):

        query = """
        INSERT INTO event_correlations
        (
            event_id,
            match_id,
            event_time,
            event_type,
            volume_delta,
            sentiment_delta,
            dominant_topic_after,
            correlation_strength,
            explanation
        )

        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
       

        ON CONFLICT (event_id)
        DO UPDATE SET

        volume_delta = EXCLUDED.volume_delta,
        sentiment_delta = EXCLUDED.sentiment_delta,
        dominant_topic_after = EXCLUDED.dominant_topic_after,
        correlation_strength = EXCLUDED.correlation_strength,
        explanation = EXCLUDED.explanation;
        """

        self.execute(
            query,
            (
                event_id,
                match_id,
                event_time,
                event_type,
                volume_delta,
                sentiment_delta,
                dominant_topic_after,
                correlation_strength,
                explanation
            )
        )

    def insert_trend_summary(
        self,
        match_id,
        match_name,
        summary_text,
        generated_at
    ):

        query = """
        INSERT INTO trend_summary
        (
            match_id,
            match_name,
            summary_text,
            generated_at
        )
        VALUES (%s,%s,%s,%s)

        ON CONFLICT (match_id)

        DO UPDATE SET

        summary_text = EXCLUDED.summary_text,
        generated_at = EXCLUDED.generated_at;
        """

        self.execute(
            query,
            (
                match_id,
                match_name,
                summary_text,
                generated_at
            )
        )

    def close(self):

        self.cursor.close()

        self.conn.close()