<# ========================================================================
Certify Intel — Release Build Script
Creates:
  1) Macro-enabled workbook (.xlsm) from a template (.xlsx) + VBA modules
  2) Client delivery ZIP (xlsm + installer + bas + docs + instructions)
  3) BUILD_REPORT.txt with hashes and verification notes

FAIL-CLOSED: any missing pre-reqs -> exit 1
Never commits artifacts; outputs only to OutDir.

USAGE EXAMPLE:
  powershell -NoProfile -ExecutionPolicy Bypass `
    -File .\scripts\Release_Build.ps1 `
    -RepoRoot "C:\Users\conno\Downloads\Certify_Health_Intelv1\Project_Tzu" `
    -TemplateXlsx "C:\Users\conno\Downloads\Certify_Health_Intelv1\Certify_Intel_ExcelOnly_v3_1_dashboard_ops_ready.xlsx"

======================================================================== #>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$RepoRoot,

  [Parameter(Mandatory=$true)]
  [string]$TemplateXlsx,

  [Parameter(Mandatory=$false)]
  [string]$WorkspacePath = "C:\Users\conno\Downloads\Certify_Health_Intelv1",

  [Parameter(Mandatory=$false)]
  [string]$OutDir = "",

  [Parameter(Mandatory=$false)]
  [string]$VersionTag = ""
)

# -----------------------------
# Helpers
# -----------------------------
function Fail([string]$msg) {
  Write-Host ""
  Write-Host ("ERROR: " + $msg) -ForegroundColor Red
  Write-Host ""
  exit 1
}

function EnsureDir([string]$p) {
  if (!(Test-Path $p)) { New-Item -ItemType Directory -Path $p | Out-Null }
}

function Sha256([string]$path) {
  if (!(Test-Path $path)) { return "" }
  return (Get-FileHash -Algorithm SHA256 -Path $path).Hash
}

# -----------------------------
# Normalize / defaults
# -----------------------------
if ([string]::IsNullOrWhiteSpace($VersionTag)) {
  $VersionTag = "v" + (Get-Date -Format "yyyyMMdd_HHmm")
}

if ([string]::IsNullOrWhiteSpace($OutDir)) {
  $OutDir = Join-Path $WorkspacePath "release_out"
}

$RepoRoot = (Resolve-Path $RepoRoot).Path
$TemplateXlsx = (Resolve-Path $TemplateXlsx).Path
# PowerShell 5.1-safe Resolve-Path
$resolvedOutDir = $null
if (-not [string]::IsNullOrWhiteSpace($OutDir)) {
  try { $resolvedOutDir = (Resolve-Path -LiteralPath $OutDir -ErrorAction Stop).Path } catch { $resolvedOutDir = $null }
}
if (-not [string]::IsNullOrWhiteSpace($resolvedOutDir)) {
  $OutDir = $resolvedOutDir
}

if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $WorkspacePath "release_out" }

# -----------------------------
# Validate inputs
# -----------------------------
if (!(Test-Path $WorkspacePath)) { Fail "WorkspacePath not found: $WorkspacePath" }
if (!(Test-Path $RepoRoot))      { Fail "RepoRoot not found: $RepoRoot" }
if (!(Test-Path $TemplateXlsx))  { Fail "TemplateXlsx not found: $TemplateXlsx" }

$vbaDir     = Join-Path $RepoRoot "vba"
$scriptsDir = Join-Path $RepoRoot "scripts"
$docsDir    = Join-Path $RepoRoot "docs"

if (!(Test-Path $vbaDir))        { Fail "Missing vba folder: $vbaDir" }
if (!(Test-Path $scriptsDir))    { Fail "Missing scripts folder: $scriptsDir" }

$basFiles = Get-ChildItem -Path $vbaDir -Filter "*.bas" -File | Sort-Object Name
if ($basFiles.Count -eq 0) { Fail "No .bas files found in: $vbaDir" }

$installPs1 = Join-Path $scriptsDir "Install_CertifyIntel.ps1"
$installBat = Join-Path $scriptsDir "Install_CertifyIntel.bat"
if (!(Test-Path $installPs1)) { Fail "Missing installer: $installPs1" }
if (!(Test-Path $installBat)) { Fail "Missing installer: $installBat" }

# Install instructions file: prefer docs/Install_Instructions.docx if present
$installDocx = Join-Path $docsDir "Install_Instructions.docx"
if (!(Test-Path $installDocx)) {
  # Allow a fallback in workspace (if you keep it there)
  $fallback = Join-Path $WorkspacePath "Install_Instructions.docx"
  if (Test-Path $fallback) { $installDocx = $fallback } else { Fail "Install_Instructions.docx not found in docs/ or workspace." }
}

# -----------------------------
# Prepare output paths
# -----------------------------
EnsureDir $OutDir

$releaseDir = Join-Path $OutDir $VersionTag
EnsureDir $releaseDir

$xlsmOut = Join-Path $releaseDir ("Certify_Intel_" + $VersionTag + ".xlsm")
$zipOut  = Join-Path $releaseDir ("Certify_Intel_" + $VersionTag + "_PACKAGE.zip")
$report  = Join-Path $releaseDir "BUILD_REPORT.txt"

# -----------------------------
# Build .xlsm via Excel COM
# -----------------------------
$xlOpenXMLWorkbookMacroEnabled = 52
$excel = $null
$wb = $null

try {
  Write-Host "== Release Build: Starting Excel automation =="
  $excel = New-Object -ComObject Excel.Application
  $excel.Visible = $false
  $excel.DisplayAlerts = $false

  $wb = $excel.Workbooks.Open($TemplateXlsx)

  # SaveAs .xlsm
  $wb.SaveAs($xlsmOut, $xlOpenXMLWorkbookMacroEnabled)

  # Ensure programmatic VBA access is allowed
  try { $null = $excel.VBE } catch {
    Fail "Excel blocked programmatic VBA access. Enable: Excel -> File -> Options -> Trust Center -> Trust Center Settings -> Macro Settings -> 'Trust access to the VBA project object model'. Then rerun."
  }

  # Import all .bas
  foreach ($f in $basFiles) {
    $wb.VBProject.VBComponents.Import($f.FullName) | Out-Null
  }

  # Run SetupUI (must exist in imported modules)
  try {
    $excel.Run("SetupUI")
  } catch {
    try { $excel.Run("$($wb.Name)!SetupUI") } catch { Fail "SetupUI macro failed or not found. Ensure SetupUI exists and runs without errors." }
  }

  $wb.Save()
  $wb.Close($true)
  $excel.Quit()

  Write-Host "== Release Build: Excel workbook created =="
  Write-Host "  $xlsmOut"
}
finally {
  if ($wb -ne $null)    { try { $wb.Close($false) } catch {} }
  if ($excel -ne $null) { try { $excel.Quit() } catch {} }
}

if (!(Test-Path $xlsmOut)) { Fail "Workbook output was not created: $xlsmOut" }

# -----------------------------
# Package ZIP
# -----------------------------
Write-Host "== Release Build: Creating ZIP package =="

$tempPkg = Join-Path $releaseDir "PACKAGE_CONTENTS"
EnsureDir $tempPkg

# Copy required artifacts into package staging
Copy-Item -Path $xlsmOut -Destination (Join-Path $tempPkg (Split-Path $xlsmOut -Leaf)) -Force
Copy-Item -Path $installPs1 -Destination (Join-Path $tempPkg "Install_CertifyIntel.ps1") -Force
Copy-Item -Path $installBat -Destination (Join-Path $tempPkg "Install_CertifyIntel.bat") -Force
Copy-Item -Path $installDocx -Destination (Join-Path $tempPkg "Install_Instructions.docx") -Force

# Include VBA modules
$pkgVbaDir = Join-Path $tempPkg "vba"
EnsureDir $pkgVbaDir
foreach ($f in $basFiles) {
  Copy-Item -Path $f.FullName -Destination (Join-Path $pkgVbaDir $f.Name) -Force
}

# Include docs snapshot (optional but recommended)
if (Test-Path $docsDir) {
  $pkgDocsDir = Join-Path $tempPkg "docs"
  EnsureDir $pkgDocsDir
  Get-ChildItem -Path $docsDir -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $pkgDocsDir $_.Name) -Force
  }
}

# Include assets (optional)
$assetsDir = Join-Path $RepoRoot "assets"
if (Test-Path $assetsDir) {
  $pkgAssetsDir = Join-Path $tempPkg "assets"
  EnsureDir $pkgAssetsDir
  Get-ChildItem -Path $assetsDir -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $pkgAssetsDir $_.Name) -Force
  }
}

# Create zip
if (Test-Path $zipOut) { Remove-Item -Force $zipOut }
Compress-Archive -Path (Join-Path $tempPkg "*") -DestinationPath $zipOut -Force

if (!(Test-Path $zipOut)) { Fail "ZIP output was not created: $zipOut" }

# -----------------------------
# Build report
# -----------------------------
$xlsmHash = Sha256 $xlsmOut
$zipHash  = Sha256 $zipOut

$lines = @()
$lines += "Certify Intel Release Build Report"
$lines += "VersionTag: $VersionTag"
$lines += "RepoRoot: $RepoRoot"
$lines += "TemplateXlsx: $TemplateXlsx"
$lines += "WorkspacePath: $WorkspacePath"
$lines += "ReleaseDir: $releaseDir"
$lines += ""
$lines += "Workbook:"
$lines += "  Path: $xlsmOut"
$lines += "  SHA256: $xlsmHash"
$lines += ""
$lines += "Package:"
$lines += "  Path: $zipOut"
$lines += "  SHA256: $zipHash"
$lines += ""
$lines += "Imported VBA modules:"
$lines += "  Count: $($basFiles.Count)"
$lines += "  Files:"
foreach ($f in $basFiles) { $lines += "    - $($f.Name)" }
$lines += ""
$lines += "Notes:"
$lines += "  - Artifacts are generated outside the repository."
$lines += "  - No secrets are embedded; API keys must be entered locally in the workbook Config sheet by the user."
$lines += "  - If Excel blocks VBA import, enable Trust Center setting: 'Trust access to the VBA project object model'."

Set-Content -Path $report -Value $lines -Encoding UTF8

Write-Host ""
Write-Host "== Release Build: COMPLETE ==" -ForegroundColor Green
Write-Host "Workbook: $xlsmOut"
Write-Host "ZIP:      $zipOut"
Write-Host "Report:   $report"
Write-Host ""
