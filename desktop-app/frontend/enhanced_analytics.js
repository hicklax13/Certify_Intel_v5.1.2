/**
 * Certify Intel - Enhanced Analytics Module
 * Advanced visualizations and market analysis
 */

// ============== Market Quadrant Analysis ==============

function renderMarketQuadrant() {
    const container = document.getElementById('marketQuadrantContainer');
    if (!container || !competitors.length) return;

    // Calculate quadrant positions
    const quadrantData = competitors.slice(0, 15).map(comp => {
        // Parse customer count as proxy for market share
        const customers = parseInt((comp.customer_count || '0').replace(/\D/g, '')) || 50;

        // Parse employee growth as proxy for growth rate
        const employees = parseInt((comp.employee_count || '0').replace(/\D/g, '')) || 50;

        // Normalize to 0-100 scale
        const maxCustomers = Math.max(...competitors.map(c =>
            parseInt((c.customer_count || '0').replace(/\D/g, '')) || 50
        ));

        const marketShare = (customers / maxCustomers) * 100;
        const growthRate = Math.random() * 50 + 25; // Would use real growth data

        return {
            name: comp.name,
            x: marketShare,
            y: growthRate,
            threat: comp.threat_level,
            customers: customers
        };
    });

    // Create quadrant chart
    container.innerHTML = `
        <div class="quadrant-chart" style="position: relative; width: 100%; height: 400px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
            <!-- Quadrant labels -->
            <div style="position: absolute; top: 10px; left: 10px; font-weight: 600; color: #059669;">🌟 Stars</div>
            <div style="position: absolute; top: 10px; right: 10px; font-weight: 600; color: #7c3aed;">❓ Question Marks</div>
            <div style="position: absolute; bottom: 10px; left: 10px; font-weight: 600; color: #2563eb;">💰 Cash Cows</div>
            <div style="position: absolute; bottom: 10px; right: 10px; font-weight: 600; color: #64748b;">🐕 Dogs</div>
            
            <!-- Quadrant lines -->
            <div style="position: absolute; top: 50%; left: 0; right: 0; border-top: 2px dashed #cbd5e1;"></div>
            <div style="position: absolute; left: 50%; top: 0; bottom: 0; border-left: 2px dashed #cbd5e1;"></div>
            
            <!-- Data points -->
            ${quadrantData.map(d => `
                <div class="quadrant-point" 
                     style="position: absolute; 
                            left: ${d.x}%; 
                            bottom: ${d.y}%; 
                            transform: translate(-50%, 50%); 
                            width: ${Math.max(20, Math.min(50, d.customers / 100))}px; 
                            height: ${Math.max(20, Math.min(50, d.customers / 100))}px; 
                            border-radius: 50%; 
                            background: ${getThreatColor(d.threat)}; 
                            opacity: 0.8;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 10px;
                            color: white;
                            font-weight: bold;"
                     title="${d.name}: ${d.customers.toLocaleString()} customers">
                </div>
            `).join('')}
        </div>
        <div class="quadrant-legend" style="display: flex; gap: 20px; justify-content: center; margin-top: 15px; flex-wrap: wrap;">
            ${quadrantData.slice(0, 8).map(d => `
                <span style="display: flex; align-items: center; gap: 5px;">
                    <span style="width: 12px; height: 12px; border-radius: 50%; background: ${getThreatColor(d.threat)};"></span>
                    ${d.name}
                </span>
            `).join('')}
        </div>
    `;
}

function getThreatColor(threat) {
    switch (threat) {
        case 'High': return '#DC3545';
        case 'Medium': return '#FFC107';
        case 'Low': return '#28A745';
        default: return '#6C757D';
    }
}


// ============== Competitive Timeline ==============

async function renderCompetitorTimeline(competitorId) {
    const container = document.getElementById('timelineContainer');
    if (!container) return;

    container.innerHTML = '<p class="loading">Loading timeline...</p>';

    // Fetch changes for this competitor
    const result = await fetchAPI(`/api/changes?competitor_id=${competitorId}&days=365`);
    const changes = result?.changes || [];

    if (changes.length === 0) {
        container.innerHTML = '<p class="empty-state">No timeline events available</p>';
        return;
    }

    container.innerHTML = `
        <div class="timeline">
            ${changes.slice(0, 20).map(change => `
                <div class="timeline-item">
                    <div class="timeline-marker ${change.severity.toLowerCase()}"></div>
                    <div class="timeline-content">
                        <div class="timeline-date">${formatDate(change.detected_at)}</div>
                        <div class="timeline-title">${change.change_type}</div>
                        <div class="timeline-detail">
                            ${change.previous_value ? `${change.previous_value} → ` : ''}${change.new_value}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}


