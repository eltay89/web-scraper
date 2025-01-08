import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ProxyManager:
    def __init__(self, config):
        self.proxies = config.get('proxies', [])
        self.current_proxy = None
        self.session = self.create_session()

    def create_session(self):
        """Create a requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get_random_proxy(self):
        """Get a random proxy from the list"""
        if self.proxies:
            return random.choice(self.proxies)
        return None

    def rotate_proxy(self):
        """Rotate to a new proxy"""
        self.current_proxy = self.get_random_proxy()
        return self.current_proxy

    def make_request(self, url, headers=None):
        """Make a request using the current proxy"""
        proxies = None
        if self.current_proxy:
            proxies = {
                'http': self.current_proxy,
                'https': self.current_proxy
            }

        try:
            response = self.session.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=10
            )
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_proxy(self, proxy):
        """Test if a proxy is working"""
        test_url = 'http://httpbin.org/ip'
        try:
            response = requests.get(
                test_url,
                proxies={'http': proxy, 'https': proxy},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def add_proxy(self, proxy):
        """Add a new proxy to the manager"""
        if proxy not in self.proxies and self.test_proxy(proxy):
            self.proxies.append(proxy)
            return True
        return False