
import requests
import json
import csv
import time
import random
from datetime import datetime

def scrape_prothom_alo_latest():
    """
    Scrape latest news articles from Prothom Alo with simplified output:
    - Title in first column
    - Full article text in second column
    - Image URL in third column
    """
    print("Starting to scrape latest news from Prothom Alo...")
    
    # Headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Referer": "https://www.prothomalo.com/",
        "Origin": "https://www.prothomalo.com"
    }
    
    # API endpoint for the latest news
    api_url = "https://www.prothomalo.com/api/v1/collections/43749?offset=0&limit=50"
    
    # Create CSV file for storing data
    with open('prothom_alo_latest.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['title', 'description', 'image_url'])
        
        try:
            print("Fetching latest articles list...")
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Check if we have items in the response
            if 'items' in data and len(data['items']) > 0:
                print(f"Found {len(data['items'])} articles. Processing...")
                
                # Process each article
                for i, item in enumerate(data['items']):
                    article_id = item.get('id')
                    if not article_id:
                        continue
                    
                    # Extract headline
                    headline = ""
                    if 'item' in item and 'headline' in item['item']:
                        headline = " ".join(item['item']['headline'])
                    
                    # Get full article content
                    article_api_url = f"https://www.prothomalo.com/api/v1/stories/{article_id}"
                    
                    try:
                        # Add a delay to avoid being blocked
                        time.sleep(random.uniform(1, 2.5))
                        
                        print(f"Fetching article {i+1}/{len(data['items'])}: {headline}")
                        article_response = requests.get(article_api_url, headers=headers)
                        article_response.raise_for_status()
                        article_data = article_response.json()
                        
                        # Extract full article content
                        full_article = ""
                        image_url = ""
                        
                        # Get main image first
                        if 'hero-image' in article_data:
                            hero_image = article_data['hero-image']
                            if 'hero-image-s3-url' in hero_image:
                                image_url = hero_image['hero-image-s3-url']
                            elif 'hero-image-url' in hero_image:
                                image_url = hero_image['hero-image-url']
                        
                        # Extract article body
                        if 'story-elements' in article_data:
                            story_elements = article_data['story-elements']
                            # Process each element
                            for element in story_elements:
                                if element['type'] == 'text':
                                    if 'content' in element:
                                        full_article += element['content'] + " "
                                # Get first image URL if we don't have one yet
                                elif element['type'] == 'image' and not image_url:
                                    if 'image-s3-url' in element:
                                        image_url = element['image-s3-url']
                                    elif 'src' in element:
                                        image_url = element['src']
                        
                        # Clean up article text
                        full_article = full_article.strip()
                        
                        # Write to CSV
                        writer.writerow([headline, full_article, image_url])
                        print(f"Saved article successfully")
                        
                    except Exception as e:
                        print(f"Error processing article: {e}")
            else:
                print("No articles found in the API response")
                
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nScraping completed. Data saved to 'prothom_alo_latest.csv'")

if __name__ == "__main__":
    scrape_prothom_alo_latest()
