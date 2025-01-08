import sqlite3
from queue import Queue
from threading import Lock

class ConnectionPool:
    def __init__(self, db_file, max_connections=5):
        self.db_file = db_file
        self.max_connections = max_connections
        self.pool = Queue(max_connections)
        self.lock = Lock()
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(self.max_connections):
            conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.pool.put(conn)

    def get_connection(self):
        """Get a database connection from the pool"""
        return self.pool.get()

    def release_connection(self, conn):
        """Release a connection back to the pool"""
        self.pool.put(conn)

    def execute_query(self, query, params=None):
        """Execute a query using connection pool"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            conn.commit()
            return result
        finally:
            self.release_connection(conn)

    def execute_many(self, query, params_list):
        """Execute many queries using connection pool"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
        finally:
            self.release_connection(conn)

    def close_all(self):
        """Close all connections in the pool"""
        with self.lock:
            while not self.pool.empty():
                conn = self.pool.get()
                conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()