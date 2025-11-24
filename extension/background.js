// Create Context Menu Items
const SERVER_URL = "https://agreement-analyzer.tail0c4bb5.ts.net";
// const SERVER_URL = "http://127.0.0.1:8001"; // Use this for local development

chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "analyze-page",
        title: "Analyze Current Page Agreement",
        contexts: ["page", "selection"]
    });
    chrome.contextMenus.create({
        id: "analyze-link",
        title: "Analyze Linked Agreement",
        contexts: ["link"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    // Get API Key
    chrome.storage.sync.get(['geminiKey'], (result) => {
        if (!result.geminiKey) {
            alert("Please set your Gemini API Key in the extension settings.");
            chrome.runtime.openOptionsPage();
            return;
        }

        const apiKey = result.geminiKey;
        
        if (info.menuItemId === "analyze-link") {
            // Scenario 1: Link Analysis (Send URL to Python)
            handleAnalysis(apiKey, SERVER_URL, null, info.linkUrl);
        } 
        else if (info.menuItemId === "analyze-page") {
            // Scenario 2: Page Analysis (Extract text via Scripting)
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => document.body.innerText
            }, (results) => {
                if (results && results[0]) {
                    handleAnalysis(apiKey, SERVER_URL, results[0].result, null);
                }
            });
        }
    });
});

async function handleAnalysis(apiKey, serverUrl, text, url) {
    // Open result tab immediately
    let resultTab;
    try {
        resultTab = await chrome.tabs.create({ url: 'result.html' });
    } catch (e) {
        console.error("Failed to create result tab:", e);
        return;
    }

    try {
        console.log("Sending request with Key:", apiKey ? "Yes" : "No"); // Debug log
        console.log("Target Server:", serverUrl);

        const response = await fetch(`${serverUrl}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                api_key: apiKey,
                text: text,
                url: url
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            // FIX: Check if detail is an object/array and stringify it
            let errorMsg = data.detail;
            if (typeof errorMsg === 'object') {
                errorMsg = JSON.stringify(errorMsg);
            }
            throw new Error(errorMsg || "Server Error");
        }

        // Success - Send result to the tab
        chrome.tabs.sendMessage(resultTab.id, { 
            action: 'displayResult', 
            data: data.result,
            error: false 
        });

    } catch (error) {
        console.error("Analysis Failed:", error);
        
        // Show error in the tab
        if (resultTab && resultTab.id) {
            chrome.tabs.sendMessage(resultTab.id, { 
                action: 'displayResult', 
                data: error.message,
                error: true 
            });
        }
    }
}