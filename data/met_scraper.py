#!/usr/bin/env python3
"""
Banking Data Scraper for the Banking Assistant

This script scrapes banking-related information from various sources
to keep the knowledge base updated with current information.
"""

import requests
import json
import time
import os
import sys
from bs4 import BeautifulSoup

# Add parent directory to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common_utils import data_processor, text_processor

# Simple logging
def log_info(msg):
    print(f"INFO: {msg}")

def log_error(msg):
    print(f"ERROR: {msg}")

class BankingDataScraper:
    # Scraper to get banking info from websites
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
    # Get RBI notifications
    def scrape_rbi_notifications(self):
        # Get RBI notifications from their website
        try:

            # RBI notifications page URL
            url = "https://www.rbi.org.in/Scripts/NotificationUser.aspx"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            notifications = []
            
            # Find notification links
            links = soup.find_all('a', href=True)

            #Only 10 is considered
            for link in links[:10]:  
                title = link.get_text(strip=True)
                if title and len(title) > 10:
                    notifications.append({
                        "title": f"RBI Notification: {title}",
                        "content": f"RBI has issued a notification regarding {title}. Please check the official RBI website for complete details.",
                        "source": "RBI Official Website",
                        "url": f"https://www.rbi.org.in{link['href']}" if link['href'].startswith('/') else link['href']
                    })
            
            log_info(f"Scraped {len(notifications)} RBI notifications")
            return notifications
            
        except Exception as e:
            log_error(f"Error scraping RBI notifications: {e}")
            return []
    
    # Get banking news
    def scrape_banking_news(self):
        # Get banking news from MoneyControl
        try:

            # MoneyControl banking news URL
            url = "https://www.moneycontrol.com/news/business/banking-finance/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            
            # Find news articles
            articles = soup.find_all('h2', class_='artTitle')

            #Only 5 is considered
            for article in articles[:5]:  
                title = article.get_text(strip=True)
                if title and len(title) > 10:
                    news_items.append({
                        "title": f"Banking News: {title}",
                        "content": f"Recent banking news: {title}. This information is from MoneyControl and may be updated regularly.",
                        "source": "MoneyControl",
                        "url": "https://www.moneycontrol.com/news/business/banking-finance/"
                    })
            
            log_info(f"Scraped {len(news_items)} banking news items")
            return news_items
            
        except Exception as e:
            log_error(f"Error scraping banking news: {e}")
            return []
    
    # Get loan rates
    def scrape_loan_rates(self):
        # Get current loan rates
        try:

            # BankBazaar loan rates URL
            url = "https://www.bankbazaar.com/personal-loan.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            rate_info = []
            
            # Extract rate information
            rate_elements = soup.find_all('div', class_='rate-info')

            #Only 3 is considered
            for element in rate_elements[:3]:
                text = element.get_text(strip=True)
                if text and '%' in text:
                    rate_info.append({
                        "title": "Current Loan Rates",
                        "content": f"Current loan rates: {text}. Rates may vary based on individual eligibility and bank policies.",
                        "source": "BankBazaar",
                        "url": "https://www.bankbazaar.com/personal-loan.html"
                    })
            
            log_info(f"Scraped {len(rate_info)} loan rate items")
            return rate_info
            
        except Exception as e:
            log_error(f"Error scraping loan rates: {e}")
            return []
    
    # Get FD rates
    def scrape_fd_rates(self):
        # Get current Fixed Deposit rates
        try:
            
            # BankBazaar FD rates URL
            url = "https://www.bankbazaar.com/fixed-deposit.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            fd_info = []
            
            # Extract FD rate information   
            rate_elements = soup.find_all('div', class_='rate-info')

            #Only 3 is considered
            for element in rate_elements[:3]:
                text = element.get_text(strip=True)
                if text and '%' in text:
                    fd_info.append({
                        "title": "Current FD Rates",
                        "content": f"Current Fixed Deposit rates: {text}. Rates may vary based on deposit amount and tenure.",
                        "source": "BankBazaar",
                        "url": "https://www.bankbazaar.com/fixed-deposit.html"
                    })
            
            log_info(f"Scraped {len(fd_info)} FD rate items")
            return fd_info
            
        except Exception as e:
            log_error(f"Error scraping FD rates: {e}")
            return []
    
    # Get all data
    def scrape_all_data(self):
        # Get all banking data from different sources
        log_info("Starting comprehensive banking data scraping...")
        
        all_data = []
        
        # Scrape from different sources
        all_data.extend(self.scrape_rbi_notifications())
        time.sleep(2)
        
        all_data.extend(self.scrape_banking_news())
        time.sleep(2)
        
        all_data.extend(self.scrape_loan_rates())
        time.sleep(2)
        
        all_data.extend(self.scrape_fd_rates())
        
        log_info(f"Total scraped items: {len(all_data)}")
        return all_data
    
    # Save data to file
    def save_to_jsonl(self, data, filename="scraped_banking_data.jsonl"):
        # Save scraped data to a file
        try:
            # Use the reusable data processor for consistent JSONL saving across the project
            filepath = os.path.join("data", filename)
            data_processor.save_jsonl(data, filepath)
            
            log_info(f"Saved {len(data)} items to {filepath}")
            
        except Exception as e:
            log_error(f"Error saving data: {e}")
    
    # Merge with existing data
    def merge_with_existing_data(self, new_data, existing_file="banking_documents.jsonl"):
        # Add new data to existing data
        try:
            existing_filepath = os.path.join("data", existing_file)
            existing_data = []
            
            # Load existing data using reusable data processor
            if os.path.exists(existing_filepath):
                existing_data = data_processor.load_jsonl(existing_filepath)
            
            # Merge data (avoid duplicates)
            existing_titles = {item.get('title', '') for item in existing_data}
            unique_new_data = [item for item in new_data if item.get('title', '') not in existing_titles]
            
            # Combine data
            combined_data = existing_data + unique_new_data
            
            # Save back to file using reusable data processor
            data_processor.save_jsonl(combined_data, existing_filepath)
            
            log_info(f"Merged {len(unique_new_data)} new items with existing data. Total: {len(combined_data)}")
            
        except Exception as e:
            log_error(f"Error merging data: {e}")

def main():
    # Main function to run the scraper
    print("Starting Banking Data Scraper...")
    
    scraper = BankingDataScraper()
    
    # Scrape all data (can be commented as this is memory intensive)
    scraped_data = scraper.scrape_all_data()
    
    if scraped_data:

        # Saving to a separate file
        scraper.save_to_jsonl(scraped_data)
        
        # Merging with existing data
        scraper.merge_with_existing_data(scraped_data)
        
        print(f"SUCCESS: Successfully scraped {len(scraped_data)} banking data items")
        print("Data saved to data/scraped_banking_data.jsonl")
        print("Existing data updated in data/banking_documents.jsonl")
    else:
        print("FAIL: No data was scraped. Check your internet connection and try again.")

if __name__ == "__main__":
    main() 