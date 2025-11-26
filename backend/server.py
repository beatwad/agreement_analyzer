from typing import Optional

import uvicorn
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
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
    llm_model: str = "gemini-2.0-flash"
    llm_model_provider: str = "Gemini"
    temperature: float = 0.4
    free_tier: bool = True
    free_tier_rpm_limit: int = 15


async def extract_text_from_url(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception:
                # If networkidle times out, we still might have useful content
                pass

            content = await page.content()
            await browser.close()

        soup = BeautifulSoup(content, "html.parser")

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
async def analyze(request: AnalysisRequest):
    if not request.api_key:
        raise HTTPException(status_code=401, detail="API Key missing")

    # 1. Determine Source (URL scrape vs Raw Text)
    content_to_analyze = request.text
    if request.url:
        content_to_analyze = await extract_text_from_url(request.url)

    if not content_to_analyze or len(content_to_analyze) < 50:
        raise HTTPException(status_code=400, detail="Not enough text found to analyze.")

    try:
        gpt_answerer = GPTAnswerer(
            api_key=request.api_key,
            llm_proxy="",
            llm_provider=request.llm_model_provider,
            llm_model=request.llm_model,
            temperature=request.temperature,
            free_tier=request.free_tier,
            free_tier_rpm_limit=request.free_tier_rpm_limit,
        )
        response = gpt_answerer.analyze_agreement(content_to_analyze)
        return {"result": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"status": "Server is running", "message": "Go to /docs to see the API documentation"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
