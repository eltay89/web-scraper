# Configuration for website scraper

# Output settings
OUTPUT_DIR = 'scraped_docs'
MARKDOWN_EXTENSION = '.md'
DEFAULT_FILENAME = 'index.md'

# Request settings
REQUEST_DELAY = 1  # seconds between requests
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
BACKOFF_FACTOR = 1

# Parallel processing settings
MAX_WORKERS = 4  # Number of parallel threads