document.getElementById('save').addEventListener('click', () => {
    const apiKey = document.getElementById('apiKey').value;
    chrome.storage.sync.set({ geminiKey: apiKey }, () => {
        document.getElementById('status').innerText = 'Saved!';
        setTimeout(() => document.getElementById('status').innerText = '', 2000);
    });
});

// Restore key on load
chrome.storage.sync.get(['geminiKey'], (result) => {
    if (result.geminiKey) {
        document.getElementById('apiKey').value = result.geminiKey;
    }
});