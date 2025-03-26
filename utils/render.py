from playwright.sync_api import sync_playwright
import time

def render(location:str, config:dict, headless:bool=True):
    '''
    Function responsible for loading and rendering all the property listings for 
    given `location`.

    Args:
     - location: (str) The place you want to render listings for.
     - config: (dict) A dict containing all the configurations for rendering.
     - headless: (bool) Set it to false if you want to see the browser rendering.
    
    Returns:
     HTML body of all the pages rendered.
    '''
    URL = config.get("url")
    TIMEOUT = config.get("timeout")
    #imp selectors
    WAIT_SELECTOR = config.get("waitSelector")
    NEXT_BUTTON_SELECTOR = config.get("items").get("nextButton").get("selector")
    SEARCH_BOX_SELECTOR = config.get("items").get("searchBox").get("selector")
    SEARCH_BOX_BUTTON_SELECTOR = config.get("items").get("searchButton").get("selector")
    SEARCH_HEADING_SELECTOR = config.get("items").get("searchHeading").get("selector")

    with sync_playwright() as p:
        all_html = [] # html from all pages

        browser = p.firefox.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            java_script_enabled=True,
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        page =  context.new_page()

        try:
            
            response = page.goto(URL, wait_until="domcontentloaded", timeout=TIMEOUT)
            print("Lets Go !!!")
            page.locator(selector=SEARCH_BOX_SELECTOR).click()
            time.sleep(2)
            page.locator(selector=SEARCH_BOX_SELECTOR).type(location, delay=300)
            page.locator(selector=SEARCH_BOX_BUTTON_SELECTOR).click()  
            print(f"Searching for properties in {location}...")
            if location in page.inner_html(SEARCH_HEADING_SELECTOR):
                print("Location Verified")
            else:
                print (f"Could not fetch data for {location}. Check spelling, zip code or try again.")
                return []
            #implementing pagination to click on next and scrape the next page
            counter = 1
            while True:
                try:
                    page.wait_for_selector(WAIT_SELECTOR, timeout=TIMEOUT) 
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(3)
                
                    all_html.append( page.inner_html("body"))
                    next_button = page.locator(NEXT_BUTTON_SELECTOR)
                    if next_button.count()==0 or not next_button.is_visible():
                        print("No further Pages to scrape")
                        break

                    #Clicks next button
                    next_button.click()
                    print(f"Moving To Page {counter}")
                    page.wait_for_selector(WAIT_SELECTOR, timeout=TIMEOUT) 
                    counter += 1
                except Exception as e:
                    print(f"Problem Occured! Error in pagination {e}.")
                    return []
            return all_html
        except Exception as e:
            print("Problem occured. check if your internet connection is working and try again.")
            return []
        
        