from fastapi import FastAPI
from main import render_and_extract

app = FastAPI(title="AiEstateScraper",
              description="Ai Powered webscraper for properties data based on given location from apartments.com")

@app.route("/scrape/{location}")
async def scrape(location:str):
    data = render_and_extract(location=location)
    return {"location": location, "properties": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

