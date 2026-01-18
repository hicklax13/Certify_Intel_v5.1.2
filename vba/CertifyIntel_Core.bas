Option Explicit

Public Const SH_CONFIG As String = "Config"
Public Const SH_INPUT As String = "Input"
Public Const SH_REVIEW As String = "Review_Queue"
Public Const SH_VERSIONS As String = "Claim_Versions"
Public Const SH_SNAP As String = "Evidence_Snapshots"
Public Const SH_EVENTS As String = "Events"
Public Const SH_ALERTS As String = "Alerts"
Public Const SH_RUNLOG As String = "Run_Log"
Public Const SH_DASH As String = "Dashboard"

Public Const T_ENTITIES As String = "tblEntities"
Public Const T_EVID As String = "tblEvidence"
Public Const T_CANDS As String = "tblClaimCandidates"
Public Const T_REV As String = "tblReviewQueue"
Public Const T_VERS As String = "tblClaimVersions"
Public Const T_SNAP As String = "tblEvidenceSnapshots"
Public Const T_EVENTS As String = "tblEvents"
Public Const T_ALERTS As String = "tblAlerts"
Public Const T_RUNLOG As String = "tblRunLog"
Public Const T_SRC As String = "tblSourcesAllowlist"

Public Function NowUtcIso() As String
    NowUtcIso = Format$(Now, "yyyy-mm-dd\Thh:nn:ss") & "Z"
End Function

Public Function NewId(ByVal prefix As String) As String
    Randomize
    NewId = prefix & "_" & Replace(Replace(Replace(Format$(Now, "yyyymmdd_hhnnss"), ":", ""), "/", ""), " ", "") & "_" & CStr(Int(Rnd() * 1000000))
End Function

Public Function GetTable(ByVal sheetName As String, ByVal tableName As String) As ListObject
    Set GetTable = ThisWorkbook.Worksheets(sheetName).ListObjects(tableName)
End Function

Public Function ColIndex(lo As ListObject, ByVal colName As String) As Long
    ColIndex = lo.ListColumns(colName).Index
End Function

Public Sub AppendRow(lo As ListObject, ByRef newRow As ListRow)
    Set newRow = lo.ListRows.Add
End Sub
