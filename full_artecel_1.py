import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re
import os

def clean_text(text):
    """Clean text by removing extra whitespace and newlines"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def scrape_prothom_alo_full_content():
    """
    Scrape latest news articles from Prothom Alo with enhanced content extraction
    to ensure full article text is captured
    """
    print("Starting to scrape complete news articles from Prothom Alo...")
    
    # Headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    # Base URL and homepage URL
    base_url = "https://www.prothomalo.com"
    home_url = base_url
    
    # Create CSV file for storing data
    csv_filename = 'prothom_alo_full_articles.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['title', 'full_content', 'image_url', 'article_url', 'published_at', 'category', 'content_length'])
        
        try:
            print("Fetching homepage to extract article links...")
            response = requests.get(home_url, headers=headers)
            response.raise_for_status()
            
            # Parse homepage HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find article links on the homepage
            article_links = []
            categories = ['bangladesh', 'world', 'economy', 'sports', 'entertainment', 'opinion', 'lifestyle', 'technology']
            
            # Look for article cards or links in major categories
            for category in categories:
                category_selector = f'a[href*="/{category}/"]'
                category_links = soup.select(category_selector)
                
                for element in category_links:
                    href = element.get('href')
                    if href and '/video/' not in href and '/gallery/' not in href and href not in article_links:
                        # Make sure it's a full URL
                        if not href.startswith('http'):
                            href = base_url + href
                        article_links.append((href, category))
            
            # Take unique articles, up to 20
            seen_urls = set()
            unique_articles = []
            for url, category in article_links:
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_articles.append((url, category))
                    if len(unique_articles) >= 20:
                        break
            
            print(f"Found {len(unique_articles)} unique article links. Processing...")
            
            # Process each article
            for i, (article_url, category) in enumerate(unique_articles):
                try:
                    # Add a random delay to avoid being blocked
                    time.sleep(random.uniform(3, 5))
                    
                    print(f"Fetching article {i+1}/{len(unique_articles)}: {article_url}")
                    article_response = requests.get(article_url, headers=headers)
                    article_response.raise_for_status()
                    
                    # Parse article HTML
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    
                    # Extract title
                    title_element = article_soup.select_one('h1')
                    title = clean_text(title_element.text) if title_element else "No title found"
                    
                    # Extract publication date
                    date_element = article_soup.select_one('time')
                    published_at = date_element.get('datetime') if date_element else ""
                    
                    # Extract main image
                    image_element = article_soup.select_one('figure img') or article_soup.select_one('.article-image img')
                    image_url = ""
                    if image_element:
                        image_url = image_element.get('src')
                        if not image_url:
                            image_url = image_element.get('data-src', '')
                    
                    # Multiple strategies to extract full article content
                    article_content = ""
                    
                    # Strategy 1: Look for article content div
                    content_div = (
                        article_soup.select_one('div[data-nt="storyPageDetailMainBlock"]') or
                        article_soup.select_one('div.story-element') or  
                        article_soup.select_one('article') or 
                        article_soup.select_one('div[itemprop="articleBody"]')
                    )
                    
                    if content_div:
                        # Get all paragraphs
                        paragraphs = content_div.select('p')
                        for p in paragraphs:
                            # Skip empty paragraphs
                            if p.text.strip():
                                article_content += p.text.strip() + "\n\n"
                    
                    # Strategy 2: If we didn't find content, try another approach
                    if not article_content or len(article_content) < 200:
                        # Try to find content blocks based on class patterns
                        content_blocks = article_soup.select('.story-element-text')
                        if content_blocks:
                            for block in content_blocks:
                                article_content += block.get_text(strip=True) + "\n\n"
                    
                    # Strategy 3: If still no content, try a broader approach
                    if not article_content or len(article_content) < 200:
                        # First try to find an article container
                        article_container = article_soup.select_one('article') or article_soup.select_one('main')
                        
                        if article_container:
                            # Get all paragraphs within the article container
                            all_paragraphs = article_container.select('p')
                            # Filter out navigation, footer, etc. (usually shorter paragraphs)
                            content_paragraphs = [p.text.strip() for p in all_paragraphs if len(p.text.strip()) > 30]
                            article_content = "\n\n".join(content_paragraphs)
                    
                    # Strategy 4: Last resort, just get all significant paragraphs from the page
                    if not article_content or len(article_content) < 200:
                        # Get all paragraphs from the page
                        all_paragraphs = article_soup.select('p')
                        # Filter out potentially irrelevant paragraphs
                        content_paragraphs = [p.text.strip() for p in all_paragraphs 
                                             if len(p.text.strip()) > 40 
                                             and 'cookie' not in p.text.lower()
                                             and 'subscribe' not in p.text.lower()]
                        article_content = "\n\n".join(content_paragraphs)
                    
                    # Clean up the content
                    article_content = article_content.strip()
                    content_length = len(article_content)
                    
                    if not article_content:
                        print(f"No content found for article: {article_url}")
                        article_content = "Content extraction failed"
                        content_length = 0
                    
                    # Write to CSV
                    writer.writerow([title, article_content, image_url, article_url, published_at, category, content_length])
                    print(f"Saved article successfully ({content_length} characters)")
                    
                    # Save debug HTML for troubleshooting if content is too short
                    if content_length < 300:
                        debug_dir = "debug_html"
                        if not os.path.exists(debug_dir):
                            os.makedirs(debug_dir)
                        article_id = article_url.split('/')[-1]
                        with open(f"{debug_dir}/{article_id}.html", "w", encoding="utf-8") as debug_file:
                            debug_file.write(article_response.text)
                        print(f"Saved debug HTML for short article: {article_id}")
                    
                except Exception as e:
                    print(f"Error processing article {article_url}: {e}")
                    
        except Exception as e:
            print(f"Error: {e}")
    
    print(f"\nScraping completed. Data saved to '{csv_filename}'")
    print(f"Check the file to verify full article content was captured.")

if __name__ == "__main__":
    scrape_prothom_alo_full_content()import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re
import os

def clean_text(text):
    """Clean text by removing extra whitespace and newlines"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def scrape_prothom_alo_full_content():
    """
    Scrape latest news articles from Prothom Alo with enhanced content extraction
    to ensure full article text is captured
    """
    print("Starting to scrape complete news articles from Prothom Alo...")
    
    # Headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    # Base URL and homepage URL
    base_url = "https://www.prothomalo.com"
    home_url = base_url
    
    # Create CSV file for storing data
    csv_filename = 'prothom_alo_full_articles.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['title', 'full_content', 'image_url', 'article_url', 'published_at', 'category', 'content_length'])
        
        try:
            print("Fetching homepage to extract article links...")
            response = requests.get(home_url, headers=headers)
            response.raise_for_status()
            
            # Parse homepage HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find article links on the homepage
            article_links = []
            categories = ['bangladesh', 'world', 'economy', 'sports', 'entertainment', 'opinion', 'lifestyle', 'technology']
            
            # Look for article cards or links in major categories
            for category in categories:
                category_selector = f'a[href*="/{category}/"]'
                category_links = soup.select(category_selector)
                
                for element in category_links:
                    href = element.get('href')
                    if href and '/video/' not in href and '/gallery/' not in href and href not in article_links:
                        # Make sure it's a full URL
                        if not href.startswith('http'):
                            href = base_url + href
                        article_links.append((href, category))
            
            # Take unique articles, up to 20
            seen_urls = set()
            unique_articles = []
            for url, category in article_links:
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_articles.append((url, category))
                    if len(unique_articles) >= 20:
                        break
            
            print(f"Found {len(unique_articles)} unique article links. Processing...")
            
            # Process each article
            for i, (article_url, category) in enumerate(unique_articles):
                try:
                    # Add a random delay to avoid being blocked
                    time.sleep(random.uniform(3, 5))
                    
                    print(f"Fetching article {i+1}/{len(unique_articles)}: {article_url}")
                    article_response = requests.get(article_url, headers=headers)
                    article_response.raise_for_status()
                    
                    # Parse article HTML
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    
                    # Extract title
                    title_element = article_soup.select_one('h1')
                    title = clean_text(title_element.text) if title_element else "No title found"
                    
                    # Extract publication date
                    date_element = article_soup.select_one('time')
                    published_at = date_element.get('datetime') if date_element else ""
                    
                    # Extract main image
                    image_element = article_soup.select_one('figure img') or article_soup.select_one('.article-image img')
                    image_url = ""
                    if image_element:
                        image_url = image_element.get('src')
                        if not image_url:
                            image_url = image_element.get('data-src', '')
                    
                    # Multiple strategies to extract full article content
                    article_content = ""
                    
                    # Strategy 1: Look for article content div
                    content_div = (
                        article_soup.select_one('div[data-nt="storyPageDetailMainBlock"]') or
                        article_soup.select_one('div.story-element') or  
                        article_soup.select_one('article') or 
                        article_soup.select_one('div[itemprop="articleBody"]')
                    )
                    
                    if content_div:
                        # Get all paragraphs
                        paragraphs = content_div.select('p')
                        for p in paragraphs:
                            # Skip empty paragraphs
                            if p.text.strip():
                                article_content += p.text.strip() + "\n\n"
                    
                    # Strategy 2: If we didn't find content, try another approach
                    if not article_content or len(article_content) < 200:
                        # Try to find content blocks based on class patterns
                        content_blocks = article_soup.select('.story-element-text')
                        if content_blocks:
                            for block in content_blocks:
                                article_content += block.get_text(strip=True) + "\n\n"
                    
                    # Strategy 3: If still no content, try a broader approach
                    if not article_content or len(article_content) < 200:
                        # First try to find an article container
                        article_container = article_soup.select_one('article') or article_soup.select_one('main')
                        
                        if article_container:
                            # Get all paragraphs within the article container
                            all_paragraphs = article_container.select('p')
                            # Filter out navigation, footer, etc. (usually shorter paragraphs)
                            content_paragraphs = [p.text.strip() for p in all_paragraphs if len(p.text.strip()) > 30]
                            article_content = "\n\n".join(content_paragraphs)
                    
                    # Strategy 4: Last resort, just get all significant paragraphs from the page
                    if not article_content or len(article_content) < 200:
                        # Get all paragraphs from the page
                        all_paragraphs = article_soup.select('p')
                        # Filter out potentially irrelevant paragraphs
                        content_paragraphs = [p.text.strip() for p in all_paragraphs 
                                             if len(p.text.strip()) > 40 
                                             and 'cookie' not in p.text.lower()
                                             and 'subscribe' not in p.text.lower()]
                        article_content = "\n\n".join(content_paragraphs)
                    
                    # Clean up the content
                    article_content = article_content.strip()
                    content_length = len(article_content)
                    
                    if not article_content:
                        print(f"No content found for article: {article_url}")
                        article_content = "Content extraction failed"
                        content_length = 0
                    
                    # Write to CSV
                    writer.writerow([title, article_content, image_url, article_url, published_at, category, content_length])
                    print(f"Saved article successfully ({content_length} characters)")
                    
                    # Save debug HTML for troubleshooting if content is too short
                    if content_length < 300:
                        debug_dir = "debug_html"
                        if not os.path.exists(debug_dir):
                            os.makedirs(debug_dir)
                        article_id = article_url.split('/')[-1]
                        with open(f"{debug_dir}/{article_id}.html", "w", encoding="utf-8") as debug_file:
                            debug_file.write(article_response.text)
                        print(f"Saved debug HTML for short article: {article_id}")
                    
                except Exception as e:
                    print(f"Error processing article {article_url}: {e}")
                    
        except Exception as e:
            print(f"Error: {e}")
    
    print(f"\nScraping completed. Data saved to '{csv_filename}'")
    print(f"Check the file to verify full article content was captured.")

if __name__ == "__main__":
    scrape_prothom_alo_full_content()
