import re
from bs4 import BeautifulSoup

class ContentValidator:
    def __init__(self, config):
        self.config = config
        self.min_length = config.get('content_filters', {}).get('min_length', 100)
        self.min_paragraphs = config.get('content_filters', {}).get('min_paragraphs', 1)
        self.allowed_domains = config.get('content_filters', {}).get('allowed_domains', [])

    def validate_content(self, content, url):
        """Validate extracted content"""
        if not content:
            return False
            
        # Check content length
        if len(content) < self.min_length:
            return False
            
        # Check number of paragraphs
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) < self.min_paragraphs:
            return False
            
        # Check domain restrictions
        if self.allowed_domains:
            domain = self.extract_domain(url)
            if domain not in self.allowed_domains:
                return False
                
        return True

    def extract_domain(self, url):
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

    def clean_html(self, html):
        """Clean and sanitize HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'iframe', 'noscript']):
            tag.decompose()
            
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
            
        return str(soup)

    def filter_content(self, content):
        """Apply content filtering rules"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove empty paragraphs
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        return '\n\n'.join(paragraphs)