import os
import time
import mysql.connector

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            connection = mysql.connector.connect(
                host=os.environ.get("MYSQL_HOST", "localhost"),
                user=os.environ.get("MYSQL_USER", "root"),
                password=os.environ.get("MYSQL_PASSWORD", "12345"),
                database=os.environ.get("MYSQL_DB", "inventory_db")
            )
            return connection
        except Exception as e:
            print(f"MySQL Connection Error: {e}. Retrying in 3 seconds...")
            retries -= 1
            time.sleep(3)
    print("Could not connect to MySQL server. Exiting.")
    return None