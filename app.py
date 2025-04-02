import streamlit as st
import os
import json
import time
import asyncio
from main import render_and_extract
import platform
import glob

# Ensure directories exist
os.makedirs("outputs", exist_ok=True)
os.makedirs("status", exist_ok=True)

# Enable debug mode
DEBUG_MODE = False  # Set to True to see debug information

# File paths for status communication
STATUS_FILE = "status/current_status.txt"
PROPERTIES_FILE = "status/properties.json"
LOG_FILE = "status/log.txt"
ACTIVE_FILE = "status/active.txt"
PAGE_INFO_FILE = "status/page_info.json"  # New file to track page progress

# Clean up any stale status files on startup
def cleanup_stale_files():
    # Check if active file exists but is stale (older than 30 minutes)
    if os.path.exists(ACTIVE_FILE):
        try:
            with open(ACTIVE_FILE, "r") as f:
                start_time = float(f.read().strip())
                if time.time() - start_time > 30 * 60:  # 30 minutes
                    # This is a stale file, remove it
                    os.remove(ACTIVE_FILE)
                    if os.path.exists(STATUS_FILE):
                        with open(STATUS_FILE, "w") as f:
                            f.write("Ready")
        except:
            # If there's any issue reading the file, just remove it
            os.remove(ACTIVE_FILE)

# Run cleanup on startup
cleanup_stale_files()

