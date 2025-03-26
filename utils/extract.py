from selectolax.parser import HTMLParser
from groq import Groq
import json
import time

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
    def __init__(self,html_pages:list, api_key:str, config:dict):
        self.html_pages = html_pages
        self.config = config
        #initialize the model
        self.client = Groq(api_key=api_key)

    def extract(self):
        '''
        Uses llm to extract all the required info.

        Returns:
        A list of jsons for each of the properties present in html passed to the instance.
        The Json contains the required data output by llm.
        '''
        HOUSE_SELECTOR = self.config.get("parentContainer").get("selector")
        SYSTEM_PROMPT = self.config.get("llmConfig").get("systemPrompt")
        MODEL = self.config.get("llmConfig").get("model")

        #it stores all the json output from llm
        properties_data = []
        if self.html_pages:
            for idx, page in enumerate(self.html_pages):
                print(f"Parsing page {idx + 1}...")
                tree = HTMLParser(page)
                houses = tree.css(HOUSE_SELECTOR)

                for idx_, house in enumerate(houses):
                    print(f"Parsing data from house no: {idx_+1}")
                    chat = self.client.chat.completions.create(
                        messages=[
                            SYSTEM_PROMPT,
                            {
                                "role":"user",
                                "content": f"Extract info from the following text:\n\n{house.text()}"
                            }
                        ],

                        model=MODEL,
                        response_format=self.config.get("llmConfig").get("responseFormat")
                    )
                    response = chat.choices[0].message.content
                    try:
                        properties_data.append(json.loads(response))
                        time.sleep(2)
                    except Exception as e:
                        print(e)
            
            return properties_data
        else:
            pass

