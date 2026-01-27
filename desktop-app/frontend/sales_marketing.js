/**
 * Certify Intel - Sales & Marketing Module JavaScript (v5.0.7)
 * Handles dimension scoring, battlecard generation, competitor comparison, and talking points.
 *
 * Integrates with existing app_v2.js and API endpoints in /api/sales-marketing/
 */

// ============== Constants ==============

const SM_DIMENSIONS = [
    { id: 'product_packaging', name: 'Product Modules & Packaging', shortName: 'Packaging', icon: '📦' },
    { id: 'integration_depth', name: 'Interoperability & Integration', shortName: 'Integration', icon: '🔗' },
    { id: 'support_service', name: 'Customer Support & Service', shortName: 'Support', icon: '🎧' },
    { id: 'retention_stickiness', name: 'Retention & Product Stickiness', shortName: 'Retention', icon: '🔒' },
    { id: 'user_adoption', name: 'User Adoption & Ease of Use', shortName: 'Adoption', icon: '👥' },
    { id: 'implementation_ttv', name: 'Implementation & Time to Value', shortName: 'Implementation', icon: '⏱️' },
    { id: 'reliability_enterprise', name: 'Reliability & Enterprise Readiness', shortName: 'Reliability', icon: '🏢' },
    { id: 'pricing_flexibility', name: 'Pricing & Commercial Flexibility', shortName: 'Pricing', icon: '💰' },
    { id: 'reporting_analytics', name: 'Reporting & Analytics', shortName: 'Analytics', icon: '📊' }
];

const SM_SCORE_LABELS = {
    1: 'Major Weakness',
    2: 'Weakness',
    3: 'Neutral',
    4: 'Strength',
    5: 'Major Strength'
};

const SM_SCORE_COLORS = {
    1: '#dc3545',
    2: '#fd7e14',
    3: '#6c757d',
    4: '#28a745',
    5: '#198754'
};

// Current state
let currentDimensionData = {};
let dimensionRadarChart = null;

// ============== Tab Navigation ==============

function showSalesMarketingTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.sm-tab-content').forEach(tab => {
        tab.style.display = 'none';
        tab.classList.remove('active');
    });
    document.querySelectorAll('.sm-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    const tab = document.getElementById('sm-' + tabName + 'Tab');
    if (tab) {
        tab.style.display = 'block';
        tab.classList.add('active');
    }

    // Highlight active button
    event.target.classList.add('active');

    // Load data for specific tabs
    if (tabName === 'dimensions') {
        // Dimensions tab - data loaded on competitor select
    } else if (tabName === 'comparison') {
        // Initialize comparison - nothing to preload
    } else if (tabName === 'talkingpoints') {
        loadTalkingPointsDimensions();
    }
}

// ============== Initialization ==============

function initSalesMarketingModule() {
    console.log('Initializing Sales & Marketing Module...');

    // Populate all competitor dropdowns
    const selects = [
        'dimensionCompetitorSelect',
        'battlecardCompetitorSelect',
        'compareCompetitor1',
        'compareCompetitor2',
        'talkingPointsCompetitor'
    ];

    // Use global competitors array from app_v2.js
    const competitorOptions = (window.competitors || [])
        .filter(c => !c.is_deleted)
        .map(c => `<option value="${c.id}">${c.name}</option>`)
        .join('');

    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            select.innerHTML = '<option value="">-- Select Competitor --</option>' + competitorOptions;
        }
    });

    // Populate dimensions dropdown for talking points
    loadTalkingPointsDimensions();

    console.log('Sales & Marketing Module initialized');
}

function loadTalkingPointsDimensions() {
    const dimSelect = document.getElementById('talkingPointsDimension');
    if (dimSelect) {
        dimSelect.innerHTML = '<option value="">All Dimensions</option>' +
            SM_DIMENSIONS.map(d => `<option value="${d.id}">${d.icon} ${d.shortName}</option>`).join('');
    }
}

// ============== Dimension Scorecard ==============