# Set up page
st.set_page_config(
    page_title="AI Estate Scraper",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    .property-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #ffffff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .property-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    }
    .property-address {
        font-weight: 600;
        font-size: 1.3em;
        color: #2c3e50;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .property-price {
        font-size: 1.6em;
        color: #27ae60;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .property-details {
        margin: 15px 0;
        font-size: 1.1em;
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
    }
    .property-detail-item {
        display: inline-block;
        background-color: #f0f7ff;
        padding: 6px 12px;
        border-radius: 20px;
        color: #2c3e50;
    }
    .property-other {
        padding-top: 10px;
        border-top: 1px solid #f0f0f0;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 8px;
        margin-top: 5px;
    }
    .property-attribute {
        margin-bottom: 5px;
        color: #333;
    }
    .property-icon {
        font-size: 2.5em;
        color: #e67e22;
        text-align: center;
        margin-bottom: 12px;
        background-color: #fff9f2;
        width: 70px;
        height: 70px;
        line-height: 70px;
        border-radius: 50%;
        margin: 0 auto 15px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        text-shadow: 0 0 1px #000;
    }
    .log-container {
        max-height: 250px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        background-color: #ffffff;
        font-family: 'Courier New', monospace;
        font-size: 0.95em;
        line-height: 1.6;
        color: #333333;
    }
    .log-entry {
        margin-bottom: 8px;
        padding: 6px 8px;
        border-bottom: 1px solid #e9e9e9;
        background-color: #fcfcfc;
        border-radius: 4px;
    }
    .log-entry:hover {
        background-color: #f5f5f5;
    }
    .timestamp {
        color: #2980b9;
        font-weight: bold;
        margin-right: 6px;
    }
    .progress-label {
        font-size: 0.9em;
        color: #444;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .section-header {
        margin-top: 25px;
        margin-bottom: 15px;
        font-weight: 600;
        color: #2c3e50;
        font-size: 1.4em;
        padding-bottom: 5px;
        border-bottom: 2px solid #f0f0f0;
    }
    .status-display {
        font-weight: 500;
        padding: 10px;
        border-radius: 6px;
        background-color: #e8f4fd;
        color: #2c3e50;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for file operations
def write_status(message):
    """Write a status message to the status file"""
    with open(STATUS_FILE, "w") as f:
        f.write(message)
    
    # Also append to log with timestamp
    with open(LOG_FILE, "a") as f:
        timestamp = time.strftime('%H:%M:%S')
        f.write(f"[{timestamp}] {message}\n")

def read_status():
    """Read the current status from the status file"""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return f.read().strip()
    return "Ready"

def read_log():
    """Read the log file"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return f.readlines()
    return []

def read_properties():
    """Read the properties file"""
    if os.path.exists(PROPERTIES_FILE):
        try:
            with open(PROPERTIES_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def write_properties(properties):
    """Write properties to the properties file"""
    with open(PROPERTIES_FILE, "w") as f:
        json.dump(properties, f, indent=4)

def is_scraping_active():
    """Check if scraping is active"""
    return os.path.exists(ACTIVE_FILE)

def mark_as_active():
    """Mark scraping as active"""
    with open(ACTIVE_FILE, "w") as f:
        f.write(str(time.time()))

def mark_as_inactive():
    """Mark scraping as inactive"""
    if os.path.exists(ACTIVE_FILE):
        os.remove(ACTIVE_FILE)

def write_page_info(current_page, total_pages=None):
    """Write page progress information"""
    info = {
        "current_page": current_page,
        "total_pages": total_pages
    }
    with open(PAGE_INFO_FILE, "w") as f:
        json.dump(info, f)

def read_page_info():
    """Read page progress information"""
    if os.path.exists(PAGE_INFO_FILE):
        try:
            with open(PAGE_INFO_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"current_page": 1, "total_pages": None}
    return {"current_page": 1, "total_pages": None}

# Progress callback
def status_callback(update_type, data):
    """Callback function for scraping progress"""
    if update_type == "status":
        write_status(data)
        
        # Track page progress
        if "Moving to page" in data:
            parts = data.split()
            try:
                page_num = int(parts[-1])
                write_page_info(page_num)
            except (ValueError, IndexError):
                pass
        elif "No further pages to scrape" in data:
            page_info = read_page_info()
            write_page_info(page_info["current_page"], page_info["current_page"])
            
    elif update_type == "property":
        # Read current properties, add new one, write back
        properties = read_properties()
        properties.append(data)
        write_properties(properties)
        # Also log the property
        with open(LOG_FILE, "a") as f:
            timestamp = time.strftime('%H:%M:%S')
            f.write(f"[{timestamp}] Found property: {data.get('address', 'Unknown')} - {data.get('price', 'N/A')}\n")
    elif update_type == "complete":
        write_status(f"Completed! Found {data} properties.")
        mark_as_inactive()

# Function to run the scraping process in a subprocess
def run_scraper(location, headless):
    import subprocess
    import sys
    
    # Clear previous status files
    if os.path.exists(STATUS_FILE):
        os.remove(STATUS_FILE)
    if os.path.exists(PROPERTIES_FILE):
        os.remove(PROPERTIES_FILE)
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    if os.path.exists(ACTIVE_FILE):
        os.remove(ACTIVE_FILE)
    if os.path.exists(PAGE_INFO_FILE):
        os.remove(PAGE_INFO_FILE)
    
    # Write initial status
    write_status(f"Starting scrape for {location}...")
    write_properties([])
    write_page_info(1)
    mark_as_active()
    
    # Create a very simple script without trying to use f-strings for the boolean
    with open("run_scraper.py", "w") as f:
        f.write("""
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

# Status callback
def status_callback(update_type, data):
    if update_type == "status":
        with open(STATUS_FILE, "w") as f:
            f.write(data)
        # Also append to log with timestamp
        with open(LOG_FILE, "a") as f:
            timestamp = time.strftime('%H:%M:%S')
            f.write(f"[{timestamp}] {data}\\n")
            
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
            f.write(f"[{timestamp}] Found property: {data.get('address', 'Unknown')} - {data.get('price', 'N/A')}\\n")
    elif update_type == "complete":
        with open(STATUS_FILE, "w") as f:
            f.write(f"Completed! Found {data} properties.")
        ensure_inactive()

async def main():
    try:
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
            f.write(f"[{timestamp}] Error: {error_msg}\\n")
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
""")
    
    # Launch the process with command line arguments for location and headless
    subprocess.Popen([
        sys.executable, 
        "run_scraper.py", 
        location, 
        str(headless)
    ])

# Check if active process is stale
def check_active_process():
    """Check if the active process is stale (hasn't updated status in a while)"""
    if not is_scraping_active():
        return False
    
    # Check if the status file was recently updated
    if os.path.exists(STATUS_FILE):
        status_mtime = os.path.getmtime(STATUS_FILE)
        current_time = time.time()
        
        # If status hasn't updated in 2 minutes, consider process stale
        if current_time - status_mtime > 120:  # 2 minutes
            write_status("Scraping process appears to be stale - automatically stopped")
            mark_as_inactive()
            return True
    
    return False

# Run the active process check
check_active_process()

# Function to determine if we're running in a cloud environment
def is_cloud_environment():
    return os.environ.get("STREAMLIT_CLOUD") is not None or \
           os.environ.get("IS_CLOUD_ENV") is not None or \
           "streamlit.app" in os.environ.get("HOSTNAME", "") or \
           os.path.exists("/.dockerenv")

# Function to load pre-scraped data
def load_prescraped_data():
    try:
        with open("outputs/outputs.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading pre-scraped data: {e}")
        return []

# Main UI
st.title("🏠 AI Estate Scraper")
st.subheader("Scrape property listings from apartments.com")

# Check if running in cloud environment and show warning
if is_cloud_environment():
    st.warning("⚠️ Running in cloud environment - live scraping is disabled. Using pre-scraped demo data instead.")

# Input form
with st.form("scraper_form"):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        location = st.text_input("Enter location to scrape (city, neighborhood, zip code)", value="New York, NY")
    
    with col2:
        headless = st.checkbox("Headless Mode", value=True, help="Run browser in headless mode (no visible browser)")
    
    submit_button = st.form_submit_button("Start Scraping", use_container_width=True)

    # Handle form submission based on environment
    if submit_button:
        if is_cloud_environment():
            # In cloud environment, use pre-scraped data
            st.session_state.demo_loaded = True
            write_status(f"Loading demo data for {location}...")
            # Set basic state for UI continuity
            write_properties(load_prescraped_data())
            write_page_info(1, 1)
            st.rerun()
        elif not is_scraping_active():
            # Only run live scraping in local environment
            run_scraper(location, headless)
            st.rerun()

# Add a demo data button outside the form
if not is_scraping_active() and not st.session_state.get("demo_loaded", False):
    if st.button("Load Demo Data"):
        st.session_state.demo_loaded = True
        write_status("Loading demo data...")
        # Set basic state for UI continuity
        write_properties(load_prescraped_data())
        write_page_info(1, 1)
        st.rerun()

# Check if scraping is active and add a stop button
if is_scraping_active():
    st.warning("⚠️ Scraping in progress. Please don't close this window.")
    
    # Add a stop button
    if st.button("Stop Scraping"):
        write_status("Scraping stopped by user")
        mark_as_inactive()
        st.rerun()

# Progress display
st.subheader("Scraping Progress")

# Get current status and properties
current_status = read_status()
properties = read_properties()
log_entries = read_log()
page_info = read_page_info()

# Page progress bar
if is_scraping_active() and page_info["current_page"] > 1:
    st.markdown("<p class='progress-label'>Page Progress:</p>", unsafe_allow_html=True)
    
    if page_info["total_pages"]:
        page_progress = min(1.0, page_info["current_page"] / page_info["total_pages"])
        st.progress(page_progress)
        st.caption(f"Page {page_info['current_page']} of {page_info['total_pages']}")
    else:
        # We don't know total pages yet, just show current page
        st.progress(0.0)  # Indeterminate progress

# Add additional checking for error status to prevent false "scraping in progress"
if is_scraping_active() and current_status.lower().startswith("error:"):
    # If there's an error message but scraping is still marked as active, fix it
    st.error(f"Scraping process failed: {current_status}")
    mark_as_inactive()
    st.rerun()

# Property progress bar
progress_percentage = 0  
if current_status.startswith("Processing property"):
    st.markdown("<p class='progress-label'>Property Progress on Current Page:</p>", unsafe_allow_html=True)
    # Try to estimate progress based on status
    try:
        # Extract numbers from status like "Processing property 5/10"
        parts = current_status.split(" ")
        for part in parts:
            if "/" in part:
                current, total = map(int, part.split("/"))
                progress_percentage = min(0.99, current / total)
                st.progress(progress_percentage)
                st.caption(f"Property {current} of {total} on current page")
                break
    except:
        st.progress(0.0)
elif is_scraping_active():
    st.progress(0.0)  # Show indeterminate progress

# Status and log display
progress_col, time_col = st.columns(2)
with progress_col:
    st.subheader("Status")
    st.markdown(f'<div class="status-display">{current_status}</div>', unsafe_allow_html=True)
    
    # Show a progress log
    st.markdown("<h3 class='section-header'>Progress Log</h3>", unsafe_allow_html=True)
    log_placeholder = st.empty()
    log_html = "<div class='log-container'>"
    for log in reversed(log_entries):
        log_parts = log.strip().split("]", 1)
        if len(log_parts) == 2:
            timestamp, message = log_parts
            log_html += f"<div class='log-entry'><span class='timestamp'>{timestamp}]</span>{message}</div>"
        else:
            log_html += f"<div class='log-entry'>{log.strip()}</div>"
    log_html += "</div>"
    log_placeholder.markdown(log_html, unsafe_allow_html=True)

with time_col:
    st.subheader("Statistics")
    
    # Calculate start time from active file if it exists
    start_time = None
    if os.path.exists(ACTIVE_FILE):
        try:
            with open(ACTIVE_FILE, "r") as f:
                start_time = float(f.read().strip())
        except:
            pass
    
    if start_time:
        elapsed = time.time() - start_time
        elapsed_formatted = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        
        if len(properties) > 0:
            avg_time = elapsed / len(properties)
            estimated_text = f"Avg. time per property: {avg_time:.1f}s"
        else:
            estimated_text = "Waiting for first property..."
            
        stats_text = f"""
        Properties found: {len(properties)}
        
        Elapsed time: {elapsed_formatted}
        
        {estimated_text}
        """
        st.info(stats_text)
    else:
        st.info("Not started")

# Results display
st.markdown("<h2 class='section-header'>Properties Found</h2>", unsafe_allow_html=True)

# Download button for the results
if properties:
    json_str = json.dumps(properties, indent=4)
    st.download_button(
        label="Download Results (JSON)",
        data=json_str,
        file_name="property_listings.json",
        mime="application/json"
    )

# Display properties in cards
property_container = st.container()
with property_container:
    if not properties:
        st.info("No properties found yet. Start a scraping job to see results here.")
    else:
        # Create a grid layout for the properties
        cols = st.columns(3)
        for i, prop in enumerate(properties):
            with cols[i % 3]:
                # Extract all property data first for debugging
                all_fields_debug = ""
                if DEBUG_MODE:
                    all_fields_debug = "<div style='display:none'>"
                    for key, value in prop.items():
                        all_fields_debug += f"{key}: {value}, "
                    all_fields_debug += "</div>"
                
                # Get property data with proper fallbacks
                address = prop.get('address', '')
                if not address or address == 'Property' or address == 'N/A':
                    # Look for alternative address data
                    address = "Property Details"
                    
                # Handle price and price_type properly
                price = prop.get('price', '')
                if not price or price == 'N/A':
                    price = "Price not available"
                
                price_type = prop.get('price_type', '')
                if price_type in ['N/A', 'range', None, '']:
                    price_type = ''
                    
                # Check if price contains "range" and fix it
                if 'range' in str(price).lower():
                    price = price.replace('range', '').strip()
                
                # Extract beds and baths more carefully
                beds = prop.get('beds', '')
                if beds == 'N/A':
                    beds = 'N/A'  # Keep N/A for display
                    
                baths = prop.get('baths', '')
                if baths == 'N/A':
                    baths = 'N/A'  # Keep N/A for display
                
                # Start building the property card
                property_html = f"""
                <div class="property-card">
                    {all_fields_debug}
                """
                
                # Only add price if it's not "Price not available"
                if price != "Price not available":
                    property_html += f'<div class="property-price">{price} <span style="font-size:0.8em;color:#7f8c8d">{price_type}</span></div>'
                
                # Show beds/baths section with proper formatting
                property_html += '<div class="property-details">'
                if beds and beds != 'N/A':
                    property_html += f'<div class="property-detail-item">{beds} beds</div>'
                if baths is None or baths == 'N/A':
                    property_html += '<div class="property-detail-item">Not specified baths</div>'
                elif baths:
                    property_html += f'<div class="property-detail-item">{baths} baths</div>'
                property_html += '</div>'
                
                # Add any other properties, excluding problematic ones
                other_props = []
                for key, value in prop.items():
                    if key not in ['price', 'price_type', 'beds', 'baths', 'address', 'range'] and value and value != 'N/A':
                        other_props.append(f'<div class="property-attribute"><b>{key.title()}:</b> {value}</div>')
                
                if other_props:
                    property_html += '<div class="property-other">'
                    property_html += ''.join(other_props)
                    property_html += '</div>'
                
                property_html += "</div>"
                st.markdown(property_html, unsafe_allow_html=True)

# Auto-refresh while scraping is active
if is_scraping_active():
    time.sleep(1)  # Small delay
    st.rerun()

# Function to display properties from a list
def display_properties(properties_list):
    """Display a list of properties in the UI"""
    if not properties_list:
        st.info("No properties found in the dataset.")
        return
    
    # Create a grid layout for the properties
    cols = st.columns(3)
    for i, prop in enumerate(properties_list):
        with cols[i % 3]:
            # Extract all property data first for debugging
            all_fields_debug = ""
            if DEBUG_MODE:
                all_fields_debug = "<div style='display:none'>"
                for key, value in prop.items():
                    all_fields_debug += f"{key}: {value}, "
                all_fields_debug += "</div>"
            
            # Get property data with proper fallbacks
            address = prop.get('address', '') or prop.get('Address', '')
            if not address or address == 'Property' or address == 'N/A':
                address = "Property Details"
                
            # Handle price and price_type properly
            price = prop.get('price', '') or prop.get('Price', '')
            if not price or price == 'N/A':
                price = "Price not available"
            
            price_type = prop.get('price_type', '') or prop.get('price_type', '')
            if price_type in ['N/A', 'range', None, '']:
                price_type = ''
                
            # Check if price contains "range" and fix it
            if 'range' in str(price).lower():
                price = price.replace('range', '').strip()
            
            # Extract beds and baths more carefully
            beds = prop.get('beds', '') or prop.get('Beds', '')
            if beds == 'N/A':
                beds = 'N/A'  # Keep N/A for display
                
            baths = prop.get('baths', '') or prop.get('Baths', '')
            if baths == 'N/A':
                baths = 'N/A'  # Keep N/A for display
            
            # Start building the property card
            property_html = f"""
            <div class="property-card">
                {all_fields_debug}
                <div class="property-address">{address}</div>
            """
            
            # Only add price if it's not "Price not available"
            if price != "Price not available":
                property_html += f'<div class="property-price">{price} <span style="font-size:0.8em;color:#7f8c8d">{price_type}</span></div>'
            
            # Show beds/baths section with proper formatting
            property_html += '<div class="property-details">'
            if beds and beds != 'N/A':
                property_html += f'<div class="property-detail-item">{beds} beds</div>'
            if baths is None or baths == 'N/A':
                property_html += '<div class="property-detail-item">Not specified baths</div>'
            elif baths:
                property_html += f'<div class="property-detail-item">{baths} baths</div>'
            property_html += '</div>'
            
            # Add any other properties, excluding problematic ones
            other_props = []
            for key, value in prop.items():
                key_lower = key.lower()
                if key_lower not in ['price', 'price_type', 'beds', 'baths', 'address', 'range'] and value and value != 'N/A':
                    other_props.append(f'<div class="property-attribute"><b>{key.title()}:</b> {value}</div>')
            
            if other_props:
                property_html += '<div class="property-other">'
                property_html += ''.join(other_props)
                property_html += '</div>'
            
            property_html += "</div>"
            st.markdown(property_html, unsafe_allow_html=True) 