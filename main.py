import json
import os
import subprocess
import dotenv
import asyncio
from utils.render import render
from utils.extract import Extract
from config.tools import get_config
from playwright.async_api import async_playwright

# Install Playwright browsers on startup
async def install_browsers():
    """Install required browsers for Playwright"""
    try:
        # Use a less privileged installation approach for Streamlit Cloud
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Browser installation failed with error: {str(e)}")
        print("Continuing with pre-installed browsers...")


async def render_and_extract(location:str,
                        headless_browser:bool=True,
                        running_from_file:bool=False,
                        callback=None):
    '''
    Function responsible for rendering and extracting property listings'data for
    given `location` and saves the json data to `outputs/output.json`.

    Args:
     - location: (str) The location you want to extract data for.
     - headless_browser: (bool) Set it to `True` if you want to see the rendering visually.
     - callback: (function) Callback function to report progress and property data.
    
    Returns:
     - list of property details in json format.
    '''
    dotenv.load_dotenv(".env")
    API_KEY = os.environ.get("GROQ_API_KEY")
    config = get_config()
    
    # For cloud deployments, always force headless mode
    if os.environ.get("STREAMLIT_CLOUD") or os.environ.get("IS_CLOUD_ENV"):
        headless_browser = True
        print("Cloud environment detected, forcing headless mode")
    
    try:
        # Try to install browsers, but don't fail if it doesn't work
        await install_browsers()
    except Exception as e:
        print(f"Browser installation skipped: {str(e)}")
        print("Will try to use pre-installed browsers...")
    
    if callback:
        callback("status", f"Starting to render pages for {location}...")
    
    html_pages = await render(location, config=config, headless=headless_browser, callback=callback)
    
    if callback:
        callback("status", f"Rendered {len(html_pages)} pages. Starting extraction...")
    
    extractor = Extract(html_pages, api_key=API_KEY, config=config, callback=callback)
    data = await extractor.execute()
    
    if data:
        if running_from_file:
            os.makedirs("outputs", exist_ok=True)
            with open("outputs/outputs.json", "w") as f:
                json.dump(data, f, indent=4)
            if callback:
                callback("status", f"Saved {len(data)} properties to outputs/outputs.json")
        return data
    
    if callback:
        callback("status", "No data was extracted. Check the logs for errors.")
    return []




if __name__ == "__main__":
    location = input("Enter the location you want to scrape property listings for: ")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(render_and_extract(location, running_from_file=True, headless_browser=False))
