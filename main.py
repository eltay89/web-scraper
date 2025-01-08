"""
Advanced Web Scraper

This script scrapes content from websites and saves it in Markdown format.
It uses the trafilatura library for robust content extraction.
"""
import requests
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
import config
from concurrent.futures import ThreadPoolExecutor, as_completed
import trafilatura
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import json
from PIL import Image
import io

# Configure retry strategy for network requests
retry_strategy = Retry(
    total=config.MAX_RETRIES,
    backoff_factor=config.BACKOFF_FACTOR,
    status_forcelist=[429, 500, 502, 503, 504]
)

# Create a requests session with retry capabilities
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)

# Mount the adapter to handle both HTTP and HTTPS requests
session.mount("http://", adapter)
session.mount("https://", adapter)

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def create_filename(url):
    """Create a filename from the URL"""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/').replace('/', '_')
    
    # Clean up the filename
    filename = f"{domain}_{path}" if path else domain
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    filename = filename[:100]  # Limit length
    return filename

def take_screenshot(url, output_dir):
    """Take a screenshot of the webpage"""
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(2)  # Wait for page to load
        
        # Create screenshot filename
        filename = create_filename(url) + ".png"
        screenshot_path = os.path.join(output_dir, filename)
        
        # Take screenshot
        screenshot = driver.get_screenshot_as_png()
        driver.quit()
        
        # Save screenshot
        image = Image.open(io.BytesIO(screenshot))
        image.save(screenshot_path)
        return screenshot_path
    except Exception as e:
        return None

def extract_metadata(html_content):
    """Extract metadata from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    metadata = {
        'title': soup.title.string if soup.title else None,
        'description': soup.find('meta', attrs={'name': 'description'})['content'] 
            if soup.find('meta', attrs={'name': 'description'}) else None,
        'keywords': soup.find('meta', attrs={'name': 'keywords'})['content']
            if soup.find('meta', attrs={'name': 'keywords'}) else None,
        'author': soup.find('meta', attrs={'name': 'author'})['content']
            if soup.find('meta', attrs={'name': 'author'}) else None,
        'timestamp': datetime.now().isoformat()
    }
    return metadata

def validate_content(content):
    """Validate extracted content"""
    if not content:
        return False
        
    # Basic validation checks
    min_length = 100  # Minimum content length
    min_paragraphs = 1  # Minimum number of paragraphs
    
    paragraphs = [p for p in content.split('\n\n') if p.strip()]
    return len(content) >= min_length and len(paragraphs) >= min_paragraphs

def extract_specific_data(html_content, queue=None):
    """Extract specific data from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract various types of content
    extracted_data = {
        'headings': [],
        'paragraphs': [],
        'tables': [],
        'lists': [],
        'images': [],
        'metadata': extract_metadata(html_content)
    }

    # Extract headings
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        extracted_data['headings'].append(heading.get_text().strip())

    # Extract paragraphs
    for paragraph in soup.find_all('p'):
        text = paragraph.get_text().strip()
        if text:
            extracted_data['paragraphs'].append(text)

    # Extract tables
    for table in soup.find_all('table'):
        rows = []
        for row in table.find_all('tr'):
            cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
            if cells:
                rows.append(cells)
        if rows:
            extracted_data['tables'].append(rows)

    # Extract lists
    for list_tag in soup.find_all(['ul', 'ol']):
        items = [li.get_text().strip() for li in list_tag.find_all('li')]
        if items:
            extracted_data['lists'].append(items)

    # Extract image sources
    for img in soup.find_all('img', src=True):
        extracted_data['images'].append(img['src'])

    if queue:
        # Format and send extracted data to GUI
        formatted_data = []
        if extracted_data['headings']:
            formatted_data.append("## Headings\n" + "\n".join(f"- {h}" for h in extracted_data['headings']))
        if extracted_data['paragraphs']:
            formatted_data.append("## Paragraphs\n" + "\n".join(f"- {p}" for p in extracted_data['paragraphs']))
        if extracted_data['tables']:
            formatted_data.append("## Tables\n" + "\n".join(
                f"Table {i+1}:\n" + "\n".join(" | ".join(row) for row in table)
                for i, table in enumerate(extracted_data['tables'])
            ))
        if extracted_data['lists']:
            formatted_data.append("## Lists\n" + "\n".join(
                f"List {i+1}:\n" + "\n".join(f"- {item}" for item in lst)
                for i, lst in enumerate(extracted_data['lists'])
            ))
        if extracted_data['images']:
            formatted_data.append("## Images\n" + "\n".join(f"- {src}" for src in extracted_data['images']))
        if extracted_data['metadata']:
            formatted_data.append("## Metadata\n" + json.dumps(extracted_data['metadata'], indent=2))

        if formatted_data:
            queue.put(("data", "\n\n".join(formatted_data)))

    return extracted_data

