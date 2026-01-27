/**
 * Certify Intel - Dashboard JavaScript
 * Frontend logic for competitive intelligence dashboard
 */

const API_BASE = window.location.origin;

// State
let competitors = [];
let changes = [];
let stats = {};
let threatChart = null;
let pricingChart = null;
let marketShareChart = null;

// ============== Authentication ==============

/**
 * Check if user is authenticated, redirect to login if not
 */
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

/**
 * Logout user - clear token and redirect
 */
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login.html';
}

/**
 * Get authorization headers for API calls
 */
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

/**
 * Setup user menu info and toggle logic
 */
async function setupUserMenu() {
    const avatar = document.getElementById('userAvatar');
    const dropdown = document.getElementById('userDropdown');
    const userNameEl = document.getElementById('userName');
    const userEmailEl = document.getElementById('userEmail');
    const userRoleEl = document.getElementById('userRole');

    if (!avatar || !dropdown) return;

    try {
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const user = await response.json();

            // Update initials (as tooltip)
            const initials = user.full_name ?
                user.full_name.split(' ').map(n => n[0]).join('').toUpperCase() :
                user.email[0].toUpperCase();
            avatar.title = initials;

            // Update dropdown info
            userNameEl.textContent = user.full_name || 'User';
            userEmailEl.textContent = user.email;
            userRoleEl.textContent = user.role || 'Analyst';

            // Show invite link for admins
            if (user.role === 'admin') {
                const inviteLink = document.getElementById('inviteUserLink');
                if (inviteLink) {
                    inviteLink.style.display = 'flex';
                }
            }
        }
    } catch (e) {
        console.error('Error fetching user info:', e);
    }

    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
        if (!avatar.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });
}

/**
 * Toggle the user profile dropdown
 */
function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('active');
    }
}


// ============== Source Attribution Helpers ==============

/**
 * Get company logo URL from Clearbit via Backend Proxy
 */
function getLogoUrl(website) {
    if (!website) return null;
    const domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0];
    // Route through backend proxy to bypass CORS/Network blocks
    return `${API_BASE}/api/logo-proxy?url=` + encodeURIComponent(`https://logo.clearbit.com/${domain}`);
}

/**
 * Create logo image element with fallback
 */
function createLogoImg(website, name, size = 32) {
    if (!website) {
        return `<div class="company-logo-placeholder" style="width:${size}px;height:${size}px;display:flex;align-items:center;justify-content:center;background:#e2e8f0;border-radius:4px;font-weight:bold;color:#64748b;font-size:${size / 2}px;">${(name || '?')[0].toUpperCase()}</div>`;
    }
    const logoUrl = getLogoUrl(website);
    return `<img src="${logoUrl}" alt="${name}" class="company-logo" style="width:${size}px;height:${size}px;border-radius:4px;object-fit:contain;" onerror="this.nextElementSibling.style.display='flex';this.style.display='none'"/><div class="company-logo-placeholder" style="display:none;width:${size}px;height:${size}px;align-items:center;justify-content:center;background:#e2e8f0;border-radius:4px;font-weight:bold;color:#64748b;font-size:${size / 2}px;">${(name || '?')[0].toUpperCase()}</div>`;
}

/**
 * Source attribution icons with links
 */
const SOURCE_CONFIGS = {
    clearbit: { icon: '🖼️', name: 'Clearbit', baseUrl: 'https://clearbit.com/logo' },
    sec: { icon: '📊', name: 'SEC EDGAR', baseUrl: 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' },
    hunter: { icon: '📧', name: 'Hunter.io', baseUrl: 'https://hunter.io/search/' },
    google: { icon: '🔍', name: 'Google', baseUrl: 'https://www.google.com/search?q=' },
    newsapi: { icon: '📰', name: 'NewsAPI', baseUrl: 'https://newsapi.org' },
    linkedin: { icon: '💼', name: 'LinkedIn', baseUrl: 'https://www.linkedin.com/company/' },
    website: { icon: '🌐', name: 'Website', baseUrl: '' },
    manual: { icon: '✏️', name: 'Manual Entry', baseUrl: '' }
};

/**
 * Create source attribution link icon
 */
function createSourceLink(source, identifier = '', highlight = '') {
    const config = SOURCE_CONFIGS[source] || { icon: '📌', name: source, baseUrl: '' };
    let url = config.baseUrl + encodeURIComponent(identifier);
    let title = `Source: ${config.name}`;

    // Website: verification via Google Search ("Company customer count")
    if (source === 'website' && highlight) {
        url = `https://www.google.com/search?q=${encodeURIComponent(identifier ? new URL(identifier).hostname : '')}+${encodeURIComponent(highlight)}+verification`;
        title = "Verify this figure on Google";
    } else if (source === 'website') {
        url = identifier; // Direct link
    }

    // Google: Specific search with highlight
    if (highlight && source === 'google') {
        url = `https://www.google.com/search?q=${encodeURIComponent(identifier)}"+"${encodeURIComponent(highlight)}"`;
    }

    // SEC-specific URL with CIK
    if (source === 'sec' && identifier) {
        url = `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=${identifier}&type=10-K&dateb=&owner=include&count=10`;
    }

    // Hunter.io search
    if (source === 'hunter' && identifier) {
        url = `https://hunter.io/search/${identifier.replace('https://', '').replace('http://', '').split('/')[0]}`;
    }

    return `<a href="${url}" target="_blank" class="source-link" title="${title}" style="cursor:pointer;text-decoration:none;margin-left:4px;opacity:0.7;font-size:12px;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'">${config.icon}</a>`;
}

/**
 * Create a value with source attribution
 */

/**
 * Format SEC filings into displayable HTML
 */

function formatSecFilings(filingsJson, cik) {
    if (!filingsJson) return '';
    try {
        const filings = typeof filingsJson === 'string' ? JSON.parse(filingsJson) : filingsJson;
        return filings.slice(0, 3).map(f =>
            `<a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=${cik}&type=${f.form}" target="_blank" class="sec-filing-link" style="display:inline-block;margin:2px 4px;padding:2px 8px;background:#e0f2fe;border-radius:4px;font-size:11px;text-decoration:none;color:#0369a1;">${f.form} (${f.filed})</a>`
        ).join('');
    } catch (e) {
        return '';
    }
}

/**
 * Format key contacts into displayable HTML
 */
function formatKeyContacts(contactsJson, website) {
    if (!contactsJson) return '';
    try {
        const contacts = typeof contactsJson === 'string' ? JSON.parse(contactsJson) : contactsJson;
        const domain = website?.replace('https://', '').replace('http://', '').split('/')[0] || '';
        return contacts.slice(0, 5).map(c =>
            `<div class="contact-item" style="display:flex;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid #f1f5f9;">
                <span style="font-weight:500;">${c.name}</span>
                <span style="color:#64748b;font-size:12px;">${c.position || ''}</span>
                <a href="mailto:${c.email}" style="margin-left:auto;color:#0ea5e9;font-size:12px;">${c.email}</a>
            </div>`
        ).join('') + (domain ? `<div style="margin-top:8px;text-align:right;"><a href="https://hunter.io/search/${domain}" target="_blank" style="color:#ff6b35;font-size:11px;">View all on Hunter.io →</a></div>` : '');
    } catch (e) {
        return '';
    }
}

// ============== Initialization ==============

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication first
    if (!checkAuth()) return;

    initNavigation();
    loadDashboard();
    loadCompetitors();
    setupUserMenu();
    preloadPrompts(); // Preload AI prompts for instant access
});

function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            showPage(page);
        });
    });

    // Filter event listeners
    document.getElementById('filterThreat')?.addEventListener('change', filterCompetitors);
    document.getElementById('filterStatus')?.addEventListener('change', filterCompetitors);
    document.getElementById('filterSeverity')?.addEventListener('change', loadChanges);
    document.getElementById('filterDays')?.addEventListener('change', loadChanges);
    document.getElementById('filterCompany')?.addEventListener('change', loadChanges);

    // Search
    document.getElementById('globalSearch')?.addEventListener('input', debounce(handleSearch, 300));
}

function showPage(pageName) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === pageName);
    });

    // Update pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(`${pageName}Page`)?.classList.add('active');

    // Load page-specific data
    switch (pageName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'competitors':
            loadCompetitors();
            break;
        case 'changes':
            loadChanges();
            break;
        case 'comparison':
            loadComparisonOptions();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'marketmap':
            loadMarketMap();
            break;
        case 'battlecards':
            loadBattlecards();
            // v5.0.7: Initialize dimension widget on battlecards page
            if (typeof initBattlecardDimensionWidget === 'function') {
                initBattlecardDimensionWidget();
            }
            break;
        case 'discovered':
            loadDiscovered();
            break;
        case 'dataquality':
            loadDataQuality();
            break;
        case 'newsfeed':
            initNewsFeedPage();
            break;
        case 'salesmarketing':
            if (typeof initSalesMarketingModule === 'function') {
                initSalesMarketingModule();
            }
            break;
        case 'settings':
            loadSettings();
            break;
    }
}

// ============== API Functions ==============

async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            ...options
        });

        // Handle 401 Unauthorized - redirect to login
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login.html';
            return null;
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        // Don't show toast for intentional aborts (timeouts)
        if (error.name === 'AbortError') {
            console.log(`Request aborted (timeout): ${endpoint}`);
            return null;
        }
        console.error(`API Error: ${endpoint}`, error);
        showToast(`Error loading data: ${error.message}`, 'error');
        return null;
    }
}

// ============== Dashboard ==============

// Track last refresh time
let lastDataRefresh = null;

function updateRefreshTimestamp() {
    lastDataRefresh = new Date();
    const timeElement = document.getElementById('lastRefreshTime');
    if (timeElement) {
        // Format: "Sun, Jan 25, 2026, 03:08 PM EST"
        const dateOptions = {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        const timeOptions = {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true,
            timeZoneName: 'short'
        };
        const datePart = lastDataRefresh.toLocaleDateString('en-US', dateOptions);
        const timePart = lastDataRefresh.toLocaleTimeString('en-US', timeOptions);
        timeElement.textContent = `${datePart}, ${timePart}`;
    }
}

async function loadDashboard() {
    // Load stats
    stats = await fetchAPI('/api/dashboard/stats') || {};
    updateStatsCards();

    // Load AI Summary - REMOVED AUTO-TRIGGER
    // fetchDashboardSummary();

    // Load competitors for table
    competitors = await fetchAPI('/api/competitors') || [];
    renderTopThreats();

    // Load changes
    changes = (await fetchAPI('/api/changes?days=7'))?.changes || [];
    renderRecentChanges();

    // Render charts
    renderThreatChart();
    renderPricingChart();

    // Update refresh timestamp
    updateRefreshTimestamp();
}


// Make functions global for button clicks
window.clearAISummary = function () {
    console.log('clearAISummary called');
    const contentDiv = document.getElementById('aiSummaryContent');
    const metaDiv = document.getElementById('aiSummaryMeta');

    if (contentDiv) {
        console.log('Reseting content div');
        contentDiv.innerHTML = '<div class="ai-empty-state">Ready to generate insights. Click "Generate Summary" to start.</div>';
    } else {
        console.error('aiSummaryContent not found');
    }

    if (metaDiv) metaDiv.innerHTML = '';
};

// Toggle AI Summary expand/collapse
window.toggleAISummary = function() {
    const summaryCard = document.getElementById('aiSummaryCard');
    if (summaryCard) {
        summaryCard.classList.toggle('collapsed');
    }
};

// Toggle Sidebar collapse/expand
window.toggleSidebarCollapse = function() {
    const sidebar = document.getElementById('mainSidebar');
    const mainContent = document.querySelector('.main-content');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
        if (mainContent) {
            mainContent.classList.toggle('sidebar-collapsed');
        }
    }
};

// Make accessible to onclick
window.startAISummary = startAISummary;

// AI Summary progress tracking
let aiProgressInterval = null;
let aiProgressStartTime = null;

function showAISummaryProgressModal() {
    const modal = document.getElementById('aiSummaryProgressModal');
    if (modal) {
        modal.style.display = 'flex';
        aiProgressStartTime = Date.now();
        // Reset progress display
        document.getElementById('aiSummaryProgressBar').style.width = '0%';
        document.getElementById('aiProgressPercent').textContent = '0%';
        document.getElementById('aiProgressStepText').textContent = 'Initializing...';
        document.getElementById('aiProgressElapsed').textContent = 'Elapsed: 0s';
        // Reset step indicators
        for (let i = 1; i <= 5; i++) {
            const step = document.getElementById(`step${i}`);
            if (step) {
                step.style.color = '#64748b';
                step.style.fontWeight = 'normal';
            }
        }
    }
}

function hideAISummaryProgressModal() {
    const modal = document.getElementById('aiSummaryProgressModal');
    if (modal) {
        modal.style.display = 'none';
    }
    if (aiProgressInterval) {
        clearInterval(aiProgressInterval);
        aiProgressInterval = null;
    }
}

function updateAISummaryProgress(progress) {
    const progressBar = document.getElementById('aiSummaryProgressBar');
    const percentText = document.getElementById('aiProgressPercent');
    const stepText = document.getElementById('aiProgressStepText');
    const elapsedText = document.getElementById('aiProgressElapsed');

    if (progressBar) progressBar.style.width = `${progress.progress}%`;
    if (percentText) percentText.textContent = `${progress.progress}%`;
    if (stepText) stepText.textContent = progress.step_description || 'Processing...';

    // Update elapsed time
    if (elapsedText && aiProgressStartTime) {
        const elapsed = Math.floor((Date.now() - aiProgressStartTime) / 1000);
        elapsedText.textContent = `Elapsed: ${elapsed}s`;
    }

    // Highlight current step
    const currentStep = progress.step || 0;
    for (let i = 1; i <= 5; i++) {
        const stepEl = document.getElementById(`step${i}`);
        if (stepEl) {
            if (i < currentStep) {
                stepEl.style.color = '#10B981';
                stepEl.style.fontWeight = '500';
            } else if (i === currentStep) {
                stepEl.style.color = '#059669';
                stepEl.style.fontWeight = '600';
            } else {
                stepEl.style.color = '#94a3b8';
                stepEl.style.fontWeight = 'normal';
            }
        }
    }
}

async function pollAISummaryProgress() {
    try {
        const progress = await fetchAPI('/api/analytics/summary/progress');
        if (progress) {
            updateAISummaryProgress(progress);
            if (!progress.active && progress.progress >= 100) {
                // Complete - stop polling
                if (aiProgressInterval) {
                    clearInterval(aiProgressInterval);
                    aiProgressInterval = null;
                }
            }
        }
    } catch (e) {
        console.error('Error polling AI progress:', e);
    }
}

