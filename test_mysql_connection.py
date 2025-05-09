import os
import pymysql
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get connection details from environment variables
mysql_user = os.environ.get("MYSQL_USER", "root")
mysql_password = os.environ.get("MYSQL_PASSWORD", "Abcd@123")
mysql_host = os.environ.get("MYSQL_HOST", "localhost")
mysql_db = os.environ.get("MYSQL_DB", "library")
mysql_port = int(os.environ.get("MYSQL_PORT", "3306"))

print(f"Attempting to connect to MySQL database: {mysql_host}:{mysql_port}/{mysql_db}")

try:
    # Try to establish a connection
    conn = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        port=mysql_port,
        connect_timeout=5
    )
    
    print("Connection successful!")
    
    # Check if the database exists
    with conn.cursor() as cursor:
        cursor.execute("SHOW DATABASES LIKE %s", (mysql_db,))
        result = cursor.fetchone()
        
        if result:
            print(f"Database '{mysql_db}' exists.")
            
            # Switch to the database and check tables
            cursor.execute(f"USE {mysql_db}")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print("Existing tables:")
                for table in tables:
                    print(f"- {table[0]}")
            else:
                print("No tables found in the database.")
                print("You may need to run the library_schema.sql script.")
        else:
            print(f"Database '{mysql_db}' does not exist.")
            print("You need to create the database first by running the library_schema.sql script.")
    
    conn.close()
    
except Exception as e:
    print(f"Connection failed: {e}")
    print("\nTroubleshooting tips:")
    print("1. Make sure MySQL server is running on your computer")
    print("2. Check that your MySQL credentials in the .env file are correct")
    print("3. Ensure the MySQL port (default: 3306) is not blocked by a firewall")
    print("4. Verify that the MySQL user has sufficient privileges")