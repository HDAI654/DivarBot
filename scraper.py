from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from logger import logger
import asyncio
import httpx

async def GetHTML(address):
    try:
        # Try to fetch the page
        async with httpx.AsyncClient() as client:
            response = await client.get(address, timeout=10)
            response.raise_for_status()
            html_content = response.text
        
        isCSR = await is_CSR(address)
        
        if isCSR != False:
            html_content = isCSR
        
        return html_content
    
    except Exception as e:
        logger.error(f"Error fetching or rendering page: {e}")
        return False

async def is_CSR(address):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # without JS
            context_nojs = await browser.new_context(java_script_enabled=False)
            page_nojs = await context_nojs.new_page()
            await page_nojs.goto(address, timeout=30000)
            dom_before = await page_nojs.content()
            await context_nojs.close()
            
            # with JS
            context_js = await browser.new_context(java_script_enabled=True)
            page_js = await context_js.new_page()
            await page_js.goto(address, timeout=30000)
            await asyncio.sleep(3)
            dom_after = await page_js.content()
            await context_js.close()
            
            await browser.close()

            diff_ratio = abs(len(dom_after) - len(dom_before)) / max(len(dom_before), 1)
            #logger.info(f"DOM difference ratio: {diff_ratio:.2f}")

            if diff_ratio > 0.3:
                return dom_after
            else:
                return False

    except Exception as e:
        logger.error(f"Error checking CSR: {e}")
        return False


async def scrape_data(page_address, ad_address, threshold):
    try:
        # Fetch the HTML content
        html_content = await GetHTML(page_address)
        if not html_content:
            return "NOHTML"
        
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # get the links of the first 5 ads on the page
        soup_ads = soup.find_all("a", class_="unsafe-kt-post-card__action", href=True)[:threshold]
        if not soup_ads:
            logger.warning("No ads found on page")
            return False
        
        # Extract ad IDs from the links
        ad_ids = [link['href'].rstrip('/').split("/")[-1] for link in soup_ads if "/v/" in link['href']]


        # Extract ID of the received ad
        my_ad_id = ad_address.rstrip('/').split("/")[-1]
        
        if my_ad_id not in ad_ids:
            return "NOTIN_THRESHOLD"

        # Check if the received ad ID is in the list of ad IDs
        return ad_ids.index(my_ad_id)

    except Exception as e:
        logger.error(f"Error scraping data: {e}")
        return False
  