// ============== Enhanced Battlecard with Insights ==============

async function viewEnhancedBattlecard(id) {
    const comp = competitors.find(c => c.id === id);
    if (!comp) return;

    // Show loading modal
    const loadingContent = `
        <div class="battlecard-full">
            <h2>🃏 ${comp.name} Battlecard</h2>
            <p class="loading">Loading comprehensive insights...</p>
        </div>
    `;
    showModal(loadingContent);

    // Fetch comprehensive insights
    const insights = await fetchAPI(`/api/competitors/${id}/insights`);

    const content = `
        <div class="battlecard-full enhanced">
            <h2>🃏 ${comp.name} - Enhanced Battlecard</h2>
            <span class="threat-badge ${comp.threat_level.toLowerCase()}">${comp.threat_level} Threat</span>
            
            <!-- AI Threat Score -->
            <div class="insight-section">
                <h3>🎯 AI Threat Assessment</h3>
                ${insights.threat?.score ? `
                    <div class="threat-score-display" style="display: flex; align-items: center; gap: 15px; margin: 10px 0;">
                        <div class="score-circle" style="width: 80px; height: 80px; border-radius: 50%; background: conic-gradient(${getThreatScoreColor(insights.threat.score)} ${insights.threat.score}%, #e5e7eb ${insights.threat.score}%); display: flex; align-items: center; justify-content: center;">
                            <span style="background: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2em;">${insights.threat.score}</span>
                        </div>
                        <div>
                            <strong>Threat Level: ${insights.threat.level}</strong>
                            <p style="margin: 5px 0; color: #64748b;">${insights.threat.reasoning}</p>
                        </div>
                    </div>
                    <div style="margin-top: 10px;">
                        <strong>Key Risks:</strong>
                        <ul>${(insights.threat.key_risks || []).map(r => `<li>${r}</li>`).join('')}</ul>
                    </div>
                ` : '<p>Threat analysis unavailable</p>'}
            </div>

            <!-- Reviews Summary -->
            <div class="insight-section">
                <h3>⭐ G2 Reviews</h3>
                ${insights.reviews?.rating ? `
                    <div style="display: flex; align-items: center; gap: 10px; margin: 10px 0;">
                        <span style="font-size: 2em; font-weight: bold;">${insights.reviews.rating}</span>
                        <div>
                            <div>${'⭐'.repeat(Math.round(insights.reviews.rating))}</div>
                            <span style="color: #64748b;">${insights.reviews.overall_sentiment} sentiment</span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">
                        <div>
                            <strong style="color: #22c55e;">✅ Strengths</strong>
                            <ul style="margin: 5px 0;">${(insights.reviews.strengths || []).map(s => `<li>${s}</li>`).join('')}</ul>
                        </div>
                        <div>
                            <strong style="color: #ef4444;">⚠️ Weaknesses</strong>
                            <ul style="margin: 5px 0;">${(insights.reviews.weaknesses || []).map(w => `<li>${w}</li>`).join('')}</ul>
                        </div>
                    </div>
                ` : '<p>Review data unavailable</p>'}
            </div>

            <!-- Hiring Trends -->
            <div class="insight-section">
                <h3>👥 Hiring Signals</h3>
                ${insights.hiring?.total_openings !== undefined ? `
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 10px 0;">
                        <div style="text-align: center; padding: 10px; background: #f8fafc; border-radius: 8px;">
                            <div style="font-size: 1.5em; font-weight: bold;">${insights.hiring.total_openings}</div>
                            <div style="color: #64748b; font-size: 0.9em;">Open Roles</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: #f8fafc; border-radius: 8px;">
                            <div style="font-size: 1.5em; font-weight: bold;">${insights.hiring.hiring_intensity}</div>
                            <div style="color: #64748b; font-size: 0.9em;">Intensity</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: #f8fafc; border-radius: 8px;">
                            <div style="font-size: 1.5em; font-weight: bold;">${insights.hiring.growth_signal}</div>
                            <div style="color: #64748b; font-size: 0.9em;">Signal</div>
                        </div>
                    </div>
                    ${insights.hiring.competitive_implications?.length ? `
                        <strong>Competitive Implications:</strong>
                        <ul>${insights.hiring.competitive_implications.map(i => `<li>${i}</li>`).join('')}</ul>
                    ` : ''}
                ` : '<p>Hiring data unavailable</p>'}
            </div>

            <!-- Recent News -->
            <div class="insight-section">
                <h3>📰 Recent News</h3>
                ${insights.news?.recent_headlines?.length ? `
                    <ul>${insights.news.recent_headlines.slice(0, 3).map(h => `<li>${h}</li>`).join('')}</ul>
                    <p style="color: #64748b; font-size: 0.9em;">
                        Sentiment: ${insights.news.sentiment?.positive || 0} positive, 
                        ${insights.news.sentiment?.negative || 0} negative, 
                        ${insights.news.sentiment?.neutral || 0} neutral
                    </p>
                ` : '<p>No recent news</p>'}
            </div>

            <!-- Quick Facts -->
            <div class="insight-section">
                <h3>📋 Quick Facts</h3>
                <table class="data-table" style="margin-bottom: 20px;">
                    <tr><td>Founded</td><td>${comp.year_founded || 'Unknown'}</td></tr>
                    <tr><td>Headquarters</td><td>${comp.headquarters || 'Unknown'}</td></tr>
                    <tr><td>Employees</td><td>${comp.employee_count || 'Unknown'}</td></tr>
                    <tr><td>Customers</td><td>${comp.customer_count || 'Unknown'}</td></tr>
                    <tr><td>Funding</td><td>${comp.funding_total || 'Unknown'}</td></tr>
                    <tr><td>Pricing</td><td>${comp.pricing_model || 'N/A'} - ${comp.base_price || 'N/A'}</td></tr>
                </table>
            </div>

            <button class="btn btn-primary" onclick="downloadBattlecard(${id})">📄 Download PDF</button>
        </div>
    `;

    showModal(content);
}

