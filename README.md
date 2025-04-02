# AI Estate Scraper

A Streamlit app that scrapes property listings from apartments.com and extracts property data using AI.

## Features

- Search for properties by location (city, neighborhood, zip code)
- View property details including price, beds, baths, and amenities
- Automatic detection of cloud environments for seamless deployment
- Demo mode with pre-scraped data

## Deployment

The app can be deployed both locally and on Streamlit Cloud.

### Local Deployment

For local deployment, you'll need to install the required dependencies:

```bash
pip install -r requirements.txt
```

Then run the app:

```bash
streamlit run app.py
```

### Streamlit Cloud Deployment

The app automatically detects when it's running on Streamlit Cloud and uses pre-scraped demo data instead of attempting live scraping, which would require system dependencies.

## Technical Details

- Built with Streamlit, Playwright, and Groq LLM
- Implements cloud environment detection
- Uses fallback mechanisms for better user experience
- Handles various edge cases and errors gracefully

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

