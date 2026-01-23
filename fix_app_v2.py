
import os

path = r"c:\Users\conno\Downloads\Certify_Health_Intelv1\Project_Intel\frontend\app.js"

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_content = ""
skip_to = -1

for i, line in enumerate(lines):
    if i < skip_to:
        continue
    
    # 1. Simplify the first createSourcedValue to just a redirect or remove it
    if "function createSourcedValue(value, source, identifier =" in line:
        # We'll just comment it out to avoid confusion
        new_content += "// Deprecated version removed in favor of unified version at L2800+\n"
        # Find end of function
        for j in range(i, i + 20):
            if "}" in lines[j] and len(lines[j].strip()) == 1:
                skip_to = j + 1
                break
        continue

    # 2. Update the calls in renderCompetitorsGrid
    if "createSourcedValue(comp.customer_count, 'website', comp.website, 'customers', comp.id, 'customer_count')" in line:
        line = line.replace(
            "createSourcedValue(comp.customer_count, 'website', comp.website, 'customers', comp.id, 'customer_count')",
            "createSourcedValue(comp.customer_count, comp.id, 'customer_count')"
        )
    if "createSourcedValue(comp.base_price, 'website', comp.website, 'pricing', comp.id, 'base_price')" in line:
        line = line.replace(
            "createSourcedValue(comp.base_price, 'website', comp.website, 'pricing', comp.id, 'base_price')",
            "createSourcedValue(comp.base_price, comp.id, 'base_price')"
        )
    if "createSourcedValue(comp.employee_count, 'linkedin', comp.name, '', comp.id, 'employee_count')" in line:
        line = line.replace(
            "createSourcedValue(comp.employee_count, 'linkedin', comp.name, '', comp.id, 'employee_count')",
            "createSourcedValue(comp.employee_count, comp.id, 'employee_count')"
        )
    if "createSourcedValue(comp.g2_rating ? comp.g2_rating + ' ⭐' : null, 'google', comp.name + ' G2 rating', '', comp.id, 'g2_rating')" in line:
        line = line.replace(
            "createSourcedValue(comp.g2_rating ? comp.g2_rating + ' ⭐' : null, 'google', comp.name + ' G2 rating', '', comp.id, 'g2_rating')",
            "createSourcedValue(comp.g2_rating ? comp.g2_rating + ' ⭐' : null, comp.id, 'g2_rating')"
        )
    
    # 3. Update the second createSourcedValue to include the edit icon
    if "function createSourcedValue(value, competitorId, fieldName, fallbackType =" in line:
        # We rewrite the whole function
        new_content += """function createSourcedValue(value, competitorId, fieldName, fallbackType = 'unknown') {
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

    // New Correction Icon logic
    const cleanValue = String(value).replace(/['"]/g, '').substring(0, 50);
    const editIcon = `<span class="edit-icon" onclick="openCorrectionModal(${competitorId}, '${fieldName}', '${cleanValue}')" style="cursor:pointer;margin-left:6px;font-size:10px;opacity:0.5;" title="Correct this data">✏️</span>`;

    return `
        <span class="sourced-value" data-competitor="${competitorId}" data-field="${fieldName}">
            ${value}
            <span class="source-icon ${sourceType}" ${clickHandler} title="Click for source">
                ${iconHtml}
            </span>
            ${tooltipHtml}
            ${editIcon}
        </span>
    `;
}
"""
        # Skip original function lines
        bracket_count = 0
        in_func = False
        for k in range(i, i + 100):
            if "{" in lines[k]:
                bracket_count += lines[k].count("{")
                in_func = True
            if "}" in lines[k]:
                bracket_count -= lines[k].count("}")
            if in_func and bracket_count == 0:
                skip_to = k + 1
                break
        continue

    new_content += line

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully fixed app.js duplicates and signatures")
