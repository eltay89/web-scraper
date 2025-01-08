import json
import os

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self.create_default_config()

    def create_default_config(self):
        """Create default configuration"""
        config = {
            'output_dir': 'scraped_data',
            'max_depth': 1,
            'max_threads': 5,
            'request_delay': 1.0,
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
            ],
            'proxies': [],
            'content_filters': {
                'min_length': 100,
                'min_paragraphs': 1,
                'allowed_domains': []
            },
            'schedules': []
        }
        self.save_config(config)
        return config

    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def get_setting(self, key, default=None):
        """Get a specific setting"""
        return self.config.get(key, default)

    def update_setting(self, key, value):
        """Update a specific setting"""
        self.config[key] = value
        self.save_config()

    def add_proxy(self, proxy):
        """Add a new proxy to the configuration"""
        if proxy not in self.config['proxies']:
            self.config['proxies'].append(proxy)
            self.save_config()

    def add_schedule(self, schedule):
        """Add a new scraping schedule"""
        self.config['schedules'].append(schedule)
        self.save_config()

    def get_random_user_agent(self):
        """Get a random user agent from the list"""
        import random
        return random.choice(self.config['user_agents'])