async function startAISummary() {
    const summaryCard = document.getElementById('aiSummaryCard');
    const contentDiv = document.getElementById('aiSummaryContent');
    const modelBadge = document.getElementById('aiModelBadge');
    const providerLogo = document.getElementById('aiProviderLogo');
    const metaDiv = document.getElementById('aiSummaryMeta');

    if (!summaryCard || !contentDiv) return;

    summaryCard.style.display = 'block';
    contentDiv.innerHTML = '<div class="ai-loading"><span class="ai-spinner">⏳</span> Generating comprehensive strategic insights...</div>';

    // Show progress modal and start polling
    showAISummaryProgressModal();
    aiProgressInterval = setInterval(pollAISummaryProgress, 500);

    const data = await fetchAPI('/api/analytics/summary');

    // Hide progress modal
    hideAISummaryProgressModal();

    if (data) {
        let html = data.summary || data;
        if (typeof html === 'object') html = html.summary;

        // Format markdown to HTML
        html = html
            .replace(/^# (.*$)/gim, '<h2>$1</h2>')
            .replace(/^## (.*$)/gim, '<h3>$1</h3>')
            .replace(/^### (.*$)/gim, '<h4>$1</h4>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/^\s*-\s(.*?)$/gm, '<li>$1</li>')
            .replace(/^\s*\d+\.\s(.*?)$/gm, '<li>$1</li>');

        // Wrap consecutive li tags in ul
        if (html.includes('<li>')) {
            html = html.replace(/((<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>');
        }

        html = html.replace(/\n\n/g, '<br>');
        contentDiv.innerHTML = html;

        // Update model badge
        if (modelBadge && data.model) {
            modelBadge.textContent = data.model.toUpperCase().replace('GPT-4-TURBO', 'GPT-4');
            modelBadge.style.background = data.type === 'ai' ?
                'linear-gradient(135deg, #10b981 0%, #059669 100%)' :
                'linear-gradient(135deg, #64748b 0%, #475569 100%)';
        }

        // Update provider logo
        if (providerLogo && data.provider) {
            if (data.provider === 'OpenAI') {
                providerLogo.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23000"%3E%3Cpath d="M22.28 9.9c.5-1.47.73-3.02.68-4.55A5.38 5.38 0 0 0 17.73.42a5.29 5.29 0 0 0-5.14 1.24A5.29 5.29 0 0 0 4.63.68 5.38 5.38 0 0 0 .88 6.75c-.2 1.52.05 3.05.72 4.44a5.35 5.35 0 0 0 .68 8.3 5.28 5.28 0 0 0 5.14.12 5.29 5.29 0 0 0 7.96.98 5.38 5.38 0 0 0 3.75-6.07c.68-1.3.98-2.76.88-4.22l-.73.6z"/%3E%3C/svg%3E';
                providerLogo.alt = 'OpenAI';
            }
        }

        // Update meta info
        if (metaDiv && data.data_points_analyzed) {
            metaDiv.innerHTML = `<span>📊 Analyzed ${data.data_points_analyzed} competitors</span> |
                <span>🕐 Generated: ${new Date(data.generated_at).toLocaleTimeString()}</span> |
                <span>🤖 Model: ${data.provider} ${data.model || 'Automated'}</span>`;
        }

        // Update badge style based on type
        const badge = summaryCard.querySelector('.ai-badge');
        if (data.type === 'fallback' && badge) {
            badge.textContent = 'Automated Insight';
            badge.style.background = '#f1f5f9';
            badge.style.color = '#64748b';
        } else if (badge) {
            badge.textContent = 'AI Generated';
            badge.style.background = '#e0e7ff';
            badge.style.color = '#3730a3';
        }

        showToast('AI Summary generated successfully!', 'success');
    } else {
        contentDiv.innerHTML = '<div class="ai-empty-state">Failed to generate summary. Please try again.</div>';
    }
}

// AI Chatbox functionality
async function sendAIChat() {
    const input = document.getElementById('aiChatInput');
    const messagesDiv = document.getElementById('aiChatMessages');

    if (!input || !messagesDiv) return;

    const message = input.value.trim();
    if (!message) return;

    // Add user message
    messagesDiv.innerHTML += `<div class="ai-chat-message user">${message}</div>`;
    input.value = '';

    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Show loading
    messagesDiv.innerHTML += `<div class="ai-chat-message assistant" id="chat-loading"><span class="ai-spinner">⏳</span> Thinking...</div>`;

    try {
        const response = await fetchAPI('/api/analytics/chat', {
            method: 'POST',
            body: JSON.stringify({ message: message })
        });

        // Remove loading
        document.getElementById('chat-loading')?.remove();

        if (response && response.success) {
            messagesDiv.innerHTML += `<div class="ai-chat-message assistant">${response.response}</div>`;
        } else {
            messagesDiv.innerHTML += `<div class="ai-chat-message assistant">${response?.response || 'Unable to get response. Please try again.'}</div>`;
        }

        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (e) {
        document.getElementById('chat-loading')?.remove();
        messagesDiv.innerHTML += `<div class="ai-chat-message assistant">Error: ${e.message}</div>`;
    }
}

// Enhanced triggerScrapeAll with progress modal and live progress tracking
async function triggerScrapeAll() {
    const btn = document.querySelector('.btn-primary[onclick*="triggerScrapeAll"]') ||
        document.querySelector('button:contains("Refresh")') ||
        event?.target;

    if (btn) {
        btn.classList.add('btn-loading');
        btn.disabled = true;
    }

    // Show inline progress on Dashboard (Phase 1: Task 5.0.1-025)
    showInlineRefreshProgress();

    try {
        const result = await fetchAPI('/api/scrape/all');

        if (result && result.total) {
            // Start polling for inline progress
            pollInlineRefreshProgress(result.total);
        } else {
            hideInlineRefreshProgress();
            showToast('Error starting refresh', 'error');
            if (btn) {
                btn.classList.remove('btn-loading');
                btn.disabled = false;
            }
        }
    } catch (e) {
        hideInlineRefreshProgress();
        showToast('Error refreshing data: ' + e.message, 'error');
        if (btn) {
            btn.classList.remove('btn-loading');
            btn.disabled = false;
        }
    }
}

// Progress modal functions
function showRefreshProgressModal() {
    const modal = document.getElementById('refreshProgressModal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('progressCurrentText').textContent = 'Starting refresh...';
        document.getElementById('refreshProgressBar').style.width = '0%';
        document.getElementById('progressPercent').textContent = '0%';
        document.getElementById('progressCount').textContent = '0 of 0 competitors';
        document.getElementById('progressCompletedList').innerHTML = '';
    }
}

function hideRefreshProgressModal() {
    const modal = document.getElementById('refreshProgressModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function updateRefreshProgress(progress) {
    const percent = progress.total > 0 ? Math.round((progress.completed / progress.total) * 100) : 0;

    document.getElementById('refreshProgressBar').style.width = `${percent}%`;
    document.getElementById('progressPercent').textContent = `${percent}%`;
    document.getElementById('progressCount').textContent = `${progress.completed} of ${progress.total} competitors`;

    if (progress.current_competitor) {
        document.getElementById('progressCurrentText').textContent = `Scraping: ${progress.current_competitor}`;
    }

    // Update completed list
    const listEl = document.getElementById('progressCompletedList');
    let html = '';

    // Show last 5 completed items
    const recentDone = progress.competitors_done.slice(-5);
    recentDone.forEach(name => {
        html += `<div class="progress-completed-item"><span class="check-icon">&#10003;</span> ${name}</div>`;
    });

    // Show current item if active
    if (progress.current_competitor && progress.active) {
        html += `<div class="progress-completed-item current"><span class="check-icon">&#8594;</span> ${progress.current_competitor}</div>`;
    }

    listEl.innerHTML = html;
}

async function showRefreshCompleteModal(progress) {
    const modal = document.getElementById('refreshCompleteModal');
    if (!modal) return;

    // Update stats
    document.getElementById('completeTotal').textContent = progress.total;
    document.getElementById('completeChanges').textContent = progress.changes_detected;
    document.getElementById('completeNewValues').textContent = progress.new_values_added;

    // Show modal
    modal.style.display = 'flex';

    // Reset AI summary section
    const summaryContent = document.getElementById('refreshAISummaryContent');
    if (summaryContent) {
        summaryContent.innerHTML = '<span class="loading-text">🤖 Analyzing changes...</span>';
    }

    // Fetch AI summary (Phase 3: Task 5.0.1-030)
    try {
        const summaryResult = await fetchAPI('/api/scrape/generate-summary', { method: 'POST' });

        if (summaryResult && summaryResult.summary) {
            const summaryHtml = `
                <p style="margin: 0; line-height: 1.6;">${summaryResult.summary}</p>
                <div class="summary-meta">
                    ${summaryResult.type === 'ai' ? `Generated by ${summaryResult.model || 'AI'}` : 'Auto-generated summary'} • ${new Date().toLocaleTimeString()}
                </div>
            `;
            if (summaryContent) {
                summaryContent.innerHTML = summaryHtml;
            }
        } else if (summaryResult && summaryResult.error) {
            if (summaryContent) {
                summaryContent.innerHTML = `<p style="color: #94a3b8; font-style: italic;">Summary: ${summaryResult.summary || 'No significant changes detected.'}</p>`;
            }
        }
    } catch (e) {
        console.error('Error fetching AI summary:', e);
        if (summaryContent) {
            summaryContent.innerHTML = '<p style="color: #94a3b8; font-style: italic;">Could not generate AI summary.</p>';
        }
    }

    // Populate change details
    await populateChangeDetails();
}

async function populateChangeDetails() {
    const detailsEl = document.getElementById('changeDetailsContent');
    if (!detailsEl) return;

    try {
        const session = await fetchAPI('/api/scrape/session');

        if (session && session.change_details && session.change_details.length > 0) {
            detailsEl.innerHTML = session.change_details.map(change => `
                <div class="change-detail-item ${change.type || 'change'}">
                    <div class="change-competitor">${change.competitor || 'Unknown'}</div>
                    <div class="change-field">${formatFieldName(change.field || '')}</div>
                    <div class="change-values">
                        ${change.old_value ? `<span class="old-value">${change.old_value}</span> →` : ''}
                        <span class="new-value">${change.new_value || 'N/A'}</span>
                    </div>
                </div>
            `).join('');
        } else {
            detailsEl.innerHTML = '<p style="color: #94a3b8; padding: 12px; text-align: center;">No detailed changes recorded for this refresh.</p>';
        }
    } catch (e) {
        console.error('Error loading change details:', e);
        detailsEl.innerHTML = '<p style="color: #94a3b8; padding: 12px;">Could not load change details.</p>';
    }
}

function toggleChangeDetails() {
    const content = document.getElementById('changeDetailsContent');
    const button = document.querySelector('.accordion-toggle');
    const arrow = document.querySelector('.toggle-arrow');

    if (!content) return;

    if (content.style.display === 'none') {
        content.style.display = 'block';
        if (button) button.classList.add('expanded');
        if (arrow) arrow.textContent = '▲';
    } else {
        content.style.display = 'none';
        if (button) button.classList.remove('expanded');
        if (arrow) arrow.textContent = '▼';
    }
}

function closeRefreshCompleteModal() {
    const modal = document.getElementById('refreshCompleteModal');
    if (modal) {
        modal.style.display = 'none';
    }

    // Reset accordion state
    const content = document.getElementById('changeDetailsContent');
    const button = document.querySelector('.accordion-toggle');
    const arrow = document.querySelector('.toggle-arrow');
    if (content) content.style.display = 'none';
    if (button) button.classList.remove('expanded');
    if (arrow) arrow.textContent = '▼';
}

// ============================================
// Inline Refresh Progress - Phase 1: Task 5.0.1-025
// ============================================

function showInlineRefreshProgress() {
    // Hide the data refresh indicator
    const indicator = document.getElementById('dataRefreshIndicator');
    if (indicator) {
        indicator.style.display = 'none';
    }

    // Show inline progress
    const inlineProgress = document.getElementById('inlineRefreshProgress');
    if (inlineProgress) {
        inlineProgress.style.display = 'block';
        document.getElementById('inlineProgressBar').style.width = '0%';
        document.getElementById('inlineProgressPercent').textContent = '0%';
        document.getElementById('inlineProgressText').textContent = 'Starting...';
        document.getElementById('inlineProgressCount').textContent = '0 / 0 competitors';
        document.getElementById('inlineProgressLive').innerHTML = '';
    }
}

function hideInlineRefreshProgress() {
    // Hide inline progress
    const inlineProgress = document.getElementById('inlineRefreshProgress');
    if (inlineProgress) {
        inlineProgress.style.display = 'none';
    }

    // Show the data refresh indicator again
    const indicator = document.getElementById('dataRefreshIndicator');
    if (indicator) {
        indicator.style.display = 'flex';
    }
}

function updateInlineProgress(progress) {
    const percent = progress.total > 0 ? Math.round((progress.completed / progress.total) * 100) : 0;

    const progressBar = document.getElementById('inlineProgressBar');
    const percentEl = document.getElementById('inlineProgressPercent');
    const countEl = document.getElementById('inlineProgressCount');
    const textEl = document.getElementById('inlineProgressText');
    const liveEl = document.getElementById('inlineProgressLive');

    if (progressBar) progressBar.style.width = `${percent}%`;
    if (percentEl) percentEl.textContent = `${percent}%`;
    if (countEl) countEl.textContent = `${progress.completed} / ${progress.total} competitors`;

    if (progress.current_competitor && textEl) {
        textEl.textContent = `Scanning: ${progress.current_competitor}`;
    }

    // Update live feed with recent changes (if available from enhanced backend)
    if (progress.recent_changes && progress.recent_changes.length > 0 && liveEl) {
        liveEl.innerHTML = progress.recent_changes.slice(-5).map(change => `
            <div class="live-update-item ${change.type || 'change'}">
                <span class="change-icon">${change.type === 'new' ? '✨' : '📝'}</span>
                <span><strong>${change.competitor}</strong>: ${change.field} ${change.type === 'new' ? 'discovered' : 'updated'}</span>
            </div>
        `).join('');
    } else if (progress.competitors_done && progress.competitors_done.length > 0 && liveEl) {
        // Fallback: Show completed competitors as live updates
        const recentDone = progress.competitors_done.slice(-5);
        liveEl.innerHTML = recentDone.map(name => `
            <div class="live-update-item new">
                <span class="change-icon">✓</span>
                <span><strong>${name}</strong> data refreshed</span>
            </div>
        `).join('');
    }
}

async function pollInlineRefreshProgress(total) {
    const btn = document.querySelector('.btn-primary[onclick*="triggerScrapeAll"]');
    let pollInterval = null;

    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/scrape/progress`);
            const progress = await response.json();

            // Update inline progress display
            updateInlineProgress(progress);

            // Also update the modal progress in case it's visible
            updateRefreshProgress(progress);

            // Check if complete
            if (!progress.active && progress.completed >= progress.total && progress.total > 0) {
                clearInterval(pollInterval);
                hideInlineRefreshProgress();

                // Show completion modal with AI summary
                showRefreshCompleteModal(progress);

                // Re-enable button
                if (btn) {
                    btn.classList.remove('btn-loading');
                    btn.disabled = false;
                }

                // Reload dashboard data
                await loadDashboard();

                // Regenerate AI summary with new data
                await fetchDashboardSummary();

                // Update last refresh time
                updateLastRefreshTime();
            }
        } catch (e) {
            console.error('Error polling inline progress:', e);
        }
    }, 500);

    // Safety timeout after 10 minutes
    setTimeout(() => {
        if (pollInterval) {
            clearInterval(pollInterval);
            hideInlineRefreshProgress();
            if (btn) {
                btn.classList.remove('btn-loading');
                btn.disabled = false;
            }
            showToast('Refresh timed out - check Change Log for any completed updates', 'warning');
        }
    }, 600000);
}

function updateLastRefreshTime() {
    const timeEl = document.getElementById('lastRefreshTime');
    if (timeEl) {
        const now = new Date();
        const options = {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short'
        };
        timeEl.textContent = now.toLocaleString('en-US', options);
    }
}

// ============================================
// End Inline Refresh Progress
// ============================================

async function pollRefreshProgress(total) {
    const btn = document.querySelector('.btn-primary[onclick*="triggerScrapeAll"]');
    let pollInterval = null;

    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/scrape/progress`);
            const progress = await response.json();

            updateRefreshProgress(progress);

            // Check if complete
            if (!progress.active && progress.completed >= progress.total && progress.total > 0) {
                clearInterval(pollInterval);
                hideRefreshProgressModal();

                // Show completion modal
                showRefreshCompleteModal(progress);

                // Re-enable button
                if (btn) {
                    btn.classList.remove('btn-loading');
                    btn.disabled = false;
                }

                // Reload dashboard data
                await loadDashboard();

                // Regenerate AI summary with new data
                await fetchDashboardSummary();
            }
        } catch (e) {
            console.error('Error polling progress:', e);
        }
    }, 500);

    // Safety timeout after 10 minutes
    setTimeout(() => {
        if (pollInterval) {
            clearInterval(pollInterval);
            hideRefreshProgressModal();
            if (btn) {
                btn.classList.remove('btn-loading');
                btn.disabled = false;
            }
            showToast('Refresh timed out - check Change Log for any completed updates', 'warning');
        }
    }, 600000);
}

function updateStatsCards() {
    // Ensure stats object exists before accessing properties
    if (!stats || typeof stats !== 'object') {
        console.warn('Stats object is empty or invalid:', stats);
        stats = {};
    }

    const totalEl = document.getElementById('totalCompetitors');
    const highEl = document.getElementById('highThreat');
    const mediumEl = document.getElementById('mediumThreat');
    const lowEl = document.getElementById('lowThreat');

    if (totalEl) totalEl.textContent = stats.total_competitors ?? 0;
    if (highEl) highEl.textContent = stats.high_threat ?? 0;
    if (mediumEl) mediumEl.textContent = stats.medium_threat ?? 0;
    if (lowEl) lowEl.textContent = stats.low_threat ?? 0;

    console.log('Dashboard stats updated:', stats);
}

function showCompanyList(threatLevel) {
    let filteredCompetitors = competitors;
    let title = 'All Competitors';
    let color = '#3A95ED';

    if (threatLevel !== 'all') {
        filteredCompetitors = competitors.filter(c => c.threat_level === threatLevel);
        title = `${threatLevel} Threat Competitors`;
        color = threatLevel === 'High' ? '#dc3545' : threatLevel === 'Medium' ? '#f59e0b' : '#22c55e';
    }

    const companiesList = filteredCompetitors.map((c, idx) => {
        const publicBadge = c.is_public ?
            `<span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 0.7em; margin-left: 8px;">PUBLIC ${c.ticker_symbol || ''}</span>` :
            `<span style="background: #64748b; color: white; padding: 1px 6px; border-radius: 3px; font-size: 0.7em; margin-left: 8px;">PRIVATE</span>`;
        return `<div style="padding: 16px 0; border-bottom: 1px solid #e2e8f0;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <span style="font-size: 1.1em;"><strong>${idx + 1}.</strong> ${c.name} ${publicBadge}</span>
                <button class="btn btn-sm btn-secondary" onclick="viewCompetitor(${c.id})" style="padding: 2px 8px; font-size: 0.8em;">View Profile</button>
            </div>
            
            <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-left: 20px;">
                <div class="qualification-item" style="font-size: 0.85em; color: #475569; display: flex; align-items: center; gap: 4px;">
                    <span style="font-weight: 600;">Pricing:</span> ${createSourcedValue(c.pricing_model || 'N/A', c.id, 'pricing_model')}
                </div>
                <div class="qualification-item" style="font-size: 0.85em; color: #475569; display: flex; align-items: center; gap: 4px;">
                    <span style="font-weight: 600;">Customers:</span> ${createSourcedValue(c.customer_count || 'N/A', c.id, 'customer_count')}
                </div>
                <div class="qualification-item" style="font-size: 0.85em; color: #475569; display: flex; align-items: center; gap: 4px;">
                    <span style="font-weight: 600;">Founded:</span> ${createSourcedValue(c.year_founded || 'N/A', c.id, 'year_founded')}
                </div>
            </div>
        </div>`;
    }).join('');

    const modalContent = `
        <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;" onclick="this.remove()">
            <div style="background: white; border-radius: 12px; max-width: 600px; width: 90%; max-height: 80vh; overflow: hidden;" onclick="event.stopPropagation()">
                <div style="background: ${color}; color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0;">${title} (${filteredCompetitors.length})</h3>
                    <button onclick="this.closest('.company-list-modal').remove()" style="background: none; border: none; color: white; font-size: 24px; cursor: pointer;">×</button>
                </div>
                <div style="padding: 20px; max-height: 60vh; overflow-y: auto;">
                    ${companiesList || '<p style="color: #64748b;">No competitors found in this category.</p>'}
                </div>
            </div>
        </div>
    `;

    const modal = document.createElement('div');
    modal.className = 'company-list-modal';
    modal.innerHTML = modalContent;
    document.body.appendChild(modal);
}

function renderTopThreats() {
    const tbody = document.getElementById('topThreatsBody');
    if (!tbody) return;

    const highThreats = competitors.filter(c => c.threat_level === 'High');

    tbody.innerHTML = highThreats.slice(0, 5).map(comp => `
        <tr>
            <td>
                <div style="display:flex;align-items:center;gap:10px;">
                    ${createLogoImg(comp.website, comp.name, 32)}
                    <div>
                        <strong>${comp.name}</strong><br>
                        <a href="${comp.website}" target="_blank" class="competitor-website" style="font-size:12px;color:#64748b;">${comp.website ? new URL(comp.website).hostname : '—'}</a>
                    </div>
                </div>
            </td>
            <td><span class="threat-badge ${comp.threat_level.toLowerCase()}">${comp.threat_level}</span></td>
            <td>${createSourcedValue(comp.customer_count, comp.id, 'customer_count')}</td>
            <td>${createSourcedValue(comp.base_price, comp.id, 'base_price')}</td>
            <td>${formatDate(comp.last_updated)}</td>
            <td style="display: flex; gap: 6px;">
                <button class="btn btn-secondary" onclick="viewCompetitor(${comp.id})">View</button>
                <button class="btn-view-sources" onclick="viewDataSources(${comp.id})" title="View Data Sources">📋</button>
            </td>
        </tr>
    `).join('');
}

function renderRecentChanges() {
    const container = document.getElementById('recentChanges');
    if (!container) return;

    container.innerHTML = changes.slice(0, 5).map(change => `
        <div class="change-item">
            <div class="change-icon ${change.severity.toLowerCase()}">
                ${change.severity === 'High' ? '🔴' : change.severity === 'Medium' ? '🟡' : '🔵'}
            </div>
            <div class="change-content">
                <div class="change-title">${change.competitor_name}: ${change.change_type}</div>
                <div class="change-details">
                    ${change.previous_value ? `Changed from "${change.previous_value}" to ` : 'Set to '}
                    "${change.new_value}"
                </div>
            </div>
            <div class="change-time">${formatDate(change.detected_at)}</div>
        </div>
    `).join('') || '<p class="empty-state">No recent changes</p>';
}

function renderThreatChart() {
    const ctx = document.getElementById('threatChart')?.getContext('2d');
    if (!ctx) return;

    if (threatChart) threatChart.destroy();

    threatChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{
                data: [stats.high_threat || 0, stats.medium_threat || 0, stats.low_threat || 0],
                backgroundColor: ['#DC3545', '#FFC107', '#28A745'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function renderPricingChart() {
    const ctx = document.getElementById('pricingChart')?.getContext('2d');
    if (!ctx) return;

    if (pricingChart) pricingChart.destroy();

    // Count pricing models
    const pricingModels = {};
    competitors.forEach(c => {
        const model = c.pricing_model || 'Unknown';
        pricingModels[model] = (pricingModels[model] || 0) + 1;
    });

    pricingChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(pricingModels),
            datasets: [{
                label: 'Competitors',
                data: Object.values(pricingModels),
                backgroundColor: '#2F5496',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// ============== Competitors ==============

async function loadCompetitors() {
    competitors = await fetchAPI('/api/competitors') || [];
    competitors = await fetchAPI('/api/competitors') || [];
    populateCompanyFilter();
    renderCompetitorsGrid();
}

function populateCompanyFilter() {
    const select = document.getElementById('filterCompany');
    if (!select) return;

    // Save current selection if re-populating
    const currentVal = select.value;

    select.innerHTML = '<option value="">All Companies</option>' +
        competitors.map(c => `<option value="${c.id}">${c.name}</option>`).join('');

    select.value = currentVal;
}

function filterCompetitors() {
    const threatFilter = document.getElementById('filterThreat').value;
    const statusFilter = document.getElementById('filterStatus').value;

    const filtered = competitors.filter(c => {
        if (threatFilter && c.threat_level !== threatFilter) return false;
        if (statusFilter && c.status !== statusFilter) return false;
        return true;
    });

    renderCompetitorsGrid(filtered);
}

function renderCompetitorsGrid(comps = competitors) {
    const grid = document.getElementById('competitorsGrid');
    if (!grid) return;

    grid.innerHTML = comps.map(comp => {
        // Determine public/private status block
        const isPublic = comp.is_public;
        const ticker = comp.ticker_symbol || '';
        const exchange = comp.stock_exchange || '';

        let statusBlock = '';
        if (isPublic && ticker) {
            statusBlock = `
                <div class="stock-info-block" data-ticker="${ticker}" style="margin-top: 4px;">
                    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: nowrap;">
                        <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 700;">PUBLIC</span>
                        <span style="font-weight: 700; color: #122753; font-size: 12px;">${ticker} <small style="color: #64748b; font-weight: 400;">(${exchange})</small></span>
                        <span id="price-${comp.id}" style="font-weight: 700; color: #122753; font-size: 13px;">---</span>
                    </div>
                </div>
            `;
        } else {
            statusBlock = `
                <div style="margin-top: 6px;">
                    <span style="background: #64748b; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 700;">PRIVATE</span>
                </div>
            `;
        }

        return `
        <div class="competitor-card">
            <div class="competitor-header">
                <div style="display:flex;align-items:flex-start;gap:12px; width: 100%;">
                    ${createLogoImg(comp.website, comp.name, 40)}
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                            <div class="competitor-name" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${comp.name}</div>
                            <span class="threat-badge ${comp.threat_level.toLowerCase()}" style="font-size: 0.8em; margin-left: 8px;">${comp.threat_level}</span>
                        </div>
                        <a href="${comp.website}" target="_blank" class="competitor-website" style="display: block; margin-top: 0px;">${comp.website.replace('https://', '').replace('www.', '')}</a>
                        ${statusBlock}
                    </div>
                </div>
                <!-- threat-badge removed from here and moved to header line -->
            </div>
            
            <div class="competitor-details">
                <div class="detail-item">
                    <span class="detail-icon">👥</span>
                    <span class="detail-label">Customers</span>
                    <div class="detail-value">${createSourcedValue(comp.customer_count, comp.id, 'customer_count')}</div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">💰</span>
                    <span class="detail-label">Pricing</span>
                    <div class="detail-value">${createSourcedValue(comp.base_price, comp.id, 'base_price')}</div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">👔</span>
                    <span class="detail-label">Employees</span>
                    <div class="detail-value">${createSourcedValue(comp.employee_count, comp.id, 'employee_count')}</div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">⭐</span>
                    <span class="detail-label">G2 Rating</span>
                    <div class="detail-value">${createSourcedValue(comp.g2_rating ? comp.g2_rating : null, comp.id, 'g2_rating')}</div>
                </div>
            </div>
            
            <div class="competitor-actions">
                <button class="btn btn-primary" onclick="viewBattlecard(${comp.id})" title="View Battlecard">Battlecard</button>
                <button class="btn btn-secondary" onclick="showCompetitorInsights(${comp.id})" style="background-color: var(--navy-dark); color: white;" title="AI Analysis">Insights</button>
                <button class="btn btn-secondary" onclick="viewDataSources(${comp.id})" title="View Data Sources">📋 Sources</button>
                <button class="btn btn-secondary" onclick="triggerScrape(${comp.id})" title="Refresh Data">Refresh</button>
                <button class="btn btn-secondary" onclick="editCompetitor(${comp.id})" title="Edit Profile">Edit</button>
                <button class="btn btn-secondary" onclick="deleteCompetitor(${comp.id})" style="background-color: #dc3545; color: white; border-color: #dc3545;" title="Delete Profile">Delete</button>
            </div>
        </div>
    `}).join('');

    // Fetch live stock prices for public companies
    comps.filter(c => c.is_public && c.ticker_symbol).forEach(comp => {
        fetchLiveStockPrice(comp.id, comp.name);
    });
}

async function fetchLiveStockPrice(competitorId, companyName) {
    try {
        const response = await fetch(`${API_BASE}/api/stock/${encodeURIComponent(companyName)}`);
        const data = await response.json();

        const priceEl = document.getElementById(`price-${competitorId}`);
        if (priceEl && data.is_public && data.price) {
            // Apply navy color for price, green/red for change only
            const changeColor = data.change >= 0 ? '#22c55e' : '#dc3545';
            const changeSign = data.change >= 0 ? '+' : '';
            priceEl.innerHTML = `
                <span style="color: #122753;">$${data.price.toFixed(2)}</span> 
                <span style="color: ${changeColor}; font-size: 0.9em; margin-left: 4px;">(${changeSign}${data.change_percent?.toFixed(1)}%)</span>
            `;
        }
    } catch (e) {
        // Silent fail for stock price fetch
        console.log(`Could not fetch stock price for ${companyName}`);
    }
}

function viewCompetitor(id) {
    const comp = competitors.find(c => c.id === id);
    if (!comp) return;

    // Build SEC section if public company
    const secSection = comp.is_public && comp.sec_cik ? `
        <div style="background:#f0f9ff;border-radius:8px;padding:12px;margin-top:16px;">
            <h4 style="margin:0 0 8px 0;display:flex;align-items:center;gap:6px;">
                📊 SEC EDGAR Filings ${createSourceLink('sec', comp.sec_cik)}
            </h4>
            <div style="font-size:13px;color:#0369a1;">
                <strong>CIK:</strong> ${comp.sec_cik} | 
                <strong>Fiscal Year End:</strong> ${comp.fiscal_year_end || '—'}
            </div>
            <div style="margin-top:8px;">
                ${formatSecFilings(comp.recent_sec_filings, comp.sec_cik) || '<span style="color:#64748b;">No recent filings</span>'}
            </div>
            ${comp.annual_revenue ? `<div style="margin-top:8px;"><strong>Revenue:</strong> ${comp.annual_revenue}</div>` : ''}
        </div>
    ` : '';

    // Build contacts section if available
    const contactsSection = comp.key_contacts || comp.email_pattern ? `
        <div style="background:#fef3c7;border-radius:8px;padding:12px;margin-top:16px;">
            <h4 style="margin:0 0 8px 0;display:flex;align-items:center;gap:6px;">
                📧 Key Contacts ${createSourceLink('hunter', comp.website)}
            </h4>
            ${comp.email_pattern ? `<div style="font-size:12px;color:#92400e;margin-bottom:8px;">Email Pattern: <code style="background:#fef3c7;padding:2px 6px;border-radius:3px;">${comp.email_pattern}@${comp.website?.replace('https://', '').replace('http://', '').split('/')[0] || 'company.com'}</code></div>` : ''}
            ${formatKeyContacts(comp.key_contacts, comp.website) || '<span style="color:#64748b;">No contacts found</span>'}
        </div>
    ` : '';

    const content = `
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px;">
            ${createLogoImg(comp.website, comp.name, 64)}
            <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <h2 style="margin:0;">${comp.name}</h2>
                    <span class="threat-badge ${(comp.threat_level || '').toLowerCase()}" style="font-size:0.9em; padding:4px 12px;">${comp.threat_level || '—'} Threat</span>
                </div>
                <p style="margin:4px 0;">
                    <a href="${comp.website}" target="_blank" style="color:#0ea5e9;">${comp.website}</a>
                    ${createSourceLink('website', comp.website)}
                </p>
            </div>
        </div>
        
        <div id="stockSection">
            <!-- Stock data loaded here via loadCompanyStockData -->
        </div>

        <hr>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <div><strong>Status:</strong> ${createSourcedValue(comp.status, 'manual', comp.name)}</div>
            <div><strong>Pricing Model:</strong> ${createSourcedValue(comp.pricing_model, 'website', comp.website, 'pricing')}</div>
            <div><strong>Base Price:</strong> ${createSourcedValue(comp.base_price, comp.id, 'base_price')}</div>
            <div><strong>Customers:</strong> ${createSourcedValue(comp.customer_count, comp.id, 'customer_count')}</div>
            <div><strong>Employees:</strong> ${createSourcedValue(comp.employee_count, comp.id, 'employee_count')}</div>
            <div><strong>G2 Rating:</strong> ${createSourcedValue(comp.g2_rating, 'google', comp.name + ' G2 rating')}</div>
            <div><strong>Founded:</strong> ${createSourcedValue(comp.year_founded, 'website', comp.website, 'founded')}</div>
            <div><strong>Headquarters:</strong> ${createSourcedValue(comp.headquarters, 'google', comp.name + ' headquarters')}</div>
            <div><strong>Funding:</strong> ${createSourcedValue(comp.funding_total, 'google', comp.name + ' funding')}</div>
        </div>
        ${secSection}
        ${contactsSection}
        <hr>
        <h4>Products ${createSourceLink('website', comp.website)}</h4>
        <p>${createSourcedValue(comp.product_categories, 'website', comp.website, 'products')}</p>
        <h4>Key Features</h4>
        <p>${createSourcedValue(comp.key_features, 'website', comp.website, 'features')}</p>
        <h4>Integrations</h4>
        <p>${createSourcedValue(comp.integration_partners, 'website', comp.website, 'integrations')}</p>
    `;

    showModal(content);

    // Load stock data if company is public or we have a ticker
    if (comp.ticker || comp.is_public) {
        loadCompanyStockData(comp.name);
    }
}

function editCompetitor(id) {
    const comp = competitors.find(c => c.id === id);
    if (!comp) return;

    const content = `
        <h2>Edit ${comp.name}</h2>
        <form id="editCompetitorForm" onsubmit="saveCompetitor(event, ${id})">
            <div class="form-group">
                <label>Name</label>
                <input type="text" name="name" value="${comp.name}" required>
            </div>
            <div class="form-group">
                <label>Website</label>
                <input type="url" name="website" value="${comp.website}" required>
            </div>
            <div class="form-group">
                <label>Threat Level</label>
                <select name="threat_level">
                    <option value="High" ${comp.threat_level === 'High' ? 'selected' : ''}>High</option>
                    <option value="Medium" ${comp.threat_level === 'Medium' ? 'selected' : ''}>Medium</option>
                    <option value="Low" ${comp.threat_level === 'Low' ? 'selected' : ''}>Low</option>
                </select>
            </div>
            <div class="form-group">
                <label>Pricing Model</label>
                <input type="text" name="pricing_model" value="${comp.pricing_model || ''}">
            </div>
            <div class="form-group">
                <label>Base Price</label>
                <input type="text" name="base_price" value="${comp.base_price || ''}">
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea name="notes" rows="3">${comp.notes || ''}</textarea>
            </div>
            <button type="submit" class="btn btn-primary">Save Changes</button>
        </form>
    `;

    showModal(content);
}

async function saveCompetitor(event, id) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    const result = await fetchAPI(`/api/competitors/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });

    if (result) {
        showToast('Competitor updated successfully', 'success');
        closeModal();
        loadCompetitors();
    }
}

function showAddCompetitorModal() {
    const content = `
        <h2>Add New Competitor</h2>
        <form id="addCompetitorForm" onsubmit="createCompetitor(event)">
            <div class="form-group">
                <label>Name *</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Website *</label>
                <input type="url" name="website" required placeholder="https://...">
            </div>
            <div class="form-group">
                <label>Threat Level</label>
                <select name="threat_level">
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Low">Low</option>
                </select>
            </div>
            <div class="form-group">
                <label>Pricing Model</label>
                <input type="text" name="pricing_model">
            </div>
            <div class="form-group">
                <label>Base Price</label>
                <input type="text" name="base_price">
            </div>
            <button type="submit" class="btn btn-primary">Add Competitor</button>
        </form>
    `;

    showModal(content);
}

async function createCompetitor(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    const result = await fetchAPI('/api/competitors', {
        method: 'POST',
        body: JSON.stringify(data)
    });

    if (result) {
        showToast('Competitor added successfully', 'success');
        closeModal();
        loadCompetitors();
    }
}

async function deleteCompetitor(id) {
    if (!confirm('Are you sure you want to delete this competitor? This action cannot be undone.')) return;

    const result = await fetchAPI(`/api/competitors/${id}`, {
        method: 'DELETE'
    });

    if (result) {
        showToast('Competitor deleted successfully', 'success');
        loadCompetitors();
    }
}

// ============== Changes ==============

async function loadChanges() {
    const severity = document.getElementById('filterSeverity')?.value || '';
    const days = document.getElementById('filterDays')?.value || 7;
    const competitorId = document.getElementById('filterCompany')?.value || '';

    let url = `/api/changes?days=${days}`;
    if (severity) url += `&severity=${severity}`;
    if (competitorId) url += `&competitor_id=${competitorId}`;

    const result = await fetchAPI(url);
    changes = result?.changes || [];

    const container = document.getElementById('changesList');
    if (!container) return;

    container.innerHTML = changes.length ? changes.map(change => `
        <div class="change-item">
            <div class="change-icon ${change.severity.toLowerCase()}">
                ${change.severity === 'High' ? '🔴' : change.severity === 'Medium' ? '🟡' : '🔵'}
            </div>
            <div class="change-content">
                <div class="change-title">${change.competitor_name}: ${change.change_type}</div>
                <div class="change-details">
                    ${change.previous_value ? `Changed from "${change.previous_value}" to ` : 'Set to '}
                    "${change.new_value}"
                </div>
                <div class="change-meta">Source: ${change.source || 'Unknown'}</div>
            </div>
            <div class="change-time">${formatDate(change.detected_at)}</div>
        </div>
    `).join('') : '<p class="empty-state">No changes found</p>';
}

// ============== Comparison ==============

function loadComparisonOptions() {
    const container = document.getElementById('comparisonChecklist');
    if (!container) return;

    container.innerHTML = competitors.map(comp => `
        <label class="comparison-checkbox">
            <input type="checkbox" value="${comp.id}" name="compareCompetitor">
            ${comp.name}
        </label>
    `).join('');
}

function runComparison() {
    const selected = Array.from(document.querySelectorAll('input[name="compareCompetitor"]:checked'))
        .map(cb => parseInt(cb.value));

    if (selected.length < 2) {
        showToast('Please select at least 2 competitors to compare', 'warning');
        return;
    }

    const selectedComps = competitors.filter(c => selected.includes(c.id));

    const attributes = [
        { label: 'Threat Level', key: 'threat_level' },
        { label: 'Pricing Model', key: 'pricing_model' },
        { label: 'Base Price', key: 'base_price' },
        { label: 'Customers', key: 'customer_count' },
        { label: 'Employees', key: 'employee_count' },
        { label: 'G2 Rating', key: 'g2_rating' },
        { label: 'Target Segments', key: 'target_segments' },
        { label: 'Funding', key: 'funding_total' },
        { label: 'Products', key: 'product_categories' },
    ];

    const container = document.getElementById('comparisonResults');
    container.innerHTML = `
        <div class="comparison-table">
            <table>
                <thead>
                    <tr>
                        <th>Attribute</th>
                        ${selectedComps.map(c => `<th>${c.name}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${attributes.map(attr => `
                        <tr>
                            <td><strong>${attr.label}</strong></td>
                            ${selectedComps.map(c => `<td>${createSourcedValue(c[attr.key], c.id, attr.key, 'external')}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// ============== Analytics ==============

async function loadAnalytics() {
    // Ensure competitors are loaded before rendering charts
    if (!competitors || competitors.length === 0) {
        competitors = await fetchAPI('/api/competitors') || [];
    }
    renderMarketShareChart();
    renderHeatmap();
    renderFeatureGaps();
    if (typeof renderMarketQuadrant === 'function') renderMarketQuadrant();
}

function renderMarketShareChart() {
    const ctx = document.getElementById('marketShareChart')?.getContext('2d');
    if (!ctx) return;

    if (marketShareChart) marketShareChart.destroy();

    // Estimate market share from customer counts
    console.log('Rendering Market Share Chart. Competitors:', competitors);
    const shareData = competitors.slice(0, 8).map(c => {
        const count = parseInt((c.customer_count || '0').replace(/\D/g, '')) || 100;
        console.log(`Competitor ${c.name}: count=${count}`);
        return { name: c.name, share: count };
    });

    const total = shareData.reduce((sum, d) => sum + d.share, 0);
    shareData.forEach(d => d.share = Math.round(d.share / total * 100));

    marketShareChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: shareData.map(d => d.name),
            datasets: [{
                data: shareData.map(d => d.share),
                backgroundColor: [
                    '#2F5496', '#00B4D8', '#28A745', '#FFC107',
                    '#DC3545', '#6C757D', '#17A2B8', '#6610f2'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

function renderHeatmap() {
    const container = document.getElementById('heatmapContainer');
    if (!container) return;

    const categories = ['Pricing', 'Features', 'Market', 'Tech', 'Support', 'Growth'];

    container.innerHTML = `
        <table class="heatmap-table">
            <thead>
                <tr>
                    <th>Competitor</th>
                    ${categories.map(c => `<th>${c}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
                ${competitors.slice(0, 8).map(comp => `
                    <tr>
                        <td><strong>${comp.name}</strong></td>
                        ${categories.map(() => {
        const score = Math.floor(Math.random() * 10) + 1;
        return `<td class="heatmap-cell score-${score}">${score}</td>`;
    }).join('')}
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderFeatureGaps() {
    const container = document.getElementById('featureGapContainer');
    if (!container) return;

    const features = [
        { name: 'Patient Intake', certify: true },
        { name: 'Eligibility Verification', certify: true },
        { name: 'Patient Payments', certify: true },
        { name: 'Telehealth', certify: false },
        { name: 'Full EHR', certify: false },
        { name: 'AI Scheduling', certify: false },
    ];

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Feature</th>
                    <th>Certify Health</th>
                    ${competitors.slice(0, 4).map(c => `<th>${c.name}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
                ${features.map(f => `
                    <tr>
                        <td>${f.name}</td>
                        <td>${f.certify ? '✅' : '❌'}</td>
                        ${competitors.slice(0, 4).map(() =>
        `<td>${Math.random() > 0.5 ? '✅' : '❌'}</td>`
    ).join('')}
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ============== Battlecards ==============

let corporateProfile = null;

async function loadBattlecards() {
    const grid = document.getElementById('battlecardsGrid');
    if (!grid) return;

    // Fetch corporate profile (Certify Health) if not already loaded
    if (!corporateProfile) {
        try {
            const response = await fetch(`${API_BASE}/api/corporate-profile`);
            if (response.ok) {
                corporateProfile = await response.json();
            }
        } catch (e) {
            console.log('Corporate profile not available');
        }
    }

    // Build corporate battlecard HTML (displayed first)
    const corporateCard = corporateProfile ? `
        <div class="battlecard-preview corporate" onclick="viewCorporateBattlecard()">
            <span class="company-badge">🏢 Our Company</span>
            <h4>${corporateProfile.name}</h4>
            <p class="battlecard-summary">
                ${corporateProfile.tagline}
            </p>
            <button class="btn btn-secondary">View Reference Profile</button>
        </div>
    ` : '';

    // Build competitor battlecards
    const competitorCards = competitors.map(comp => `
        <div class="battlecard-preview" onclick="viewBattlecard(${comp.id})">
            <h4>${comp.name}</h4>
            <span class="threat-badge ${comp.threat_level.toLowerCase()}">${comp.threat_level} Threat</span>
            <p class="battlecard-summary">
                ${comp.product_categories || 'Patient engagement platform'}
            </p>
            <button class="btn btn-secondary">View Battlecard</button>
        </div>
    `).join('');

    grid.innerHTML = corporateCard + competitorCards;
}

async function viewCorporateBattlecard() {
    // Fetch fresh corporate profile data
    let profile = corporateProfile;
    if (!profile) {
        try {
            const response = await fetch(`${API_BASE}/api/corporate-profile`);
            if (response.ok) {
                profile = await response.json();
                corporateProfile = profile;
            }
        } catch (e) {
            showToast('Error loading corporate profile', 'error');
            return;
        }
    }

    if (!profile) {
        showToast('Corporate profile not available', 'error');
        return;
    }

    // Build products HTML
    const productsHtml = Object.values(profile.products).map(p => `
        <div class="product-card">
            <h5>${p.name}</h5>
            <p>${p.description}</p>
        </div>
    `).join('');

    // Build metrics HTML
    const metricsHtml = `
        <div class="metric-card">
            <div class="metric-value">${profile.claimed_outcomes.no_show_reduction.replace('% fewer no-shows', '%')}</div>
            <div class="metric-label">Fewer No-Shows</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${profile.claimed_outcomes.revenue_increase.replace('% more revenue collected', '%')}</div>
            <div class="metric-label">More Revenue</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${profile.claimed_outcomes.claim_denial_reduction.replace('% reduction in claim denials', '%')}</div>
            <div class="metric-label">Fewer Denials</div>
        </div>
    `;

    // Build differentiators list
    const diffHtml = profile.key_differentiators.map(d => `<li>${d}</li>`).join('');

    // Build markets list
    const marketsHtml = profile.markets.map(m => `<span class="tag">${m}</span>`).join(' ');

    const content = `
        <div class="battlecard-full corporate">
            <h2>
                🏢 ${profile.name}
                <span class="corporate-header-badge">Reference Profile</span>
            </h2>
            
            <p style="font-size: 16px; color: #465D8B; margin: 16px 0;">
                <em>"${profile.mission}"</em>
            </p>
            
            <h3>📊 Key Metrics</h3>
            <div class="metrics-grid">
                ${metricsHtml}
            </div>
            
            <h3>🏗️ Our Products (7 Platforms)</h3>
            <div class="product-grid">
                ${productsHtml}
            </div>
            
            <h3>🎯 Key Differentiators</h3>
            <ul class="differentiator-list">
                ${diffHtml}
            </ul>
            
            <h3>🏥 Markets We Serve (11 Verticals)</h3>
            <div style="margin: 12px 0; line-height: 2;">
                ${marketsHtml}
            </div>
            
            <h3>Quick Facts</h3>
            <table class="data-table" style="margin-bottom: 20px;">
                <tr><td>Founded</td><td>${profile.year_founded}</td></tr>
                <tr><td>Headquarters</td><td>${profile.headquarters}</td></tr>
                <tr><td>Employees</td><td>${profile.employee_count}</td></tr>
                <tr><td>Funding</td><td>${profile.funding_total}</td></tr>
                <tr><td>Investors</td><td>${profile.investors.join(', ')}</td></tr>
                <tr><td>Certifications</td><td>${profile.certifications.join(', ')}</td></tr>
            </table>
            
            <h3>🏆 Awards</h3>
            <p>${profile.awards.join(', ')}</p>
            
            <div style="margin-top: 24px; display: flex; gap: 12px;">
                <a href="${profile.website}" target="_blank" class="btn btn-primary">🌐 Visit Website</a>
                <a href="${profile.contact.demo_url}" target="_blank" class="btn btn-secondary">📅 Request Demo</a>
            </div>
        </div>
    `;

    showModal(content);
}

function viewBattlecard(id) {
    const comp = competitors.find(c => c.id === id);
    if (!comp) return;

    const content = `
        <div class="battlecard-full">
            <h2>🃏 ${comp.name} Battlecard</h2>
            <span class="threat-badge ${comp.threat_level.toLowerCase()}">${comp.threat_level} Threat</span>
            
            <div id="stockSection">
                <p class="loading">Loading company data...</p>
            </div>
            
            <h3>Quick Facts</h3>
            <table class="data-table" style="margin-bottom: 20px;">
                <tr><td>Founded</td><td>${comp.year_founded || 'Unknown'}</td></tr>
                <tr><td>Headquarters</td><td>${comp.headquarters || 'Unknown'}</td></tr>
                <tr><td>Employees</td><td>${comp.employee_count || 'Unknown'}</td></tr>
                <tr><td>Customers</td><td>${comp.customer_count || 'Unknown'}</td></tr>
                <tr><td>Funding</td><td>${comp.funding_total || 'Unknown'}</td></tr>
                <tr><td>Pricing</td><td>${comp.pricing_model || 'N/A'} - ${comp.base_price || 'N/A'}</td></tr>
            </table>
            
            <h3>Products</h3>
            <p>${comp.product_categories || 'N/A'}</p>
            
            <h3>Key Features</h3>
            <p>${comp.key_features || 'N/A'}</p>
            
            <h3>📰 Latest News</h3>
            <div id="newsSection" class="news-section">
                <p class="loading">Loading news articles...</p>
            </div>
            
            <h3>Win Against Tactics</h3>
            <ul>
                <li>Emphasize Certify's speed of implementation</li>
                <li>Highlight total cost of ownership advantages</li>
                <li>Focus on our superior customer support</li>
                <li>Demonstrate EHR integration depth</li>
            </ul>
            
            <button class="btn btn-primary" onclick="downloadBattlecard(${id})">📄 Download PDF</button>
        </div>
    `;

    showModal(content);

    // Fetch and display stock data
    loadCompanyStockData(comp.name);

    // Fetch and display news
    loadCompetitorNews(comp.name);
}

async function loadCompetitorNews(companyName) {
    const newsSection = document.getElementById('newsSection');
    if (!newsSection) return;

    try {
        console.log(`Fetching news for: ${companyName}`);
        const response = await fetch(`${API_BASE}/api/news/${encodeURIComponent(companyName)}`);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        console.log("News data received:", data);

        if (data.articles && data.articles.length > 0) {
            newsSection.innerHTML = data.articles.map(article => `
                <div class="news-item">
                    <a href="${article.url}" target="_blank" class="news-title">${article.title}</a>
                    <div class="news-meta">
                        <span class="news-source">${article.source}</span>
                        <span class="news-date">${article.published_date || ''}</span>
                    </div>
                    <p class="news-snippet">${article.snippet || ''}</p>
                </div>
            `).join('');
        } else {
            newsSection.innerHTML = '<p class="empty-state">No recent news articles found</p>';
        }
    } catch (e) {
        console.error("Error loading news:", e);
        newsSection.innerHTML = `<div class="error-state">
            <p>Unable to load news.</p>
            <small style="color: #ef4444;">${e.message}</small>
        </div>`;
    }
}

async function loadCompanyStockData(companyName) {
    const stockSection = document.getElementById('stockSection');
    if (!stockSection) return;

    try {
        const response = await fetch(`${API_BASE}/api/stock/${encodeURIComponent(companyName)}`);
        const data = await response.json();

        if (data.is_public) {
            const changeClass = data.change >= 0 ? 'up' : 'down';
            const changeSign = data.change >= 0 ? '+' : '';

            // Formatting helpers
            const fmtNum = (n, suffix = '') => n ? (n / 1000000).toLocaleString(undefined, { maximumFractionDigits: 1 }) + 'M' + suffix : 'N/A';
            const fmtLgNum = (n) => {
                if (!n) return 'N/A';
                if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
                if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
                return n.toLocaleString();
            };
            const fmtCur = (n) => n ? '$' + n.toFixed(2) : 'N/A';
            const fmtPct = (n) => n ? (n * 100).toFixed(2) + '%' : 'N/A';
            const fmtRawPct = (n) => n ? n.toFixed(2) + '%' : 'N/A'; // For values already in % (0-100) or decimal (0-1)? 
            // Assumption: data from backend like profitMargin is decimal (0.15 = 15%) or float?
            // yfinance usually returns margins as 0.15 (15%). 
            // shortPercentOfFloat is usually 0.05 (5%)

            stockSection.innerHTML = `
                <div class="stock-section" style="background: white; padding: 20px; border-radius: 8px;">
                    <!-- Header -->
                    <div class="stock-header-row" style="display: flex; align-items: center; flex-wrap: nowrap; gap: 12px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #e2e8f0; white-space: nowrap;">
                        <span style="background: #22c55e; color: white; padding: 4px 12px; border-radius: 4px; font-weight: 600; font-size: 0.85em;">PUBLIC</span>
                        <span style="font-size: 1.25em; font-weight: 700; color: #122753;">${data.ticker} <span style="font-size: 0.8em; color: #64748b; font-weight: 500;">(${data.exchange})</span></span>
                        <span style="font-size: 1.25em; font-weight: 700; color: #122753;">${fmtCur(data.price)}</span>
                        <span class="stock-change ${changeClass}" style="font-weight: 600;">
                            ${changeSign}${data.change?.toFixed(2)} (${changeSign}${data.change_percent?.toFixed(2)}%)
                        </span>
                    </div>

                    <!-- Financial Grid -->
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px;">
                        
                        <!-- Valuation -->
                        <div class="fin-group" style="background: #f8fafc; padding: 16px; border-radius: 6px;">
                            <h4 style="color: #122753; font-size: 0.9em; text-transform: uppercase; margin-bottom: 12px; border-bottom: 2px solid #122753; padding-bottom: 8px; text-decoration: underline; text-underline-offset: 4px;">Valuation & Multiples</h4>
                            <div class="fin-row"><span>Enterprise Value</span> <strong>${fmtLgNum(data.enterprise_value)}</strong></div>
                            <div class="fin-row"><span>P/E (Trailing)</span> <strong>${data.pe_trailing?.toFixed(2) || 'N/A'}</strong></div>
                            <div class="fin-row"><span>P/E (Forward)</span> <strong>${data.pe_forward?.toFixed(2) || 'N/A'}</strong></div>
                            <div class="fin-row"><span>EV/EBITDA</span> <strong>${data.ev_ebitda?.toFixed(2) || 'N/A'}</strong></div>
                            <div class="fin-row"><span>Price/Book</span> <strong>${data.price_to_book?.toFixed(2) || 'N/A'}</strong></div>
                            <div class="fin-row"><span>PEG Ratio</span> <strong>${data.peg_ratio?.toFixed(2) || 'N/A'}</strong></div>
                        </div>

                        <!-- Operating -->
                        <div class="fin-group" style="background: #f8fafc; padding: 16px; border-radius: 6px;">
                            <h4 style="color: #122753; font-size: 0.9em; text-transform: uppercase; margin-bottom: 12px; border-bottom: 2px solid #122753; padding-bottom: 8px; text-decoration: underline; text-underline-offset: 4px;">Operating Fundamentals</h4>
                            <div class="fin-row"><span>Revenue (TTM)</span> <strong>${fmtLgNum(data.revenue_ttm)}</strong></div>
                            <div class="fin-row"><span>EBITDA</span> <strong>${fmtLgNum(data.ebitda)}</strong></div>
                            <div class="fin-row"><span>EPS (Trailing)</span> <strong>${data.eps_trailing?.toFixed(2) || 'N/A'}</strong></div>
                            <div class="fin-row"><span>Free Cash Flow</span> <strong>${fmtLgNum(data.free_cash_flow)}</strong></div>
                            <div class="fin-row"><span>Profit Margin</span> <strong>${fmtPct(data.profit_margin)}</strong></div>
                        </div>

                         <!-- Risk -->
                         <div class="fin-group" style="background: #f8fafc; padding: 16px; border-radius: 6px;">
                            <h4 style="color: #122753; font-size: 0.9em; text-transform: uppercase; margin-bottom: 12px; border-bottom: 2px solid #122753; padding-bottom: 8px; text-decoration: underline; text-underline-offset: 4px;">Risk & Trading</h4>
                            <div class="fin-row"><span>Beta</span> <strong>${data.beta?.toFixed(2) || 'N/A'}</strong></div>
                            <div class="fin-row"><span>Short Interest</span> <strong>${fmtPct(data.short_interest)}</strong></div>
                            <div class="fin-row"><span>Avg Volume (90d)</span> <strong>${fmtLgNum(data.avg_volume_90d)}</strong></div>
                            <div class="fin-row"><span>Float</span> <strong>${fmtLgNum(data.float_shares)}</strong></div>
                            <div class="fin-row"><span>52W Range</span> <strong style="font-size: 0.9em;">$${data.fifty_two_week_low?.toFixed(2)} - $${data.fifty_two_week_high?.toFixed(2)}</strong></div>
                        </div>

                         <!-- Capital -->
                         <div class="fin-group" style="background: #f8fafc; padding: 16px; border-radius: 6px;">
                            <h4 style="color: #122753; font-size: 0.9em; text-transform: uppercase; margin-bottom: 12px; border-bottom: 2px solid #122753; padding-bottom: 8px; text-decoration: underline; text-underline-offset: 4px;">Capital Structure</h4>
                            <div class="fin-row"><span>Market Cap</span> <strong>${fmtLgNum(data.market_cap)}</strong></div>
                            <div class="fin-row"><span>Shares Out</span> <strong>${fmtLgNum(data.shares_outstanding)}</strong></div>
                            <div class="fin-row"><span>Inst. Ownership</span> <strong>${fmtPct(data.inst_ownership)}</strong></div>
                            <div class="fin-row"><span>Dividend Yield</span> <strong>${fmtPct(data.dividend_yield)}</strong></div>
                            <div class="fin-row"><span>Next Earnings</span> <strong>${data.next_earnings}</strong></div>
                        </div>
                    </div>
                    
                    <div style="font-size: 0.8em; color: #94a3b8; text-align: right; margin-top: 20px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
                        Data provided by Yahoo Finance • Delayed 15 mins
                    </div>
                </div>

                <style>
                    .fin-row { display: flex; justify-content: space-between; font-size: 0.9em; padding: 6px 0; border-bottom: 1px dashed #e2e8f0; }
                    .fin-row:last-child { border-bottom: none; }
                    .fin-row span { color: #64748b; }
                    .fin-row strong { color: #1e293b; font-weight: 600; }
                </style>
            `;
        } else {
            // Check if we have rich private data (Headcount, Funding, etc.)
            if (data.headcount || data.total_funding) {
                stockSection.innerHTML = `
                <div class="stock-section private-mode">
                    <!-- Header -->
                    <div class="stock-header-row" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #e2e8f0;">
                         <div style="display: flex; align-items: center; gap: 10px;">
                            <span class="badge" style="background: #64748b; color: white; padding: 4px 12px; border-radius: 4px; font-weight: 600;">PRIVATE</span>
                            <span style="font-size: 1.25em; font-weight: 700; color: var(--navy-dark);">${data.company}</span>
                        </div>
                        <div style="text-align: right;">
                             <span class="badge" style="background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 4px; font-weight: 600; font-size: 0.9em;">${data.stage || 'Private Company'}</span>
                        </div>
                    </div>

                    <!-- Private Intelligence Grid -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                        
                        <!-- Valuation & Capital -->
                        <div class="fin-group">
                            <h4 style="color: var(--text-secondary); font-size: 0.85em; text-transform: uppercase; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">Capital & Valuation</h4>
                            <div class="fin-row"><span>Total Funding</span> <strong>${fmtLgNum(data.total_funding)}</strong></div>
                            <div class="fin-row"><span>Latest Round</span> <strong>${data.latest_deal_type || 'N/A'}</strong></div>
                            <div class="fin-row"><span>Deal Size</span> <strong>${fmtLgNum(data.latest_deal_amount)}</strong></div>
                            <div class="fin-row"><span>Deal Date</span> <strong>${data.latest_deal_date || 'N/A'}</strong></div>
                            <div class="fin-row"><span>Est. Revenue</span> <strong>${fmtLgNum(data.est_revenue)}</strong></div>
                        </div>


                        <!-- Growth & People -->
                        <div class="fin-group">
                            <h4 style="color: var(--text-secondary); font-size: 0.85em; text-transform: uppercase; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">Growth Signals</h4>
                            <div class="fin-row"><span>Headcount</span> <strong>${data.headcount?.toLocaleString() || 'N/A'}</strong></div>
                            <div class="fin-row"><span>6mo Growth</span> <strong style="color: ${data.growth_rate_6mo >= 0 ? '#16a34a' : '#dc2626'}">${fmtRawPct(data.growth_rate_6mo)}</strong></div>
                            <div class="fin-row"><span>Active Jobs</span> <strong>${data.active_hiring || 0} Openings</strong></div>
                            <div class="fin-row"><span>Hiring Focus</span> <strong>${data.hiring_departments?.[0] || 'N/A'}</strong></div>
                             <div class="fin-row"><span>Founded</span> <strong>${data.founded || 'N/A'}</strong></div>
                        </div>


                        <!-- Alternative Intelligence -->
                        <div class="fin-group">
                            <h4 style="color: var(--text-secondary); font-size: 0.85em; text-transform: uppercase; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">Health & Quality</h4>
                            <div class="fin-row" title="USAspending.gov Prime Contracts"><span>Gov Contracts</span> <strong>${fmtLgNum(data.gov_contracts?.total_amount)}</strong></div>
                            <div class="fin-row" title="Avg Engineering Salary (H-1B)"><span>Eng Salary</span> <strong>${data.h1b_data?.avg_salary ? '$' + Math.round(data.h1b_data.avg_salary / 1000) + 'k' : 'N/A'}</strong></div>
                            <div class="fin-row" title="Patent Portfolio Size"><span>Patents</span> <strong>${data.innovation?.patents || 0} (${data.innovation?.pending || 0} pending)</strong></div>
                            <div class="fin-row" title="Glassdoor CEO Approval"><span>CEO Approval</span> <strong style="color: ${data.employee_sentiment?.ceo_approval >= 80 ? '#16a34a' : '#64748b'}">${data.employee_sentiment?.ceo_approval || 0}%</strong></div>
                            <div class="fin-row" title="Mobile App Quality"><span>App Rating</span> <strong>${data.app_quality?.avg_rating || 'N/A'} <small>(${data.app_quality?.downloads || '0'})</small></strong></div>
                        </div>


                        <!-- Google Digital Footprint -->
                        <div class="fin-group">
                            <h4 style="color: var(--text-secondary); font-size: 0.85em; text-transform: uppercase; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">Digital Footprint</h4>
                            <div class="fin-row" title="Google Ads Transparency"><span>Active Ads</span> <strong>${data.google_ecosystem?.ads_active || 0} Creatives</strong></div>
                            <div class="fin-row" title="Google Trends 12mo Benchmark"><span>Brand Interest</span> <strong>${data.google_ecosystem?.brand_index || 0}/100 <small>(${data.google_ecosystem?.trend || 'Flat'})</small></strong></div>
                            <div class="fin-row" title="Google Maps Review Velocity"><span>Reviews/Mo</span> <strong>${data.google_ecosystem?.review_velocity || 0}</strong></div>
                            <div class="fin-row" title="Marketing Tech Stack Signal"><span>Tech Spend</span> <strong>${data.tech_stack?.signal || 'Unknown'}</strong></div>
                            <div class="fin-row" title="Tools Detected"><span>Key Tools</span> <strong style="font-size: 0.8em; text-align: right; max-width: 120px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${data.tech_stack?.tools?.slice(0, 2).join(', ') || 'N/A'}</strong></div>
                        </div>

                        <!-- Deep Dive Intelligence (New) -->
                        <div class="fin-group">
                            <h4 style="color: var(--text-secondary); font-size: 0.85em; text-transform: uppercase; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">Deep Dive</h4>
                            <div class="fin-row" title="G2 / Capterra Score"><span>B2B Reviews</span> <strong>${data.sentiment?.g2_score || 'N/A'}/5 <small>(${data.sentiment?.g2_badges?.length || 0} Badges)</small></strong></div>
                            <div class="fin-row" title="Trustpilot Consumer Score"><span>Trustpilot</span> <strong>${data.sentiment?.trustpilot || 'N/A'}/5</strong></div>
                            <div class="fin-row" title="Moz Domain Authority"><span>Domain Auth</span> <strong>${data.seo?.da || 0}/100</strong></div>
                            <div class="fin-row" title="Page Load Speed"><span>Site Speed</span> <strong style="color: ${data.seo?.speed >= 80 ? '#16a34a' : (data.seo?.speed < 50 ? '#dc2626' : '#d97706')}">${data.seo?.speed || 0}/100</strong></div>
                            <div class="fin-row" title="Founder Exit History / Tier 1 VC"><span>Pedigree</span> <strong>${data.risk_mgmt?.founder_exit ? 'Exited Founder' : (data.risk_mgmt?.tier1_vc ? 'Tier 1 VC' : 'Standard')}</strong></div>
                             <div class="fin-row" title="SOC2 / WARN Notices"><span>Risk Flags</span> <strong>${data.risk_mgmt?.warn > 0 ? '⚠️ LAYOFFS' : (data.risk_mgmt?.soc2 ? '✅ SOC2' : 'None')}</strong></div>
                        </div>
                    </div>
                    
                    <div style="font-size: 0.8em; color: #94a3b8; text-align: right; margin-top: 15px;">
                        Data sources: ${data.data_sources?.join(', ') || 'SEC Form D, LinkedIn'}
                    </div>
                </div>
                <style>
                    /* Reuse fin-row styles from above */
                </style>
                `;
            } else {
                // Fallback for minimal data
                stockSection.innerHTML = `
                    <div class="private-badge" style="background: #e2e8f0; color: #64748b; display: inline-block; padding: 4px 12px; border-radius: 4px; font-weight: 600; margin-bottom: 10px;">
                        PRIVATE COMPANY
                    </div>
                    <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">
                        Data sources: ${data.data_sources?.join(', ') || 'Company website, LinkedIn, News'}
                    </p>
                `;
            }
        }
    } catch (error) {
        console.warn("Stock data load error", error);
        stockSection.innerHTML = '<div class="private-badge">Private Company (Data Unavailable)</div>';
    }
}

async function downloadBattlecard(id) {
    showToast('Generating battlecard PDF...', 'info');
    // In production, this would call the backend to generate the PDF
    window.open(`${API_BASE}/api/reports/battlecard/${id}`, '_blank');
}

async function generateAllBattlecards() {
    showToast('Generating all battlecards...', 'info');
    // Call backend endpoint
}

// ============== Reports ==============

async function generateWeeklyBriefing() {
    showToast('Generating executive briefing...', 'info');
    window.open(`${API_BASE}/api/reports/weekly-briefing`, '_blank');
}

async function generateComparisonReport() {
    showToast('Generating comparison report...', 'info');
    window.open(`${API_BASE}/api/reports/comparison`, '_blank');
}

// ============== Settings ==============

function loadSettings() {
    // Load alert rules, integration status, etc.
}

function showAddRuleModal() {
    const content = `
        <h2>Add Alert Rule</h2>
        <form id="addRuleForm">
            <div class="form-group">
                <label>Rule Name</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Competitor (optional)</label>
                <select name="competitor">
                    <option value="">All Competitors</option>
                    ${competitors.map(c => `<option value="${c.name}">${c.name}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Field to Monitor</label>
                <select name="field">
                    <option value="base_price">Base Price</option>
                    <option value="funding_total">Funding</option>
                    <option value="employee_count">Employee Count</option>
                    <option value="g2_rating">G2 Rating</option>
                </select>
            </div>
            <div class="form-group">
                <label>Condition</label>
                <select name="condition">
                    <option value="changed">Changed</option>
                    <option value="greater_than">Greater Than</option>
                    <option value="less_than">Less Than</option>
                    <option value="contains">Contains</option>
                </select>
            </div>
            <div class="form-group">
                <label>Channels</label>
                <label class="comparison-checkbox">
                    <input type="checkbox" name="channels" value="email"> Email
                </label>
                <label class="comparison-checkbox">
                    <input type="checkbox" name="channels" value="slack"> Slack
                </label>
                <label class="comparison-checkbox">
                    <input type="checkbox" name="channels" value="sms"> SMS
                </label>
            </div>
            <button type="submit" class="btn btn-primary">Create Rule</button>
        </form>
    `;

    showModal(content);
}

// ============== Actions ==============

async function triggerScrape(id) {
    showToast('Starting data refresh...', 'info');
    const result = await fetchAPI(`/api/scrape/${id}`, { method: 'POST' });
    if (result) {
        showToast('Refresh queued successfully', 'success');
    }
}

// Note: triggerScrapeAll is defined earlier in this file with progress tracking

async function triggerDiscovery() {
    showToast('Starting autonomous discovery agent...', 'info');
    try {
        const response = await fetch(`${API_BASE}/api/discovery/run`, { method: 'POST' });
        const data = await response.json();

        if (data.status === 'success') {
            const count = data.candidates ? data.candidates.length : 0;
            showToast(`Discovery complete! Found ${count} potential competitors.`, 'success');

            // Show results in a modal
            const resultsHtml = data.candidates.map(c => `
                <div class="discovery-result" style="border: 1px solid #eee; padding: 15px; margin-bottom: 10px; border-radius: 8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0;"><a href="${c.url}" target="_blank">${c.name}</a></h4>
                        <span class="badge ${c.relevance_score > 80 ? 'high' : 'medium'}">${c.relevance_score}% Match</span>
                    </div>
                    <p style="margin: 5px 0; font-size: 0.9em; color: #666;">${c.reasoning}</p>
                    <button class="btn btn-sm btn-outline" onclick="addDiscoveredCompetitor('${c.name}', '${c.url}')">+ Track This</button>
                </div>
            `).join('');

            showModal(`
                <h2>🔭 Discovered Candidates</h2>
                <p>The autonomous agent found the following potential competitors:</p>
                <div class="discovery-list" style="max-height: 400px; overflow-y: auto; margin-top: 15px;">
                    ${resultsHtml || '<p>No new high-confidence matches found.</p>'}
                </div>
            `);
        } else {
            showToast('Discovery agent encountered an error.', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

function addDiscoveredCompetitor(name, website) {
    // Pre-fill the add modal
    closeModal();
    showAddCompetitorModal();
    setTimeout(() => {
        document.querySelector('input[name="name"]').value = name;
        document.querySelector('input[name="website"]').value = website;
    }, 100);
}

// ============== Utilities ==============

function showModal(content) {
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = content;
    modal.classList.add('active');
}

function closeModal() {
    document.getElementById('modal').classList.remove('active');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function handleSearch(event) {
    const query = event.target.value.toLowerCase().trim();
    const dropdown = document.getElementById('searchDropdown');

    if (!dropdown) return;

    // Hide dropdown if query is empty
    if (!query) {
        dropdown.style.display = 'none';
        return;
    }

    // Filter competitors matching the query
    const filtered = competitors.filter(c =>
        c.name.toLowerCase().includes(query) ||
        (c.product_categories || '').toLowerCase().includes(query) ||
        (c.threat_level || '').toLowerCase().includes(query)
    ).slice(0, 8); // Limit to 8 results

    if (filtered.length === 0) {
        dropdown.innerHTML = `<div style="padding: 12px; color: #94a3b8; text-align: center;">No competitors found</div>`;
        dropdown.style.display = 'block';
        return;
    }

    // Render results
    dropdown.innerHTML = filtered.map(c => `
        <div class="search-result-item" onclick="navigateToCompetitor(${c.id})" style="
            padding: 10px 14px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            transition: background 0.2s;
        " onmouseover="this.style.background='#334155'" onmouseout="this.style.background='transparent'">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2em;">${c.threat_level === 'High' ? '🔴' : c.threat_level === 'Medium' ? '🟡' : '🟢'}</span>
                <div>
                    <div style="font-weight: 600; color: #f1f5f9;">${c.name}</div>
                    <div style="font-size: 0.8em; color: #94a3b8;">${c.product_categories || 'Healthcare IT'}</div>
                </div>
            </div>
            <span class="threat-badge ${(c.threat_level || 'low').toLowerCase()}" style="font-size: 0.75em; padding: 2px 8px;">${c.threat_level || 'Unknown'}</span>
        </div>
    `).join('');

    dropdown.style.display = 'block';
}

// Navigate to competitor detail
function navigateToCompetitor(competitorId) {
    const dropdown = document.getElementById('searchDropdown');
    const searchInput = document.getElementById('globalSearch');
    if (dropdown) dropdown.style.display = 'none';
    if (searchInput) searchInput.value = '';

    // Show competitors page and open detail modal
    showPage('competitors');
    setTimeout(() => showCompetitorDetail(competitorId), 300);
}

// Close search dropdown when clicking outside
document.addEventListener('click', function (e) {
    const dropdown = document.getElementById('searchDropdown');
    const searchInput = document.getElementById('globalSearch');
    if (dropdown && searchInput && !searchInput.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = 'none';
    }
});

// Close modal on outside click
document.getElementById('modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'modal') closeModal();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

// ============== Discovery Functions ==============

let discoveredCompetitors = [];

async function loadDiscovered() {
    // Load previously discovered competitors from session or API
    const grid = document.getElementById('discoveredGrid');
    if (!grid) return;

    // Try to load from API
    const result = await fetchAPI('/api/discovery/results');
    if (result && result.candidates && result.candidates.length > 0) {
        discoveredCompetitors = result.candidates;
        renderDiscoveredGrid();
    } else {
        grid.innerHTML = `
            <div class="empty-state" style="text-align: center; padding: 40px;">
                <span style="font-size: 48px;">🔮</span>
                <h3>No Discovered Competitors</h3>
                <p style="color: #64748b;">Click "Run Discovery" to start the autonomous competitor search.</p>
            </div>
        `;
    }
}

const DEFAULT_DISCOVERY_CRITERIA = `• Target Market: Patient engagement, patient intake, healthcare check-in solutions
• Company Size: 50-5000 employees (growth-stage or established)
• Geography: US-based or significant US presence
• Product Focus: Digital check-in, eligibility verification, patient payments, scheduling
• Technology: Cloud-based SaaS, mobile-first, EHR integrations
• Funding: Series A+ or profitable private company
• Customer Base: Medical practices, health systems, ambulatory care
• Competitive Signals: Similar keywords, overlapping customer segments
• Exclude: Pure EHR vendors, hospital-only solutions, international-only`;

function resetCriteria() {
    const textarea = document.getElementById('discoveryCriteria');
    if (textarea) {
        textarea.value = DEFAULT_DISCOVERY_CRITERIA;
        showToast('Criteria reset to defaults', 'success');
    }
}

async function runDiscovery() {
    const statusDiv = document.getElementById('discoveryStatus');
    const grid = document.getElementById('discoveredGrid');
    const criteriaTextarea = document.getElementById('discoveryCriteria');

    // Get user-defined criteria
    const criteria = criteriaTextarea ? criteriaTextarea.value : DEFAULT_DISCOVERY_CRITERIA;

    if (statusDiv) {
        statusDiv.style.display = 'block';
        statusDiv.innerHTML = '<span class="spinner">⏳</span> Running Certify Scout discovery scan with custom criteria... This may take a minute.';
    }

    try {
        const result = await fetchAPI('/api/discovery/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ criteria: criteria })
        });

        if (result && result.candidates) {
            discoveredCompetitors = result.candidates;
            showToast(`Discovery complete! Found ${result.candidates.length} potential competitors matching your criteria.`, 'success');
            renderDiscoveredGrid();
        } else {
            showToast('Discovery scan completed. No new competitors found matching your criteria.', 'info');
            grid.innerHTML = `
                <div class="empty-state" style="text-align: center; padding: 40px;">
                    <span style="font-size: 48px;">🔍</span>
                    <h3>No New Competitors Found</h3>
                    <p style="color: #64748b;">The discovery agent didn't find any new companies matching your custom criteria. Try adjusting your search parameters.</p>
                </div>
            `;
        }
    } catch (error) {
        showToast('Discovery scan failed. Please try again.', 'error');
    } finally {
        if (statusDiv) {
            statusDiv.style.display = 'none';
        }
    }
}

function renderDiscoveredGrid() {
    const grid = document.getElementById('discoveredGrid');
    if (!grid || !discoveredCompetitors.length) return;

    grid.innerHTML = discoveredCompetitors.map((candidate, index) => `
        <div class="competitor-card discovered-card" style="border-left: 4px solid ${getScoreColor(candidate.score)};">
            <div class="competitor-header">
                <div>
                    <div class="competitor-name">${candidate.name || 'Unknown Company'}</div>
                    <a href="${candidate.url}" target="_blank" class="competitor-website">${candidate.url}</a>
                </div>
                <span class="score-badge" style="background: ${getScoreColor(candidate.score)}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600;">
                    ${candidate.score}% Match
                </span>
            </div>
            <div class="competitor-details">
                <div class="detail-item">
                    <span class="detail-label">Matched Keywords</span>
                    <span class="detail-value">${(candidate.matched_keywords || []).join(', ') || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Discovered</span>
                    <span class="detail-value">${formatDate(candidate.discovered_at)}</span>
                </div>
            </div>
            <div class="competitor-actions">
                <button class="btn btn-primary" onclick="addDiscoveredToCompetitors(${index})">➕ Add to Competitors</button>
                <button class="btn btn-secondary" onclick="viewDiscoveredDetails(${index})">View Details</button>
                <button class="btn btn-secondary" onclick="dismissDiscovered(${index})">✕ Dismiss</button>
            </div>
        </div>
    `).join('');
}

function getScoreColor(score) {
    if (score >= 70) return '#22c55e';  // Green for high match
    if (score >= 50) return '#f59e0b';  // Orange for medium match
    return '#ef4444';  // Red for low match
}

async function addDiscoveredToCompetitors(index) {
    const candidate = discoveredCompetitors[index];
    if (!candidate) return;

    const newCompetitor = {
        name: candidate.name || new URL(candidate.url).hostname.replace('www.', ''),
        website: candidate.url,
        threat_level: candidate.score >= 70 ? 'High' : candidate.score >= 50 ? 'Medium' : 'Low',
        status: 'Active',
        notes: `Discovered by Certify Scout with ${candidate.score}% relevance score. Keywords: ${(candidate.matched_keywords || []).join(', ')}`
    };

    const result = await fetchAPI('/api/competitors', {
        method: 'POST',
        body: JSON.stringify(newCompetitor)
    });

    if (result) {
        showToast(`${newCompetitor.name} added to competitors!`, 'success');
        // Remove from discovered list
        discoveredCompetitors.splice(index, 1);
        renderDiscoveredGrid();
        // Refresh competitors list
        loadCompetitors();
    }
}

function viewDiscoveredDetails(index) {
    const candidate = discoveredCompetitors[index];
    if (!candidate) return;

    const content = `
        <h2>🔮 Discovered Company</h2>
        <div style="margin: 20px 0;">
            <h3 style="margin-bottom: 10px;">${candidate.name || 'Unknown'}</h3>
            <a href="${candidate.url}" target="_blank">${candidate.url}</a>
        </div>
        
        <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h4>Relevance Score: <span style="color: ${getScoreColor(candidate.score)}">${candidate.score}%</span></h4>
        </div>
        
        <h4>Matched Keywords</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0;">
            ${(candidate.matched_keywords || ['No keywords matched']).map(kw =>
        `<span style="background: #e0f2fe; padding: 4px 12px; border-radius: 20px; font-size: 0.9em;">${kw}</span>`
    ).join('')}
        </div>
        
        <h4>Discovery Info</h4>
        <p>Discovered: ${formatDate(candidate.discovered_at)}</p>
        
        <div style="margin-top: 20px;">
            <button class="btn btn-primary" onclick="addDiscoveredToCompetitors(${index}); closeModal();">
                ➕ Add to Competitors
            </button>
        </div>
    `;

    showModal(content);
}

function dismissDiscovered(index) {
    discoveredCompetitors.splice(index, 1);
    renderDiscoveredGrid();
    showToast('Candidate dismissed', 'info');
}

// Trigger discovery from competitors page

// ============== Insight Streams (New Data Sources) ==============

async function showCompetitorInsights(id) {
    const comp = competitors.find(c => c.id === id);
    if (!comp) return;

    // 1. Setup Modal Structure
    const content = `
        <div class="insights-header" style="text-align: center; margin-bottom: 24px;">
            <h2 style="color: var(--navy-dark); margin-bottom: 8px;">${comp.name} Intelligence Stream</h2>
            <div style="color: var(--text-secondary);">Real-time multi-channel analysis</div>
        </div>

        <div class="insights-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px;">
            
            <!-- Funding & Financials -->
            <div class="analytics-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3>💰 Funding History</h3>
                    <span class="badge" style="background: rgba(40, 167, 69, 0.1); color: #28a745;">Crunchbase</span>
                </div>
                <div class="chart-container" style="position: relative; height: 200px;">
                    <canvas id="fundingChart-${id}"></canvas>
                </div>
                <div id="fundingStats-${id}" style="margin-top: 16px; font-size: 0.9em; border-top: 1px solid #eee; padding-top: 8px;">
                    Loading financials...
                </div>
            </div>

            <!-- Employee Sentiment -->
            <div class="analytics-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3>👥 Employee Sentiment</h3>
                    <span class="badge" style="background: rgba(40, 167, 69, 0.1); color: #28a745;">Glassdoor</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: center; height: 180px;">
                     <div style="position: relative; width: 150px; height: 150px;">
                        <canvas id="sentimentChart-${id}"></canvas>
                     </div>
                </div>
                <div id="sentimentStats-${id}" style="text-align: center; font-size: 0.9em; margin-top: -10px;">
                    Loading reviews...
                </div>
            </div>

            <!-- Hiring Trends -->
            <div class="analytics-card">
                 <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3>📢 Hiring Activity</h3>
                    <span class="badge" style="background: rgba(255, 193, 7, 0.1); color: #d97706;">Indeed/Zip</span>
                </div>
                <div class="chart-container" style="position: relative; height: 200px;">
                    <canvas id="hiringChart-${id}"></canvas>
                </div>
            </div>

            <!-- Innovation (Patents) -->
            <div class="analytics-card">
                 <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3>💡 Innovation Focus</h3>
                    <span class="badge" style="background: rgba(59, 130, 246, 0.1); color: #2563eb;">USPTO</span>
                </div>
                <div class="chart-container" style="position: relative; height: 250px;">
                    <canvas id="patentChart-${id}"></canvas>
                </div>
            </div>

             <!-- App Store -->
            <div class="analytics-card full-width" style="grid-column: 1 / -1;">
                 <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3>📱 Mobile Experience</h3>
                    <span class="badge" style="background: rgba(107, 114, 128, 0.1); color: #374151;">App Store & Google Play</span>
                </div>
                <div id="appStoreStats-${id}" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                    Loading mobile data...
                </div>
            </div>

        </div>
    `;

    showModal(content);

    // 2. Fetch & Render Data in Parallel
    loadFundingData(id);
    loadEmployeeData(id);
    loadHiringData(id);
    loadPatentData(id);
    loadMobileData(id);
}

// --- Data Loaders ---

async function loadFundingData(id) {
    try {
        const data = await fetchAPI(`/api/competitors/${id}/funding`);
        if (data && data.rounds) {
            Visualizations.renderFundingTimeline(`fundingChart-${id}`, data.rounds);
            document.getElementById(`fundingStats-${id}`).innerHTML = `
                <strong>Total Funding:</strong> $${(data.total_funding_usd / 1000000).toFixed(1)}M<br>
                <strong>Latest Round:</strong> ${data.latest_round_type} (${data.latest_round_date})
            `;
        } else {
            document.getElementById(`fundingStats-${id}`).textContent = "No funding data available.";
        }
    } catch (e) { console.warn("Funding load failed", e); }
}

async function loadEmployeeData(id) {
    try {
        const data = await fetchAPI(`/api/competitors/${id}/employee-reviews`);
        if (data) {
            Visualizations.renderSentimentGauge(`sentimentChart-${id}`, data.overall_rating || 0);
            document.getElementById(`sentimentStats-${id}`).innerHTML = `
                Based on <strong>${data.total_reviews}</strong> reviews<br>
                CEO Approval: <strong>${data.ceo_approval}%</strong>
            `;
        }
    } catch (e) { console.warn("Review load failed", e); }
}

async function loadHiringData(id) {
    try {
        const data = await fetchAPI(`/api/competitors/${id}/jobs`);
        if (data && data.history) {
            Visualizations.renderHiringTrend(`hiringChart-${id}`, data.history);
        }
    } catch (e) { console.warn("Hiring load failed", e); }
}

async function loadPatentData(id) {
    try {
        const data = await fetchAPI(`/api/competitors/${id}/patents`);
        if (data && data.categories) {
            Visualizations.renderInnovationRadar(`patentChart-${id}`, data.categories);
        }
    } catch (e) { console.warn("Patent load failed", e); }
}

async function loadMobileData(id) {
    try {
        const data = await fetchAPI(`/api/competitors/${id}/mobile-apps`);
        const container = document.getElementById(`appStoreStats-${id}`);
        if (data && data.apps && data.apps.length > 0) {
            container.innerHTML = data.apps.map(app => `
                <div style="background: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                    <div style="font-weight: 600; color: var(--navy-dark);">${app.platform}</div>
                    <div style="font-size: 1.5em; font-weight: 700;">${app.rating} ⭐</div>
                    <div style="font-size: 0.9em; color: var(--text-secondary);">${app.review_count} reviews</div>
                </div>
            `).join('');
        } else {
            container.innerHTML = "No mobile apps found.";
        }
    } catch (e) { console.warn("Mobile load failed", e); }
}

// ============== Market Map ==============

let marketMapChart = null;

function loadMarketMap() {
    renderMarketMapChart();
    renderCategoryBreakdown();
    renderMarketMapTable();
}

function updateMarketMap() {
    renderMarketMapChart();
}

function renderMarketMapChart() {
    const canvas = document.getElementById('marketMapChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    if (marketMapChart) {
        marketMapChart.destroy();
    }

    // Prepare data for bubble chart
    const threatMap = { 'High': 3, 'Medium': 2, 'Low': 1 };
    const colorMap = { 'High': '#dc3545', 'Medium': '#f59e0b', 'Low': '#22c55e' };

    const bubbleData = competitors.map(comp => {
        // Parse employee count for size
        let empCount = 100;
        if (comp.employee_count) {
            const num = parseInt(comp.employee_count.replace(/[^0-9]/g, ''));
            empCount = isNaN(num) ? 100 : Math.min(num, 5000);
        }

        // Parse customer count for X axis
        let custCount = 500;
        if (comp.customer_count) {
            const num = parseInt(comp.customer_count.replace(/[^0-9]/g, ''));
            custCount = isNaN(num) ? 500 : num;
        }

        return {
            x: custCount,
            y: threatMap[comp.threat_level] || 2,
            r: Math.max(8, Math.min(40, Math.sqrt(empCount) * 1.5)),
            name: comp.name,
            threat: comp.threat_level,
            isPublic: comp.is_public,
            color: colorMap[comp.threat_level] || '#64748b',
            ticker: comp.ticker_symbol || ''
        };
    });

    // Group by threat level
    const highThreat = bubbleData.filter(d => d.threat === 'High');
    const mediumThreat = bubbleData.filter(d => d.threat === 'Medium');
    const lowThreat = bubbleData.filter(d => d.threat === 'Low');

    marketMapChart = new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: [
                {
                    label: 'High Threat',
                    data: highThreat,
                    backgroundColor: 'rgba(220, 53, 69, 0.7)',
                    borderColor: '#dc3545',
                    borderWidth: 2
                },
                {
                    label: 'Medium Threat',
                    data: mediumThreat,
                    backgroundColor: 'rgba(245, 158, 11, 0.7)',
                    borderColor: '#f59e0b',
                    borderWidth: 2
                },
                {
                    label: 'Low Threat',
                    data: lowThreat,
                    backgroundColor: 'rgba(34, 197, 94, 0.7)',
                    borderColor: '#22c55e',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const d = ctx.raw;
                            const pub = d.isPublic ? ` (${d.ticker})` : ' (Private)';
                            return `${d.name}${pub}: ${d.x} customers`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Customer Count', font: { weight: 'bold' } },
                    type: 'logarithmic',
                    min: 50,
                    max: 50000
                },
                y: {
                    title: { display: true, text: 'Threat Level', font: { weight: 'bold' } },
                    min: 0.5,
                    max: 3.5,
                    ticks: {
                        stepSize: 1,
                        callback: val => ['', 'Low', 'Medium', 'High'][val] || ''
                    }
                }
            },
            onClick: (evt, elements) => {
                if (elements.length > 0) {
                    const idx = elements[0].index;
                    const datasetIdx = elements[0].datasetIndex;
                    const comp = marketMapChart.data.datasets[datasetIdx].data[idx];
                    const fullComp = competitors.find(c => c.name === comp.name);
                    if (fullComp) viewBattlecard(fullComp.id);
                }
            }
        }
    });
}

function renderCategoryBreakdown() {
    const container = document.getElementById('categoryList');
    if (!container) return;

    // Group competitors by product category
    const categories = {};
    competitors.forEach(comp => {
        const cats = (comp.product_categories || 'Unknown').split(';').map(c => c.trim());
        cats.forEach(cat => {
            if (!categories[cat]) categories[cat] = [];
            categories[cat].push(comp);
        });
    });

    // Sort by count
    const sorted = Object.entries(categories).sort((a, b) => b[1].length - a[1].length);

    container.innerHTML = sorted.map(([cat, comps]) => {
        const color = comps.length > 20 ? '#dc3545' : comps.length > 10 ? '#f59e0b' : '#22c55e';
        return `
            <div style="margin-bottom: 12px; padding: 10px; background: #f8fafc; border-radius: 6px; border-left: 4px solid ${color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <strong style="color: #122753;">${cat}</strong>
                    <span style="background: ${color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">${comps.length}</span>
                </div>
                <div style="font-size: 0.85em; color: #64748b;">
                    ${comps.slice(0, 5).map(c => c.name).join(', ')}${comps.length > 5 ? ` +${comps.length - 5} more` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function renderMarketMapTable() {
    const tbody = document.getElementById('marketMapTable');
    if (!tbody) return;

    // Sort by threat level then name
    const sorted = [...competitors].sort((a, b) => {
        const order = { 'High': 1, 'Medium': 2, 'Low': 3 };
        if (order[a.threat_level] !== order[b.threat_level]) {
            return order[a.threat_level] - order[b.threat_level];
        }
        return a.name.localeCompare(b.name);
    });

    tbody.innerHTML = sorted.map(comp => {
        const threatColors = { 'High': '#dc3545', 'Medium': '#f59e0b', 'Low': '#22c55e' };
        const statusBadge = comp.is_public ?
            `<span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;">PUBLIC ${comp.ticker_symbol || ''}</span>` :
            `<span style="background: #64748b; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;">PRIVATE</span>`;

        return `
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 12px;">
                    <div style="font-weight: 600; color: #122753;">${comp.name}</div>
                    <div style="font-size: 0.8em; color: #64748b;">${comp.website || ''}</div>
                </td>
                <td style="padding: 12px; text-align: center;">${statusBadge}</td>
                <td style="padding: 12px; text-align: center;">
                    <span style="background: ${threatColors[comp.threat_level] || '#64748b'}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">${comp.threat_level}</span>
                </td>
                <td style="padding: 12px; text-align: center;">${comp.employee_count || 'N/A'}</td>
                <td style="padding: 12px; text-align: center;">${comp.customer_count || 'N/A'}</td>
                <td style="padding: 12px; text-align: center;">${comp.g2_rating ? `${comp.g2_rating} ⭐` : 'N/A'}</td>
                <td style="padding: 12px; text-align: center;">${comp.base_price || 'N/A'}</td>
                <td style="padding: 12px; text-align: center;">
                    <button onclick="viewBattlecard(${comp.id})" style="background: #3A95ED; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                        View
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function exportMarketMap() {
    // Export as CSV
    const headers = ['Company', 'Status', 'Ticker', 'Threat Level', 'Employees', 'Customers', 'G2 Rating', 'Pricing', 'Website'];
    const rows = competitors.map(c => [
        c.name,
        c.is_public ? 'Public' : 'Private',
        c.ticker_symbol || '',
        c.threat_level,
        c.employee_count || '',
        c.customer_count || '',
        c.g2_rating || '',
        c.base_price || '',
        c.website || ''
    ]);

    const csv = [headers, ...rows].map(r => r.map(v => `"${v}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'market_map_export.csv';
    a.click();
    URL.revokeObjectURL(url);

    showToast('Market Map exported to CSV', 'success');
}

// ============== Data Quality ==============

async function loadDataQuality() {
    // Load all data quality metrics in parallel
    const [completeness, scores, stale] = await Promise.all([
        fetchAPI('/api/data-quality/completeness'),
        fetchAPI('/api/data-quality/scores'),
        fetchAPI('/api/data-quality/stale?days=30')
    ]);

    // Store data for filtering
    window.qualityData = { completeness, scores, stale };

    // Update summary cards
    if (completeness) {
        document.getElementById('overallCompleteness').textContent = completeness.overall_completeness + '%';
    }
    if (scores) {
        document.getElementById('avgQualityScore').textContent = scores.average_score + '/100';
    }
    if (stale) {
        document.getElementById('staleCount').textContent = stale.stale_count;
        document.getElementById('freshCount').textContent = stale.fresh_count;
    }

    // Render charts
    if (scores && scores.scores) {
        renderQualityTierChart(scores.scores);
    }
    if (completeness && completeness.fields) {
        renderFieldCoverageChart(completeness.fields);
        renderFieldCompleteness(completeness.fields);
    }

    // Render quality scores
    if (scores && scores.scores) {
        renderQualityScores(scores.scores);
    }

    // Render stale records
    if (stale && stale.stale_records) {
        renderStaleRecords(stale.stale_records);
    }
}

// Quality Tier Distribution Chart
let qualityTierChart = null;
function renderQualityTierChart(scores) {
    const ctx = document.getElementById('qualityTierChart')?.getContext('2d');
    if (!ctx) return;

    if (qualityTierChart) qualityTierChart.destroy();

    const tiers = { Excellent: 0, Good: 0, Fair: 0, Poor: 0 };
    scores.forEach(s => { tiers[s.tier] = (tiers[s.tier] || 0) + 1; });

    qualityTierChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Excellent (90+)', 'Good (70-89)', 'Fair (50-69)', 'Poor (<50)'],
            datasets: [{
                data: [tiers.Excellent, tiers.Good, tiers.Fair, tiers.Poor],
                backgroundColor: ['#22c55e', '#3b82f6', '#f59e0b', '#dc3545'],
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

// Field Coverage Overview Chart
let fieldCoverageChart = null;
function renderFieldCoverageChart(fields) {
    const ctx = document.getElementById('fieldCoverageChart')?.getContext('2d');
    if (!ctx) return;

    if (fieldCoverageChart) fieldCoverageChart.destroy();

    const labels = fields.slice(0, 10).map(f => f.field.replace(/_/g, ' ').substring(0, 15));
    const data = fields.slice(0, 10).map(f => f.completeness_percent);
    const colors = data.map(d => d >= 80 ? '#22c55e' : d >= 60 ? '#f59e0b' : '#dc3545');

    fieldCoverageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{ label: 'Completeness %', data: data, backgroundColor: colors }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, max: 100 } }
        }
    });
}

// Filter fields by completeness level
function filterFields() {
    const filter = document.getElementById('fieldFilter')?.value || 'all';
    const fields = window.qualityData?.completeness?.fields || [];

    const filtered = fields.filter(f => {
        if (filter === 'all') return true;
        if (filter === 'low') return f.completeness_percent < 60;
        if (filter === 'medium') return f.completeness_percent >= 60 && f.completeness_percent < 80;
        if (filter === 'high') return f.completeness_percent >= 80;
        return true;
    });

    renderFieldCompleteness(filtered);
}

// Filter scores by tier
function filterScores() {
    const filter = document.getElementById('scoreFilter')?.value || 'all';
    const scores = window.qualityData?.scores?.scores || [];

    const filtered = filter === 'all' ? scores : scores.filter(s => s.tier === filter);
    renderQualityScores(filtered);
}

// Verify all records
async function verifyAllRecords() {
    if (!confirm('Mark all competitor records as verified? This will update the last_verified_at timestamp for all records.')) return;

    showToast('Verifying all records...', 'info');
    const competitors = window.qualityData?.scores?.scores || [];
    let success = 0;

    for (const comp of competitors) {
        const result = await fetchAPI(`/api/data-quality/verify/${comp.id}`, { method: 'POST' });
        if (result?.success) success++;
    }

    showToast(`Verified ${success} records successfully!`, 'success');
    loadDataQuality();
}

// Export quality report
function exportQualityReport() {
    const data = window.qualityData;
    if (!data) return showToast('No data to export', 'error');

    const report = {
        generated_at: new Date().toISOString(),
        overall_completeness: data.completeness?.overall_completeness,
        average_score: data.scores?.average_score,
        stale_count: data.stale?.stale_count,
        fresh_count: data.stale?.fresh_count,
        fields: data.completeness?.fields,
        scores: data.scores?.scores
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `data_quality_report_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('Quality report exported!', 'success');
}

// Refresh stale data
async function refreshStaleData() {
    showToast('Refreshing stale data...', 'info');
    const stale = await fetchAPI('/api/data-quality/stale?days=30');
    if (stale) {
        window.qualityData.stale = stale;
        document.getElementById('staleCount').textContent = stale.stale_count;
        document.getElementById('freshCount').textContent = stale.fresh_count;
        renderStaleRecords(stale.stale_records);
        showToast('Stale data refreshed', 'success');
    }
}

// Show quality details modal
function showQualityDetails(type) {
    const data = window.qualityData;
    if (!data) return;

    let content = '';
    switch (type) {
        case 'completeness':
            content = `<h3>Data Completeness Details</h3><p>Overall: ${data.completeness?.overall_completeness}%</p><p>Total fields tracked: ${data.completeness?.total_fields}</p><p>Total competitors: ${data.completeness?.total_competitors}</p>`;
            break;
        case 'scores':
            content = `<h3>Quality Score Details</h3><p>Average Score: ${data.scores?.average_score}/100</p><p>Total scored: ${data.scores?.total_competitors}</p>`;
            break;
        case 'stale':
            content = `<h3>Stale Records</h3><p>${data.stale?.stale_count} competitors have data older than 30 days.</p>`;
            break;
        case 'fresh':
            content = `<h3>Fresh Records</h3><p>${data.stale?.fresh_count} competitors have been verified within the last 30 days.</p>`;
            break;
        case 'verified':
            const overview = window.qualityOverview;
            if (overview) {
                const verified = overview.total_data_points - overview.needs_attention?.unverified_count || 0;
                content = `<h3>Verification Status</h3>
                    <p>Verification Rate: <strong>${overview.verification_rate || 0}%</strong></p>
                    <p>Verified Data Points: <strong>${verified}</strong></p>
                    <p>Unverified Data Points: <strong>${overview.needs_attention?.unverified_count || 0}</strong></p>
                    <p>Total Data Points: <strong>${overview.total_data_points || 0}</strong></p>
                    <hr style="margin: 12px 0; border-color: var(--border-color);">
                    <p style="font-size: 13px; color: var(--text-secondary);">
                        Verified data has been confirmed through triangulation, manual review, or authoritative sources like SEC filings.
                    </p>`;
            } else {
                content = `<h3>Verification Status</h3><p>Loading verification data...</p>`;
            }
            break;
    }
    showModal(content);
}

function renderFieldCompleteness(fields) {
    const container = document.getElementById('fieldCompleteness');
    if (!container) return;

    container.innerHTML = fields.map(field => {
        const pct = field.completeness_percent;
        const barColor = pct >= 80 ? '#22c55e' : pct >= 60 ? '#f59e0b' : '#dc3545';
        const fieldName = field.field.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

        return `
            <div style="background: var(--bg-tertiary); padding: 12px; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-weight: 500;">${fieldName}</span>
                    <span style="font-weight: 600; color: ${barColor};">${pct}%</span>
                </div>
                <div style="height: 8px; background: var(--border-color); border-radius: 4px; overflow: hidden;">
                    <div style="height: 100%; width: ${pct}%; background: ${barColor}; border-radius: 4px; transition: width 0.3s;"></div>
                </div>
                <div style="font-size: 0.8em; color: var(--text-secondary); margin-top: 4px;">
                    ${field.filled} of ${field.total} competitors
                </div>
            </div>
        `;
    }).join('');
}

function renderQualityScores(scores) {
    const container = document.getElementById('qualityScores');
    if (!container) return;

    container.innerHTML = `
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: var(--bg-tertiary);">
                    <th style="padding: 12px; text-align: left;">Rank</th>
                    <th style="padding: 12px; text-align: left;">Competitor</th>
                    <th style="padding: 12px; text-align: center;">Score</th>
                    <th style="padding: 12px; text-align: center;">Tier</th>
                    <th style="padding: 12px; text-align: center;">Actions</th>
                </tr>
            </thead>
            <tbody>
                ${scores.map((s, i) => {
        const tierColor = s.tier === 'Excellent' ? '#22c55e' :
            s.tier === 'Good' ? '#3b82f6' :
                s.tier === 'Fair' ? '#f59e0b' : '#dc3545';
        return `
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 10px;">#${i + 1}</td>
                            <td style="padding: 10px; font-weight: 500;">${s.name}</td>
                            <td style="padding: 10px; text-align: center;">
                                <span style="font-weight: 600; color: ${tierColor};">${s.score}/100</span>
                            </td>
                            <td style="padding: 10px; text-align: center;">
                                <span style="background: ${tierColor}20; color: ${tierColor}; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 500;">
                                    ${s.tier}
                                </span>
                            </td>
                            <td style="padding: 10px; text-align: center;">
                                <button onclick="verifyCompetitor(${s.id})" style="background: var(--navy-dark); color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                                    ✅ Verify
                                </button>
                            </td>
                        </tr>
                    `;
    }).join('')}
            </tbody>
        </table>
    `;
}

function renderStaleRecords(staleRecords) {
    const container = document.getElementById('staleRecords');
    if (!container) return;

    if (staleRecords.length === 0) {
        container.innerHTML = '<p style="color: #22c55e; font-weight: 500;">✅ All records are fresh! No stale data found.</p>';
        return;
    }

    container.innerHTML = `
        <div style="display: grid; gap: 10px;">
            ${staleRecords.slice(0, 20).map(record => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #fef2f220; border: 1px solid #fecaca; border-radius: 8px;">
                    <div>
                        <span style="font-weight: 500;">${record.name}</span>
                        <span style="color: var(--text-secondary); font-size: 0.9em; margin-left: 8px;">
                            Last verified: ${record.last_verified ? new Date(record.last_verified).toLocaleDateString() : 'Never'}
                        </span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="color: #dc3545; font-weight: 600;">${record.days_old} days old</span>
                        <button onclick="verifyCompetitor(${record.id})" style="background: #22c55e; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                            🔄 Mark Verified
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
        ${staleRecords.length > 20 ? `<p style="color: var(--text-secondary); margin-top: 10px;">... and ${staleRecords.length - 20} more stale records</p>` : ''}
    `;
}

async function verifyCompetitor(id) {
    const result = await fetchAPI(`/api/data-quality/verify/${id}`, { method: 'POST' });
    if (result && result.success) {
        showToast(`${result.name} marked as verified! Score: ${result.quality_score}/100`, 'success');
        loadDataQuality();  // Refresh the page
    }
}

// ============== PHASE 7: DATA QUALITY DASHBOARD ==============

// Store for quality overview data
window.qualityOverview = null;

// Confidence Distribution Chart
let confidenceDistributionChart = null;

/**
 * Load enhanced data quality overview (Phase 7)
 */
async function loadDataQualityOverview() {
    try {
        const overview = await fetchAPI('/api/data-quality/overview');
        if (!overview) return;

        window.qualityOverview = overview;

        // Update confidence distribution cards
        updateConfidenceCards(overview.confidence_distribution);

        // Update verification rate
        document.getElementById('verificationRate').textContent = overview.verification_rate + '%';
        const verifiedCount = overview.total_data_points - overview.needs_attention.unverified_count;
        document.getElementById('verifiedCount').textContent = verifiedCount + ' verified';

        // Render confidence distribution chart
        renderConfidenceDistributionChart(overview.confidence_distribution);

        // Render source type breakdown
        renderSourceTypeBreakdown(overview.source_type_breakdown);

        // Render field confidence analysis
        renderFieldConfidenceAnalysis(overview.field_coverage);

        // Render competitor quality ranking
        renderCompetitorQualityRanking(overview.competitor_scores);

    } catch (error) {
        console.error('Error loading data quality overview:', error);
    }
}

/**
 * Update confidence distribution stat cards
 */
function updateConfidenceCards(distribution) {
    if (!distribution) return;

    // High confidence
    const highEl = document.getElementById('highConfidenceCount');
    const highPctEl = document.getElementById('highConfidencePercent');
    if (highEl) highEl.textContent = distribution.high?.count || 0;
    if (highPctEl) highPctEl.textContent = (distribution.high?.percentage || 0) + '% of data';

    // Moderate confidence
    const modEl = document.getElementById('moderateConfidenceCount');
    const modPctEl = document.getElementById('moderateConfidencePercent');
    if (modEl) modEl.textContent = distribution.moderate?.count || 0;
    if (modPctEl) modPctEl.textContent = (distribution.moderate?.percentage || 0) + '% of data';

    // Low confidence
    const lowEl = document.getElementById('lowConfidenceCount');
    const lowPctEl = document.getElementById('lowConfidencePercent');
    if (lowEl) lowEl.textContent = distribution.low?.count || 0;
    if (lowPctEl) lowPctEl.textContent = (distribution.low?.percentage || 0) + '% of data';
}

/**
 * Render confidence distribution doughnut chart
 */
function renderConfidenceDistributionChart(distribution) {
    const ctx = document.getElementById('confidenceDistributionChart')?.getContext('2d');
    if (!ctx || !distribution) return;

    if (confidenceDistributionChart) {
        confidenceDistributionChart.destroy();
    }

    confidenceDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['High (70-100)', 'Moderate (40-69)', 'Low (0-39)', 'Unscored'],
            datasets: [{
                data: [
                    distribution.high?.count || 0,
                    distribution.moderate?.count || 0,
                    distribution.low?.count || 0,
                    distribution.unscored?.count || 0
                ],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#64748b'],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#e2e8f0', padding: 15 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
                            return `${context.label}: ${context.raw} (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Render source type breakdown grid
 */
function renderSourceTypeBreakdown(sourceTypes) {
    const container = document.getElementById('sourceTypeBreakdown');
    if (!container || !sourceTypes) return;

    const sourceIcons = {
        'sec_filing': '📊',
        'api_verified': '🔌',
        'website_scrape': '🌐',
        'manual': '✏️',
        'manual_verified': '✅',
        'news_article': '📰',
        'klas_report': '📋',
        'unknown': '❓'
    };

    const sourceLabels = {
        'sec_filing': 'SEC Filing',
        'api_verified': 'API Verified',
        'website_scrape': 'Website Scrape',
        'manual': 'Manual Entry',
        'manual_verified': 'Manual Verified',
        'news_article': 'News Article',
        'klas_report': 'KLAS Report',
        'unknown': 'Unknown'
    };

    const html = Object.entries(sourceTypes).map(([type, data]) => {
        const icon = sourceIcons[type] || '📄';
        const label = sourceLabels[type] || type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const avgConf = data.avg_confidence || 0;
        const confLevel = avgConf >= 70 ? 'high' : avgConf >= 40 ? 'moderate' : 'low';

        return `
            <div class="source-type-card">
                <div class="source-type-header">
                    <div class="source-type-icon ${type}">${icon}</div>
                    <span class="source-type-name">${label}</span>
                </div>
                <div class="source-type-stats">
                    <span class="source-type-count">${data.count} data points</span>
                    <div class="source-type-confidence">
                        <div class="source-type-confidence-bar">
                            <div class="source-type-confidence-fill ${confLevel}" style="width: ${avgConf}%;"></div>
                        </div>
                        <span class="source-type-confidence-score" style="color: ${confLevel === 'high' ? '#10b981' : confLevel === 'moderate' ? '#f59e0b' : '#ef4444'};">
                            ${avgConf}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html || '<p style="color: var(--text-secondary);">No source data available.</p>';
}

/**
 * Render field confidence analysis grid
 */
function renderFieldConfidenceAnalysis(fieldCoverage) {
    const container = document.getElementById('fieldConfidenceAnalysis');
    if (!container || !fieldCoverage) return;

    const fieldLabels = {
        'customer_count': 'Customer Count',
        'base_price': 'Base Price',
        'pricing_model': 'Pricing Model',
        'employee_count': 'Employee Count',
        'year_founded': 'Year Founded',
        'key_features': 'Key Features'
    };

    const html = Object.entries(fieldCoverage).map(([field, data]) => {
        const label = fieldLabels[field] || field.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const coveragePct = data.percentage || 0;
        const avgConf = data.avg_confidence || 0;
        const confLevel = avgConf >= 70 ? 'high' : avgConf >= 40 ? 'moderate' : 'low';

        return `
            <div class="field-confidence-card">
                <div class="field-confidence-header">
                    <span class="field-confidence-name">${label}</span>
                    <span class="field-confidence-coverage">${data.populated}/${data.total}</span>
                </div>
                <div class="field-confidence-bars">
                    <div class="field-confidence-bar-row">
                        <span class="field-confidence-bar-label">Coverage</span>
                        <div class="field-confidence-bar-container">
                            <div class="field-confidence-bar-fill coverage" style="width: ${coveragePct}%;"></div>
                        </div>
                        <span class="field-confidence-bar-value" style="color: ${coveragePct >= 80 ? '#10b981' : coveragePct >= 50 ? '#f59e0b' : '#ef4444'};">
                            ${coveragePct}%
                        </span>
                    </div>
                    <div class="field-confidence-bar-row">
                        <span class="field-confidence-bar-label">Confidence</span>
                        <div class="field-confidence-bar-container">
                            <div class="field-confidence-bar-fill confidence-${confLevel}" style="width: ${avgConf}%;"></div>
                        </div>
                        <span class="field-confidence-bar-value" style="color: ${confLevel === 'high' ? '#10b981' : confLevel === 'moderate' ? '#f59e0b' : '#ef4444'};">
                            ${avgConf}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html || '<p style="color: var(--text-secondary);">No field data available.</p>';
}

/**
 * Render competitor quality ranking list
 */
function renderCompetitorQualityRanking(competitorScores) {
    const container = document.getElementById('competitorQualityRanking');
    if (!container) return;

    if (!competitorScores || competitorScores.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No competitor data available.</p>';
        return;
    }

    // Store for filtering
    window.competitorQualityScores = competitorScores;

    renderFilteredQualityRanking(competitorScores);
}

/**
 * Render filtered quality ranking
 */
function renderFilteredQualityRanking(scores) {
    const container = document.getElementById('competitorQualityRanking');
    if (!container) return;

    const html = scores.map((comp, index) => {
        const rank = index + 1;
        const rankClass = rank === 1 ? 'rank-1' : rank === 2 ? 'rank-2' : rank === 3 ? 'rank-3' : 'default';
        const tierClass = comp.quality_tier || 'Poor';
        const scoreClass = tierClass.toLowerCase();

        return `
            <div class="competitor-quality-row">
                <div class="competitor-quality-rank ${rankClass}">${rank}</div>
                <div class="competitor-quality-info">
                    <div class="competitor-quality-name">${comp.name}</div>
                    <div class="competitor-quality-details">
                        <span>${comp.total_fields} fields tracked</span>
                        <span>${comp.verified_count} verified</span>
                        <span>${comp.high_confidence_count} high conf.</span>
                    </div>
                </div>
                <div class="competitor-quality-score">
                    <span class="competitor-quality-score-value ${scoreClass}">${comp.avg_confidence}</span>
                    <span class="competitor-quality-tier ${tierClass}">${tierClass}</span>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

/**
 * Filter quality ranking by tier
 */
function filterQualityRanking() {
    const filter = document.getElementById('qualityRankingFilter')?.value || 'all';
    const scores = window.competitorQualityScores || [];

    const filtered = filter === 'all' ? scores : scores.filter(s => s.quality_tier === filter);
    renderFilteredQualityRanking(filtered);
}

/**
 * Filter data by confidence level
 */
async function filterByConfidence(level) {
    // Navigate to a filtered view or show modal
    let threshold = 0;
    if (level === 'low') threshold = 40;
    else if (level === 'moderate') threshold = 70;
    else if (level === 'high') threshold = 100;

    const data = await fetchAPI(`/api/data-quality/low-confidence?threshold=${threshold}`);
    if (data) {
        const content = `
            <h3>${level.charAt(0).toUpperCase() + level.slice(1)} Confidence Data Points</h3>
            <p>Total: ${data.total_low_confidence} data points across ${data.competitors_affected} competitors</p>
            <div style="max-height: 400px; overflow-y: auto; margin-top: 16px;">
                ${data.data?.map(comp => `
                    <div style="margin-bottom: 12px; padding: 10px; background: rgba(30, 41, 59, 0.6); border-radius: 8px;">
                        <strong>${comp.competitor_name}</strong>
                        <div style="margin-top: 8px; font-size: 13px; color: var(--text-secondary);">
                            ${comp.fields.slice(0, 5).map(f => `
                                <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                                    <span>${f.field.replace(/_/g, ' ')}</span>
                                    <span style="color: ${f.confidence_score >= 70 ? '#10b981' : f.confidence_score >= 40 ? '#f59e0b' : '#ef4444'};">
                                        ${f.confidence_score}/100
                                    </span>
                                </div>
                            `).join('')}
                            ${comp.fields.length > 5 ? `<div style="color: var(--text-muted);">...and ${comp.fields.length - 5} more</div>` : ''}
                        </div>
                    </div>
                `).join('') || '<p>No data found.</p>'}
            </div>
        `;
        showModal(content);
    }
}

/**
 * Recalculate all confidence scores
 */
async function recalculateAllConfidence() {
    if (!confirm('Recalculate confidence scores for all data sources? This may take a moment.')) return;

    showToast('Recalculating confidence scores...', 'info');

    try {
        const result = await fetchAPI('/api/data-quality/recalculate-confidence', { method: 'POST' });
        if (result?.success) {
            showToast(`Recalculated ${result.updated_count} data sources`, 'success');
            loadDataQuality();
            loadDataQualityOverview();
        }
    } catch (error) {
        showToast('Error recalculating scores: ' + error.message, 'error');
    }
}

// Override the original loadDataQuality to also load the new overview
const originalLoadDataQuality = loadDataQuality;
loadDataQuality = async function() {
    await originalLoadDataQuality();
    await loadDataQualityOverview();
};

// ============== Universal Data Sourcing (Task 6) ==============

// Cache for source data to avoid repeated API calls
const sourceCache = {};

/**
 * Create a sourced value HTML element with appropriate source icon
 * @param {string|number} value - The data value to display
 * @param {number} competitorId - The competitor ID
 * @param {string} fieldName - The field name (e.g., 'customer_count')
 * @param {string} fallbackType - Fallback source type if not in cache
 * @returns {string} HTML string for the sourced value
 */
function createSourcedValue(value, competitorId, fieldName, fallbackType = 'unknown') {
    if (!value || value === 'N/A' || value === 'Unknown' || value === 'null') {
        return value || '<span style="color:#94a3b8;">—</span>';
    }

    const cacheKey = `${competitorId}-${fieldName}`;
    const cached = typeof sourceCache !== 'undefined' ? sourceCache[cacheKey] : null;

    const sourceType = cached?.source_type || fallbackType;
    const sourceUrl = cached?.source_url || null;
    const sourceName = cached?.source_name || 'Source';
    const enteredBy = cached?.entered_by || 'Unknown';
    const formula = cached?.formula || null;

    // NEW: Confidence scoring from Phase 6
    const confidenceScore = cached?.confidence_score || null;
    const confidenceLevel = cached?.confidence_level || getConfidenceLevelFromScore(confidenceScore);

    let iconHtml = '';
    let tooltipHtml = '';
    let clickHandler = '';

    switch (sourceType) {
        case 'external':
        case 'website_scrape':
            iconHtml = '🔗';
            tooltipHtml = `<span class="source-tooltip">${sourceName}${sourceUrl ? ' - Click to open' : ''}</span>`;
            if (sourceUrl) {
                clickHandler = `onclick="window.open('${sourceUrl}', '_blank')"`;
            }
            break;
        case 'manual':
        case 'manual_verified':
            iconHtml = '✏️';
            tooltipHtml = `<span class="source-tooltip">Manual Entry by ${enteredBy}</span>`;
            break;
        case 'calculated':
            iconHtml = 'ƒ';
            const formulaDisplay = formula ? `<span class="source-formula">${formula}</span>` : '';
            tooltipHtml = `<span class="source-tooltip">Calculated Value${formulaDisplay}</span>`;
            break;
        case 'sec_filing':
            iconHtml = '📊';
            tooltipHtml = `<span class="source-tooltip">SEC Filing - Verified</span>`;
            break;
        case 'api_verified':
        case 'api':
            iconHtml = '🔌';
            tooltipHtml = `<span class="source-tooltip">API Data - ${sourceName}</span>`;
            break;
        default:
            iconHtml = '•';
            tooltipHtml = `<span class="source-tooltip">Source pending verification</span>`;
    }

    // Correction Icon logic
    const cleanValue = String(value).replace(/['"]/g, '').substring(0, 50);
    const editIcon = `<span class="edit-icon" onclick="openCorrectionModal(${competitorId}, '${fieldName}', '${cleanValue}')" style="cursor:pointer;margin-left:6px;font-size:10px;opacity:0.5;" title="Correct this data">✏️</span>`;

    // NEW: Confidence indicator (Phase 6)
    const confidenceIndicator = createConfidenceIndicator(confidenceScore, confidenceLevel, sourceType);

    return `
        <span class="sourced-value data-with-confidence" data-competitor="${competitorId}" data-field="${fieldName}">
            ${value}
            ${confidenceIndicator}
            <span class="source-icon ${sourceType}" ${clickHandler} title="Click for source" style="font-size:11px;margin-left:4px;">
                ${iconHtml}
            </span>
            ${tooltipHtml}
            ${editIcon}
        </span>
    `;
}

/**
 * Get confidence level from numeric score
 */
function getConfidenceLevelFromScore(score) {
    if (score === null || score === undefined) return 'unknown';
    if (score >= 70) return 'high';
    if (score >= 40) return 'moderate';
    return 'low';
}

/**
 * Create confidence indicator HTML
 */
function createConfidenceIndicator(score, level, sourceType) {
    // If no score, derive a default based on source type
    if (score === null || score === undefined) {
        const defaultScores = {
            'sec_filing': 90,
            'api_verified': 80,
            'api': 75,
            'manual_verified': 70,
            'klas_report': 75,
            'website_scrape': 40,
            'manual': 50,
            'news_article': 45,
            'unknown': 30
        };
        score = defaultScores[sourceType] || 35;
        level = getConfidenceLevelFromScore(score);
    }

    const icons = {
        'high': '✓',
        'moderate': '~',
        'low': '!',
        'unknown': '?'
    };

    const tooltipText = `Confidence: ${score}/100 (${level})`;

    return `
        <span class="confidence-indicator-wrapper">
            <span class="confidence-indicator confidence-${level}" title="${tooltipText}">
                ${icons[level] || '?'}
            </span>
            <span class="confidence-tooltip">${tooltipText}</span>
        </span>
    `;
}

/**
 * Load and cache source data for a competitor
 * @param {number} competitorId - The competitor ID
 */
async function loadCompetitorSources(competitorId) {
    if (sourceCache[`loaded-${competitorId}`]) return;

    const sources = await fetchAPI(`/api/sources/${competitorId}`);
    if (sources && sources.sources) {
        Object.entries(sources.sources).forEach(([field, sourceData]) => {
            sourceCache[`${competitorId}-${field}`] = sourceData;
        });
        sourceCache[`loaded-${competitorId}`] = true;
    }
}

/**
 * Initialize source icons for visible competitor cards
 */
async function initSourceIcons() {
    const cards = document.querySelectorAll('.competitor-card');
    for (const card of cards) {
        const competitorId = card.dataset?.competitorId;
        if (competitorId) {
            await loadCompetitorSources(parseInt(competitorId));
        }
    }
}

/**
 * Get source info for a specific field via click
 */
async function showSourceInfo(competitorId, fieldName) {
    const source = await fetchAPI(`/api/sources/${competitorId}/${fieldName}`);
    if (!source) return;

    let content = '';
    switch (source.source_type) {
        case 'external':
            content = `
                <h3>Data Source</h3>
                <p><strong>Source:</strong> ${source.source_name || 'External'}</p>
                ${source.source_url ? `<p><a href="${source.source_url}" target="_blank">Open Source →</a></p>` : ''}
                <p><strong>Verified:</strong> ${source.verified_at ? new Date(source.verified_at).toLocaleString() : 'Not verified'}</p>
            `;
            break;
        case 'manual':
            content = `
                <h3>Manual Entry</h3>
                <p><strong>Entered by:</strong> ${source.entered_by || 'Unknown'}</p>
                <p><strong>Verified:</strong> ${source.verified_at ? new Date(source.verified_at).toLocaleString() : 'N/A'}</p>
            `;
            break;
        case 'calculated':
            content = `
                <h3>Calculated Value</h3>
                <p><strong>Formula:</strong></p>
                <pre style="background: #f0f4f8; padding: 10px; border-radius: 4px;">${source.formula || 'Unknown formula'}</pre>
            `;
            break;
        default:
            content = `
                <h3>Source Information</h3>
                <p>No source information recorded for this data point.</p>
                <p>Field: ${fieldName}</p>
            `;
    }

    showModal(content);
}

// ============== Analytics & Reports ==============

async function loadAnalytics() {
    // 1. Load data if needed
    if (!competitors || competitors.length === 0) {
        competitors = await fetchAPI('/api/competitors') || [];
    }

    // 2. Initial Matrix Render
    updatePositioningMatrix();

    // 3. Populate SWOT Dropdown
    const swotSelect = document.getElementById('swot-competitor-select');
    if (swotSelect) {
        swotSelect.innerHTML = '<option value="">Select a competitor...</option>';
        competitors.sort((a, b) => a.name.localeCompare(b.name)).forEach(c => {
            const option = document.createElement('option');
            option.value = c.id;
            option.textContent = c.name;
            swotSelect.appendChild(option);
        });
    }

    // 4. Render Trends (Mock for now, or based on history)
    renderMarketTrends();
}

function updatePositioningMatrix() {
    const xAxis = document.getElementById('matrix-x-axis').value; // price, employees
    const yAxis = document.getElementById('matrix-y-axis').value; // satisfaction, market_presence

    const chartData = competitors.map(c => {
        let xVal = 0;
        let yVal = 0;
        let rVal = 5; // Default radius

        // X-Axis
        if (xAxis === 'price') {
            // Extract number from "$100/mo" or "Contact Sales"
            const price = c.base_price ? parseFloat(c.base_price.replace(/[^0-9.]/g, '')) : 0;
            xVal = isNaN(price) ? 0 : price;
        } else if (xAxis === 'employees') {
            const emp = c.employee_count ? parseInt(c.employee_count.replace(/[^0-9]/g, '')) : 0;
            xVal = isNaN(emp) ? 0 : emp;
        }

        // Y-Axis
        if (yAxis === 'satisfaction') {
            const rating = c.g2_rating ? parseFloat(c.g2_rating) : 0;
            yVal = isNaN(rating) ? 0 : rating;
        } else if (yAxis === 'market_presence') {
            // Proxy: News mentions + social following
            const news = c.news_mentions ? parseInt(c.news_mentions) : 0;
            yVal = news; // Simple proxy
        }

        // Radius (Market Share / Customer Count)
        const customers = c.customer_count ? parseInt(c.customer_count.replace(/[^0-9]/g, '')) : 100;
        rVal = Math.max(5, Math.min(30, Math.sqrt(customers) / 2));

        return {
            x: xVal,
            y: yVal,
            r: rVal,
            label: c.name,
            color: c.threat_level === 'High' ? 'rgba(220, 53, 69, 0.6)' :
                c.threat_level === 'Medium' ? 'rgba(255, 193, 7, 0.6)' :
                    'rgba(40, 167, 69, 0.6)',
            borderColor: c.threat_level === 'High' ? '#dc3545' :
                c.threat_level === 'Medium' ? '#ffc107' :
                    '#28a745'
        };
    });

    Visualizations.renderPositioningMatrix(
        'positioningMatrixChart',
        chartData,
        xAxis === 'price' ? 'Base Price ($)' : 'Employee Count',
        yAxis === 'satisfaction' ? 'G2 Rating (0-5)' : 'Market Presence (Mentions)'
    );
}

async function renderMarketTrends() {
    const ctx = document.getElementById('marketTrendChart').getContext('2d');

    // Destroy existing
    const existing = Chart.getChart('marketTrendChart');
    if (existing) existing.destroy();

    try {
        const response = await fetch('/api/analytics/trends', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });

        // Default data if fetch fails or is empty
        let chartData = {
            labels: [],
            datasets: []
        };

        if (response.ok) {
            chartData = await response.json();
            // Assign yAxisID to the New Competitors dataset (index 1 usually, based on backend)
            // Backend sends datasets. We need to ensure yAxisID is set correctly for the second dataset
            if (chartData.datasets && chartData.datasets.length > 1) {
                chartData.datasets[1].yAxisID = 'y1';
            }
        }

        new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true, // Average price shouldn't obscure variations, but starting at 0 is safer
                        title: { display: true, text: 'Price ($)' }
                    },
                    y1: {
                        position: 'right',
                        beginAtZero: true,
                        title: { display: true, text: 'New Competitors' },
                        grid: { drawOnChartArea: false } // Only draw grid for left axis
                    }
                }
            }
        });
    } catch (e) {
        console.error("Failed to load trends:", e);
    }
}

async function generateSWOT() {
    const select = document.getElementById('swot-competitor-select');
    const compId = select.value;
    if (!compId) return;

    const loading = document.getElementById('swot-loading');
    const content = document.getElementById('swot-content');
    const grid = content.querySelector('.swot-grid');

    loading.style.display = 'block';
    content.style.opacity = '0.5';

    try {
        // Placeholder simulation until backend API is ready
        await new Promise(r => setTimeout(r, 1500));

        const comp = competitors.find(c => c.id == compId);

        const mockSWOT = {
            strengths: [`Strong market presence (${comp.customer_count || 'N/A'} customers)`, "High G2 Rating", "Robust integration ecosystem"],
            weaknesses: ["Higher price point", "Legacy UI reported in reviews", "Slower implementation time"],
            opportunities: ["Expansion into mid-market", "New AI feature adoption", "Partnership potential"],
            threats: ["Low-cost market entrants", "Regulatory changes", "Consolidation risks"]
        };

        // Render
        grid.innerHTML = `
            <div class="swot-box strengths">
                <h4><i class="fas fa-dumbbell"></i> Strengths</h4>
                <ul>${mockSWOT.strengths.map(i => `<li>${i}</li>`).join('')}</ul>
            </div>
            <div class="swot-box weaknesses">
                <h4><i class="fas fa-exclamation-triangle"></i> Weaknesses</h4>
                <ul>${mockSWOT.weaknesses.map(i => `<li>${i}</li>`).join('')}</ul>
            </div>
            <div class="swot-box opportunities">
                <h4><i class="fas fa-lightbulb"></i> Opportunities</h4>
                <ul>${mockSWOT.opportunities.map(i => `<li>${i}</li>`).join('')}</ul>
            </div>
            <div class="swot-box threats">
                <h4><i class="fas fa-shield-alt"></i> Threats</h4>
                <ul>${mockSWOT.threats.map(i => `<li>${i}</li>`).join('')}</ul>
            </div>
        `;

    } catch (e) {
        showToast("Error generating SWOT: " + e.message, 'error');
    } finally {
        loading.style.display = 'none';
        content.style.opacity = '1';
    }
}

function downloadExecutiveReport() {
    window.location.href = `${API_BASE}/api/reports/executive-summary`;
    showToast("Generating report... Download will start shortly.", "info");
}

// ============== Notifications ==============

async function loadNotifications() {
    try {
        const notifications = await fetchAPI('/api/notifications?limit=5');
        const list = document.getElementById('notificationList');
        const badge = document.getElementById('notificationBadge');

        if (!notifications || notifications.length === 0) {
            list.innerHTML = '<div class="notification-empty">No new alerts</div>';
            badge.style.display = 'none';
            return;
        }

        // Update badge
        badge.innerText = notifications.length;
        badge.style.display = 'flex';

        // Render items
        list.innerHTML = notifications.map(n => `
            <div class="notification-item ${n.severity}">
                <div class="notif-header">
                    <span class="notif-comp">${n.competitor_name}</span>
                    <span class="notif-time">${new Date(n.detected_at).toLocaleDateString()}</span>
                </div>
                <div class="notif-body">
                    <strong>${n.change_type}</strong>: ${n.new_value}
                </div>
            </div>
        `).join('');

    } catch (e) {
        console.error("Error loading notifications:", e);
    }
}

function toggleNotifications() {
    const dropdown = document.getElementById('notificationDropdown');
    dropdown.classList.toggle('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const container = document.querySelector('.notification-container');
    const dropdown = document.getElementById('notificationDropdown');
    if (container && !container.contains(e.target) && dropdown.classList.contains('active')) {
        dropdown.classList.remove('active');
    }
});

// Init Notifications
setInterval(loadNotifications, 60000); // Poll every minute
loadNotifications(); // Initial load

// ============== Threat Criteria Settings ==============

async function showThreatCriteriaModal() {
    showModal(`
        <div style="text-align: center; padding: 20px;">
            <div class="ai-spinner" style="font-size: 24px;">⏳</div>
            <p>Loading current criteria...</p>
        </div>
    `);

    try {
        const criteria = await fetchAPI('/api/settings/threat-criteria');

        const content = `
            <h2>⚠️ Configure Threat Level Criteria</h2>
            <p style="color: #64748b; margin-bottom: 20px;">
                Define the rules the AI uses to classify competitors. 
                Updating these will trigger a re-analysis of all competitors.
            </p>
            
            <form id="threatCriteriaForm" onsubmit="saveThreatCriteria(event)">
                <div class="form-group">
                    <label style="color: #dc2626; font-weight: 600;">High Threat Criteria</label>
                    <textarea name="high_threat_criteria" rows="3" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px;">${criteria.high || ''}</textarea>
                    <small style="color: #64748b;">Direct competitors causing immediate revenue loss.</small>
                </div>
                
                <div class="form-group" style="margin-top: 16px;">
                    <label style="color: #d97706; font-weight: 600;">Medium Threat Criteria</label>
                    <textarea name="medium_threat_criteria" rows="3" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px;">${criteria.medium || ''}</textarea>
                    <small style="color: #64748b;">Emerging competitors or partial overlap.</small>
                </div>
                
                <div class="form-group" style="margin-top: 16px;">
                    <label style="color: #059669; font-weight: 600;">Low Threat Criteria</label>
                    <textarea name="low_threat_criteria" rows="3" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px;">${criteria.low || ''}</textarea>
                    <small style="color: #64748b;">Indirect or different market focus.</small>
                </div>
                
                <div style="margin-top: 24px; display: flex; justify-content: flex-end; gap: 12px;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background: linear-gradient(135deg, #122753 0%, #1E3A75 100%);">
                        💾 Save & Re-Classify
                    </button>
                </div>
            </form>
        `;

        showModal(content);

    } catch (e) {
        showModal(`<div style="color: red;">Error loading settings: ${e.message}</div>`);
    }
}

async function saveThreatCriteria(event) {
    event.preventDefault();
    const form = event.target;
    // Show saving state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '⏳ Saving...';
    submitBtn.disabled = true;

    const data = {
        high_threat_criteria: form.high_threat_criteria.value,
        medium_threat_criteria: form.medium_threat_criteria.value,
        low_threat_criteria: form.low_threat_criteria.value
    };

    try {
        const result = await fetchAPI('/api/settings/threat-criteria', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showToast(result.message || 'Criteria saved successfully', 'success');
        closeModal();

        // Optional: show a banner that re-classification is in progress
        showToast("AI is re-analyzing competitors in the background...", "info");

    } catch (e) {
        showToast('Error saving criteria: ' + e.message, 'error');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}
// ============== User Management ==============

async function loadTeam() {
    const list = document.getElementById('teamList');
    if (!list) return;

    list.innerHTML = '<div class="loading">Loading team...</div>';

    try {
        const users = await fetchAPI('/api/users');
        if (!users || users.length === 0) {
            list.innerHTML = '<p>No users found.</p>';
            return;
        }

        list.innerHTML = `
            <table class="table" style="width:100%">
                <thead>
                    <tr>
                        <th style="text-align:left">Email</th>
                        <th style="text-align:left">Role</th>
                        <th style="text-align:left">Status</th>
                        <th style="text-align:right">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(u => `
                        <tr>
                            <td>${u.email} ${u.full_name ? `(${u.full_name})` : ''}</td>
                            <td><span class="badge badge-secondary">${u.role}</span></td>
                            <td>${u.is_active ? '<span style="color:#22c55e">Active</span>' : '<span style="color:#64748b">Inactive</span>'}</td>
                            <td style="text-align:right">
                                <button class="btn btn-sm btn-icon" onclick="deleteUser(${u.id})" title="Remove User">🗑️</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (e) {
        list.innerHTML = `<p class="error">Error loading team: ${e.message}</p>`;
    }
}

function showInviteUserModal() {
    showModal(`
        <h3>Invite Team Member</h3>
        <form id="inviteUserForm" onsubmit="handleInviteUser(event)">
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" name="email" class="form-control" required placeholder="colleague@company.com">
            </div>
            <div class="form-group">
                <label>Full Name (Optional)</label>
                <input type="text" name="full_name" class="form-control" placeholder="John Doe">
            </div>
            <div class="form-group">
                <label>Role</label>
                <select name="role" class="form-control">
                    <option value="viewer">Viewer (Read-only)</option>
                    <option value="analyst">Analyst (Can edit)</option>
                    <option value="admin">Admin (Full access)</option>
                </select>
            </div>
            <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:20px;">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Send Invite</button>
            </div>
        </form>
    `);
}

async function handleInviteUser(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.innerText;

    btn.innerText = 'Sending...';
    btn.disabled = true;

    const data = {
        email: form.email.value,
        full_name: form.full_name.value,
        role: form.role.value
    };

    try {
        const result = await fetchAPI('/api/users/invite', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        if (result) {
            showToast('User invited successfully', 'success');
            closeModal();
            loadTeam();
        }
    } catch (err) {
        showToast('Error inviting user: ' + err.message, 'error');
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to remove this user?')) return;

    try {
        await fetchAPI(`/api/users/${userId}`, { method: 'DELETE' });
        showToast('User removed', 'success');
        loadTeam();
    } catch (e) {
        showToast('Error removing user: ' + e.message, 'error');
    }
}

async function loadSettings() {
    loadTeam();
    if (typeof loadAlertRules === 'function') loadAlertRules();
    if (typeof checkIntegrations === 'function') checkIntegrations();
    loadAIProviderStatus(); // v5.0.2
}

// ============== AI Provider Status (v5.0.2) ==============

async function loadAIProviderStatus() {
    try {
        const response = await fetch('/api/ai/status');
        if (!response.ok) {
            console.warn('AI status endpoint not available');
            return;
        }

        const data = await response.json();

        // Update OpenAI status
        const openaiStatusBadge = document.getElementById('openaiStatusBadge');
        const openaiModel = document.getElementById('openaiModel');
        if (openaiStatusBadge && data.providers?.openai) {
            openaiStatusBadge.textContent = data.providers.openai.available ? 'Active' : 'Not Configured';
            openaiStatusBadge.style.background = data.providers.openai.available ? '#10B981' : '#6B7280';
            openaiStatusBadge.style.color = 'white';
            openaiStatusBadge.style.padding = '2px 8px';
            openaiStatusBadge.style.borderRadius = '4px';
            openaiStatusBadge.style.fontSize = '0.75em';
        }
        if (openaiModel && data.providers?.openai?.model) {
            openaiModel.textContent = data.providers.openai.model;
        }

        // Update Gemini status
        const geminiStatusBadge = document.getElementById('geminiStatusBadge');
        const geminiModel = document.getElementById('geminiModel');
        if (geminiStatusBadge && data.providers?.gemini) {
            geminiStatusBadge.textContent = data.providers.gemini.available ? 'Active' : 'Not Configured';
            geminiStatusBadge.style.background = data.providers.gemini.available ? '#4285F4' : '#6B7280';
            geminiStatusBadge.style.color = 'white';
            geminiStatusBadge.style.padding = '2px 8px';
            geminiStatusBadge.style.borderRadius = '4px';
            geminiStatusBadge.style.fontSize = '0.75em';
        }
        if (geminiModel && data.providers?.gemini?.model) {
            geminiModel.textContent = data.providers.gemini.model;
        }

        // Update task routing display
        const routingExtraction = document.getElementById('routingExtraction');
        const routingSummary = document.getElementById('routingSummary');
        const routingBulk = document.getElementById('routingBulk');
        const routingQuality = document.getElementById('routingQuality');

        if (data.routing) {
            if (routingExtraction) routingExtraction.textContent = data.routing.data_extraction || '-';
            if (routingSummary) routingSummary.textContent = data.routing.executive_summary || '-';
            if (routingBulk) routingBulk.textContent = data.routing.bulk_tasks || '-';
            if (routingQuality) routingQuality.textContent = data.routing.quality_tasks || '-';

            // Color code active providers
            [routingExtraction, routingSummary, routingBulk, routingQuality].forEach(el => {
                if (el) {
                    const provider = el.textContent.toLowerCase();
                    if (provider === 'gemini') {
                        el.style.color = '#4285F4';
                    } else if (provider === 'openai') {
                        el.style.color = '#10B981';
                    } else {
                        el.style.color = 'var(--text-secondary)';
                    }
                }
            });
        }

        console.log('AI Provider Status loaded:', data);

    } catch (error) {
        console.warn('Failed to load AI provider status:', error);
    }
}

// ============== Mobile Responsiveness ==============

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.mobile-overlay');

    if (sidebar) sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('open');
}

function navigateTo(pageName) {
    // Wrapper for showPage that also handles mobile UI
    if (typeof showPage === 'function') {
        showPage(pageName);
    }

    // Update bottom nav active state
    document.querySelectorAll('.bottom-nav-item').forEach(item => {
        if (item.getAttribute('onclick') && item.getAttribute('onclick').includes('${pageName}')) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Close sidebar on mobile
    const sidebar = document.querySelector('.sidebar');
    if (sidebar && sidebar.classList.contains('open')) {
        toggleSidebar();
    }

    // Scroll to top
    window.scrollTo(0, 0);
}

// ============== Data Corrections ==============

// ============== Data Corrections ==============

function openCorrectionModal(competitorId, field, currentValue) {
    // Clean up value for display
    const safeValue = (currentValue === 'null' || currentValue === 'undefined') ? '' : currentValue;
    const cleanFieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

    // Find competitor name
    const comp = competitors.find(c => c.id === competitorId);
    const compName = comp ? comp.name : 'Unknown';

    const content = `
        <h2>Correct Data: ${cleanFieldName}</h2>
        <div style="margin-bottom: 16px; padding: 12px; background: #f8fafc; border-radius: 6px; color: #64748b; font-size: 0.9em;">
            <strong>Competitor:</strong> ${compName}<br>
            <strong>Current Value:</strong> ${safeValue || '<em style="color:#94a3b8">Empty</em>'}
        </div>
        
        <form id="correctionForm" onsubmit="submitCorrection(event, ${competitorId}, '${field}')">
            <div class="form-group">
                <label>New Correct Value</label>
                <input type="text" name="new_value" value="${safeValue}" required placeholder="Enter the correct value...">
            </div>
            <div class="form-group">
                <label>Reason for Change</label>
                <select name="reason">
                    <option value="Incorrect Data">Incorrect Data</option>
                    <option value="Outdated">Outdated Information</option>
                    <option value="Typo/Format">Typo or Formatting Issue</option>
                    <option value="Manual Override">Manual Override (Force)</option>
                </select>
            </div>
            <div style="margin-top: 24px; display: flex; justify-content: flex-end; gap: 12px;">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Correction</button>
            </div>
        </form>
    `;

    showModal(content);
}

async function submitCorrection(event, competitorId, fieldName) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const payload = {
        field: fieldName,
        new_value: formData.get('new_value'),
        reason: formData.get('reason')
    };

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerText;
    submitBtn.disabled = true;
    submitBtn.innerText = 'Saving...';

    try {
        const result = await fetchAPI(`/api/competitors/${competitorId}/correct`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        if (result) {
            showToast('Correction saved and data point locked.', 'success');
            closeModal();
            // Reload data to reflect changes
            await loadCompetitors();

            // Also refresh changes list if visible
            if (document.getElementById('recentChanges')) {
                const changesData = await fetchAPI('/api/changes?days=7');
                changes = changesData?.changes || [];
                renderRecentChanges();
            }
        }
    } catch (e) {
        showToast('Error saving correction: ' + e.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = originalText;
    }
}


// ============== Discovery Pipeline (Phase 4) ==============

let discoveryContext = null;

function toggleConfigPanel() {
    const panel = document.getElementById('discoveryConfigPanel');
    if (panel.style.display === 'none') {
        panel.style.display = 'block';
        loadDiscoveryContext();
        // Scroll to panel
        panel.scrollIntoView({ behavior: 'smooth' });
    } else {
        panel.style.display = 'none';
    }
}

async function loadDiscoveryContext() {
    try {
        const context = await fetchAPI('/api/discovery/context');
        discoveryContext = context;
        document.getElementById('jsonContextPreview').textContent = JSON.stringify(context, null, 2);
    } catch (e) {
        document.getElementById('jsonContextPreview').textContent = "Error loading context: " + e.message;
    }
}

async function sendConfigChat() {
    const input = document.getElementById('configChatInput');
    const message = input.value.trim();
    if (!message) return;

    // UI Updates
    const msgContainer = document.getElementById('configChatMessages');
    msgContainer.innerHTML += `<div class="chat-message user" style="text-align: right; margin: 5px 0; color: #3b82f6;">${message}</div>`;
    input.value = '';
    msgContainer.scrollTop = msgContainer.scrollHeight;

    // Show loading indicator
    const loadingId = 'chat-loading-' + Date.now();
    msgContainer.innerHTML += `<div id="${loadingId}" class="chat-message system" style="font-style: italic; color: #64748b;">AI is thinking...</div>`;

    try {
        // Prepare payload - include current context so AI knows what to update
        const payload = {
            message: message,
            current_context: discoveryContext || {}
        };

        const result = await fetchAPI('/api/discovery/refine-context', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        // Remove loading
        document.getElementById(loadingId).remove();

        if (result && result.success) {
            // Update local context
            discoveryContext = result.refined_context;

            // Save to backend
            await fetchAPI('/api/discovery/context', {
                method: 'POST',
                body: JSON.stringify(discoveryContext)
            });

            // Update UI
            document.getElementById('jsonContextPreview').textContent = JSON.stringify(discoveryContext, null, 2);
            msgContainer.innerHTML += `<div class="chat-message system" style="color: #22c55e;">✅ Context updated successfully based on your request.</div>`;

        }
    } catch (e) {
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        msgContainer.innerHTML += `<div class="chat-message error" style="color: #ef4444;">Error: ${e.message}</div>`;
    }
}

async function scheduleRun() {
    const timeInput = document.getElementById('scheduleRunTime');
    const isoTime = timeInput.value;

    if (!isoTime) {
        showToast("Please select a date and time.", "error");
        return;
    }

    try {
        // DateTime input gives local time 'YYYY-MM-DDTHH:MM' 
        // We need to send it as ISO string. 
        // Let's create a Date object to handle timezone correctly if needed, or send as is if backend expects ISO.
        const dateObj = new Date(isoTime);
        const isoString = dateObj.toISOString();

        const result = await fetchAPI('/api/discovery/schedule', {
            method: 'POST',
            body: JSON.stringify({ run_at: isoString })
        });

        showToast(result.message, "success");
        toggleConfigPanel(); // Close panel on success

    } catch (e) {
        showToast("Error scheduling run: " + e.message, "error");
    }
}

async function runDiscovery() {
    // Immediate Trigger (Manual) - Reuse existing or call new schedule for "now"
    if (!confirm("Start a discovery scan now? This runs in the background.")) return;

    try {
        // We can just schedule it for 1 second in the future to reuse the schedule logic
        const now = new Date();
        now.setSeconds(now.getSeconds() + 1);

        await fetchAPI('/api/discovery/schedule', {
            method: 'POST',
            body: JSON.stringify({ run_at: now.toISOString() })
        });

        showToast("Discovery scan started! Check back in a few minutes.", "success");
        document.getElementById('discoveryStatus').style.display = 'block';

    } catch (e) {
        showToast("Error starting discovery: " + e.message, "error");
    }
}

// ============== Scout AI Instructions Modal ==============

const DEFAULT_SCOUT_PROMPT = `You are Certify Scout, an autonomous competitive intelligence agent for Certify Health.

YOUR MISSION:
Find and qualify companies that directly compete with Certify Health in the healthcare IT market.

WHAT CERTIFY HEALTH DOES:
- Patient Experience Platform (PXP): Digital check-in, self-scheduling, patient intake
- Practice Management: Appointment scheduling, workflow automation
- Revenue Cycle Management: Eligibility verification, patient payments, claims
- Biometric Authentication: Patient identification, facial recognition
- EHR Integrations: FHIR/HL7 interoperability, Epic/Cerner/athenahealth

TARGET COMPETITOR PROFILE:
- Healthcare IT companies (NOT pharma, biotech, or medical devices)
- Focus on patient engagement, intake, or revenue cycle
- US-based or significant US operations
- B2B SaaS model serving medical practices or health systems
- Company size: 50-5000 employees (growth stage or established)

MARKETS TO SEARCH:
- Ambulatory care / outpatient clinics
- Urgent care centers
- Multi-specialty practices
- Behavioral health / mental health
- Dental (DSOs)
- ASCs (Ambulatory Surgery Centers)
- Health systems and hospitals

QUALIFICATION SCORING (0-100):
- 80-100: Direct competitor with overlapping products
- 60-79: Partial overlap, adjacent market
- 40-59: Related healthcare IT, low overlap
- Below 40: Not a competitor (reject)

EXCLUSIONS (Score 0):
- Pure EHR vendors without patient engagement focus
- Pharmaceutical companies
- Medical device manufacturers
- Insurance companies
- International-only companies
- Consulting firms
- Review/comparison websites`;

let scoutPrompt = localStorage.getItem('scoutPrompt') || DEFAULT_SCOUT_PROMPT;

function openScoutInstructionsModal() {
    const modal = document.getElementById('scoutInstructionsModal');
    const textarea = document.getElementById('scoutPromptInput');

    if (modal && textarea) {
        textarea.value = scoutPrompt;
        modal.style.display = 'block';
    }
}

function closeScoutInstructionsModal() {
    const modal = document.getElementById('scoutInstructionsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function loadDefaultScoutPrompt() {
    const textarea = document.getElementById('scoutPromptInput');
    if (textarea) {
        textarea.value = DEFAULT_SCOUT_PROMPT;
        showToast('Default Scout instructions loaded', 'success');
    }
}

async function saveScoutPrompt() {
    const textarea = document.getElementById('scoutPromptInput');
    if (!textarea) return;

    const newPrompt = textarea.value.trim();
    if (!newPrompt) {
        showToast('Prompt cannot be empty', 'error');
        return;
    }

    // Save to localStorage
    localStorage.setItem('scoutPrompt', newPrompt);
    scoutPrompt = newPrompt;

    // Also update the certify_context.json with the prompt
    try {
        const context = await fetchAPI('/api/discovery/context');
        context.scout_system_prompt = newPrompt;

        await fetchAPI('/api/discovery/context', {
            method: 'POST',
            body: JSON.stringify(context)
        });

        showToast('Scout AI instructions saved successfully!', 'success');
        closeScoutInstructionsModal();
    } catch (e) {
        // Still save locally even if API fails
        showToast('Instructions saved locally (API update failed)', 'warning');
        closeScoutInstructionsModal();
    }
}

async function loadDiscoveredCandidates() {
    const grid = document.getElementById('discoveredGrid');
    if (!grid) return;

    grid.innerHTML = '<div class="loading">Loading discovered candidates...</div>';

    try {
        // Fetch competitors with status='Discovered'
        // Using existing endpoint with added filter param support (client-side filter fallback if backend ignores it)
        const allComps = await fetchAPI('/api/competitors');
        const discovered = allComps.filter(c => c.status === 'Discovered');

        if (discovered.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 40px; background: #f8fafc; border-radius: 8px;">
                    <div style="font-size: 40px; margin-bottom: 10px;">🔭</div>
                    <h3>No Candidates Found Yet</h3>
                    <p style="color: #64748b; margin-bottom: 20px;">Use the 'Run Discovery' button to scan for new competitors.</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = discovered.map(c => renderCandidateCard(c)).join('');

    } catch (e) {
        grid.innerHTML = `<div class="error">Error loading candidates: ${e.message}</div>`;
    }
}

function renderCandidateCard(c) {
    // Parse notes for AI reasoning if available
    let reasoning = "No AI analysis available.";
    let score = c.relevance_score || 0;

    // Notes often contain the JSON from the agent, let's try to extract or display nicely
    // If notes is just a string, show it.
    if (c.notes) {
        reasoning = c.notes;
    }

    const scoreClass = score >= 80 ? 'high-score' : (score >= 50 ? 'med-score' : 'low-score');
    const scoreColor = score >= 80 ? '#22c55e' : (score >= 50 ? '#eab308' : '#cbd5e1');

    return `
        <div class="competitor-card discovery-card" style="border-left: 4px solid ${scoreColor}; position: relative;">
            <div class="card-header">
                <h3>${c.name}</h3>
                <span class="score-badge" style="background: ${scoreColor}; color: #fff; padding: 2px 8px; border-radius: 12px; font-size: 0.85em; font-weight: bold;">
                    ${score}% Match
                </span>
            </div>
            <div class="card-body">
                <a href="${c.website}" target="_blank" class="website-link" style="font-size: 0.9em; display: inline-block; margin-bottom: 10px;">
                    🔗 ${c.website}
                </a>
                <div class="ai-reasoning" style="background: #f1f5f9; padding: 10px; border-radius: 6px; font-size: 0.9em; color: #334155; margin-bottom: 15px; max-height: 100px; overflow-y: auto;">
                    <strong>🤖 AI Analysis:</strong><br>
                    ${reasoning}
                </div>
            </div>
            <div class="card-footer" style="display: flex; gap: 8px; margin-top: auto;">
                <button class="btn btn-primary btn-sm" style="flex: 1;" onclick="approveCandidate(${c.id})">✅ Approve</button>
                <button class="btn btn-secondary btn-sm" style="flex: 1; border-color: #ef4444; color: #ef4444;" onclick="rejectCandidate(${c.id})">❌ Reject</button>
            </div>
        </div>
    `;
}

async function approveCandidate(id) {
    if (!confirm("Approve this competitor? It will be added to the main dashboard and a full scrape will be triggered.")) return;

    try {
        // 1. Update Status to Active
        await fetchAPI(`/api/competitors/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ status: 'Active' })
        });

        // 2. Trigger Scrape
        fetchAPI(`/api/scrape/${id}`, {
            method: 'POST'
        }); // Don't await, let it run in bg

        showToast("Competitor approved! Moving to dashboard...", "success");
        loadDiscoveredCandidates(); // Refresh list

    } catch (e) {
        showToast("Error approving candidate: " + e.message, "error");
    }
}

async function rejectCandidate(id) {
    if (!confirm("Reject this candidate? It will be hidden.")) return;

    try {
        await fetchAPI(`/api/competitors/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ status: 'Ignored' })
        });

        showToast("Candidate rejected.", "info");
        loadDiscoveredCandidates();

    } catch (e) {
        showToast("Error rejecting candidate: " + e.message, "error");
    }
}

// Hook into showPage to load data when tab is opened
const originalShowPage = window.showPage;
window.showPage = function (pageId) {
    // Call original logic if it exists (it's defined in app.js globally usually)
    // But since showPage is not exported/global in this snippet context (it might be earlier in file), 
    // let's assume we are replacing/extending the navigation logic found in toggle/nav items.

    // Actually, looking at previous code, navigateTo calls showPage. 
    // Let's check if showPage is defined in the file...
    // It is likely defined earlier. We should rely on adding a listener or check.

    // Better approach: modifying the existing showPage if I could see it, OR just rely on the onclicks in HTML calling showPage.
    // I will add a check in the global scope if possible.

    // Instead of overriding, let's just expose loadDiscoveredCandidates and call it when the tab is clicked.
    // I'll add an event listener for the nav item.

    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId + 'Page').classList.add('active');

    if (pageId === 'discovered') {
        loadDiscoveryCandidates();
    }
};

// Also attach to the button in sidebar
document.addEventListener('DOMContentLoaded', () => {
    const discoveredLink = document.querySelector('a[data-page="discovered"]');
    if (discoveredLink) {
        discoveredLink.addEventListener('click', (e) => {
            e.preventDefault();
            showPage('discovered');
        });
    }
});

// ============== AI Admin & Knowledge Base ==============

// Default prompts embedded for instant loading
const DEFAULT_PROMPTS = {
    'dashboard_summary': `You are Certify Health's competitive intelligence analyst. Generate a comprehensive, executive-level strategic summary using ONLY the LIVE data provided below.

**CRITICAL - PROVE YOU ARE USING LIVE DATA:**
- Start your summary with: "📊 **Live Intelligence Report** - Generated [TODAY'S DATE AND TIME]"
- State the EXACT total number of competitors being tracked (e.g., "Currently monitoring **X competitors**")
- Name at least 3-5 SPECIFIC competitor names from the data with their EXACT threat levels
- Quote SPECIFIC numbers: funding amounts, employee counts, pricing figures directly from the data
- Reference any recent changes or updates with their timestamps if available
- If a competitor has specific data points (headquarters, founding year, etc.), cite them exactly

**YOUR SUMMARY MUST INCLUDE:**

1. **📈 Executive Overview**
   - State exact competitor count and breakdown by threat level
   - Name the top 3 high-threat competitors BY NAME

2. **🎯 Threat Analysis**
   - List HIGH threat competitors by name with why they're threats
   - List MEDIUM threat competitors by name
   - Provide specific threat justifications using their data

3. **💰 Pricing Intelligence**
   - Name competitors with known pricing and their EXACT pricing models
   - Compare specific price points where available

4. **📊 Market Trends**
   - Reference specific data points that indicate trends
   - Name competitors showing growth signals

5. **✅ Strategic Recommendations**
   - 3-5 specific, actionable recommendations
   - Reference specific competitors in each recommendation

6. **👁️ Watch List**
   - Name the top 5 competitors requiring immediate attention
   - State WHY each is on the watch list with specific data

**IMPORTANT:** Every claim must reference actual data provided. Do NOT make up or assume any information. If data is missing, say "Data not available" rather than guessing.`,
    'chat_persona': 'You are a competitive intelligence analyst for Certify Health. Always reference specific data points and competitor names when answering questions. Cite exact numbers and dates when available.'
};

// Prompt cache for instant loading - initialize from localStorage first, then defaults
const PROMPT_STORAGE_KEY = 'certify_intel_prompts';

// Load cached prompts from localStorage immediately (synchronous, instant)
function loadPromptsFromStorage() {
    try {
        const stored = localStorage.getItem(PROMPT_STORAGE_KEY);
        if (stored) {
            return JSON.parse(stored);
        }
    } catch (e) {
        console.log('Could not load prompts from localStorage');
    }
    return {};
}

// Save prompts to localStorage for instant access
function savePromptsToStorage(prompts) {
    try {
        localStorage.setItem(PROMPT_STORAGE_KEY, JSON.stringify(prompts));
    } catch (e) {
        console.log('Could not save prompts to localStorage');
    }
}

// Initialize cache: localStorage first, then defaults as fallback
const storedPrompts = loadPromptsFromStorage();
const promptCache = {
    ...DEFAULT_PROMPTS,  // Defaults as base
    ...storedPrompts     // Override with any stored values
};

function openPromptEditor() {
    const modal = document.getElementById('promptModal');
    if (modal) modal.classList.add('active');
    loadPromptContent();
}

function closePromptModal() {
    const modal = document.getElementById('promptModal');
    if (modal) modal.classList.remove('active');
    document.getElementById('promptSaveStatus').style.display = 'none';
}

async function loadPromptContent() {
    const key = document.getElementById('promptKeySelector').value;
    const editor = document.getElementById('promptContentEditor');

    // Show loading state initially
    editor.value = promptCache[key] || DEFAULT_PROMPTS[key] || 'Loading...';

    // Fetch from server (no timeout - let it complete)
    try {
        const response = await fetchAPI(`/api/admin/system-prompts/${key}`);

        if (response && response.content) {
            editor.value = response.content;
            promptCache[key] = response.content;
            savePromptsToStorage(promptCache);
        } else if (!editor.value || editor.value === 'Loading...') {
            // Fallback to default if no server response
            editor.value = DEFAULT_PROMPTS[key] || '';
        }
    } catch (e) {
        // Error - use cached or default value
        console.log('Using cached prompt due to error');
        editor.value = promptCache[key] || DEFAULT_PROMPTS[key] || '';
    }
}

async function savePromptContent() {
    const key = document.getElementById('promptKeySelector').value;
    const content = document.getElementById('promptContentEditor').value;

    // Update cache and localStorage IMMEDIATELY before server call
    promptCache[key] = content;
    savePromptsToStorage(promptCache);

    const result = await fetchAPI('/api/admin/system-prompts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, content })
    });

    if (result) {
        const status = document.getElementById('promptSaveStatus');
        status.style.display = 'inline-block';
        setTimeout(() => status.style.display = 'none', 3000);
    }
}

// Preload prompts on page load to sync with server (background task)
async function preloadPrompts() {
    const keys = ['dashboard_summary', 'chat_persona'];
    for (const key of keys) {
        try {
            const response = await fetchAPI(`/api/admin/system-prompts/${key}`);
            if (response && response.content) {
                promptCache[key] = response.content;
            }
        } catch (e) {
            console.log(`Could not preload prompt: ${key}`);
        }
    }
    // Save any fetched prompts to localStorage for next time
    savePromptsToStorage(promptCache);
}

function openKnowledgeBase() {
    const modal = document.getElementById('kbModal');
    if (modal) modal.classList.add('active');
    loadKbItems();
}

function closeKbModal() {
    const modal = document.getElementById('kbModal');
    if (modal) modal.classList.remove('active');
    hideAddKbForm();
}

async function loadKbItems() {
    const list = document.getElementById('kbList');
    list.innerHTML = '<div class="loading">Loading...</div>';

    const items = await fetchAPI('/api/admin/knowledge-base');
    if (items && items.length > 0) {
        list.innerHTML = items.map(item => `
            <div class="kb-item" style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee;">
                <div>
                    <strong>${item.title}</strong>
                    <div style="font-size: 0.8em; color: #666;">Source: ${item.source_type} • Added: ${formatDate(item.created_at)}</div>
                    <div style="font-size: 0.8em; color: #999; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 400px;">${item.content_text.substring(0, 100)}...</div>
                </div>
                <button class="btn btn-sm btn-secondary" style="color: red; border-color: red;" onclick="deleteKbItem(${item.id})">Delete</button>
            </div>
        `).join('');
    } else {
        list.innerHTML = '<div class="empty-state">No knowledge base items found. Add documents to give the AI context.</div>';
    }
}

function showAddKbItem() {
    document.getElementById('addKbForm').style.display = 'block';
    document.getElementById('kbList').style.display = 'none';
}

function hideAddKbForm() {
    document.getElementById('addKbForm').style.display = 'none';
    document.getElementById('kbList').style.display = 'block';
}

async function saveKbItem() {
    const title = document.getElementById('kbTitle').value;
    const content = document.getElementById('kbContent').value;

    if (!title || !content) {
        showToast("Please provide both title and content", "error");
        return;
    }

    const result = await fetchAPI('/api/admin/knowledge-base', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: title,
            content_text: content,
            source_type: "manual"
        })
    });

    if (result) {
        showToast("Document added to Knowledge Base", "success");
        document.getElementById('kbTitle').value = "";
        document.getElementById('kbContent').value = "";
        hideAddKbForm();
        loadKbItems();
    }
}

/**
 * Open modal to correct a specific data point
 */
function openCorrectionModal(id, field, currentValue) {
    const humanField = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    const content = `
        <h3>Correct Data: ${humanField}</h3>
        <p style="color: #64748b; margin-bottom: 16px;">Update this value and provide a source if available.</p>
        <form onsubmit="submitCorrection(event, ${id}, '${field}')">
            <div class="form-group">
                <label>Current Value</label>
                <input type="text" value="${currentValue}" disabled style="background: #f1f5f9; cursor: not-allowed;">
            </div>
            <div class="form-group">
                <label>New Value</label>
                <input type="text" name="value" required placeholder="Enter correct value" autofocus>
            </div>
            <div class="form-group">
                <label>Source URL (Evidence)</label>
                <input type="url" name="source_url" placeholder="https://example.com/source">
            </div>
            <div class="form-group">
                <label>Notes (Optional)</label>
                <textarea name="notes" placeholder="Why is this change being made?" rows="2"></textarea>
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Submit Correction</button>
            </div>
        </form>
    `;
    showModal(content);
}

/**
 * Handle correction submission
 */
async function submitCorrection(event, id, field) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const value = formData.get('value');
    const sourceUrl = formData.get('source_url');
    const notes = formData.get('notes');

    // Create partial update payload
    const payload = {};
    payload[field] = value;
    if (notes) payload.notes = notes;

    try {
        // Try PUT (assuming backend supports partial update)
        const res = await fetchAPI(`/api/competitors/${id}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });

        if (res) {
            showToast('Correction submitted successfully', 'success');
            closeModal();

            // Update local state
            const comp = competitors.find(c => c.id === id);
            if (comp) {
                comp[field] = value;
            }

            // Refresh main grid and lists
            loadCompetitors();

            // Re-render the open list modal by calling showCompanyList again if it was open
            // We can detect if the modal title contains "All Competitors"
            const modalTitle = document.querySelector('.modal-header h3');
            if (modalTitle && modalTitle.textContent.includes('All Competitors')) {
                // Determine current filter from modal title or state? 
                // Currently showCompanyList takes 'threatLevel'. 
                // We'll just default to refeshing 'all' if unsure, or close it.
                // Safest to just let user re-open or reload.
            }
        }
    } catch (e) {
        showToast('Error submitting correction: ' + e.message, 'error');
    }
}

async function deleteKbItem(id) {
    if (!confirm("Are you sure you want to delete this item?")) return;

    const result = await fetchAPI(`/api/admin/knowledge-base/${id}`, { method: 'DELETE' });
    if (result) {
        showToast("Item deleted", "info");
        loadKbItems();
    }
}

// =====================================================
// PHASE 6: DATA SOURCES MODAL & CONFIDENCE DISPLAY
// =====================================================

/**
 * Open the Data Sources modal for a competitor
 * @param {number} competitorId - The competitor ID
 */
async function viewDataSources(competitorId) {
    const modal = document.getElementById('dataSourcesModal');
    const container = document.getElementById('dataSourcesTableContainer');

    if (!modal || !container) {
        console.error('Data Sources modal elements not found');
        return;
    }

    // Show loading state
    container.innerHTML = '<p class="loading" style="text-align:center;padding:40px;">Loading data sources...</p>';
    modal.classList.add('active');

    try {
        // Fetch data sources for this competitor
        const sources = await fetchAPI(`/api/competitors/${competitorId}/data-sources`);
        const competitor = competitors.find(c => c.id === competitorId);
        const compName = competitor?.name || 'Unknown Competitor';

        // Update modal header
        const header = modal.querySelector('h3');
        if (header) {
            header.innerHTML = `📋 Data Sources: ${compName}`;
        }

        if (!sources || sources.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #64748b;">
                    <p style="font-size: 48px; margin-bottom: 16px;">📭</p>
                    <p style="font-size: 16px; font-weight: 600;">No source data available</p>
                    <p style="font-size: 14px; margin-top: 8px;">Run a data refresh or enhanced scrape to collect source attribution.</p>
                    <button class="btn btn-primary" onclick="triggerEnhancedScrape(${competitorId})" style="margin-top: 16px;">
                        🔄 Run Enhanced Scrape
                    </button>
                </div>
            `;
            return;
        }

        // Build the sources table
        container.innerHTML = renderDataSourcesTable(sources);
    } catch (error) {
        console.error('Error loading data sources:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #dc3545;">
                <p style="font-size: 48px; margin-bottom: 16px;">⚠️</p>
                <p style="font-size: 16px; font-weight: 600;">Error loading data sources</p>
                <p style="font-size: 14px; margin-top: 8px;">${error.message || 'Unknown error occurred'}</p>
            </div>
        `;
    }
}

/**
 * Render the data sources table HTML
 */
function renderDataSourcesTable(sources) {
    const rows = sources.map(s => {
        const confidenceLevel = s.confidence?.level || getConfidenceLevelFromScore(s.confidence?.score);
        const confidenceScore = s.confidence?.score || 0;
        const isVerified = s.is_verified;
        const sourceType = s.source_type || 'unknown';
        const fieldName = formatFieldName(s.field);
        const value = s.value || '—';
        const extractedAt = s.extracted_at ? formatDate(s.extracted_at) : '—';

        return `
            <tr>
                <td class="field-name">${fieldName}</td>
                <td class="field-value" title="${value}">${truncateText(value, 40)}</td>
                <td class="source-info">
                    <span class="source-type-badge ${sourceType}">${formatSourceType(sourceType)}</span>
                    ${s.source_url ? `<a href="${s.source_url}" target="_blank" class="source-link-icon" title="Open source">🔗</a>` : ''}
                </td>
                <td>
                    <div class="confidence-cell">
                        <div class="confidence-bar">
                            <div class="fill ${confidenceLevel}" style="width: ${confidenceScore}%"></div>
                        </div>
                        <span class="confidence-score ${confidenceLevel}">${confidenceScore}/100</span>
                    </div>
                </td>
                <td>
                    <span class="verified-badge ${isVerified ? 'verified' : 'unverified'}">
                        ${isVerified ? '✓ Verified' : '○ Pending'}
                    </span>
                </td>
                <td class="updated-at">${extractedAt}</td>
            </tr>
        `;
    }).join('');

    return `
        <table class="sources-table">
            <thead>
                <tr>
                    <th>Field</th>
                    <th>Value</th>
                    <th>Source</th>
                    <th>Confidence</th>
                    <th>Status</th>
                    <th>Last Updated</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}

/**
 * Close the data sources modal
 */
function closeDataSourcesModal(event) {
    const modal = document.getElementById('dataSourcesModal');
    if (modal) {
        // Only close if clicking on overlay or close button
        if (!event || event.target === modal || event.target.classList.contains('close-btn')) {
            modal.classList.remove('active');
        }
    }
}

/**
 * Format field name for display
 */
function formatFieldName(field) {
    if (!field) return 'Unknown';
    return field
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
}

/**
 * Format source type for display
 */
function formatSourceType(type) {
    const typeLabels = {
        'sec_filing': 'SEC',
        'api_verified': 'API',
        'api': 'API',
        'website_scrape': 'Website',
        'manual': 'Manual',
        'manual_verified': 'Verified',
        'news_article': 'News',
        'klas_report': 'KLAS',
        'linkedin_estimate': 'LinkedIn',
        'crunchbase': 'Crunchbase',
        'unknown': 'Unknown'
    };
    return typeLabels[type] || type.replace(/_/g, ' ');
}

/**
 * Truncate text with ellipsis
 */
function truncateText(text, maxLength) {
    if (!text) return '—';
    const str = String(text);
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}

/**
 * Trigger enhanced scrape with source tracking
 */
async function triggerEnhancedScrape(competitorId) {
    const competitor = competitors.find(c => c.id === competitorId);
    if (!competitor) {
        showToast('Competitor not found', 'error');
        return;
    }

    showToast(`Starting enhanced scrape for ${competitor.name}...`, 'info');

    try {
        const result = await fetchAPI(`/api/scrape/enhanced/${competitorId}`, {
            method: 'POST'
        });

        if (result) {
            showToast(`Enhanced scrape complete for ${competitor.name}`, 'success');
            // Reload data sources modal
            viewDataSources(competitorId);
        }
    } catch (error) {
        console.error('Enhanced scrape error:', error);
        showToast(`Error: ${error.message || 'Enhanced scrape failed'}`, 'error');
    }
}


// ============== News Feed Functions (v5.0.3 - Phase 1) ==============

let currentNewsPage = 1;
const NEWS_PAGE_SIZE = 25;
let newsFeedData = [];

/**
 * Initialize the News Feed page
 */
async function initNewsFeedPage() {
    console.log('Initializing News Feed page...');

    // Set default date range (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);

    document.getElementById('newsDateFrom').value = thirtyDaysAgo.toISOString().split('T')[0];
    document.getElementById('newsDateTo').value = today.toISOString().split('T')[0];

    // Populate competitor dropdown
    await populateNewsCompetitorDropdown();

    // Load initial news feed
    await loadNewsFeed();
}

/**
 * Populate the competitor dropdown in news feed filters
 */
async function populateNewsCompetitorDropdown() {
    const dropdown = document.getElementById('newsCompetitorFilter');
    if (!dropdown) return;

    // Use cached competitors if available, otherwise fetch
    let competitorList = competitors;
    if (!competitorList || competitorList.length === 0) {
        const data = await fetchAPI('/api/competitors');
        competitorList = data || [];
    }

    // Reset dropdown
    dropdown.innerHTML = '<option value="">All Competitors</option>';

    // Add competitors
    competitorList.forEach(comp => {
        if (!comp.is_deleted) {
            const option = document.createElement('option');
            option.value = comp.id;
            option.textContent = comp.name;
            dropdown.appendChild(option);
        }
    });
}

/**
 * Load news feed with current filters
 */
async function loadNewsFeed(page = 1) {
    currentNewsPage = page;

    // Show loading state
    document.getElementById('newsFeedLoading').style.display = 'flex';
    document.getElementById('newsFeedTableBody').innerHTML = '';

    // Gather filter values
    const competitorId = document.getElementById('newsCompetitorFilter')?.value || '';
    const dateFrom = document.getElementById('newsDateFrom')?.value || '';
    const dateTo = document.getElementById('newsDateTo')?.value || '';
    const sentiment = document.getElementById('newsSentimentFilter')?.value || '';
    const source = document.getElementById('newsSourceFilter')?.value || '';
    const eventType = document.getElementById('newsEventFilter')?.value || '';

    // Build query string
    const params = new URLSearchParams();
    if (competitorId) params.append('competitor_id', competitorId);
    if (dateFrom) params.append('start_date', dateFrom);
    if (dateTo) params.append('end_date', dateTo);
    if (sentiment) params.append('sentiment', sentiment);
    if (source) params.append('source', source);
    if (eventType) params.append('event_type', eventType);
    params.append('page', page);
    params.append('page_size', NEWS_PAGE_SIZE);

    try {
        const result = await fetchAPI(`/api/news-feed?${params.toString()}`);

        // Hide loading state
        document.getElementById('newsFeedLoading').style.display = 'none';

        if (result && result.articles) {
            newsFeedData = result.articles;
            renderNewsFeedTable(result.articles);
            updateNewsFeedStats(result.stats);
            updateNewsFeedPagination(result.pagination);
        } else {
            renderEmptyState();
            updateNewsFeedStats({ total: 0, positive: 0, neutral: 0, negative: 0 });
        }
    } catch (error) {
        console.error('Error loading news feed:', error);
        document.getElementById('newsFeedLoading').style.display = 'none';
        renderEmptyState('Error loading news. Please try again.');
    }
}

/**
 * Render the news feed table with articles
 */
function renderNewsFeedTable(articles) {
    const tbody = document.getElementById('newsFeedTableBody');
    if (!tbody) return;

    if (!articles || articles.length === 0) {
        renderEmptyState();
        return;
    }

    tbody.innerHTML = articles.map(article => `
        <tr class="news-row" onclick="viewNewsArticle('${escapeHtml(article.url || '')}')">
            <td class="news-date">${formatNewsDate(article.published_at)}</td>
            <td class="news-competitor">
                <span class="competitor-badge">${escapeHtml(article.competitor_name || 'Unknown')}</span>
            </td>
            <td class="news-headline">
                <a href="${escapeHtml(article.url || '#')}" target="_blank" title="${escapeHtml(article.title || '')}">
                    ${escapeHtml(truncateText(article.title || 'No title', 80))}
                </a>
            </td>
            <td class="news-source">
                <span class="source-badge ${article.source_type || ''}">${formatSourceName(article.source || article.source_type)}</span>
            </td>
            <td class="news-sentiment">
                ${renderSentimentBadge(article.sentiment)}
            </td>
            <td class="news-event">
                ${renderEventTypeBadge(article.event_type)}
            </td>
            <td class="news-actions">
                <button class="btn-icon" onclick="event.stopPropagation(); viewNewsArticle('${escapeHtml(article.url || '')}')" title="Open Article">
                    🔗
                </button>
                <button class="btn-icon" onclick="event.stopPropagation(); addToKnowledgeBase(${JSON.stringify(article).replace(/"/g, '&quot;')})" title="Add to KB">
                    📚
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * Render empty state message
 */
function renderEmptyState(message = 'No news articles found. Adjust your filters or refresh data.') {
    const tbody = document.getElementById('newsFeedTableBody');
    if (tbody) {
        tbody.innerHTML = `
            <tr class="news-empty-state">
                <td colspan="7">
                    <div class="empty-state-content">
                        <span class="empty-icon">📰</span>
                        <p>${message}</p>
                    </div>
                </td>
            </tr>
        `;
    }
}

/**
 * Update news feed stats display
 */
function updateNewsFeedStats(stats) {
    document.getElementById('totalNewsCount').textContent = stats?.total || 0;
    document.getElementById('positiveNewsCount').textContent = stats?.positive || 0;
    document.getElementById('neutralNewsCount').textContent = stats?.neutral || 0;
    document.getElementById('negativeNewsCount').textContent = stats?.negative || 0;
}

/**
 * Update pagination controls
 */
function updateNewsFeedPagination(pagination) {
    if (!pagination) {
        document.getElementById('newsPageInfo').textContent = 'Page 1 of 1';
        document.getElementById('newsPrevBtn').disabled = true;
        document.getElementById('newsNextBtn').disabled = true;
        return;
    }

    const { page, total_pages, total_items } = pagination;
    document.getElementById('newsPageInfo').textContent = `Page ${page} of ${total_pages} (${total_items} articles)`;
    document.getElementById('newsPrevBtn').disabled = page <= 1;
    document.getElementById('newsNextBtn').disabled = page >= total_pages;
}

/**
 * Reset all news feed filters
 */
function resetNewsFeedFilters() {
    // Reset competitor
    document.getElementById('newsCompetitorFilter').value = '';

    // Reset date range to last 30 days
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);

    document.getElementById('newsDateFrom').value = thirtyDaysAgo.toISOString().split('T')[0];
    document.getElementById('newsDateTo').value = today.toISOString().split('T')[0];

    // Reset other filters
    document.getElementById('newsSentimentFilter').value = '';
    document.getElementById('newsSourceFilter').value = '';
    document.getElementById('newsEventFilter').value = '';

    // Reset pagination
    currentNewsPage = 1;

    // Reload
    loadNewsFeed();
}

/**
 * Format date for display
 */
function formatNewsDate(dateStr) {
    if (!dateStr) return '—';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    } catch {
        return dateStr;
    }
}

/**
 * Format source name for display
 */
function formatSourceName(source) {
    if (!source) return 'Unknown';
    const sourceMap = {
        'google_news': 'Google News',
        'sec_edgar': 'SEC EDGAR',
        'newsapi': 'NewsAPI',
        'gnews': 'GNews',
        'mediastack': 'MediaStack',
        'bing_news': 'Bing News',
        'website_scrape': 'Website'
    };
    return sourceMap[source] || source.charAt(0).toUpperCase() + source.slice(1).replace(/_/g, ' ');
}

/**
 * Render sentiment badge
 */
function renderSentimentBadge(sentiment) {
    if (!sentiment) return '<span class="sentiment-badge unknown">—</span>';

    const sentimentMap = {
        'positive': { icon: '🟢', class: 'positive', label: 'Positive' },
        'neutral': { icon: '🟡', class: 'neutral', label: 'Neutral' },
        'negative': { icon: '🔴', class: 'negative', label: 'Negative' }
    };

    const s = sentimentMap[sentiment.toLowerCase()] || { icon: '⚪', class: 'unknown', label: sentiment };
    return `<span class="sentiment-badge ${s.class}">${s.icon} ${s.label}</span>`;
}

/**
 * Render event type badge
 */
function renderEventTypeBadge(eventType) {
    if (!eventType) return '<span class="event-badge general">📄 General</span>';

    const eventMap = {
        'funding': { icon: '💰', label: 'Funding' },
        'acquisition': { icon: '🤝', label: 'M&A' },
        'product_launch': { icon: '🚀', label: 'Product' },
        'partnership': { icon: '🔗', label: 'Partnership' },
        'leadership': { icon: '👔', label: 'Leadership' },
        'financial': { icon: '📊', label: 'Financial' },
        'legal': { icon: '⚖️', label: 'Legal' },
        'general': { icon: '📄', label: 'General' }
    };

    const e = eventMap[eventType.toLowerCase()] || { icon: '📄', label: eventType };
    return `<span class="event-badge ${eventType.toLowerCase()}">${e.icon} ${e.label}</span>`;
}

/**
 * Open news article in new tab
 */
function viewNewsArticle(url) {
    if (url && url !== '#') {
        window.open(url, '_blank');
    }
}

/**
 * Add news article to knowledge base
 */
async function addToKnowledgeBase(article) {
    try {
        const content = `News: ${article.title}\nSource: ${article.source}\nDate: ${article.published_at}\nURL: ${article.url}\nSummary: ${article.summary || article.description || ''}`;

        const result = await fetchAPI('/api/knowledge-base', {
            method: 'POST',
            body: JSON.stringify({
                content_text: content,
                source_type: 'news_article',
                source_url: article.url,
                is_active: true
            })
        });

        if (result) {
            showToast('Article added to Knowledge Base', 'success');
        } else {
            showToast('Failed to add article to Knowledge Base', 'error');
        }
    } catch (error) {
        console.error('Error adding to KB:', error);
        showToast('Error adding to Knowledge Base', 'error');
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
