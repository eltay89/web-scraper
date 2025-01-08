import sqlite3
import time
from functools import wraps
from hashlib import md5

class CacheManager:
    def __init__(self, cache_file='scraper_cache.db'):
        self.conn = sqlite3.connect(cache_file)
        self.create_tables()

    def create_tables(self):
        """Create cache tables"""
        cursor = self.conn.cursor()
        
        # Create cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expiration INTEGER NOT NULL
            )
        ''')
        
        # Create index on expiration
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expiration 
            ON cache(expiration)
        ''')
        
        self.conn.commit()

    def get(self, key):
        """Get cached value"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT value FROM cache
            WHERE key = ? AND expiration > ?
        ''', (key, time.time()))
        
        result = cursor.fetchone()
        return result[0] if result else None

    def set(self, key, value, ttl=3600):
        """Set cached value with TTL"""
        cursor = self.conn.cursor()
        expiration = time.time() + ttl
        
        cursor.execute('''
            INSERT OR REPLACE INTO cache (key, value, expiration)
            VALUES (?, ?, ?)
        ''', (key, value, expiration))
        
        self.conn.commit()

    def clear_expired(self):
        """Clear expired cache entries"""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM cache
            WHERE expiration <= ?
        ''', (time.time(),))
        
        self.conn.commit()
        return cursor.rowcount

    def cache_decorator(self, ttl=3600):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self.generate_cache_key(func, args, kwargs)
                cached_value = self.get(cache_key)
                
                if cached_value is not None:
                    return cached_value
                    
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator

    def generate_cache_key(self, func, args, kwargs):
        """Generate cache key from function and arguments"""
        key_parts = [
            func.__module__,
            func.__name__,
            str(args),
            str(kwargs)
        ]
        return md5(''.join(key_parts).encode('utf-8')).hexdigest()

    def close(self):
        """Close database connection"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()