import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re

def clean_text(text):
    """Clean text by removing extra whitespace and newlines"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def scrape_prothom_alo_story_elements():
    """
    Scrape latest news articles from Prothom Alo focusing specifically on
    extracting content from 'story-element story-element-text' elements
    """
    print("Starting to scrape Prothom Alo articles (story-element-text extraction)...")
    
    # Headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
    }
    
    # Base URL and homepage URL
    base_url = "https://www.prothomalo.com"
    home_url = base_url
    
    # Create CSV file for storing data
    csv_filename = 'prothom_alo_full_content.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['title', 'full_content', 'image_url', 'article_url', 'published_at'])
        
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
                    if href and '/video/' not in href and '/gallery/' not in href:
                        # Make sure it's a full URL
                        if not href.startswith('http'):
                            href = base_url + href
                        article_links.append(href)
            
            # Take unique articles, up to 20
            unique_articles = list(set(article_links))[:20]
            
            print(f"Found {len(unique_articles)} unique article links. Processing...")
            
            # Process each article
            for i, article_url in enumerate(unique_articles):
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
                    image_element = article_soup.select_one('figure img')
                    image_url = ""
                    if image_element:
                        image_url = image_element.get('src')
                        if not image_url:
                            image_url = image_element.get('data-src', '')
                    
                    # FOCUS: Extract content ONLY from story-element-text elements
                    article_content = ""
                    
                    # Find all elements with class 'story-element-text' or 'story-element story-element-text'
                    story_elements = article_soup.select('.story-element-text')
                    
                    if story_elements:
                        for element in story_elements:
                            # Extract text from each story element
                            element_text = element.get_text(strip=True)
                            if element_text:
                                article_content += element_text + "\n\n"
                    
                    # Clean up the content
                    article_content = article_content.strip()
                    
                    if not article_content:
                        print(f"No story-element-text found for article: {article_url}")
                        # Fallback: Try another common content selector just for this article
                        fallback_elements = article_soup.select('.storyContent p')
                        if fallback_elements:
                            for p in fallback_elements:
                                article_content += p.get_text(strip=True) + "\n\n"
                            article_content = article_content.strip()
                            print(f"Used fallback method and found {len(article_content)} characters")
                        else:
                            article_content = "Content extraction failed - no story-element-text found"
                    
                    # Write to CSV
                    writer.writerow([title, article_content, image_url, article_url, published_at])
                    print(f"Saved article successfully ({len(article_content)} characters)")
                    
                except Exception as e:
                    print(f"Error processing article {article_url}: {e}")
                    
        except Exception as e:
            print(f"Error: {e}")
    
    print(f"\nScraping completed. Data saved to '{csv_filename}'")

if __name__ == "__main__":
    scrape_prothom_alo_story_elements()
