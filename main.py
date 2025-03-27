import json
import os
import dotenv
import asyncio
from utils.render import render
from utils.extract import Extract
from config.tools import get_config
    

async def render_and_extract(location:str,
                        headless_browser:bool=True,
                        running_from_file:bool=False):
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
    html_pages = await render(location, config=config, headless=headless_browser)
    extractor = Extract(html_pages, api_key=API_KEY, config=config)
    data = await extractor.execute()
    if data:
        if running_from_file:
            with open("outputs/outputs.json", "w") as f:
                json.dump(data, f, indent=4)
        return data

    




if __name__ == "__main__":
    location = input("Enter the location you want to scrape property listings for: ")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(render_and_extract(location, running_from_file=True, headless_browser=False))
