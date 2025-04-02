# AI Estate Scraper

A web-based interface for scraping property listings from apartments.com with real-time progress updates and results display.

## Features

- Real-time property scraping with visual feedback
- Progress tracking and status updates
- Immediate display of properties as they're found
- Download results as JSON
- User-friendly interface

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```
   playwright install
   ```
4. Create a `.env` file in the root directory with your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```
2. Enter a location (city, neighborhood, or zip code)
3. Choose whether to run in headless mode or not
4. Click "Start Scraping" and watch the results in real-time

## How It Works

The application uses:
- Playwright for rendering and interacting with web pages
- Groq API (with LLama 3) for extracting property information
- Streamlit for the web interface
- Selectolax for HTML parsing

As properties are found, they are immediately displayed in the interface, allowing you to see results as they come in rather than waiting for the entire scraping process to finish.

## Requirements

- Python 3.7+
- Groq API key
- Internet connection

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
│    ├── extract.py          # Main scraper logic using LLM and Selectolax
│    └── render.py           # Handles rendering and data processing using Playwright
│
├── .env                    # Environment variables (e.g., API keys, LLM credentials)
├── main.py                 # Entry point for the scraper
└── requirements.txt        # Project dependencies
```

## Dependencies

```
groq
playwright
selectolax
python-dotenv
```

## License

This project is licensed under the MIT License.

