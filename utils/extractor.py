from selectolax.parser import HTMLParser
from groq import Groq
import json
import asyncio

async def extract_property_data(html, config, api_key, page_number=1, callback=None):
    """Extract property data from HTML using LLM"""
    if callback:
        callback("status", f"Extracting properties from page {page_number}")
    
    # Parse HTML
    tree = HTMLParser(html)
    house_selector = config.get("parentContainer").get("selector")
    houses = tree.css(house_selector)
    
    if callback:
        callback("status", f"Found {len(houses)} properties on page {page_number}")
    
    # LLM config
    system_prompt = config.get("llmConfig").get("systemPrompt")
    model = config.get("llmConfig").get("model") 
    response_format = config.get("llmConfig").get("responseFormat")
    
    # Initialize Groq client if API key is provided
    client = None
    if api_key:
        client = Groq(api_key=api_key)
    
    properties = []
    
    # Process each house
    for i, house in enumerate(houses):
        if callback:
            callback("status", f"Processing property {i+1}/{len(houses)} on page {page_number}")
        
        # If we don't have a client, return dummy data
        if not client:
            dummy_data = {
                "Price": f"${1000 + (i * 500)}",
                "price_type": "fixed",
                "Beds": 2,
                "Baths": 2.0,
                "Address": f"Sample Property {i+1}, Page {page_number}"
            }
            properties.append(dummy_data)
            if callback:
                callback("property", dummy_data)
            continue
        
        # Extract data with LLM
        try:
            chat = client.chat.completions.create(
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
            property_data = json.loads(response)
            properties.append(property_data)
            
            if callback:
                callback("property", property_data)
                
        except Exception as e:
            print(f"Error extracting data: {e}")
            # Add placeholder data on error
            error_data = {
                "Price": "N/A",
                "price_type": "fixed",
                "Beds": 0,
                "Baths": None,
                "Address": f"Error processing property {i+1}"
            }
            properties.append(error_data)
            if callback:
                callback("property", error_data)
        
        # Delay to avoid rate limiting
        await asyncio.sleep(1)
    
    return properties 