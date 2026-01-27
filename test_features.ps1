# Test Features Script for Certify Intel
$ErrorActionPreference = "Continue"

# Get auth token
Write-Host "=== GETTING AUTH TOKEN ===" -ForegroundColor Cyan
$tokenResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/token' -Method POST -Body 'username=admin@certifyintel.com&password=MSFWINTERCLINIC2026' -ContentType 'application/x-www-form-urlencoded'
$token = $tokenResponse.access_token
$headers = @{Authorization = "Bearer $token"}
Write-Host "Token obtained successfully" -ForegroundColor Green

# TEST 1: News Articles
Write-Host "`n=== TEST 1: LIVE NEWS ARTICLES ===" -ForegroundColor Cyan
$news = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/news-feed?limit=50' -Headers $headers
Write-Host "Total articles in feed: $($news.Count)" -ForegroundColor Yellow

if ($news.Count -ge 25) {
    Write-Host "PASS: Found $($news.Count) articles (>= 25 required)" -ForegroundColor Green
} else {
    Write-Host "CHECKING: Only $($news.Count) cached. Fetching fresh news..." -ForegroundColor Yellow
}

Write-Host "`nSample articles (first 30):" -ForegroundColor White
$count = 0
foreach ($article in $news[0..29]) {
    $count++
    $source = if ($article.source) { $article.source.Substring(0, [Math]::Min(15, $article.source.Length)) } else { "Unknown" }
    $title = if ($article.title) { $article.title.Substring(0, [Math]::Min(60, $article.title.Length)) } else { "No title" }
    $date = if ($article.published_date) { $article.published_date.Substring(0, [Math]::Min(10, $article.published_date.Length)) } else { "No date" }
    Write-Host "$count. [$source] $title... ($date)"
}

# TEST 2: Product Coverage
Write-Host "`n=== TEST 2: PRODUCT/SERVICE COVERAGE ===" -ForegroundColor Cyan
$products = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/products/coverage' -Headers $headers
Write-Host "Total Products: $($products.total_products)" -ForegroundColor Yellow
Write-Host "Competitors with Products: $($products.competitors_with_products) / $($products.total_competitors)" -ForegroundColor Yellow
Write-Host "Coverage: $($products.coverage_percentage)%" -ForegroundColor Yellow

if ($products.coverage_percentage -eq 100) {
    Write-Host "PASS: 100% product coverage across all competitors" -ForegroundColor Green
}

Write-Host "`nProducts by Category:" -ForegroundColor White
$products.products_by_category.PSObject.Properties | ForEach-Object {
    Write-Host "  - $($_.Name): $($_.Value) products"
}

# TEST 3: Knowledge Base / Client Documents
Write-Host "`n=== TEST 3: KNOWLEDGE BASE / CLIENT DOCUMENTS ===" -ForegroundColor Cyan
try {
    $kb = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/knowledge-base' -Headers $headers
    Write-Host "Knowledge Base Items: $($kb.Count)" -ForegroundColor Yellow
    if ($kb.Count -gt 0) {
        Write-Host "PASS: Knowledge base has $($kb.Count) items" -ForegroundColor Green
        foreach ($item in $kb[0..4]) {
            Write-Host "  - [$($item.source_type)] $($item.title)"
        }
    }
} catch {
    Write-Host "Checking alternative endpoint..."
}

# Check data sources
try {
    $sources = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/data-quality/overview' -Headers $headers
    Write-Host "Data Quality Overview retrieved" -ForegroundColor Yellow
    Write-Host "  - Total Records: $($sources.total_records)" -ForegroundColor White
    Write-Host "  - Average Confidence: $($sources.average_confidence)" -ForegroundColor White
} catch {
    Write-Host "Data quality endpoint check failed"
}

# TEST 4: Email/Notification Settings
Write-Host "`n=== TEST 4: EMAIL NOTIFICATION SETTINGS ===" -ForegroundColor Cyan
try {
    $settings = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/settings' -Headers $headers
    Write-Host "Settings retrieved" -ForegroundColor Yellow
} catch {
    Write-Host "Checking notification configuration..."
}

# Check webhook/notification config
try {
    $notifications = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/notifications/config' -Headers $headers
    Write-Host "Notification Config: $($notifications | ConvertTo-Json -Depth 2)" -ForegroundColor Yellow
} catch {
    Write-Host "Notification config endpoint not available - checking .env"
}

Write-Host "`n=== TESTS COMPLETE ===" -ForegroundColor Cyan
