from playwright.async_api import async_playwright
import asyncio

async def render(location:str, config:dict, headless:bool=True):
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

    async with async_playwright() as p:
        all_html = [] # html from all pages

        browser = await p.firefox.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            java_script_enabled=True,
        )
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        page =  await context.new_page()

        try:
            
            await page.goto(URL, wait_until="domcontentloaded", timeout=TIMEOUT)
            print("Lets Go !!!")
            await page.locator(selector=SEARCH_BOX_SELECTOR).click()
            await asyncio.sleep(2)
            await page.locator(selector=SEARCH_BOX_SELECTOR).type(location, delay=300)
            await page.locator(selector=SEARCH_BOX_BUTTON_SELECTOR).click()  
            print(f"Searching for properties in {location}...")
            await asyncio.sleep(3)  # Wait a bit for the URL to update
            current_url = page.url

            if location.replace(" ", "-").lower() in current_url.lower():
                print(f"Location Verified!")
            else:
                print(f"Error: Location not found!")
                return []

            #implementing pagination to click on next and scrape the next page
            counter = 1
            while True:
                try:
                    await page.wait_for_selector(WAIT_SELECTOR, timeout=TIMEOUT) 
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(3)
                
                    all_html.append( await page.inner_html("body"))
                    next_button = page.locator(NEXT_BUTTON_SELECTOR)
                    if await next_button.count()==0 or not await next_button.is_visible():
                        print("No further Pages to scrape")
                        break

                    #Clicks next button
                    await next_button.click(timeout=TIMEOUT)
                    print(f"Moving To Page {counter}")
                    await page.wait_for_selector(WAIT_SELECTOR, timeout=TIMEOUT) 
                    counter += 1
                except Exception as e:
                    print(f"Problem Occured! Error in pagination {e}.")
                    return []
            return all_html
        except Exception as e:
            print(f"Problem occured{e}. check if your internet connection is working and try again.")
            return []
  