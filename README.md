# Agreement Analyzer Chrome Extension

A Google Chrome Extension that uses AI to analyze text or link to Terms of Service/User Agreement/Contract and finds the real and potential red flags in it. It connects to a local Python backend powered by **FastAPI**, **LangChain**, and **Google Gemini** (can be replaced with any other LLM provider).

## 🚀 Features

*   **Analyze Page:** Right-click anywhere on a page to analyze the visible text.
*   **Analyze Link:** Right-click a link (e.g., "Terms of Service") to scrape that URL and analyze its content without visiting it manually.
    *   **AI Summaries:** Uses LLM to highlight key points, red flags, and summaries.
    *   **Language Support:** Analyze agreements in any language and get results in your preferred language (or auto-detect).
    *   **Multi-Model Support:** Works with Google Gemini (default), OpenAI, Claude (Anthropic), and Ollama (local LLMs).
    *   **BYOK (Bring Your Own Key):** Securely input your own Google Gemini API Key in the extension settings.

## 🛠️ Tech Stack

*   **Frontend:** Chrome Extension (Manifest V3), JavaScript, HTML.
*   **Backend:** Python 3.9+, FastAPI, Uvicorn.
*   **AI Orchestration:** LangChain (Google GenAI).
*   **Scraping:** BeautifulSoup4, Requests.

---

## 📋 Prerequisites

1.  **Python 3.9** or higher installed.
2.  **uv** installed (see [uv documentation](https://github.com/astral-sh/uv)).
3.  **Google Chrome** (or Chromium-based browsers like Brave/Edge).
4.  **Google Gemini API Key** (Get one for free at [Google AI Studio](https://aistudio.google.com/)).

---

## 📂 Project Structure

```text
agreement-analyzer/
├── backend/               # Python Server
│   ├── server.py          # FastAPI application logic
│   ├── pyproject.toml     # Python dependencies (managed by uv)
│   └── uv.lock            # Dependency lock file
├── extension/             # Chrome Extension Source
│   ├── manifest.json      # Extension configuration
│   ├── background.js      # Logic for context menus & API calls
│   ├── options.html       # Settings page (API Key input)
│   ├── options.js         # Settings logic
│   └── icon.png           # (Optional) App Icon
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Backend Setup (Python)

1.  Navigate to the `backend` folder:
    ```bash
    cd backend
    ```
2.  Install the required dependencies:
    ```bash
    uv sync
    ```
3.  Start the server:
    ```bash
    # Option A: Direct Python run
    uv run server.py
    
    # Option B: Using Uvicorn directly (recommended for dev)
    uv run uvicorn server:app --reload --port 8001
    ```
    *The server will run at `http://127.0.0.1:8001`.*

#### Alternative: Run with Docker Compose

1.  Navigate to the project root:
    ```bash
    cd agreement-analyzer
    ```
2.  Start the service:
    ```bash
    docker-compose up --build -d
    ```
    *The server will run at `http://localhost:8001` (or your configured port).*

### 2. Extension Setup (Chrome)

1.  Open Chrome and navigate to `chrome://extensions/`.
2.  Enable **Developer mode** using the toggle in the top-right corner.
3.  Click the **Load unpacked** button.
4.  Select the `extension` folder from this project.

---

## 📖 Usage Guide

### Step 1: Configure API Key & Settings
1.  Click the extension icon (puzzle piece) in Chrome and find "Agreement Analyzer".
2.  Right-click the icon and select **Options**.
3.  Select your preferred **Language** for the analysis results (or leave as "Auto-detect").
4.  Select your preferred **Model Provider** and **LLM Model**.
5.  Paste your **API Key**.
6.  Set **Free Tier** to true if you uses model with free tier.
7.  Set **Free Tier RPM Limit** to the maximum number of requests per minute that model provider allows for free tier.
8.  Set **Temperature** to the desired value between 0.0 and 1.0 (the more temperature, the more creative the model is and vice versa).
9.  Click **Save** to apply your settings.

### Step 2: Analyze Text
*   **Current Page:** Right-click anywhere on a webpage $\rightarrow$ Select **"Analyze Current Page Agreement"**.
*   **Linked Page:** Right-click on a hyperlink (e.g., "Terms & Conditions") $\rightarrow$ Select **"Analyze Linked Agreement"**.

### Step 3: View Results
Wait a few seconds (depending on the length of the text). An alert popup will appear displaying the AI-generated analysis.

---

## 🔧 Troubleshooting

**Error: "Failed to fetch"**
*   Ensure the Python server is running (`http://127.0.0.1:8001` or your configured IP/Port).
*   Check if your firewall is blocking the connection.

**Error: "400 Not enough text found"**
*   The page or link might be empty or protected by JavaScript that `BeautifulSoup` cannot execute. This tool works best on static text pages.

**Error: "401 API Key missing"**
*   Go to the Extension Options page and ensure your Gemini API key is saved.

**Alert box cuts off text**
*   Standard JavaScript `alert()` boxes have character limits. For a better experience, view the `server.py` logs to see the full Markdown output, or check the browser console.

---

## 📝 License
This project is open-source. Feel free to modify and distribute.