function getThreatScoreColor(score) {
    if (score >= 70) return '#DC3545';
    if (score >= 40) return '#FFC107';
    return '#28A745';
}


// ============== Win/Loss Tracker ==============

let winLossData = [];

function showWinLossModal() {
    const content = `
        <h2>🏆 Log Competitive Deal</h2>
        <form id="winLossForm" onsubmit="logWinLoss(event)">
            <div class="form-group">
                <label>Competitor</label>
                <select name="competitor_id" required>
                    ${competitors.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Deal Name</label>
                <input type="text" name="deal_name" required placeholder="e.g., Mercy Health System">
            </div>
            <div class="form-group">
                <label>Deal Value ($)</label>
                <input type="number" name="deal_value" placeholder="100000">
            </div>
            <div class="form-group">
                <label>Outcome</label>
                <select name="outcome" required>
                    <option value="Won">Won ✅</option>
                    <option value="Lost">Lost ❌</option>
                </select>
            </div>
            <div class="form-group">
                <label>Loss Reason (if applicable)</label>
                <select name="loss_reason">
                    <option value="">N/A</option>
                    <option value="Price">Price</option>
                    <option value="Features">Features</option>
                    <option value="Integration">Integration</option>
                    <option value="Relationship">Existing Relationship</option>
                    <option value="Support">Support Concerns</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea name="notes" rows="3" placeholder="Additional context..."></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Log Deal</button>
        </form>
    `;
    showModal(content);
}

function logWinLoss(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    // Add to local storage for now
    const deal = {
        ...data,
        id: Date.now(),
        logged_at: new Date().toISOString()
    };

    winLossData.push(deal);
    localStorage.setItem('certifyIntelWinLoss', JSON.stringify(winLossData));

    showToast(`Deal logged: ${data.outcome} against ${competitors.find(c => c.id == data.competitor_id)?.name}`, 'success');
    closeModal();
    renderWinLossStats();
}

