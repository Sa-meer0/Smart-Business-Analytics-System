import pymysql
from pymysql import Error
from config import Config


class Database:
    """Database connection handler using context manager pattern"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def __enter__(self):
        """Establish database connection when entering context"""
        try:
            self.connection = pymysql.connect(
                host=Config.DB_HOST,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            self.cursor = self.connection.cursor()
            return self
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close database connection when exiting context"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            
    def execute_query(self, query, params=None):
        """Execute a query and return cursor for result fetching"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except Error as e:
            print(f"Query execution error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise
            
    def fetch_one(self, query, params=None):
        """Execute query and fetch one row"""
        self.execute_query(query, params)
        return self.cursor.fetchone()
        
    def fetch_all(self, query, params=None):
        """Execute query and fetch all rows"""
        self.execute_query(query, params)
        return self.cursor.fetchall()
    
    def insert_one(self, query, params=None):
        """Execute query and return last insert ID"""
        self.execute_query(query, params)
        return self.cursor.lastrowid
    
    def get_table_columns(self, table_name):
        """Get column names for a table"""
        self.execute_query(f"DESCRIBE {table_name}")
        return self.cursor.fetchall()