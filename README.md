# AiEstateScraper: Apartment Data Scraper

This project is a web scraper that uses Large Language Models (LLMs), Playwright, and Selectolax to extract property listings from **apartments.com**. It retrieves details such as price, address, and other property-related information for a given location.

## Features

- **Scrape apartments.com**: Extract property listings based on user-provided locations.
- **Playwright for automation**: Simulate human-like browser interactions to avoid detection.
- **Selectolax for parsing**: Efficiently parse and extract data from HTML content.
- **LLM Integration**: Utilize a Large Language Model for data processing or enhancing extracted information.
- **Structured Outputs**: Store extracted data in a JSON format.

## Project Structure

```
AiEstateScraper/
├── config/                 # Configuration files
│    ├── config.json         # Stores scraper settings 
│    └── tools.py            # Helper functions for configuration handling
│
├── outputs/                # Directory for storing scraped data
│    └── outputs.json        # JSON file containing extracted property listings
│
├── utils/                  # Utility scripts
│    ├── extract.py          # Main scraper logic using Playwright and Selectolax
│    └── render.py           # Handles rendering and data processing
│
├── .env                    # Environment variables (e.g., API keys, LLM credentials)
├── main.py                 # Entry point for the scraper
└── requirements.txt        # Project dependencies
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/nazzal5448/AiEstateScraper.git
   cd AiEstateScraper
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. Set up the `.env` file with GROQ_API_KEY = "your_groq_api_key"

## Usage


1. Run the scraper:

   ```bash
   python main.py
   ```
2. Enter location in terminal.

3. View the results in `outputs/outputs.json`.

## Custom Configurations

You can configure the scraper by modifying `config/tools.py` and then running it. 

## Dependencies

```
groq
playwright
selectolax
python-dotenv
```

## License

This project is licensed under the MIT License.

