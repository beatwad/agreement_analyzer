chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'displayResult') {
        const loadingDiv = document.getElementById('loading');
        const contentDiv = document.getElementById('content');

        loadingDiv.style.display = 'none';
        contentDiv.style.display = 'block';

        if (request.error) {
            contentDiv.innerHTML = `
                <div class="error">
                    <h3>Analysis Failed</h3>
                    <p>${escapeHtml(request.data)}</p>
                </div>
            `;
        } else {
            try {
                contentDiv.innerHTML = marked.parse(request.data);
            } catch (e) {
                contentDiv.innerHTML = `<div class="error">Error parsing markdown result: ${e.message}</div>`;
            }
        }
    }
});

function escapeHtml(text) {
    if (typeof text !== 'string') return text;
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
