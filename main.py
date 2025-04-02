import json
import os
import subprocess
import dotenv
import asyncio
from utils.render import render
from utils.extractor import extract_property_data
from config.tools import get_config
from playwright.async_api import async_playwright

# Function to check if running in cloud environment
def is_cloud_environment():
    return os.environ.get("STREAMLIT_CLOUD") is not None or \
           os.environ.get("IS_CLOUD_ENV") is not None or \
           "streamlit.app" in os.environ.get("HOSTNAME", "") or \
           os.path.exists("/.dockerenv")

# Install Playwright browsers on startup
async def install_browsers():
    """Install required browsers for Playwright"""
    # Skip installation in cloud environments
    if is_cloud_environment():
        print("Cloud environment detected - skipping browser installation")
        return
    
    try:
        # Use a less privileged installation approach
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Browser installation failed with error: {str(e)}")
        print("Continuing with pre-installed browsers...")

async def render_and_extract(location, headless_browser=True, running_from_file=False, callback=None):
    """Render webpage and extract data"""
    # Check for cloud environment
    if is_cloud_environment():
        if callback:
            callback("status", "Cloud environment detected - cannot perform live scraping. Using demo data.")
        print("Cloud environment detected - cannot perform live scraping")
        return load_demo_data()
    
    try:
        # Load environment variables
        dotenv.load_dotenv(".env")
        
        # Try to install browsers, but don't fail if it doesn't work
        await install_browsers()
    except Exception as e:
        print(f"Browser installation skipped: {str(e)}")
        print("Will try to use pre-installed browsers...")
    
    # Initialize empty properties list
    properties = []
    
    # Get API key from environment variables
    API_KEY = os.environ.get("GROQ_API_KEY")
    config = get_config()
    
    if callback:
        callback("status", f"Starting scrape for {location}")

    # Render the HTML pages
    html_pages = await render(location, config=config, headless=headless_browser, callback=callback)
    
    # Count the total properties found
    property_count = 0
    
    # Extract data from each HTML page
    for index, html in enumerate(html_pages):
        if callback:
            callback("status", f"Extracting data from page {index+1}/{len(html_pages)}")
            
        properties_from_page = await extract_property_data(
            html, 
            config=config, 
            api_key=API_KEY,
            page_number=index+1,
            callback=callback
        )
        
        property_count += len(properties_from_page)
        properties.extend(properties_from_page)
    
    # Store the properties in a file
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/outputs.json", "w") as f:
        json.dump(properties, f, indent=4)
    
    if callback:
        callback("status", f"Completed scraping {len(html_pages)} pages with {property_count} properties found!")
        callback("complete", property_count)
    
    return properties

def load_demo_data():
    """Load pre-scraped data for demo purposes"""
    try:
        with open("outputs/outputs.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading demo data: {e}")
        return []

def get_config():
    """Read configuration from config file"""
    with open("config/config.json", "r") as f:
        return json.load(f)

if __name__ == "__main__":
    location = input("Enter the location you want to scrape property listings for: ")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(render_and_extract(location, running_from_file=True, headless_browser=False))
