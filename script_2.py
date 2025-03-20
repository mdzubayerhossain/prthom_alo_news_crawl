import requests
import csv
import time
import random
import json

def scrape_prothom_alo_latest():
    print("Starting to scrape latest news from Prothom Alo...")
    
    headers = {
        "User -Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Referer": "https://www.prothomalo.com/",
        "Origin": "https://www.prothomalo.com"
    }
    
    api_url = "https://www.prothomalo.com/api/v1/collections/43749?offset=0&limit=50"
    
    with open('prothom_alo_latest.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['title', 'description', 'image_url'])
        
        try:
            print("Fetching latest articles list...")
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                print(f"Found {len(data['items'])} articles. Processing...")
                
                for i, item in enumerate(data['items']):
                    article_id = item.get('id')
                    if not article_id:
                        continue
                    
                    headline = " ".join(item['item'].get('headline', []))
                    article_api_url = f"https://www.prothomalo.com/api/v1/stories/{article_id}"
                    
                    try:
                        time.sleep(random.uniform(1, 2.5))
                        print(f"Fetching article {i+1}/{len(data['items'])}: {headline}")
                        article_response = requests.get(article_api_url, headers=headers)
                        article_response.raise_for_status()
                        article_data = article_response.json()
                        
                        full_article = ""
                        image_url = ""
                        
                        # Get main image first
                        if 'hero-image' in article_data:
                            hero_image = article_data['hero-image']
                            image_url = hero_image.get('hero-image-s3-url') or hero_image.get('hero-image-url', "")
                        
                        # Extract article body
                        if 'story-elements' in article_data:
                            story_elements = article_data['story-elements']
                            for element in story_elements:
                                if element['type'] == 'text' and 'content' in element:
                                    full_article += element['content'] + " "
                                elif element['type'] == 'image' and not image_url:
                                    image_url = element.get('image-s3-url') or element.get('src', "")
                        
                        full_article = full_article.strip()
                        
                        # Log if no content was found
                        if not full_article:
                            print(f"No content found for article: {headline}")
                            print("API Response:", json.dumps(article_data, ensure_ascii=False, indent=2))  # Print the full response
                        
                        # Write to CSV
                        writer.writerow([headline, full_article, image_url])
                        print(f"Saved article successfully")
                        
                    except Exception as e:
                        print(f"Error processing article {headline}: {e}")
            else:
                print("No articles found in the API response")
                
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nScraping completed. Data saved to 'prothom_alo_latest.csv'")

if __name__ == "__main__":
    scrape_prothom_alo_latest()
