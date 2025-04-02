from selectolax.parser import HTMLParser
from groq import Groq
import json
import asyncio

class Extract:
    '''
    Extracts the following details from the given html for all properties:
    {
        - price
        - price_type
        - beds
        - baths
        - address
    }
    '''
    def __init__(self, html_pages:list, api_key:str, config:dict, callback=None):
        self.html_pages = html_pages
        self.config = config
        self.callback = callback  # Callback function to report progress
        #initialize the model
        self.client = Groq(api_key=api_key)

    async def extract(self, house, model:str, system_prompt:str, response_format:dict):
        '''
        Uses llm to extract the required data from the given house html/text.

        Args:
         - house: (node) A selectolax node of single property listing.
         - model: (str) The LLM model to use for processing
         - system_prompt: (str)Set of instructions for LLM.
         - response_format: (dict) The type of response the LLM should give. e.g. {"type":"json_object"}

        Returns:
        All property details in json.
        '''
        

        try:
            chat = self.client.chat.completions.create(
                messages=[
                    system_prompt,
                    {
                        "role": "user",
                        "content": f"Extract info from the following text:\n\n{house.text()}",
                    },
                ],
                model=model,
                response_format=response_format,
            )
            response = chat.choices[0].message.content
            return json.loads(response)
        except Exception as e:
            print(f"Error extracting data: {e}")
            return None
        
    
    async def execute(self):
        '''
        Executes the parsing and extraction process for all property nodes recieved from HTML.

        Returns:
         A json of all the property data.
        '''
        HOUSE_SELECTOR = self.config.get("parentContainer").get("selector")
        SYSTEM_PROMPT = self.config.get("llmConfig").get("systemPrompt")
        MODEL = self.config.get("llmConfig").get("model")
        RESPONSE_FORMAT = self.config.get("llmConfig").get("responseFormat")
         # Store all extracted property data
        properties_data = []

        if not self.html_pages:
            if self.callback:
                self.callback("status", "No HTML pages to process.")
            return properties_data

        total_pages = len(self.html_pages)
        for idx, page in enumerate(self.html_pages):
            page_msg = f"Parsing page {idx + 1} of {total_pages}..."
            print(page_msg)
            if self.callback:
                self.callback("status", page_msg)
            
            tree = HTMLParser(page)
            houses = tree.css(HOUSE_SELECTOR)
            total_houses = len(houses)
            
            if self.callback:
                self.callback("status", f"Found {total_houses} properties on page {idx + 1}")

            for i, house in enumerate(houses):
                if self.callback:
                    self.callback("status", f"Processing property {i+1}/{total_houses} on page {idx+1}")
                
                result = await self.extract(house, system_prompt=SYSTEM_PROMPT, model=MODEL, response_format=RESPONSE_FORMAT)
                if result:
                    properties_data.append(result)
                    if self.callback:
                        self.callback("property", result)
                
                # Async delay to avoid rate-limiting
                await asyncio.sleep(1)

            # Delay between pages to avoid rate-limiting
            await asyncio.sleep(2)

        if self.callback:
            self.callback("complete", len(properties_data))
        return properties_data
