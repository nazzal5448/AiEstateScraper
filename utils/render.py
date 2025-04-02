from playwright.async_api import async_playwright
import asyncio
import os
import sys

# Function to check if running in cloud environment
def is_cloud_environment():
    # Check for common cloud environment indicators
    if (os.environ.get("STREAMLIT_CLOUD") is not None or 
            os.environ.get("IS_CLOUD_ENV") is not None or 
            "streamlit.app" in os.environ.get("HOSTNAME", "") or 
            os.path.exists("/.dockerenv")):
        return True
    
    # Check for Streamlit Cloud specific paths
    if (os.path.exists("/mount/src") or 
            "/home/adminuser/venv" in sys.path or 
            os.path.exists("/home/adminuser/venv")):
        return True
        
    # Check if we're running in a path that looks like Streamlit Cloud
    current_path = os.getcwd()
    if "/mount/src" in current_path:
        return True
        
    return False

async def render(location:str, config:dict, headless:bool=True, callback=None):
    '''
    Function responsible for loading and rendering all the property listings for 
    given `location`.

    Args:
     - location: (str) The place you want to render listings for.
     - config: (dict) A dict containing all the configurations for rendering.
     - headless: (bool) Set it to false if you want to see the browser rendering.
     - callback: (function) Optional callback for status updates.
    
    Returns:
     HTML body of all the pages rendered.
    '''
    # Check for cloud environment first - prevent browser launch in cloud
    if is_cloud_environment():
        error_msg = "Cloud environment detected - cannot launch browser"
        print(error_msg)
        if callback:
            callback("status", error_msg)
        return []
        
    URL = config.get("url")
    TIMEOUT = config.get("timeout")
    #imp selectors
    WAIT_SELECTOR = config.get("waitSelector")
    NEXT_BUTTON_SELECTOR = config.get("items").get("nextButton").get("selector")
    SEARCH_BOX_SELECTOR = config.get("items").get("searchBox").get("selector")
    SEARCH_BOX_BUTTON_SELECTOR = config.get("items").get("searchButton").get("selector")

    if callback:
        callback("status", f"Starting browser...")
    
    # Additional check right before browser launch
    if is_cloud_environment():
        error_msg = "Cloud environment detected - cannot launch browser"
        print(error_msg)
        if callback:
            callback("status", error_msg)
        return []

    async with async_playwright() as p:
        all_html = [] # html from all pages

        if callback:
            callback("status", f"Launching browser with headless={headless}...")
            
        # Final check before actual browser launch
        if is_cloud_environment():
            error_msg = "Cloud environment detected - cannot launch browser"
            print(error_msg)
            if callback:
                callback("status", error_msg)
            return []

        try:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                java_script_enabled=True,
            )
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """)
            page = await context.new_page()

            try:
                status_msg = f"Navigating to {URL}..."
                print(status_msg)
                if callback:
                    callback("status", status_msg)
                    
                await page.goto(URL, wait_until="domcontentloaded", timeout=TIMEOUT)
                
                status_msg = "Initialized site navigation"
                print(status_msg)
                if callback:
                    callback("status", status_msg)
                    
                await page.locator(selector=SEARCH_BOX_SELECTOR).click()
                await asyncio.sleep(2)
                
                status_msg = f"Entering location: {location}"
                print(status_msg)
                if callback:
                    callback("status", status_msg)
                    
                await page.locator(selector=SEARCH_BOX_SELECTOR).type(location, delay=300)
                
                status_msg = f"Searching for properties in {location}..."
                print(status_msg)
                if callback:
                    callback("status", status_msg)
                    
                await page.locator(selector=SEARCH_BOX_BUTTON_SELECTOR).click()  
                await asyncio.sleep(3)  # Wait a bit for the URL to update
                current_url = page.url

                if location.replace(" ", "-").lower()[:6] in current_url.lower():
                    status_msg = f"Location verified! URL: {current_url}"
                    print(status_msg)
                    if callback:
                        callback("status", status_msg)
                else:
                    status_msg = f"Error: Location not found in URL: {current_url}"
                    print(status_msg)
                    if callback:
                        callback("status", status_msg)
                    return []

                #implementing pagination to click on next and scrape the next page
                counter = 1
                while True:
                    try:
                        status_msg = f"Processing page {counter}..."
                        print(status_msg)
                        if callback:
                            callback("status", status_msg)
                            
                        await page.wait_for_selector(WAIT_SELECTOR, timeout=TIMEOUT) 
                        
                        status_msg = f"Scrolling page {counter} to load all content..."
                        print(status_msg)
                        if callback:
                            callback("status", status_msg)
                            
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(3)
                    
                        status_msg = f"Capturing HTML from page {counter}"
                        print(status_msg)
                        if callback:
                            callback("status", status_msg)
                            
                        all_html.append(await page.inner_html("body"))
                        
                        next_button = page.locator(NEXT_BUTTON_SELECTOR)
                        if await next_button.count()==0 or not await next_button.is_visible():
                            status_msg = f"No further pages to scrape. Total pages: {counter}"
                            print(status_msg)
                            if callback:
                                callback("status", status_msg)
                            break

                        #Clicks next button
                        status_msg = f"Moving to page {counter+1}..."
                        print(status_msg)
                        if callback:
                            callback("status", status_msg)
                            
                        await next_button.click(timeout=TIMEOUT)
                        await page.wait_for_selector(WAIT_SELECTOR, timeout=TIMEOUT) 
                        counter += 1
                    except Exception as e:
                        error_msg = f"Problem occurred! Error in pagination: {e}."
                        print(error_msg)
                        if callback:
                            callback("status", error_msg)
                        return all_html if all_html else []
                        
                status_msg = f"Successfully scraped {len(all_html)} pages"
                print(status_msg)
                if callback:
                    callback("status", status_msg)
                    
                return all_html
            except Exception as e:
                error_msg = f"Problem occurred: {e}. Check if your internet connection is working and try again."
                print(error_msg)
                if callback:
                    callback("status", error_msg)
                return []
        except Exception as e:
            error_msg = f"Problem occurred: {e}. Check if your internet connection is working and try again."
            print(error_msg)
            if callback:
                callback("status", error_msg)
            return []
  