function renderWinLossStats() {
    // Load from localStorage
    const stored = localStorage.getItem('certifyIntelWinLoss');
    if (stored) {
        winLossData = JSON.parse(stored);
    }

    const container = document.getElementById('winLossContainer');
    if (!container) return;

    const wins = winLossData.filter(d => d.outcome === 'Won').length;
    const losses = winLossData.filter(d => d.outcome === 'Lost').length;
    const total = wins + losses;
    const winRate = total > 0 ? Math.round((wins / total) * 100) : 0;

    // Loss reasons breakdown
    const lossReasons = {};
    winLossData.filter(d => d.outcome === 'Lost').forEach(d => {
        const reason = d.loss_reason || 'Unknown';
        lossReasons[reason] = (lossReasons[reason] || 0) + 1;
    });

    container.innerHTML = `
        <div class="win-loss-stats" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
            <div style="text-align: center; padding: 20px; background: #dcfce7; border-radius: 8px;">
                <div style="font-size: 2em; font-weight: bold; color: #16a34a;">${wins}</div>
                <div>Wins</div>
            </div>
            <div style="text-align: center; padding: 20px; background: #fee2e2; border-radius: 8px;">
                <div style="font-size: 2em; font-weight: bold; color: #dc2626;">${losses}</div>
                <div>Losses</div>
            </div>
            <div style="text-align: center; padding: 20px; background: #e0f2fe; border-radius: 8px;">
                <div style="font-size: 2em; font-weight: bold; color: #0284c7;">${winRate}%</div>
                <div>Win Rate</div>
            </div>
        </div>
        ${losses > 0 ? `
            <h4>Loss Reasons</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                ${Object.entries(lossReasons).map(([reason, count]) => `
                    <span style="background: #fef2f2; padding: 5px 12px; border-radius: 20px; color: #b91c1c;">
                        ${reason}: ${count}
                    </span>
                `).join('')}
            </div>
        ` : ''}
        <button class="btn btn-primary" style="margin-top: 15px;" onclick="showWinLossModal()">+ Log New Deal</button>
    `;
}


// ============== Webhooks Management ==============

function showWebhookSettings() {
    const stored = localStorage.getItem('certifyIntelWebhooks');
    const webhooks = stored ? JSON.parse(stored) : [];

    const content = `
        <h2>🔗 Webhook Configuration</h2>
        <p style="color: #64748b; margin-bottom: 20px;">Configure webhooks to receive real-time notifications on competitor changes.</p>
        
        <form id="webhookForm" onsubmit="addWebhook(event)">
            <div class="form-group">
                <label>Webhook URL</label>
                <input type="url" name="url" required placeholder="https://hooks.slack.com/...">
            </div>
            <div class="form-group">
                <label>Event Types</label>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    <label><input type="checkbox" name="events" value="price_change"> Price Changes</label>
                    <label><input type="checkbox" name="events" value="threat_level"> Threat Level</label>
                    <label><input type="checkbox" name="events" value="new_competitor"> New Competitor</label>
                    <label><input type="checkbox" name="events" value="news_alert"> News Alert</label>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">Add Webhook</button>
        </form>
        
        <h3 style="margin-top: 20px;">Active Webhooks</h3>
        <div id="webhookList">
            ${webhooks.length ? webhooks.map((w, i) => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #f8fafc; border-radius: 8px; margin-top: 10px;">
                    <div>
                        <code style="word-break: break-all;">${w.url}</code>
                        <div style="color: #64748b; font-size: 0.9em; margin-top: 5px;">Events: ${w.events.join(', ')}</div>
                    </div>
                    <button class="btn btn-secondary" onclick="removeWebhook(${i})">Remove</button>
                </div>
            `).join('') : '<p class="empty-state">No webhooks configured</p>'}
        </div>
    `;
    showModal(content);
}

function addWebhook(event) {
    event.preventDefault();
    const form = event.target;
    const url = form.querySelector('input[name="url"]').value;
    const events = Array.from(form.querySelectorAll('input[name="events"]:checked')).map(cb => cb.value);

    if (events.length === 0) {
        showToast('Please select at least one event type', 'warning');
        return;
    }

    const stored = localStorage.getItem('certifyIntelWebhooks');
    const webhooks = stored ? JSON.parse(stored) : [];
    webhooks.push({ url, events, created_at: new Date().toISOString() });
    localStorage.setItem('certifyIntelWebhooks', JSON.stringify(webhooks));

    showToast('Webhook added successfully', 'success');
    showWebhookSettings(); // Refresh modal
}

function removeWebhook(index) {
    const stored = localStorage.getItem('certifyIntelWebhooks');
    const webhooks = stored ? JSON.parse(stored) : [];
    webhooks.splice(index, 1);
    localStorage.setItem('certifyIntelWebhooks', JSON.stringify(webhooks));

    showToast('Webhook removed', 'info');
    showWebhookSettings(); // Refresh modal
}


// Initialize enhanced features
document.addEventListener('DOMContentLoaded', () => {
    // Load win/loss data
    renderWinLossStats();
});
