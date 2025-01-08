from hashlib import md5
from database_manager import DatabaseManager

class ContentDeduplicator:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def is_duplicate(self, content):
        """Check if content already exists in database"""
        content_hash = self.generate_content_hash(content)
        return self.db_manager.content_exists(content_hash)

    def generate_content_hash(self, content):
        """Generate MD5 hash of content"""
        return md5(content.encode('utf-8')).hexdigest()

    def process_content(self, content):
        """Process content to remove duplicates"""
        if self.is_duplicate(content):
            return None
            
        # Additional processing can be added here
        return content

    def find_similar_content(self, content, threshold=0.8):
        """Find similar content using text similarity"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Get existing content from database
        existing_content = [r[3] for r in self.db_manager.get_results(limit=1000)]
        
        if not existing_content:
            return []
            
        # Calculate similarity scores
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(existing_content + [content])
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        
        # Find similar content above threshold
        similar = []
        for i, score in enumerate(similarity_scores[0]):
            if score > threshold:
                similar.append({
                    'content': existing_content[i],
                    'similarity': float(score)
                })
                
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)

    def remove_duplicates(self):
        """Remove duplicate content from database"""
        cursor = self.db_manager.conn.cursor()
        
        # Find and remove duplicates
        cursor.execute('''
            DELETE FROM results
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM results
                GROUP BY content_hash
            )
        ''')
        
        self.db_manager.conn.commit()
        return cursor.rowcount