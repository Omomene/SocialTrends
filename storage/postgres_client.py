import psycopg2


def get_postgres():

    return psycopg2.connect(
        host="postgres",
        database="socialtrends",
        user="app",
        password="app12345"
    )