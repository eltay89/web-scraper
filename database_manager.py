import sqlite3
from datetime import datetime
from hashlib import md5

class DatabaseManager:
    def __init__(self, db_file='scraper.db'):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        """Create necessary database tables"""
        cursor = self.conn.cursor()
        
        # Create results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create unique index on content hash
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_content_hash 
            ON results(content_hash)
        ''')
        
        self.conn.commit()

    def save_result(self, url, content, metadata=None):
        """Save scraping result to database"""
        content_hash = self.generate_content_hash(content)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO results (url, content_hash, content, metadata)
                VALUES (?, ?, ?, ?)
            ''', (url, content_hash, content, str(metadata)))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Content already exists
            return False

    def generate_content_hash(self, content):
        """Generate MD5 hash of content for deduplication"""
        return md5(content.encode('utf-8')).hexdigest()

    def get_results(self, limit=100, offset=0):
        """Get stored results"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM results
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        return cursor.fetchall()

    def search_results(self, query):
        """Search stored results"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM results
            WHERE content LIKE ?
            ORDER BY timestamp DESC
        ''', (f'%{query}%',))
        return cursor.fetchall()

    def close(self):
        """Close database connection"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()