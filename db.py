import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'bus_depot')
            )
            print(os.getenv('DB_HOST'))
            print(os.getenv('DB_USER'))
            print(os.getenv('DB_PASSWORD'))
            print(os.getenv('DB_NAME'))
            print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
    
    def execute_query(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            print(50*"*")
            print(cursor)
            print(50*"*")
            return cursor
        except Error as e:
            print(f"Error executing query: {e}")
            return None
    def fetch_all(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()  # Явно получаем все результаты
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
        finally:
            if cursor:
                cursor.close()  # Всегда закрываем курсор

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")