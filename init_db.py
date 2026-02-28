import os
import mysql.connector

def init_db():
    print("Connecting to MySQL server...")
    try:
        # Connect to MySQL server without specifying database first
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", "12345")
        )
        cursor = connection.cursor()
        
        # Read the SQL file
        with open('src/database/init_db.sql', 'r') as f:
            sql_script = f.read()
            
        # Split script by semicolon
        statements = sql_script.split(';')
        
        for statement in statements:
            if statement.strip():
                print(f"Executing: {statement.strip()[:50]}...")
                cursor.execute(statement)
                
        connection.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    init_db()
