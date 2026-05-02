import mysql.connector
from mysql.connector import Error

def get_connection():
    """Create and return a MySQL connection"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='mydatabase',
            user='admin',
            password='1234',
            port=3307
        )
        if conn.is_connected():
            print("Connected to MySQL Server", conn.get_server_info())
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print("Connected to database:", record)
            cursor.close()
            return conn  # <-- return the connection object
    except Error as e:
        print("Error while connecting to database:", e)
        return None
