param(
  [string]$WorkspacePath = "C:\Users\conno\Downloads\Certify_Health_Intelv1",
  [string]$WorkbookXlsx  = "$(Join-Path $WorkspacePath 'Certify_Intel_ExcelOnly_v3_1_dashboard_ops_ready.xlsx')",
  [string]$OutXlsm       = "$(Join-Path $WorkspacePath 'Certify_Intel_ExcelOnly_v3_1_dashboard_ops_ready.xlsm')"
)

function Fail($msg){
  Write-Host ""
  Write-Host "ERROR: $msg" -ForegroundColor Red
  Write-Host ""
  exit 1
}

if (!(Test-Path $WorkspacePath)) { Fail "Workspace folder not found: $WorkspacePath" }
if (!(Test-Path $WorkbookXlsx))  { Fail "Workbook not found: $WorkbookXlsx" }

$basFiles = Get-ChildItem -Path $PSScriptRoot -Filter "*.bas" | Sort-Object Name
if ($basFiles.Count -eq 0) { Fail "No .bas modules found in: $PSScriptRoot" }

$xlOpenXMLWorkbookMacroEnabled = 52

$excel = $null
$wb = $null

try {
  $excel = New-Object -ComObject Excel.Application
  $excel.Visible = $false
  $excel.DisplayAlerts = $false

  $wb = $excel.Workbooks.Open($WorkbookXlsx)
  $wb.SaveAs($OutXlsm, $xlOpenXMLWorkbookMacroEnabled)

  try { $null = $excel.VBE } catch {
    Fail "Excel blocked programmatic VBA access. Enable: File -> Options -> Trust Center -> Trust Center Settings -> Macro Settings -> 'Trust access to the VBA project object model'. Then re-run."
  }

  foreach ($f in $basFiles) {
    $wb.VBProject.VBComponents.Import($f.FullName) | Out-Null
  }

  try { $excel.Run("SetupUI") } catch { try { $excel.Run("$($wb.Name)!SetupUI") } catch { Fail "SetupUI macro failed. Run SetupUI manually in VBA editor." } }

  $wb.Save()
  $wb.Close($true)
  $excel.Quit()

  Write-Host ""
  Write-Host "DONE: Created macro-enabled workbook:" -ForegroundColor Green
  Write-Host "  $OutXlsm"
  Write-Host ""
} finally {
  if ($wb -ne $null) { try { $wb.Close($false) } catch {} }
  if ($excel -ne $null) { try { $excel.Quit() } catch {} }
}
