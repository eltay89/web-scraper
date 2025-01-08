# Advanced Web Scraper

A powerful and feature-rich web scraping tool built with Python.

## Features

- **Content Extraction**: Extract text, images, tables, and lists from web pages
- **JavaScript Rendering**: Supports JavaScript-heavy websites using Selenium
- **Metadata Extraction**: Automatically extracts page metadata
- **Screenshots**: Captures screenshots of web pages
- **Content Validation**: Ensures extracted content meets quality standards
- **GUI Interface**: User-friendly graphical interface for easy operation
- **Multi-threading**: Scrape multiple pages simultaneously
- **Error Handling**: Robust error handling and logging
- **Export Options**: Export results in multiple formats (Markdown, JSON, CSV, HTML)
- **Proxy Support**: Rotate proxies to avoid detection
- **Scheduling**: Schedule scraping tasks to run automatically
- **Configuration Management**: Save and load settings
- **Content Filtering**: Apply custom content filtering rules
- **Database Storage**: Store results in SQLite database
- **Content Deduplication**: Automatically detect and remove duplicate content
- **Similarity Detection**: Find similar content using machine learning
- **Advanced Analytics**: Generate reports and statistics
- **Caching**: Cache frequent requests for improved performance
- **Connection Pooling**: Optimized database connection management
- **OCR Support**: Extract text from images using OCR
- **Content Translation**: Translate extracted content
- **Distributed Scraping**: Support for distributed scraping across multiple nodes

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/web-scraper.git
   cd web-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR:
   - Windows: Download from https://github.com/tesseract-ocr/tesseract
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

4. Download ChromeDriver from https://sites.google.com/chromium.org/driver/
   and place it in your system PATH

## Usage

### GUI Mode
Run the GUI application:
```bash
python gui.py
```

### Command Line Mode
You can also run the scraper from the command line:
```bash
python main.py https://example.com
```

### Database Features
The scraper automatically stores results in a SQLite database (scraper.db). You can:
- View stored results
- Search content
- Remove duplicates
- Find similar content
- Generate reports

### Content Processing
The scraper provides advanced content processing:
- Content deduplication
- Similarity detection
- OCR for image content
- Content translation
- Caching for improved performance

### Configuration
Edit `config.json` to customize:
- Output directory
- Request settings
- Parallel processing settings
- Content type filters
- Proxy settings
- Scheduling options
- Database settings
- Deduplication thresholds
- Cache settings
- OCR settings
- Translation settings

### Scheduling
To schedule scraping tasks:
1. Open the GUI
2. Go to the Scheduler tab
3. Add a new schedule with URL and interval
4. Enable the schedule

### Exporting Data
The scraper supports multiple export formats:
- Markdown (.md)
- JSON (.json)
- CSV (.csv)
- HTML (.html)

Select your preferred format in the Export menu.

## Advanced Features

### Performance Optimization
- Caching for frequent requests
- Connection pooling for database operations
- Optimized database queries
- Request throttling
- Resource pooling

### Content Processing
- OCR for image content extraction
- Content translation
- Advanced content filtering
- Machine learning-based classification
- Similarity detection

### Distributed Scraping
- Support for multiple scraping nodes
- Centralized job management
- Distributed result collection
- Fault tolerance

## License

MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.