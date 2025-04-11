import requests
from bs4 import BeautifulSoup
import time
import csv
from pathlib import Path
import os

# Base configuration for Bazaar site
class BazaarConfig:
    """Configuration settings for Bazaar e-commerce site"""
    # Base URL for data source (can be changed to your preferred source)
    SOURCE_URL = 'https://en-ae.sssports.com'
    
    # Categories to include in the Bazaar store
    CATEGORIES = [
        {"enter link"},
        {"enter link"},
        {"enter link"}
    ]
    
    # Output directory for product data
    OUTPUT_DIR = Path(__file__).parent.parent / "data"
    
    # Price calculation parameters
    SHIPPING_COST = 4000  # Base shipping cost
    EXCHANGE_RATE = 78    # Currency exchange rate
    PROFIT_MARGIN = 25    # Profit margin percentage

# Ensure data directory exists
os.makedirs(BazaarConfig.OUTPUT_DIR, exist_ok=True)

def fetch_page(session, url, retries=3):
    """Fetch the HTML content of a URL with retries."""
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print(f"Retrying {url}... ({attempt + 1}/{retries})")
                time.sleep(2)
            else:
                print(f"Error fetching {url}: {e}")
                return None

def fetch_product_links(session, category_url, category_name):
    """Fetch all product links from a category page."""
    print(f"Fetching {category_name} product links from {category_url}...")
    product_links = []
    current_url = category_url
    
    while current_url:
        content = fetch_page(session, current_url)
        if not content:
            break
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract product links from the current page
        productlist = soup.find_all('div', class_='product-grid__item')
        for item in productlist:
            for link in item.find_all('a', href=True, class_='link'):
                full_link = BazaarConfig.SOURCE_URL + link['href'] if not link['href'].startswith('http') else link['href']
                product_links.append({"url": full_link, "category": category_name})
        
        # Check for pagination to fetch the next page
        load_more_button = soup.find('button', class_='js-show-more-btn')
        if load_more_button and 'data-url' in load_more_button.attrs:
            next_url = load_more_button['data-url']
            current_url = BazaarConfig.SOURCE_URL + next_url if not next_url.startswith('http') else next_url
        else:
            break
            
    print(f"Found {len(product_links)} {category_name} products")
    return product_links

def calculate_price(original_price, shipping=BazaarConfig.SHIPPING_COST, 
                   exchange_rate=BazaarConfig.EXCHANGE_RATE, 
                   margin=BazaarConfig.PROFIT_MARGIN):
    """Calculate the final selling price including shipping, exchange rate, and profit margin."""
    base_price = original_price * exchange_rate + shipping
    final_price = ((base_price / 100) * margin) + base_price
    return round(final_price, -3)  # Round to nearest thousand

def extract_product_details(session, product_info):
    """Extract detailed information about a product."""
    url = product_info["url"]
    category = product_info["category"]
    
    content = fetch_page(session, url)
    if not content:
        return None
        
    soup = BeautifulSoup(content, 'html.parser')
    
    try:
        # Extract basic product info
        title = soup.select_one('h1.product-info__title').text.strip() if soup.select_one('h1.product-info__title') else "Unknown Product"
        brand = soup.select_one('div.product-info__brand').text.strip() if soup.select_one('div.product-info__brand') else "Unknown Brand"
        
        # Extract price
        price_elem = soup.select_one('span.product-info__price-new')
        if price_elem:
            price_text = price_elem.text.strip()
            # Extract numeric value from price text (e.g., "AED 499.00" -> 499.00)
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_text)
            original_price = float(price_match.group().replace(',', '')) if price_match else 0
        else:
            original_price = 0
            
        # Calculate price for Bazaar store
        bazaar_price = calculate_price(original_price)
        
        # Extract product images
        images = []
        image_containers = soup.select('div.product-gallery__slide img')
        for img in image_containers:
            if 'src' in img.attrs:
                image_url = img['src']
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                images.append(image_url)
        
        # Extract product description
        description = ""
        desc_container = soup.select_one('div.product-info__description')
        if desc_container:
            description = desc_container.text.strip()
            
        # Extract available sizes
        sizes = []
        size_containers = soup.select('div.size-picker__options label')
        for size_elem in size_containers:
            size_text = size_elem.text.strip()
            if size_text:
                sizes.append(size_text)
                
        # Create product data structure
        product_data = {
            "id": url.split('/')[-1] if '/' in url else url,
            "url": url,
            "title": title,
            "brand": brand,
            "category": category,
            "original_price": original_price,
            "bazaar_price": bazaar_price,
            "description": description,
            "images": images,
            "sizes": sizes
        }
        
        return product_data
        
    except Exception as e:
        print(f"Error extracting details from {url}: {e}")
        return None

def main():
    """Main function to scrape product data for Bazaar e-commerce site."""
    start_time = time.perf_counter()
    
    # Create a session for making HTTP requests
    with requests.Session() as session:
        all_product_links = []
        
        # Fetch product links from all categories
        for category in BazaarConfig.CATEGORIES:
            category_links = fetch_product_links(session, category["url"], category["category"])
            all_product_links.extend(category_links)
            
        print(f"Total products found across all categories: {len(all_product_links)}")
        
        # Save all product links to a file
        links_file = BazaarConfig.OUTPUT_DIR / "product_links.txt"
        with open(links_file, 'w') as f:
            for product_info in all_product_links:
                f.write(f"{product_info['url']},{product_info['category']}\n")
        
        print(f"Product links saved to {links_file}")
        
        # Extract detailed information for each product (limit to 50 products for MVP)
        print("Extracting detailed product information...")
        product_details = []
        
        for product_info in all_product_links[:50]:  # Limit to 50 products
            details = extract_product_details(session, product_info)
            if details:
                product_details.append(details)
                
        print(f"Extracted details for {len(product_details)} products")
        
        # Save product details to CSV
        csv_file = BazaarConfig.OUTPUT_DIR / "bazaar_products.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["id", "title", "brand", "category", "original_price", 
                         "bazaar_price", "description", "images", "sizes", "url"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in product_details:
                # Convert lists to string for CSV storage
                product_row = product.copy()
                product_row["images"] = "|".join(product["images"])
                product_row["sizes"] = "|".join(product["sizes"])
                writer.writerow(product_row)
                
        print(f"Product data saved to {csv_file}")
    
    # Calculate and display execution time
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Scraping completed in {elapsed_time:.1f} seconds")

if __name__ == "__main__":
    main()
