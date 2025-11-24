// Function to show modal with scrollable content
function showModal(message, isError) {
    // Remove existing modal if any
    const existingModal = document.getElementById('agreement-analyzer-modal');
    if (existingModal) {
        existingModal.remove();
    }

    // Create modal overlay
    const modal = document.createElement('div');
    modal.id = 'agreement-analyzer-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        z-index: 1000000;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    `;

    // Create modal container
    const container = document.createElement('div');
    container.style.cssText = `
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        width: 90%;
        max-width: 800px;
        max-height: 90vh;
        display: flex;
        flex-direction: column;
        position: relative;
    `;

    // Create header
    const header = document.createElement('div');
    header.style.cssText = `
        padding: 20px;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8f9fa;
        border-radius: 8px 8px 0 0;
    `;

    const title = document.createElement('h2');
    title.textContent = isError ? 'Error' : 'Analysis Result';
    title.style.cssText = `
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #333;
    `;

    const closeBtn = document.createElement('button');
    closeBtn.textContent = '×';
    closeBtn.style.cssText = `
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
    `;
    closeBtn.onmouseover = () => { closeBtn.style.background = '#e0e0e0'; closeBtn.style.color = '#333'; };
    closeBtn.onmouseout = () => { closeBtn.style.background = 'none'; closeBtn.style.color = '#666'; };
    closeBtn.onclick = () => modal.remove();

    header.appendChild(title);
    header.appendChild(closeBtn);

    // Create content area
    const content = document.createElement('div');
    // Use marked.parse if available, otherwise fallback to textContent
    if (typeof marked !== 'undefined' && marked.parse) {
        content.innerHTML = marked.parse(message);
    } else {
        content.textContent = message;
    }
    content.style.cssText = `
        padding: 20px;
        overflow-y: auto;
        flex: 1;
        word-wrap: break-word;
        line-height: 1.6;
        color: ${isError ? '#d32f2f' : '#333'};
    `;

    // Style markdown elements if using marked
    if (typeof marked !== 'undefined') {
        const style = document.createElement('style');
        style.textContent = `
            #agreement-analyzer-modal h1, #agreement-analyzer-modal h2, #agreement-analyzer-modal h3 { margin-top: 1em; margin-bottom: 0.5em; }
            #agreement-analyzer-modal p { margin-bottom: 1em; }
            #agreement-analyzer-modal ul, #agreement-analyzer-modal ol { padding-left: 20px; margin-bottom: 1em; }
            #agreement-analyzer-modal li { margin-bottom: 0.5em; }
            #agreement-analyzer-modal code { background: #f5f5f5; padding: 2px 4px; border-radius: 4px; font-family: monospace; }
            #agreement-analyzer-modal pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
        `;
        content.appendChild(style);
    }

    container.appendChild(header);
    container.appendChild(content);
    modal.appendChild(container);

    // Close on background click
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    };

    // Close on Escape key
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);

    document.body.appendChild(modal);
}

// Create Context Menu Items
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
        // const serverUrl = "http://104.164.54.196:8001";
        const serverUrl = "http://127.0.0.1:8000";

        if (info.menuItemId === "analyze-link") {
            // Scenario 1: Link Analysis (Send URL to Python)
            handleAnalysis(apiKey, serverUrl, null, info.linkUrl, tab.id);
        } 
        else if (info.menuItemId === "analyze-page") {
            // Scenario 2: Page Analysis (Extract text via Scripting)
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => document.body.innerText
            }, (results) => {
                if (results && results[0]) {
                    handleAnalysis(apiKey, serverUrl, results[0].result, null, tab.id);
                }
            });
        }
    });
});

async function handleAnalysis(apiKey, serverUrl, text, url, tabId) {
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

        // Success - Show result in modal
        await chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ['marked.min.js']
        });
        
        await chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: showModal,
            args: [data.result, false]
        });

    } catch (error) {
        console.error("Analysis Failed:", error);
        
        // Show error in modal
        try {
            await chrome.scripting.executeScript({
                target: { tabId: tabId },
                files: ['marked.min.js']
            });
            
            await chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: showModal,
                args: [error.message, true]
            });
        } catch (uiError) {
            console.error("Failed to show error modal:", uiError);
        }
    }
}
