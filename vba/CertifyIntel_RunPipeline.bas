Option Explicit

Public Sub RunPipeline()
    On Error GoTo EH
    LogRun "running", "Pipeline start"

    DiscoverCompetitors
    FetchEvidenceAndExtract
    PromoteToClaimVersions
    DiffSnapshotsToEvents
    EvaluateAlerts

    ThisWorkbook.RefreshAll
    LogRun "completed", "Pipeline completed"
    Exit Sub
EH:
    LogRun "failed", "ERROR: " & Err.Description
End Sub

Private Sub LogRun(ByVal status As String, ByVal notes As String)
    Dim lo As ListObject: Set lo = GetTable(SH_RUNLOG, T_RUNLOG)
    Dim lr As ListRow: AppendRow lo, lr
    lr.Range(1, ColIndex(lo, "run_id")).Value = NewId("RUN")
    lr.Range(1, ColIndex(lo, "started_at_utc")).Value = NowUtcIso()
    lr.Range(1, ColIndex(lo, "mode")).Value = "manual"
    lr.Range(1, ColIndex(lo, "status")).Value = status
    lr.Range(1, ColIndex(lo, "notes")).Value = notes
End Sub
