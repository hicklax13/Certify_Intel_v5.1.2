/**
 * Certify Intel - Dashboard JavaScript
 * Frontend logic for competitive intelligence dashboard
 */

const API_BASE = 'http://localhost:8000';

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
function createSourcedValue(value, source, identifier = '', highlight = '') {
    if (value === null || value === undefined || value === '') return '<span style="color:#94a3b8;">—</span>';
    return `<span class="sourced-value">${value}${createSourceLink(source, identifier, highlight)}</span>`;
}

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
            break;
        case 'discovered':
            loadDiscovered();
            break;
        case 'dataquality':
            loadDataQuality();
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
        console.error(`API Error: ${endpoint}`, error);
        showToast(`Error loading data: ${error.message}`, 'error');
        return null;
    }
}

// ============== Dashboard ==============

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

// Make accessible to onclick
window.startAISummary = startAISummary;

async function startAISummary() {
    const summaryCard = document.getElementById('aiSummaryCard');
    const contentDiv = document.getElementById('aiSummaryContent');
    const modelBadge = document.getElementById('aiModelBadge');

    // modelBadge removal caused error in previous refactor, ignoring for now as it was removed from HTML
    const providerLogo = document.getElementById('aiProviderLogo');
    const metaDiv = document.getElementById('aiSummaryMeta');

    if (!summaryCard || !contentDiv) return;

    summaryCard.style.display = 'block';
    contentDiv.innerHTML = '<div class="ai-loading"><span class="ai-spinner">⏳</span> Generating comprehensive strategic insights...</div>';

    const data = await fetchAPI('/api/analytics/summary');

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

// Enhanced triggerScrapeAll with loading state and summary refresh
async function triggerScrapeAll() {
    const btn = document.querySelector('.btn-primary[onclick*="triggerScrapeAll"]') ||
        document.querySelector('button:contains("Refresh")') ||
        event?.target;

    if (btn) {
        btn.classList.add('btn-loading');
        btn.disabled = true;
    }

    showToast('Refreshing all competitor data...', 'info');

    try {
        const result = await fetchAPI('/api/scrape/all');

        if (result) {
            showToast('Data refresh complete! Regenerating summary...', 'success');

            // Reload dashboard data
            await loadDashboard();

            // Regenerate AI summary with new data
            await fetchDashboardSummary();

            showToast('Dashboard fully updated with latest data', 'success');
        }
    } catch (e) {
        showToast('Error refreshing data: ' + e.message, 'error');
    } finally {
        if (btn) {
            btn.classList.remove('btn-loading');
            btn.disabled = false;
        }
    }
}

function updateStatsCards() {
    document.getElementById('totalCompetitors').textContent = stats.total_competitors || 0;
    document.getElementById('highThreat').textContent = stats.high_threat || 0;
    document.getElementById('mediumThreat').textContent = stats.medium_threat || 0;
    document.getElementById('lowThreat').textContent = stats.low_threat || 0;
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
        return `<div style="padding: 8px 0; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
            <span><strong>${idx + 1}.</strong> ${c.name} ${publicBadge}</span>
            <span style="color: #64748b; font-size: 0.85em;">${c.customer_count || 'N/A'} customers</span>
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
            <td>${createSourcedValue(comp.customer_count, 'website', comp.website, 'customers')}</td>
            <td>${createSourcedValue(comp.base_price, 'website', comp.website, 'pricing')}</td>
            <td>${formatDate(comp.last_updated)}</td>
            <td>
                <button class="btn btn-secondary" onclick="viewCompetitor(${comp.id})">View</button>
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
        // Determine public/private badge
        const isPublic = comp.is_public;
        const ticker = comp.ticker_symbol || '';
        const exchange = comp.stock_exchange || '';

        let statusBadge = '';
        if (isPublic && ticker) {
            statusBadge = `
                <div class="stock-inline-badge" data-ticker="${ticker}" style="display: flex; align-items: center; gap: 6px; margin-top: 4px;">
                    <span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.75em; font-weight: 600;">PUBLIC</span>
                    <span style="font-weight: 600; color: #122753; font-size: 0.85em;">${ticker}</span>
                    <span style="color: #64748b; font-size: 0.75em;">(${exchange})</span>
                    <span class="live-price" id="price-${comp.id}" style="font-weight: 600; font-size: 0.85em; color: #122753;">---</span>
                </div>
            `;
        } else {
            statusBadge = `
                <div style="margin-top: 4px;">
                    <span style="background: #64748b; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.75em; font-weight: 600;">PRIVATE</span>
                </div>
            `;
        }

        return `
        <div class="competitor-card">
            <div class="competitor-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    ${createLogoImg(comp.website, comp.name, 40)}
                    <div>
                        <div class="competitor-name">${comp.name}</div>
                        ${statusBadge}
                        <a href="${comp.website}" target="_blank" class="competitor-website">${comp.website}</a>
                    </div>
                </div>
                <span class="threat-badge ${comp.threat_level.toLowerCase()}">${comp.threat_level}</span>
            </div>
            <div class="competitor-details">
                <div class="detail-item">
                    <span class="detail-label">Customers</span>
                    <span class="detail-value">${createSourcedValue(comp.customer_count, 'website', comp.website, 'customers')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Pricing</span>
                    <span class="detail-value">${createSourcedValue(comp.base_price, 'website', comp.website, 'pricing')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Employees</span>
                    <span class="detail-value">${createSourcedValue(comp.employee_count, 'linkedin', comp.name)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">G2 Rating</span>
                    <span class="detail-value">${createSourcedValue(comp.g2_rating ? comp.g2_rating + ' ⭐' : null, 'google', comp.name + ' G2 rating')}</span>
                </div>
            </div>
            <div class="competitor-actions">
                <button class="btn btn-primary" onclick="viewBattlecard(${comp.id})">Battlecard</button>
                <button class="btn btn-secondary" onclick="showCompetitorInsights(${comp.id})" style="background-color: var(--navy-dark); color: white;">📊 Insights</button>
                <button class="btn btn-secondary" onclick="triggerScrape(${comp.id})">Refresh</button>
                <button class="btn btn-secondary" onclick="editCompetitor(${comp.id})">Edit</button>
                <button class="btn btn-secondary" onclick="deleteCompetitor(${comp.id})" style="background-color: #dc3545; color: white; border-color: #dc3545;">Delete</button>
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
            const changeClass = data.change >= 0 ? 'color: #22c55e' : 'color: #dc3545';
            const changeSign = data.change >= 0 ? '+' : '';
            priceEl.innerHTML = `<span style="${changeClass}">$${data.price.toFixed(2)} (${changeSign}${data.change_percent?.toFixed(1)}%)</span>`;
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
            <div>
                <h2 style="margin:0;">${comp.name}</h2>
                <p style="margin:4px 0;">
                    <a href="${comp.website}" target="_blank" style="color:#0ea5e9;">${comp.website}</a>
                    ${createSourceLink('website', comp.website)}
                </p>
            </div>
        </div>
        <hr>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <div><strong>Status:</strong> ${createSourcedValue(comp.status, 'manual', comp.name)}</div>
            <div><strong>Threat Level:</strong> <span class="threat-badge ${(comp.threat_level || '').toLowerCase()}">${comp.threat_level || '—'}</span></div>
            <div><strong>Pricing Model:</strong> ${createSourcedValue(comp.pricing_model, 'website', comp.website, 'pricing')}</div>
            <div><strong>Base Price:</strong> ${createSourcedValue(comp.base_price, 'website', comp.website, 'pricing')}</div>
            <div><strong>Customers:</strong> ${createSourcedValue(comp.customer_count, 'website', comp.website, 'customers')}</div>
            <div><strong>Employees:</strong> ${createSourcedValue(comp.employee_count, 'linkedin', comp.name)}</div>
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
        const response = await fetch(`${API_BASE}/api/news/${encodeURIComponent(companyName)}`);
        const data = await response.json();

        if (data.articles && data.articles.length > 0) {
            newsSection.innerHTML = data.articles.map(article => `
                <div class="news-item">
                    <a href="${article.url}" target="_blank" class="news-title">${article.title}</a>
                    <div class="news-meta">
                        <span class="news-source">${article.source}</span>
                        <span class="news-date">${article.published_date}</span>
                    </div>
                    <p class="news-snippet">${article.snippet || ''}</p>
                </div>
            `).join('');
        } else {
            newsSection.innerHTML = '<p class="empty-state">No recent news articles found</p>';
        }
    } catch (error) {
        newsSection.innerHTML = '<p class="empty-state">Unable to load news</p>';
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
                    <div class="stock-header-row" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #e2e8f0;">
                         <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="background: #22c55e; color: white; padding: 4px 12px; border-radius: 4px; font-weight: 600; font-size: 0.85em;">PUBLIC</span>
                            <span style="font-size: 1.25em; font-weight: 700; color: #122753;">${data.ticker} <span style="font-size: 0.8em; color: #64748b; font-weight: 500;">(${data.exchange})</span></span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.5em; font-weight: 700; color: #122753;">${fmtCur(data.price)}</div>
                            <div class="stock-change ${changeClass}" style="font-weight: 600;">
                                ${changeSign}${data.change?.toFixed(2)} (${changeSign}${data.change_percent?.toFixed(2)}%)
                            </div>
                        </div>
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

async function triggerScrapeAll() {
    try {
        const response = await fetch(`${API_BASE}/api/scrape/all`, { method: 'POST' });
        if (response.ok) {
            const result = await response.json();
            showToast(`Refreshing ${result.competitor_ids?.length || 'all'} competitors...`, 'success');
            // Reload dashboard after a short delay
            setTimeout(() => loadDashboard(), 3000);
        } else {
            showToast('Failed to start refresh', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

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
        return value || 'N/A';
    }

    const cacheKey = `${competitorId}-${fieldName}`;
    const cached = sourceCache[cacheKey];

    const sourceType = cached?.source_type || fallbackType;
    const sourceUrl = cached?.source_url || null;
    const sourceName = cached?.source_name || 'Source';
    const enteredBy = cached?.entered_by || 'Unknown';
    const formula = cached?.formula || null;

    let iconHtml = '';
    let tooltipHtml = '';
    let clickHandler = '';

    switch (sourceType) {
        case 'external':
            iconHtml = '🔗';
            tooltipHtml = `<span class="source-tooltip">${sourceName}${sourceUrl ? ' - Click to open' : ''}</span>`;
            if (sourceUrl) {
                clickHandler = `onclick="window.open('${sourceUrl}', '_blank')"`;
            }
            break;
        case 'manual':
            iconHtml = '✏️';
            tooltipHtml = `<span class="source-tooltip">Manual Entry by ${enteredBy}</span>`;
            break;
        case 'calculated':
            iconHtml = 'ƒ';
            const formulaDisplay = formula ? `<span class="source-formula">${formula}</span>` : '';
            tooltipHtml = `<span class="source-tooltip">Calculated Value${formulaDisplay}</span>`;
            break;
        default:
            iconHtml = '•';
            tooltipHtml = `<span class="source-tooltip">Source pending verification</span>`;
    }

    return `
        <span class="sourced-value" data-competitor="${competitorId}" data-field="${fieldName}">
            ${value}
            <span class="source-icon ${sourceType}" ${clickHandler} title="Click for source">
                ${iconHtml}
            </span>
            ${tooltipHtml}
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

function renderMarketTrends() {
    // Placeholder trend chart
    const ctx = document.getElementById('marketTrendChart').getContext('2d');

    // Destroy existing
    const existing = Chart.getChart('marketTrendChart');
    if (existing) existing.destroy();

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Avg Market Price',
                data: [1200, 1250, 1240, 1300, 1310, 1350],
                borderColor: '#3A95ED',
                tension: 0.4
            }, {
                label: 'New Competitors',
                data: [2, 0, 1, 3, 0, 1],
                borderColor: '#DC3545',
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: false, title: { display: true, text: 'Price ($)' } },
                y1: { position: 'right', beginAtZero: true, title: { display: true, text: 'Count' } }
            }
        }
    });
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
