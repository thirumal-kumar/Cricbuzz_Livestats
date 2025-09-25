import mysql.connector
import sqlite3
import os
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        """Get database connection with Windows path fix"""
        try:
            db_type = os.getenv('DB_TYPE', 'sqlite')
            
            if db_type == 'mysql':
                self.connection = mysql.connector.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    user=os.getenv('DB_USER', 'root'),
                    password=os.getenv('DB_PASSWORD', ''),
                    database=os.getenv('DB_NAME', 'cricket_stats')
                )
            else:  # SQLite with Windows path handling
                base_dir = Path(__file__).parent.parent
                db_path = base_dir / os.getenv('DB_PATH', 'cricket_stats.db')
                self.connection = sqlite3.connect(str(db_path), check_same_thread=False)
                
            return self.connection
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
            return None

    def close_connection(self):
        if self.connection:
            self.connection.close()

db_instance = DatabaseConnection()

def get_db_connection():
    return db_instance.get_connection()

def execute_query(query, params=None, fetch=True):
    """Universal query executor"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch and query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return result, columns
        else:
            conn.commit()
            return cursor.rowcount if not fetch else None
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return None
    finally:
        cursor.close()