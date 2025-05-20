import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
from logger import logger

def GetHTML(address):
    try:
        # Try to fetch the page using requests
        response = requests.get(address, timeout=10)
        response.raise_for_status()
        html_content = response.text
        
        # Check if the page is possibly rendered using CSR
        if is_CSR(address):
            # Use Playwright to fetch rendered HTML
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(address, timeout=30000)
                time.sleep(3)  # Wait for JavaScript to render content
                html_content = page.content()
                browser.close()
        
        return html_content
    
    except Exception as e:
        logger.error(f"Error fetching or rendering page: {e}")
        return False

def is_CSR(address):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            # without JS
            context_nojs = browser.new_context(java_script_enabled=False)
            page_nojs = context_nojs.new_page()
            page_nojs.goto(address, timeout=30000)
            time.sleep(2)
            dom_before = page_nojs.content()
            context_nojs.close()
            
            # with JS
            context_js = browser.new_context(java_script_enabled=True)
            page_js = context_js.new_page()
            page_js.goto(address, timeout=30000)
            time.sleep(5)
            dom_after = page_js.content()
            context_js.close()
            
            browser.close()

            diff_ratio = abs(len(dom_after) - len(dom_before)) / max(len(dom_before), 1)
            #logger.info(f"DOM difference ratio: {diff_ratio:.2f}")

            if diff_ratio > 0.3:
                return True
            else:
                return False

    except Exception as e:
        logger.error(f"Error checking CSR: {e}")
        return False


def scrape_data(page_address, ad_address):
    try:
        # Fetch the HTML content
        html_content = GetHTML(page_address)
        if not html_content:
            return False
        
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # get the links of the first 5 ads on the page
        soup_ads = soup.find_all("a", class_="unsafe-kt-post-card__action", href=True)[:5]
        if not soup_ads:
            logger.warning("No ads found on page")
            return False
        
        # Extract ad IDs from the links
        ad_ids = [link['href'].rstrip('/').split("/")[-1] for link in soup_ads if "/v/" in link['href']]
        print(ad_ids)


        # Extract ID of the received ad
        my_ad_id = ad_address.rstrip('/').split("/")[-1]
        print("--")
        print(my_ad_id)

        # Check if the received ad ID is in the list of ad IDs
        return my_ad_id in ad_ids

    except Exception as e:
        logger.error(f"Error scraping data: {e}")
        return None
  
  
print(scrape_data("https://divar.ir/s/arak", "/v/موتور-هندا-۲۰۰-انژکتور-دیسکی-دزدگیر-دار/AasgGQra"))