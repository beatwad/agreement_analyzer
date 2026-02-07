from typing import Optional

import uvicorn
import io
import asyncio
from loguru import logger
from pypdf import PdfReader
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
        logger.info(f"Starting URL extraction: {url}")
        async with async_playwright() as p:
            if url.lower().endswith(".pdf"):
                request_context = await p.request.new_context()
                response = await request_context.get(url)

                if response.ok:
                    data = await response.body()
                    logger.info(f"File downloaded. Size: {len(data)} bytes")

                    pdf_file = io.BytesIO(data)
                    reader = PdfReader(pdf_file)
                    logger.info(f"Number of pages: {len(reader.pages)}")

                    full_text = ""
                    for page in reader.pages:
                        full_text += page.extract_text() + "\n"

                    return full_text
                else:
                    logger.error(f"Failed to load: {response.status}")
                    raise HTTPException(
                        status_code=400, detail=f"Failed to load: {response.status}"
                    )

            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            response = None
            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                logger.debug(
                    f"Page loaded: {url}, status: {response.status if response else 'N/A'}"
                )
            except Exception as e:
                logger.warning(f"Page navigation timeout or error for {url}: {str(e)}")
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
        result = "\n".join(chunk for chunk in chunks if chunk)
        logger.info(f"URL extraction completed (HTML): {len(result)} characters")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scrape URL {url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")


@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    logger.info(
        f"Analysis request received - Provider: {request.llm_model_provider}, "
        f"Model: {request.llm_model}, URL: {request.url is not None}, "
        f"Text provided: {request.text is not None}"
    )

    if not request.api_key:
        logger.warning("Analysis request rejected: API Key missing")
        raise HTTPException(status_code=401, detail="API Key missing")

    # 1. Determine Source (URL scrape vs Raw Text)
    content_to_analyze = request.text
    if request.url:
        logger.info(f"Extracting content from URL: {request.url}")
        content_to_analyze = await extract_text_from_url(request.url)
    elif request.text:
        logger.info(f"Using provided text: {len(request.text)} characters")

    if not content_to_analyze or len(content_to_analyze) < 50:
        logger.warning(
            f"Insufficient content to analyze: {len(content_to_analyze) if content_to_analyze else 0} characters"
        )
        raise HTTPException(status_code=400, detail="Not enough text found to analyze.")

    logger.info(
        f"Starting LLM analysis: {len(content_to_analyze)} characters, free_tier={request.free_tier}"
    )
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
        logger.info(f"Analysis completed successfully: {len(response)} characters in response")
        # with open("response.txt", "w") as f:
        #     f.write(response)
        return {"result": response}

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"status": "Server is running", "message": "Go to /docs to see the API documentation"}


if __name__ == "__main__":
    logger.info("Starting Agreement Analyzer server on 0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
