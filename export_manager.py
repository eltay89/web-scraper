import os
import json
import csv
from datetime import datetime

class ExportManager:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_as_markdown(self, content, filename):
        """Export content as markdown file"""
        path = os.path.join(self.output_dir, f"{filename}.md")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    def export_as_json(self, data, filename):
        """Export data as JSON file"""
        path = os.path.join(self.output_dir, f"{filename}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return path

    def export_as_csv(self, data, filename):
        """Export data as CSV file"""
        path = os.path.join(self.output_dir, f"{filename}.csv")
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if isinstance(data, dict):
                writer.writerow(data.keys())
                writer.writerow(data.values())
            elif isinstance(data, list):
                writer.writerow(data[0].keys())
                for item in data:
                    writer.writerow(item.values())
        return path

    def export_as_html(self, content, filename):
        """Export content as HTML file"""
        path = os.path.join(self.output_dir, f"{filename}.html")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"<html><body>\n{content}\n</body></html>")
        return path

    def generate_filename(self, url):
        """Generate a filename based on URL and timestamp"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path.replace('/', '_') if parsed.path else 'index'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{domain}_{path}_{timestamp}"