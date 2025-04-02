import asyncio
import os
import json
import time
import sys
import traceback
from main import render_and_extract

# Get command line arguments
if len(sys.argv) < 3:
    print("Error: Missing arguments")
    sys.exit(1)

location = sys.argv[1]
headless_str = sys.argv[2]
headless = (headless_str.lower() == 'true')

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

# Status file paths
STATUS_FILE = "status/current_status.txt"
PROPERTIES_FILE = "status/properties.json"
LOG_FILE = "status/log.txt"
ACTIVE_FILE = "status/active.txt"
PAGE_INFO_FILE = "status/page_info.json"

# Make sure to mark as inactive when exiting
def ensure_inactive():
    if os.path.exists(ACTIVE_FILE):
        try:
            os.remove(ACTIVE_FILE)
            print("Marked as inactive on exit")
        except:
            pass

# Function to load pre-scraped demo data
def load_demo_data():
    try:
        with open("outputs/outputs.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading demo data: {e}")
        return []

# Status callback
def status_callback(update_type, data):
    if update_type == "status":
        with open(STATUS_FILE, "w") as f:
            f.write(data)
        # Also append to log with timestamp
        with open(LOG_FILE, "a") as f:
            timestamp = time.strftime('%H:%M:%S')
            f.write(f"[{timestamp}] {data}\n")
            
        # Track page progress
        if "Moving to page" in data:
            parts = data.split()
            try:
                page_num = int(parts[-1])
                # Update page info
                page_info = {"current_page": page_num, "total_pages": None}
                with open(PAGE_INFO_FILE, "w") as f:
                    json.dump(page_info, f)
            except (ValueError, IndexError):
                pass
        elif "No further pages to scrape" in data:
            # We've reached the last page
            try:
                with open(PAGE_INFO_FILE, "r") as f:
                    page_info = json.load(f)
                page_info["total_pages"] = page_info["current_page"]
                with open(PAGE_INFO_FILE, "w") as f:
                    json.dump(page_info, f)
            except:
                pass
            
    elif update_type == "property":
        # Read current properties, add new one, write back
        properties = []
        if os.path.exists(PROPERTIES_FILE):
            try:
                with open(PROPERTIES_FILE, "r") as f:
                    properties = json.load(f)
            except:
                properties = []
        properties.append(data)
        with open(PROPERTIES_FILE, "w") as f:
            json.dump(properties, f, indent=4)
        # Also log the property
        with open(LOG_FILE, "a") as f:
            timestamp = time.strftime('%H:%M:%S')
            f.write(f"[{timestamp}] Found property: {data.get('address', 'Unknown')} - {data.get('price', 'N/A')}\n")
    elif update_type == "complete":
        with open(STATUS_FILE, "w") as f:
            f.write(f"Completed! Found {data} properties.")
        ensure_inactive()

async def main():
    try:
        # Check if running in cloud environment
        if is_cloud_environment():
            print("Cloud environment detected - using demo data instead of scraping")
            with open(STATUS_FILE, "w") as f:
                f.write(f"Using pre-scraped demo data instead of live scraping")
                
            # Load demo data
            demo_properties = load_demo_data()
            for prop in demo_properties:
                status_callback("property", prop)
                await asyncio.sleep(0.1)  # Small delay between properties
                
            status_callback("complete", len(demo_properties))
            return
            
        print(f"Starting scraping process for {location} with headless={headless}")
        await render_and_extract(
            location=location,
            headless_browser=headless,
            running_from_file=True,
            callback=status_callback
        )
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        with open(STATUS_FILE, "w") as f:
            f.write(f"Error: {error_msg}")
        with open(LOG_FILE, "a") as f:
            timestamp = time.strftime('%H:%M:%S')
            f.write(f"[{timestamp}] Error: {error_msg}\n")
        traceback.print_exc()
    finally:
        ensure_inactive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        with open(STATUS_FILE, "w") as f:
            f.write(f"Scraping failed with error: {str(e)}")
        traceback.print_exc()
    finally:
        # Always make sure we mark scraping as inactive
        ensure_inactive()
