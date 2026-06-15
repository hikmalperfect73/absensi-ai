# config/database.py
import mysql.connector
import os

def get_db():
    # Railway otomatis set variable ini saat pakai MySQL plugin
    conn = mysql.connector.connect(
        host=os.getenv('MYSQLHOST', os.getenv('DB_HOST', 'localhost')),
        user=os.getenv('MYSQLUSER', os.getenv('DB_USER', 'root')),
        password=os.getenv('MYSQLPASSWORD', os.getenv('DB_PASS', '')),
        database=os.getenv('MYSQLDATABASE', os.getenv('DB_NAME', 'absensi_ai')),
        port=int(os.getenv('MYSQLPORT', 3306)),
        charset='utf8mb4'
    )
    return conn
