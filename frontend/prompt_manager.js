/**
 * Prompt Manager - Frontend Logic
 */

async function loadSystemPrompts() {
    // Load Dashboard Summary Prompt
    try {
        const summaryPrompt = await fetchAPI('/api/admin/system-prompts/dashboard_summary');
        const defaultText = `You are Certify Health's competitive intelligence analyst. Generate a comprehensive, executive-level strategic summary using the data displayed throughout the pages of the web application.

Your summary MUST include:
1. **Executive Overview** - High-level market position assessment
2. **Threat Analysis** - Breakdown of competitive landscape by threat level (High/Medium/Low)
3. **Pricing Intelligence** - Analysis of competitor pricing strategies and models
4. **Market Trends** - Emerging patterns and shifts
5. **Strategic Recommendations** - 3-5 specific, actionable recommendations
6. **Watch List** - Key competitors requiring immediate attention

Use data-driven insights. Be specific with numbers and competitor names. Format with markdown headers and bullet points.`;

        if (summaryPrompt && summaryPrompt.content) {
            document.getElementById('summaryPromptInput').value = summaryPrompt.content;
        } else {
            document.getElementById('summaryPromptInput').value = defaultText;
        }
    } catch (e) {
        console.error("Failed to load prompt:", e);
        // Fallback if API fails
        document.getElementById('summaryPromptInput').value = "Error loading prompt. Please refresh.";
    }
}

async function saveSystemPrompt(key) {
    const inputId = key === 'dashboard_summary' ? 'summaryPromptInput' : 'chatPersonaInput';
    const content = document.getElementById(inputId).value;

    try {
        const response = await fetchAPI('/api/admin/system-prompts', {
            method: 'POST',
            body: JSON.stringify({
                key: key,
                content: content
            })
        });

        if (response) {
            showToast('Prompt updated successfully', 'success');
            document.getElementById('promptEditorModal').style.display = 'none'; // Close modal

            // If it was the summary prompt, just notify user
            if (key === 'dashboard_summary') {
                console.log("Summary prompt updated.");
            }
        }
    } catch (e) {
        showToast('Error updating prompt: ' + e.message, 'error');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if we are on the settings page or dashboard where this modal might exist
    const btn = document.getElementById('editPromptBtn');
    if (btn) {
        btn.addEventListener('click', () => {
            loadSystemPrompts();
            document.getElementById('promptEditorModal').style.display = 'flex';
        });
    }
});
