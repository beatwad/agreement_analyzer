// const SERVER_URL = "http://localhost:8001";
const SERVER_URL = "https://chancellor-science-whose-optimal.trycloudflare.com";

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
    // Get Settings
    chrome.storage.sync.get({
        geminiKey: '',
        modelProvider: 'Gemini',
        modelName: 'gemini-2.0-flash',
        temperature: 0.4,
        freeTier: true,
        rpmLimit: 15
    }, (result) => {
        if (!result.geminiKey) {
            alert("Please set your API Key in the extension settings.");
            chrome.runtime.openOptionsPage();
            return;
        }

        const config = {
            apiKey: result.geminiKey,
            modelProvider: result.modelProvider,
            modelName: result.modelName,
            temperature: result.temperature,
            freeTier: result.freeTier,
            rpmLimit: result.rpmLimit
        };
        
        if (info.menuItemId === "analyze-link") {
            // Scenario 1: Link Analysis (Send URL to Python)
            handleAnalysis(config, SERVER_URL, null, info.linkUrl);
        } 
        else if (info.menuItemId === "analyze-page") {
            // Scenario 2: Page Analysis (Extract text via Scripting)
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => document.body.innerText
            }, (results) => {
                if (results && results[0]) {
                    handleAnalysis(config, SERVER_URL, results[0].result, null);
                }
            });
        }
    });
});

async function handleAnalysis(config, serverUrl, text, url) {
    // Open result tab immediately
    let resultTab;
    try {
        resultTab = await chrome.tabs.create({ url: 'result.html' });
    } catch (e) {
        console.error("Failed to create result tab:", e);
        return;
    }

    try {
        console.log("Sending request with Key:", config.apiKey ? "Yes" : "No"); // Debug log
        console.log("Target Server:", serverUrl);

        const response = await fetch(`${serverUrl}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                api_key: config.apiKey,
                text: text,
                url: url,
                llm_model: config.modelName,
                llm_model_provider: config.modelProvider,
                temperature: config.temperature,
                free_tier: config.freeTier,
                free_tier_rpm_limit: config.rpmLimit
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
