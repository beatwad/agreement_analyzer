from typing import Optional

import uvicorn
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from llm import GPTAnswerer

app = FastAPI()

# Allow Chrome Extension to access this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with chrome-extension://<ID>
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    api_key: str
    text: Optional[str] = None
    url: Optional[str] = None


def extract_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()

        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")


@app.post("/analyze")
async def analyze_agreement(request: AnalysisRequest):
    print(request)

    if not request.api_key:
        raise HTTPException(status_code=401, detail="API Key missing")

    # 1. Determine Source (URL scrape vs Raw Text)
    content_to_analyze = request.text
    if request.url:
        content_to_analyze = extract_text_from_url(request.url)

    if not content_to_analyze or len(content_to_analyze) < 50:
        raise HTTPException(status_code=400, detail="Not enough text found to analyze.")

    try:
        gpt_answerer = GPTAnswerer(request.api_key, "")
        response = gpt_answerer.analyze_agreement(content_to_analyze)
        return {"result": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"status": "Server is running", "message": "Go to /docs to see the API documentation"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
