import requests
import time
import random
from utils.common_utils import text_processor

# Search the web for banking info
def live_web_search(query: str, num_results: int = 5) -> str:
    # Look for banking stuff on the internet
    print(f"WEB SEARCH: Looking for '{query}' on the web...")
    
    # Websites to search
    search_sources = [
        {"name": "DuckDuckGo", "url": "https://lite.duckduckgo.com/lite/", "method": "POST", "params": {"q": f"{query} Indian banking RBI", "kl": "in-en", "df": "d"}},
        {"name": "DuckDuckGo Alternative", "url": "https://html.duckduckgo.com/html/", "method": "POST", "params": {"q": f"{query} banking India RBI"}}
    ]
    
    all_results = []
    
    for source in search_sources:
        try:
            print(f"WEB SEARCH: Trying {source['name']}...")
            
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
            
            if source["method"] == "POST":
                response = requests.post(source["url"], data=source["params"], headers=headers, timeout=15)
            else:
                response = requests.get(source["url"], params=source["params"], headers=headers, timeout=15)
            
            print(f"WEB SEARCH: {source['name']} status: {response.status_code}")
            
            if response.status_code in [200, 202]:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                
                # HTML tags to look for
                selectors = ["a", "h3", "p", "div", "span", "div.result__body", "div.result__snippet"]
                
                found_elements = []
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        found_elements.extend(elements)
                        print(f"WEB SEARCH: Found {len(elements)} elements with '{selector}'")
                
                # Get text from each element
                for element in found_elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 15 and len(text) < 300:
                        # Banking words to look for
                        banking_keywords = ['bank', 'rbi', 'loan', 'account', 'kyc', 'emi', 'fd', 'rd', 'rate', 'interest', 'savings', 'current', 'credit', 'debit', 'repo', 'monetary', 'policy', 'finance', 'investment', 'deposit', 'withdrawal', 'transfer', 'upi', 'neft', 'rtgs']
                        
                        if any(keyword in text.lower() for keyword in banking_keywords):
                            clean_text = text_processor.clean_text(text)
                            if clean_text not in all_results:
                                all_results.append(clean_text)
                                print(f"WEB SEARCH: Added result: {clean_text[:50]}...")
                        
                        if len(all_results) >= num_results * 2:
                            break
                
                if len(all_results) >= num_results:
                    break
                    
        except Exception as e:
            print(f"WEB SEARCH: Error with {source['name']}: {e}")
            continue
    
    # Return results or fallback
    if all_results:
        return "\n\n".join(all_results[:num_results])
    else:
        return "Sorry, couldn't find any banking info right now. Try asking about specific banking topics like 'savings account' or 'RBI repo rate'."

# Get latest banking news
def search_banking_news(query: str = "Indian banking news RBI") -> str:
    # Get latest banking news
    print(f"NEWS SEARCH: Looking for banking news...")
    
    # Some recent banking news (fallback)
    fallback_news = """
    Latest Banking News:
    1. RBI keeps repo rate at 6.50% (unchanged since February 2023)
    2. New KYC guidelines for better security
    3. UPI transactions growing fast in India
    4. Digital banking becoming more popular
    5. New loan products from major banks
    
    For latest news, check:
    • RBI: https://www.rbi.org.in
    • MoneyControl: https://www.moneycontrol.com/news/business/banking-finance/
    """
    
    # Try to get real news
    news_sources = [
        {"name": "RBI", "url": "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"},
        {"name": "MoneyControl", "url": "https://www.moneycontrol.com/news/business/banking-finance/"}
    ]
    
    found_news = []
    
    for source in news_sources:
        try:
            print(f"NEWS SEARCH: Trying {source['name']}...")
            
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(source['url'], headers=headers, timeout=20)
            print(f"NEWS SEARCH: {source['name']} status: {response.status_code}")
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for news content
                for element in soup.find_all(["p", "h3", "div"]):
                    text = element.get_text(strip=True)
                    if text and len(text) > 30 and len(text) < 200:
                        if any(word in text.lower() for word in ['rbi', 'bank', 'loan', 'rate', 'announces', 'new']):
                            clean_text = text_processor.clean_text(text)
                            news_item = f"{source['name']}: {clean_text}"
                            if news_item not in found_news:
                                found_news.append(news_item)
                                print(f"NEWS SEARCH: Found news from {source['name']}: {clean_text[:60]}...")
                                
                                if len(found_news) >= 5:
                                    break
                                    
        except Exception as e:
            print(f"NEWS SEARCH: Error with {source['name']}: {e}")
            continue
    
    if found_news:
        return "\n\n".join(found_news)
    else:
        return fallback_news

# Get current RBI repo rate
def get_current_repo_rate() -> str:
    # Get current RBI repo rate
    print(f"REPO RATE SEARCH: Looking for current repo rate...")
    
    # Fallback info
    fallback_info = """
    Current RBI Repo Rate: 6.50% (as of latest MPC meeting)
    
    This rate has been unchanged since February 2023.
    For the most current rate, check RBI's official website.
    """
    
    # Try to get real-time info
    rbi_sources = [
        {"name": "RBI Press Releases", "url": "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"},
        {"name": "RBI Homepage", "url": "https://www.rbi.org.in/"}
    ]
    
    for source in rbi_sources:
        try:
            print(f"REPO RATE SEARCH: Trying {source['name']}...")
            
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(source['url'], headers=headers, timeout=15)
            print(f"REPO RATE SEARCH: {source['name']} status: {response.status_code}")
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for repo rate info
                for element in soup.find_all(["p", "h3", "div"]):
                    text = element.get_text(strip=True)
                    if text and 'repo rate' in text.lower():
                        if any(word in text.lower() for word in ['6.50', '6.5', '6.25', '6.75']):
                            print(f"REPO RATE SEARCH: Found rate info: {text[:100]}...")
                            return f"Current RBI Repo Rate: {text}"
                            
        except Exception as e:
            print(f"REPO RATE SEARCH: Error with {source['name']}: {e}")
            continue
    
    # Try web search as backup
    try:
        print(f"REPO RATE SEARCH: Trying web search...")
        web_results = live_web_search("current RBI repo rate 2024", 3)
        if web_results and "error" not in web_results.lower():
            return f"Current RBI Repo Rate (from web search):\n{web_results}"
    except:
        pass
    
    return fallback_info

# Search for banking regulations
def search_banking_regulations(query: str) -> str:
    # Search for banking rules and regulations
    print(f"REGULATION SEARCH: Looking for banking regulations...")
    
    # Try web search first
    try:
        web_results = live_web_search(f"{query} banking regulations RBI rules", 3)
        if web_results and "error" not in web_results.lower():
            return f"Banking Regulations (from web search):\n{web_results}"
    except:
        pass
    
    # Fallback info
    return """
    Common Banking Regulations in India:
    
    1. KYC (Know Your Customer) - Required for all accounts
    2. RBI Guidelines - Banks must follow RBI rules
    3. Digital Lending Rules - New guidelines for online loans
    4. Payment Security - UPI and digital payment rules
    5. Customer Protection - Banks must protect customer data
    
    For detailed regulations, visit RBI's official website.
    """ 