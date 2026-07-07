import psycopg2
import pandas as pd

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="dvdrental",
        user="postgres",
        password="rahmamaya"
    )

def fetch_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df