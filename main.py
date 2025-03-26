import json
import os
import dotenv
from utils.render import render
from utils.extract import Extract
from config.tools import get_config
    

def render_and_extract(location:str,
                        headless_browser:bool=True):
    '''
    Function responsible for rendering and extracting property listings'data for
    given `location` and saves the json data to `outputs/output.json`.

    Args:
     - location: (str) The location you want to extract data for.
     - headless_browser: (bool) Set it to `True` if you want to see the rendering visually.
    
    Returns:
     - None
    '''
    dotenv.load_dotenv(".env")
    API_KEY = os.environ.get("GROQ_API_KEY")

    config = get_config()
    html_pages = render(location, config=config, headless=headless_browser)
    extractor = Extract(html_pages, api_key=API_KEY, config=config)
    data = extractor.extract()
    if data:
        with open("outputs/outputs.json", "w") as f:
            json.dump(data, f, indent=4)




if __name__ == "__main__":
    location = input("Enter the location you want to scrape property listings for: ")
    render_and_extract(location, headless_browser=True)