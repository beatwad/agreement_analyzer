# Agreement Analyzer Chrome Extension

A Google Chrome Extension that uses AI to analyze legal text, Terms of Service, and contracts. It connects to a local Python backend powered by **FastAPI**, **LangChain**, and **Google Gemini**.

## 🚀 Features

*   **Analyze Page:** Right-click anywhere on a page to analyze the visible text.
*   **Analyze Link:** Right-click a link (e.g., "Terms of Service") to scrape that URL and analyze its content without visiting it manually.
*   **AI Summaries:** Uses Google's Gemini Pro model to highlight key points, red flags, and summaries.
*   **BYOK (Bring Your Own Key):** Securely input your own Google Gemini API Key in the extension settings.

## 🛠️ Tech Stack

*   **Frontend:** Chrome Extension (Manifest V3), JavaScript, HTML.
*   **Backend:** Python 3.9+, FastAPI, Uvicorn.
*   **AI Orchestration:** LangChain (Google GenAI).
*   **Scraping:** BeautifulSoup4, Requests.

---

## 📋 Prerequisites

1.  **Python 3.9** or higher installed.
2.  **Google Chrome** (or Chromium-based browsers like Brave/Edge).
3.  **Google Gemini API Key** (Get one for free at [Google AI Studio](https://aistudio.google.com/)).

---

## 📂 Project Structure

```text
agreement-analyzer/
├── backend/               # Python Server
│   ├── server.py          # FastAPI application logic
│   └── requirements.txt   # Python dependencies
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
    pip install -r requirements.txt
    ```
3.  Start the server:
    ```bash
    # Option A: Direct Python run
    python server.py
    
    # Option B: Using Uvicorn directly (recommended for dev)
    uvicorn app --reload
    ```
    *The server will run at `http://127.0.0.1:8000`.*

### 2. Extension Setup (Chrome)

1.  Open Chrome and navigate to `chrome://extensions/`.
2.  Enable **Developer mode** using the toggle in the top-right corner.
3.  Click the **Load unpacked** button.
4.  Select the `extension` folder from this project.

---

## 📖 Usage Guide

### Step 1: Configure API Key
1.  Click the extension icon (puzzle piece) in Chrome and find "Agreement Analyzer".
2.  Right-click the icon and select **Options**.
3.  Paste your **Google Gemini API Key** into the field and click **Save**.

### Step 2: Analyze Text
*   **Current Page:** Right-click anywhere on a webpage $\rightarrow$ Select **"Analyze Current Page Agreement"**.
*   **Linked Page:** Right-click on a hyperlink (e.g., "Terms & Conditions") $\rightarrow$ Select **"Analyze Linked Agreement"**.

### Step 3: View Results
Wait a few seconds (depending on the length of the text). An alert popup will appear displaying the AI-generated analysis.

---

## 🔧 Troubleshooting

**Error: "Failed to fetch"**
*   Ensure the Python server is running (`http://127.0.0.1:8000`).
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