def scrape_page(url, base_url, queue=None, depth=0):
    """
    Scrape a single webpage and extract its main content and links.

    Args:
        url (str): The full URL of the page to scrape.
        base_url (str): The base URL of the website.
        queue (Queue): Optional queue for progress updates
        depth (int): Current scraping depth

    Returns:
        None
    """
    global total_pages, successful_pages, failed_pages

    try:
        time.sleep(config.REQUEST_DELAY)
        response = session.get(url, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()

        # Use trafilatura to extract main content in Markdown format
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            # Extract specific data first
            extracted_data = extract_specific_data(downloaded, queue)
            
            extracted_content = trafilatura.extract(
                downloaded,
                output_format='markdown',
                favor_precision=True,
                include_links=True,
                include_tables=True,
                include_images=True,
                include_formatting=True,
                include_comments=False,
                deduplicate=True
            )

            # Validate content
            if not validate_content(extracted_content):
                raise ValueError("Content validation failed")

            # Combine extracted content with specific data
            if extracted_content:
                markdown_content = extracted_content + "\n\n"
                if extracted_data['headings']:
                    markdown_content += "## Extracted Headings\n" + "\n".join(f"- {h}" for h in extracted_data['headings']) + "\n\n"
                if extracted_data['tables']:
                    markdown_content += "## Extracted Tables\n" + "\n".join(
                        f"Table {i+1}:\n" + "\n".join(" | ".join(row) for row in table)
                        for i, table in enumerate(extracted_data['tables'])
                    ) + "\n\n"
                
                # Take screenshot
                screenshot_path = take_screenshot(url, config.OUTPUT_DIR)
                if screenshot_path:
                    markdown_content += f"## Screenshot\n![Screenshot]({os.path.basename(screenshot_path)})\n\n"
        else:
            log_error(f"Failed to download content from {url}")
            failed_pages += 1
            if queue:
                queue.put(("progress", {
                    "total": total_pages,
                    "success": successful_pages,
                    "failed": failed_pages
                }))
            return
        
        if extracted_content:
            successful_pages += 1
            file_name = create_filename(url) + config.MARKDOWN_EXTENSION

            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"Saved {file_name}")
            except Exception as e:
                log_error(f"Error saving file {file_name}: {str(e)}")
                failed_pages += 1
                if queue:
                    queue.put(("progress", {
                        "total": total_pages,
                        "success": successful_pages,
                        "failed": failed_pages
                    }))
                return

            # Extract links using trafilatura
            try:
                extracted_links = trafilatura.extract_links(downloaded) or []
            except Exception as e:
                log_error(f"Error extracting links from {url}: {str(e)}")
                extracted_links = []
            
            if extracted_links and depth < config.MAX_DEPTH:
                total_pages = len(scraped_urls)
                with tqdm(total=total_pages, desc="Scraping Progress") as pbar:
                    urls_to_scrape = []
                    for link_data in extracted_links:
                        link = link_data['href']
                        full_url = urljoin(base_url, link)

                        if full_url not in scraped_urls:
                            scraped_urls.add(full_url)
                            total_pages += 1
                            pbar.total = total_pages
                            urls_to_scrape.append(full_url)

                    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
                        futures = {executor.submit(scrape_page, url, base_url, queue, depth+1): url for url in urls_to_scrape}
                        for future in as_completed(futures):
                            try:
                                future.result()
                            except Exception as e:
                                log_error(f"Error processing page: {str(e)}")
                                failed_pages += 1
                            finally:
                                pbar.update(1)
                                if queue:
                                    queue.put(("progress", {
                                        "total": total_pages,
                                        "success": successful_pages,
                                        "failed": failed_pages
                                    }))
        else:
            log_error(f"Could not extract content from {url}")
            failed_pages += 1
            if queue:
                queue.put(("progress", {
                    "total": total_pages,
                    "success": successful_pages,
                    "failed": failed_pages
                }))

    except requests.exceptions.Timeout as e:
        log_error(f"Timeout error: {url} - {str(e)}")
        failed_pages += 1
        if queue:
            queue.put(("progress", {
                "total": total_pages,
                "success": successful_pages,
                "failed": failed_pages
            }))
        return
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            log_error(f"Forbidden error: {url} - {str(e)}")
        else:
            log_error(f"HTTP error: {url} - {str(e)}")
        failed_pages += 1
        if queue:
            queue.put(("progress", {
                "total": total_pages,
                "success": successful_pages,
                "failed": failed_pages
            }))
        return
    except requests.exceptions.RequestException as e:
        log_error(f"Request error: {url} - {str(e)}")
        failed_pages += 1
        if queue:
            queue.put(("progress", {
                "total": total_pages,
                "success": successful_pages,
                "failed": failed_pages
            }))
        return

def log_error(message):
    """Logs an error message to a file."""
    with open('scraping_errors.log', 'a', encoding='utf-8') as log_file:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {message}\n")

def main(start_url, queue=None, max_depth=1):
    """
    Main function to start the scraping process.

    Args:
        start_url (str): The URL to start scraping from
        queue (Queue): Optional queue for progress updates
        max_depth (int): Maximum scraping depth

    Returns:
        None
    """
    global scraped_urls, total_pages, successful_pages, failed_pages
    scraped_urls = set([start_url])
    total_pages = 1
    successful_pages = 0
    failed_pages = 0
    config.MAX_DEPTH = max_depth

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    original_dir = os.getcwd()

    try:
        os.chdir(config.OUTPUT_DIR)
        scrape_page(start_url, start_url, queue)

        print("\nScraping complete!")
        print(f"Total pages discovered: {total_pages}")
        print(f"Successfully scraped pages: {successful_pages}")
        print(f"Failed pages: {failed_pages}")
        success_rate = (successful_pages / total_pages) * 100 if total_pages > 0 else 0
        print(f"Success rate: {success_rate:.2f}%")

        return successful_pages > 0

    finally:
        os.chdir(original_dir)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Please provide a URL to scrape")