async function loadCompetitorDimensions() {
    const competitorId = document.getElementById('dimensionCompetitorSelect').value;
    if (!competitorId) {
        document.getElementById('dimensionGrid').innerHTML =
            '<p class="sm-placeholder">Select a competitor to view and edit their 9-dimension scorecard.</p>';
        document.getElementById('dimensionProfileSummary').style.display = 'none';
        return;
    }

    try {
        showLoading('Loading dimension scores...');

        const response = await fetch(`/api/sales-marketing/competitors/${competitorId}/dimensions`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        currentDimensionData = data;

        // Update profile summary
        updateDimensionSummary(data);

        // Render dimension grid
        renderDimensionGrid(data);

        hideLoading();
    } catch (error) {
        console.error('Failed to load dimensions:', error);
        hideLoading();
        showNotification('Failed to load dimension scores', 'error');
    }
}

function updateDimensionSummary(data) {
    const summary = document.getElementById('dimensionProfileSummary');
    summary.style.display = 'flex';

    document.getElementById('smOverallScore').textContent =
        data.overall_score ? data.overall_score.toFixed(1) + '/5' : 'Not Scored';
    document.getElementById('smStrengthCount').textContent = data.strengths?.length || 0;
    document.getElementById('smWeaknessCount').textContent = data.weaknesses?.length || 0;

    const priorityEl = document.getElementById('smSalesPriority');
    priorityEl.textContent = data.sales_priority || 'Not Set';
    priorityEl.className = 'sm-summary-value sm-priority-' + (data.sales_priority || 'low').toLowerCase();
}

function renderDimensionGrid(data) {
    const grid = document.getElementById('dimensionGrid');

    grid.innerHTML = SM_DIMENSIONS.map(dim => {
        const dimData = data.dimensions?.[dim.id] || {};
        const score = dimData.score || 0;
        const evidence = dimData.evidence || '';
        const updated = dimData.updated_at ? new Date(dimData.updated_at).toLocaleDateString() : '';

        return `
            <div class="sm-dimension-card" data-dimension="${dim.id}">
                <div class="sm-dimension-header">
                    <span class="sm-dimension-icon">${dim.icon}</span>
                    <span class="sm-dimension-name">${dim.name}</span>
                </div>
                <div class="sm-dimension-score">
                    ${renderScoreSelector(dim.id, score)}
                </div>
                <div class="sm-dimension-evidence">
                    <textarea
                        placeholder="Enter evidence and sources for this score..."
                        id="evidence-${dim.id}"
                        class="form-control"
                        rows="3"
                    >${evidence}</textarea>
                </div>
                <div class="sm-dimension-footer">
                    <span class="sm-dimension-meta">
                        ${updated ? `Updated: ${updated}` : 'Not scored yet'}
                    </span>
                    <button class="btn btn-sm btn-primary" onclick="saveDimensionScore('${dim.id}')">
                        Save
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function renderScoreSelector(dimensionId, currentScore) {
    return `<div class="sm-score-selector">` +
        [1, 2, 3, 4, 5].map(score => `
            <button
                class="sm-score-btn ${score === currentScore ? 'active' : ''}"
                onclick="selectDimensionScore('${dimensionId}', ${score})"
                title="${SM_SCORE_LABELS[score]}"
                style="${score === currentScore ? `background-color: ${SM_SCORE_COLORS[score]}; color: white;` : ''}"
            >
                ${score}
            </button>
        `).join('') +
    `</div>`;
}

function selectDimensionScore(dimensionId, score) {
    const card = document.querySelector(`[data-dimension="${dimensionId}"]`);
    if (!card) return;

    // Remove active class from all buttons
    card.querySelectorAll('.sm-score-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.style.backgroundColor = '';
        btn.style.color = '';
    });

    // Set active on selected
    const selectedBtn = card.querySelector(`.sm-score-btn:nth-child(${score})`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
        selectedBtn.style.backgroundColor = SM_SCORE_COLORS[score];
        selectedBtn.style.color = 'white';
    }
}

async function saveDimensionScore(dimensionId) {
    const competitorId = document.getElementById('dimensionCompetitorSelect').value;
    if (!competitorId) {
        showNotification('Please select a competitor first', 'error');
        return;
    }

    const card = document.querySelector(`[data-dimension="${dimensionId}"]`);
    const activeBtn = card.querySelector('.sm-score-btn.active');
    const evidence = document.getElementById(`evidence-${dimensionId}`).value;

    if (!activeBtn) {
        showNotification('Please select a score (1-5)', 'error');
        return;
    }

    const score = parseInt(activeBtn.textContent);

    try {
        const response = await fetch(
            `/api/sales-marketing/competitors/${competitorId}/dimensions/${dimensionId}?user_email=${encodeURIComponent(getCurrentUserEmail())}`,
            {
                method: 'PUT',
                headers: {
                    ...getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    dimension_id: dimensionId,
                    score: score,
                    evidence: evidence,
                    source: 'manual',
                    confidence: 'medium'
                })
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        showNotification(`${getDimensionName(dimensionId)} saved (Score: ${score})`, 'success');

        // Refresh to update summary
        await loadCompetitorDimensions();

    } catch (error) {
        console.error('Failed to save dimension:', error);
        showNotification('Failed to save dimension score', 'error');
    }
}

async function saveAllDimensions() {
    const competitorId = document.getElementById('dimensionCompetitorSelect').value;
    if (!competitorId) {
        showNotification('Please select a competitor first', 'error');
        return;
    }

    const updates = [];

    SM_DIMENSIONS.forEach(dim => {
        const card = document.querySelector(`[data-dimension="${dim.id}"]`);
        if (!card) return;

        const activeBtn = card.querySelector('.sm-score-btn.active');
        const evidence = document.getElementById(`evidence-${dim.id}`).value;

        if (activeBtn) {
            updates.push({
                dimension_id: dim.id,
                score: parseInt(activeBtn.textContent),
                evidence: evidence,
                source: 'manual',
                confidence: 'medium'
            });
        }
    });

    if (updates.length === 0) {
        showNotification('No dimensions have scores selected', 'warning');
        return;
    }

    try {
        showLoading('Saving all dimensions...');

        const response = await fetch(
            `/api/sales-marketing/competitors/${competitorId}/dimensions/bulk-update?user_email=${encodeURIComponent(getCurrentUserEmail())}`,
            {
                method: 'POST',
                headers: {
                    ...getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();
        hideLoading();

        showNotification(`Saved ${result.successful} dimension(s)`, 'success');

        // Refresh
        await loadCompetitorDimensions();

    } catch (error) {
        hideLoading();
        console.error('Failed to save dimensions:', error);
        showNotification('Failed to save dimensions', 'error');
    }
}

async function aiSuggestDimensions() {
    const competitorId = document.getElementById('dimensionCompetitorSelect').value;
    if (!competitorId) {
        showNotification('Please select a competitor first', 'error');
        return;
    }

    try {
        showLoading('AI analyzing competitor data...');

        const response = await fetch(
            `/api/sales-marketing/competitors/${competitorId}/dimensions/ai-suggest`,
            {
                method: 'POST',
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        hideLoading();

        if (!data.suggestions || Object.keys(data.suggestions).length === 0) {
            showNotification('No AI suggestions available - not enough data', 'warning');
            return;
        }

        // Apply suggestions to the UI
        Object.entries(data.suggestions).forEach(([dimId, suggestion]) => {
            if (suggestion.score) {
                selectDimensionScore(dimId, suggestion.score);
            }
            if (suggestion.evidence) {
                const evidenceField = document.getElementById(`evidence-${dimId}`);
                if (evidenceField && !evidenceField.value) {
                    evidenceField.value = suggestion.evidence;
                }
            }
        });

        showNotification(`AI suggested ${Object.keys(data.suggestions).length} dimension score(s)`, 'success');

    } catch (error) {
        hideLoading();
        console.error('AI suggestion failed:', error);
        showNotification('AI suggestion failed', 'error');
    }
}

// ============== Dynamic Battlecards ==============

async function generateDynamicBattlecard() {
    const competitorId = document.getElementById('battlecardCompetitorSelect').value;
    const battlecardType = document.getElementById('battlecardType').value;

    if (!competitorId) {
        showNotification('Please select a competitor', 'error');
        return;
    }

    const container = document.getElementById('dynamicBattlecardContent');
    container.innerHTML = '<div class="sm-loading">Generating battlecard...</div>';

    try {
        const response = await fetch('/api/sales-marketing/battlecards/generate', {
            method: 'POST',
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                competitor_id: parseInt(competitorId),
                battlecard_type: battlecardType
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        renderDynamicBattlecard(data);

    } catch (error) {
        console.error('Failed to generate battlecard:', error);
        container.innerHTML = '<p class="sm-error">Failed to generate battlecard. Please try again.</p>';
        showNotification('Battlecard generation failed', 'error');
    }
}

function renderDynamicBattlecard(data) {
    const container = document.getElementById('dynamicBattlecardContent');

    const sectionsHtml = data.sections.map(section => {
        let contentHtml = '';

        if (typeof section.content === 'string') {
            contentHtml = `<p>${section.content}</p>`;
        } else if (Array.isArray(section.content)) {
            contentHtml = '<ul>' + section.content.map(item => {
                if (typeof item === 'object') {
                    return '<li>' + Object.entries(item)
                        .map(([k, v]) => `<strong>${formatLabel(k)}:</strong> ${v}`)
                        .join('<br>') + '</li>';
                }
                return `<li>${item}</li>`;
            }).join('') + '</ul>';
        } else if (typeof section.content === 'object') {
            contentHtml = '<div class="sm-facts-grid">' +
                Object.entries(section.content)
                    .map(([k, v]) => `<div class="sm-fact"><span class="sm-fact-label">${formatLabel(k)}</span><span class="sm-fact-value">${v}</span></div>`)
                    .join('') +
                '</div>';
        }

        return `
            <div class="sm-battlecard-section">
                <h4>${section.title}</h4>
                ${contentHtml}
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <div class="sm-battlecard">
            <div class="sm-battlecard-header">
                <h3>${data.title}</h3>
                <div class="sm-battlecard-actions">
                    ${data.id ? `
                        <button class="btn btn-secondary" onclick="exportBattlecardMarkdown(${data.id})">
                            📝 Export Markdown
                        </button>
                        <button class="btn btn-primary" onclick="exportBattlecardPDF(${data.id})">
                            📄 Export PDF
                        </button>
                    ` : ''}
                </div>
            </div>
            <div class="sm-battlecard-meta">
                <span>Type: ${data.battlecard_type}</span>
                <span>Generated: ${new Date(data.generated_at).toLocaleString()}</span>
            </div>
            <div class="sm-battlecard-body">
                ${sectionsHtml}
            </div>
        </div>
    `;
}

async function exportBattlecardPDF(battlecardId) {
    window.open(`/api/sales-marketing/battlecards/${battlecardId}/pdf`, '_blank');
}

async function exportBattlecardMarkdown(battlecardId) {
    window.open(`/api/sales-marketing/battlecards/${battlecardId}/markdown`, '_blank');
}

// ============== Competitor Comparison ==============

async function loadDimensionComparison() {
    const comp1 = document.getElementById('compareCompetitor1').value;
    const comp2 = document.getElementById('compareCompetitor2').value;

    if (!comp1 || !comp2) {
        showNotification('Please select two competitors to compare', 'error');
        return;
    }

    if (comp1 === comp2) {
        showNotification('Please select different competitors', 'error');
        return;
    }

    try {
        showLoading('Loading comparison...');

        const response = await fetch('/api/sales-marketing/compare/dimensions', {
            method: 'POST',
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                competitor_ids: [parseInt(comp1), parseInt(comp2)]
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        hideLoading();

        renderComparisonRadarChart(data);
        renderComparisonDetails(data);

    } catch (error) {
        hideLoading();
        console.error('Comparison failed:', error);
        showNotification('Failed to load comparison', 'error');
    }
}

function renderComparisonRadarChart(data) {
    const ctx = document.getElementById('dimensionRadarChart').getContext('2d');

    // Destroy existing chart
    if (dimensionRadarChart) {
        dimensionRadarChart.destroy();
    }

    const labels = SM_DIMENSIONS.map(d => d.shortName);
    const datasets = data.competitors.map((comp, i) => ({
        label: comp.name,
        data: SM_DIMENSIONS.map(d => comp.dimensions[d.id]?.score || 0),
        borderColor: i === 0 ? '#2F5496' : '#22c55e',
        backgroundColor: i === 0 ? 'rgba(47, 84, 150, 0.2)' : 'rgba(34, 197, 94, 0.2)',
        borderWidth: 2,
        pointRadius: 4
    }));

    dimensionRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    min: 0,
                    max: 5,
                    ticks: {
                        stepSize: 1,
                        display: true
                    },
                    pointLabels: {
                        font: { size: 11 }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

function renderComparisonDetails(data) {
    const container = document.getElementById('comparisonDetails');

    // Find advantages and weaknesses
    const comp1 = data.competitors[0];
    const comp2 = data.competitors[1];

    let detailsHtml = '<div class="sm-comparison-grid">';

    SM_DIMENSIONS.forEach(dim => {
        const score1 = comp1.dimensions[dim.id]?.score || 0;
        const score2 = comp2.dimensions[dim.id]?.score || 0;
        const diff = score1 - score2;

        let indicator = '';
        if (diff > 0) indicator = `<span class="sm-indicator sm-better">${comp1.name} +${diff}</span>`;
        else if (diff < 0) indicator = `<span class="sm-indicator sm-worse">${comp2.name} +${Math.abs(diff)}</span>`;
        else indicator = '<span class="sm-indicator sm-even">Even</span>';

        detailsHtml += `
            <div class="sm-comparison-row">
                <span class="sm-dim-icon">${dim.icon}</span>
                <span class="sm-dim-name">${dim.shortName}</span>
                <span class="sm-score">${score1 || '-'}</span>
                <span class="sm-vs">vs</span>
                <span class="sm-score">${score2 || '-'}</span>
                ${indicator}
            </div>
        `;
    });

    detailsHtml += '</div>';
    container.innerHTML = detailsHtml;
}

async function compareVsCertify() {
    const comp1 = document.getElementById('compareCompetitor1').value;
    if (!comp1) {
        showNotification('Please select a competitor in the first dropdown', 'error');
        return;
    }

    try {
        showLoading('Comparing vs Certify Health...');

        const response = await fetch(`/api/sales-marketing/compare/${comp1}/vs-certify`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        hideLoading();

        // Transform to comparison format
        const comparisonData = {
            competitors: [
                {
                    name: data.competitor.name,
                    dimensions: Object.fromEntries(
                        Object.entries(data.competitor.scores).map(([k, v]) => [k, { score: v }])
                    )
                },
                {
                    name: 'Certify Health',
                    dimensions: Object.fromEntries(
                        Object.entries(data.certify_health.scores).map(([k, v]) => [k, { score: v }])
                    )
                }
            ]
        };

        renderComparisonRadarChart(comparisonData);
        renderCertifyComparisonDetails(data);

    } catch (error) {
        hideLoading();
        console.error('Certify comparison failed:', error);
        showNotification('Failed to load Certify comparison', 'error');
    }
}

function renderCertifyComparisonDetails(data) {
    const container = document.getElementById('comparisonDetails');

    let html = `
        <div class="sm-certify-comparison">
            <h4>Competitive Analysis vs ${data.competitor.name}</h4>

            <div class="sm-advantages">
                <h5>Our Advantages (${data.advantages.length})</h5>
                ${data.advantages.length ? data.advantages.map(a => `
                    <div class="sm-advantage-item">
                        <span class="sm-adv-dim">${a.dimension}</span>
                        <span class="sm-adv-scores">Certify: ${a.certify_score} vs ${a.competitor_score}</span>
                        <span class="sm-adv-gap">+${a.gap} advantage</span>
                    </div>
                `).join('') : '<p>No clear advantages identified</p>'}
            </div>

            <div class="sm-challenges">
                <h5>Challenges (${data.challenges.length})</h5>
                ${data.challenges.length ? data.challenges.map(c => `
                    <div class="sm-challenge-item">
                        <span class="sm-ch-dim">${c.dimension}</span>
                        <span class="sm-ch-scores">Certify: ${c.certify_score} vs ${c.competitor_score}</span>
                        <span class="sm-ch-gap">-${c.gap} gap</span>
                    </div>
                `).join('') : '<p>No significant challenges identified</p>'}
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// ============== Talking Points ==============

async function loadTalkingPoints() {
    const competitorId = document.getElementById('talkingPointsCompetitor').value;
    if (!competitorId) {
        document.getElementById('talkingPointsList').innerHTML =
            '<p class="sm-placeholder">Select a competitor to view talking points organized by dimension.</p>';
        return;
    }

    const dimensionId = document.getElementById('talkingPointsDimension').value || '';
    const pointType = document.getElementById('talkingPointsType').value || '';

    try {
        let url = `/api/sales-marketing/competitors/${competitorId}/talking-points?`;
        if (dimensionId) url += `dimension_id=${dimensionId}&`;
        if (pointType) url += `point_type=${pointType}&`;

        const response = await fetch(url, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        renderTalkingPoints(data.talking_points);

    } catch (error) {
        console.error('Failed to load talking points:', error);
        showNotification('Failed to load talking points', 'error');
    }
}

function renderTalkingPoints(points) {
    const container = document.getElementById('talkingPointsList');

    if (!points || points.length === 0) {
        container.innerHTML = `
            <div class="sm-empty-state">
                <p>No talking points found for this selection.</p>
                <button class="btn btn-primary" onclick="showAddTalkingPointModal()">
                    ➕ Add First Talking Point
                </button>
            </div>
        `;
        return;
    }

    // Group by dimension
    const byDimension = {};
    points.forEach(p => {
        if (!byDimension[p.dimension_id]) {
            byDimension[p.dimension_id] = [];
        }
        byDimension[p.dimension_id].push(p);
    });

    let html = '';
    Object.entries(byDimension).forEach(([dimId, dimPoints]) => {
        const dim = SM_DIMENSIONS.find(d => d.id === dimId) || { icon: '?', name: dimId };

        html += `
            <div class="sm-tp-dimension">
                <h4>${dim.icon} ${dim.name}</h4>
                <div class="sm-tp-list">
                    ${dimPoints.map(p => `
                        <div class="sm-talking-point sm-tp-${p.point_type}">
                            <div class="sm-tp-header">
                                <span class="sm-tp-type">${formatPointType(p.point_type)}</span>
                                ${p.effectiveness_score ? `
                                    <span class="sm-tp-effectiveness" title="Effectiveness">
                                        ${'★'.repeat(p.effectiveness_score)}${'☆'.repeat(5 - p.effectiveness_score)}
                                    </span>
                                ` : ''}
                            </div>
                            <p class="sm-tp-content">${p.content}</p>
                            ${p.context ? `<p class="sm-tp-context">Context: ${p.context}</p>` : ''}
                            <div class="sm-tp-footer">
                                <span class="sm-tp-meta">By ${p.created_by} on ${new Date(p.created_at).toLocaleDateString()}</span>
                                <button class="btn btn-sm btn-secondary" onclick="deleteTalkingPoint(${p.id})">Delete</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function showAddTalkingPointModal() {
    const competitorId = document.getElementById('talkingPointsCompetitor').value;
    if (!competitorId) {
        showNotification('Please select a competitor first', 'error');
        return;
    }

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'addTalkingPointModal';
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };

    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Add Talking Point</h3>
                <button class="modal-close" onclick="document.getElementById('addTalkingPointModal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>Dimension</label>
                    <select id="newTpDimension" class="form-select">
                        ${SM_DIMENSIONS.map(d => `<option value="${d.id}">${d.icon} ${d.name}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>Type</label>
                    <select id="newTpType" class="form-select">
                        <option value="strength">Strength</option>
                        <option value="weakness">Weakness</option>
                        <option value="objection">Objection</option>
                        <option value="counter">Counter-Point</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Talking Point</label>
                    <textarea id="newTpContent" class="form-control" rows="3" placeholder="Enter the talking point..."></textarea>
                </div>
                <div class="form-group">
                    <label>Context (Optional)</label>
                    <input type="text" id="newTpContext" class="form-control" placeholder="When to use this talking point">
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="document.getElementById('addTalkingPointModal').remove()">Cancel</button>
                <button class="btn btn-primary" onclick="saveTalkingPoint()">Save</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

async function saveTalkingPoint() {
    const competitorId = document.getElementById('talkingPointsCompetitor').value;
    const dimensionId = document.getElementById('newTpDimension').value;
    const pointType = document.getElementById('newTpType').value;
    const content = document.getElementById('newTpContent').value;
    const context = document.getElementById('newTpContext').value;

    if (!content.trim()) {
        showNotification('Please enter the talking point content', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/sales-marketing/talking-points?user_email=${encodeURIComponent(getCurrentUserEmail())}`, {
            method: 'POST',
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                competitor_id: parseInt(competitorId),
                dimension_id: dimensionId,
                point_type: pointType,
                content: content.trim(),
                context: context.trim() || null
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        document.getElementById('addTalkingPointModal').remove();
        showNotification('Talking point added', 'success');
        loadTalkingPoints();

    } catch (error) {
        console.error('Failed to save talking point:', error);
        showNotification('Failed to save talking point', 'error');
    }
}

async function deleteTalkingPoint(pointId) {
    if (!confirm('Delete this talking point?')) return;

    try {
        const response = await fetch(`/api/sales-marketing/talking-points/${pointId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        showNotification('Talking point deleted', 'success');
        loadTalkingPoints();

    } catch (error) {
        console.error('Failed to delete talking point:', error);
        showNotification('Failed to delete talking point', 'error');
    }
}

// ============== Utility Functions ==============

function getDimensionName(dimensionId) {
    const dim = SM_DIMENSIONS.find(d => d.id === dimensionId);
    return dim ? dim.name : dimensionId;
}

function formatLabel(label) {
    return label.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatPointType(type) {
    const labels = {
        strength: '💪 Strength',
        weakness: '⚠️ Weakness',
        objection: '🤔 Objection',
        counter: '🔄 Counter'
    };
    return labels[type] || type;
}

function getCurrentUserEmail() {
    // Try to get from localStorage or return default
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return user.email || 'system@certifyhealth.com';
}

function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

function showLoading(message) {
    // Use existing loading mechanism from app_v2.js if available
    if (typeof window.showLoadingOverlay === 'function') {
        window.showLoadingOverlay(message);
    } else {
        console.log('Loading:', message);
    }
}

function hideLoading() {
    if (typeof window.hideLoadingOverlay === 'function') {
        window.hideLoadingOverlay();
    }
}

function showNotification(message, type) {
    // Use existing notification mechanism from app_v2.js if available
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
    } else {
        console.log(`[${type}] ${message}`);
        alert(message);
    }
}

// ============== Battlecard Page Dimension Widget (v5.0.7) ==============

/**
 * Initialize the dimension widget on the Battlecard page.
 * Called when the battlecards page loads.
 */
async function initBattlecardDimensionWidget() {
    const select = document.getElementById('battlecardDimensionCompetitor');
    if (!select) return;

    try {
        const response = await fetch('/api/competitors', {
            headers: getAuthHeaders()
        });

        if (!response.ok) return;

        const competitors = await response.json();

        select.innerHTML = '<option value="">-- Select Competitor for Dimensions --</option>';
        competitors.forEach(c => {
            const option = document.createElement('option');
            option.value = c.id;
            option.textContent = `${c.name} (${c.threat_level || 'Unknown'} Threat)`;
            select.appendChild(option);
        });

    } catch (error) {
        console.error('Failed to load competitors for dimension widget:', error);
    }
}

/**
 * Load and display dimension scores for the selected competitor in the widget.
 */
async function loadBattlecardDimensionWidget() {
    const competitorId = document.getElementById('battlecardDimensionCompetitor').value;
    const container = document.getElementById('battlecardDimensionScores');

    if (!competitorId) {
        container.innerHTML = '<p class="sm-placeholder">Select a competitor to see their dimension scores</p>';
        return;
    }

    try {
        const response = await fetch(`/api/sales-marketing/competitors/${competitorId}/dimensions`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        renderDimensionWidget(data);

    } catch (error) {
        console.error('Failed to load dimension widget:', error);
        container.innerHTML = '<p class="sm-placeholder">Failed to load dimension scores</p>';
    }
}

/**
 * Render the compact dimension scores widget.
 */
function renderDimensionWidget(data) {
    const container = document.getElementById('battlecardDimensionScores');

    const dimensions = data.dimensions || {};
    const overall = data.overall_score;

    let html = '<div class="dimension-widget-grid">';

    // Overall score badge
    if (overall) {
        html += `
            <div class="dimension-widget-overall">
                <span class="widget-overall-label">Overall</span>
                <span class="widget-overall-score">${overall.toFixed(1)}/5</span>
            </div>
        `;
    }

    // Compact dimension scores
    SM_DIMENSIONS.forEach(dim => {
        const dimData = dimensions[dim.id] || {};
        const score = dimData.score;
        const scoreColor = score ? SM_SCORE_COLORS[score] : '#ccc';
        const scoreLabel = score ? SM_SCORE_LABELS[score] : 'Not Scored';

        html += `
            <div class="dimension-widget-item" title="${dim.name}: ${scoreLabel}">
                <span class="widget-dim-icon">${dim.icon}</span>
                <span class="widget-dim-name">${dim.shortName}</span>
                <span class="widget-dim-score" style="background-color: ${scoreColor}">
                    ${score || '-'}
                </span>
            </div>
        `;
    });

    html += '</div>';

    // Quick actions
    html += `
        <div class="dimension-widget-actions">
            <button class="btn btn-sm btn-secondary" onclick="showPage('salesmarketing'); setTimeout(() => {
                document.getElementById('dimensionCompetitorSelect').value = '${data.competitor_id}';
                loadCompetitorDimensions();
            }, 100);">
                📊 View Full Scorecard
            </button>
            <button class="btn btn-sm btn-primary" onclick="showPage('salesmarketing'); setTimeout(() => {
                showSalesMarketingTab('battlecards');
                document.getElementById('battlecardCompetitorSelect').value = '${data.competitor_id}';
            }, 100);">
                ⚔️ Generate Dimension Battlecard
            </button>
        </div>
    `;

    container.innerHTML = html;
}

// ============== Export for Global Access ==============

window.initSalesMarketingModule = initSalesMarketingModule;
window.showSalesMarketingTab = showSalesMarketingTab;
window.loadCompetitorDimensions = loadCompetitorDimensions;
window.selectDimensionScore = selectDimensionScore;
window.saveDimensionScore = saveDimensionScore;
window.saveAllDimensions = saveAllDimensions;
window.aiSuggestDimensions = aiSuggestDimensions;
window.generateDynamicBattlecard = generateDynamicBattlecard;
window.exportBattlecardPDF = exportBattlecardPDF;
window.exportBattlecardMarkdown = exportBattlecardMarkdown;
window.loadDimensionComparison = loadDimensionComparison;
window.compareVsCertify = compareVsCertify;
window.loadTalkingPoints = loadTalkingPoints;
window.showAddTalkingPointModal = showAddTalkingPointModal;
window.saveTalkingPoint = saveTalkingPoint;
window.deleteTalkingPoint = deleteTalkingPoint;
window.initBattlecardDimensionWidget = initBattlecardDimensionWidget;
window.loadBattlecardDimensionWidget = loadBattlecardDimensionWidget;
