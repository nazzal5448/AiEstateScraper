import json

_config = {
    "url": "https://apartments.com",
    "timeout":120000,
    "waitSelector": "div#placardContainer ul li.mortar-wrapper",

    "parentContainer":{
        "selector":"div#placardContainer ul li.mortar-wrapper",
        "type":"[node]",
        "description": "returns all the property listings separately as nodes."
    },

    "items":{
        "searchHeading":{
            "selector":"div.placardContainer > h1.placardSearchHeading",
            "type": "node",
            "description": "Used to fetch the location currently being scraped."
        },
        "searchBox":{
            "selector": "input#quickSearchLookup",
            "type": "node",
            "description": "Search box used to type lookup location."
        },

        "searchButton":{
            "selector": "button.typeaheadSearch",
            "type": "node",
            "description": "Search button which is clicked after location is enetered in search box."
        },
        "nextButton":{
            "selector": "a[aria-label='Next Page'] > span.pagingBtn",
            "type": "node",
            "description": "returns the next button used to go forward."
        }
    },

    "llmConfig": {
        "model":"llama-3.1-8b-instant",
        "responseFormat": { "type": "json_object" },

            "systemPrompt":{
                "role": "system",
                "content": """You are an assistant that extracts structured data from real estate listings. 
                You will receive Text content from HTML of each property listing, and your task is to extract and return the relevant information in valid JSON format.

                Required fields:
                - 'Price': (string) Price of the property. can be a range or single value.  
                - 'price_type': (string) "range" if there is a price range, otherwise "fixed".
                - 'Beds': (int) Number of bedrooms.
                - 'Baths': (float) Number of bathrooms if given otherwise return null.
                - 'Address': (string) The address of the house. if not given, return null.

                Example output:
                {
                    "Price": "2300-3500",
                    "price_type": "range",
                    "Beds": 2,
                    "Baths":3.5,
                    "Address": "Main avenue field, 365 street"
                }

                **Important Notes:**
                - Extract numerical values only, removing currency symbols.
                - Ensure the output is valid JSON.

                IMPORTANT: Output ONLY valid JSON—no explanations, no summaries, and no preamble.
                """
            }
    },    
    
}


def get_config():
    return _config

def generate_config():
    with open("config/config.json", "w") as f:
        json.dump(_config, f, indent=4, ensure_ascii=True) 

if __name__ == "__main__":
    generate_config()