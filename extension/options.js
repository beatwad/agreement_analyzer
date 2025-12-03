// Default settings
const defaults = {
    language: '',
    geminiKey: '',
    modelProvider: 'Gemini',
    modelName: 'gemini-2.0-flash',
    temperature: 0.4,
    freeTier: true,
    rpmLimit: 15
};

document.getElementById('save').addEventListener('click', () => {
    const language = document.getElementById('language').value;
    const apiKey = document.getElementById('apiKey').value;
    const modelProvider = document.getElementById('modelProvider').value;
    const modelName = document.getElementById('modelName').value;
    const temperature = parseFloat(document.getElementById('temperature').value);
    const freeTier = document.getElementById('freeTier').checked;
    const rpmLimit = parseInt(document.getElementById('rpmLimit').value);

    chrome.storage.sync.set({ 
        language: language,
        geminiKey: apiKey,
        modelProvider: modelProvider,
        modelName: modelName,
        temperature: temperature,
        freeTier: freeTier,
        rpmLimit: rpmLimit
    }, () => {
        document.getElementById('status').innerText = 'Saved!';
        setTimeout(() => document.getElementById('status').innerText = '', 2000);
    });
});

// Restore settings on load
document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.sync.get(defaults, (items) => {
        document.getElementById('language').value = items.language;
        document.getElementById('apiKey').value = items.geminiKey;
        document.getElementById('modelProvider').value = items.modelProvider;
        document.getElementById('modelName').value = items.modelName;
        document.getElementById('temperature').value = items.temperature;
        document.getElementById('freeTier').checked = items.freeTier;
        document.getElementById('rpmLimit').value = items.rpmLimit;
    });
});
