Option Explicit

Public Sub CreateReviewTask(ByVal entityId As String, ByVal fieldKey As String, ByVal severity As String, ByVal reason As String, ByVal evidenceId As String, ByVal url As String)
    Dim lo As ListObject: Set lo = GetTable(SH_REVIEW, T_REV)
    Dim lr As ListRow: AppendRow lo, lr
    lr.Range(1, ColIndex(lo, "task_id")).Value = NewId("TASK")
    lr.Range(1, ColIndex(lo, "created_at")).Value = NowUtcIso()
    lr.Range(1, ColIndex(lo, "entity_id")).Value = entityId
    lr.Range(1, ColIndex(lo, "field_key")).Value = fieldKey
    lr.Range(1, ColIndex(lo, "severity")).Value = severity
    lr.Range(1, ColIndex(lo, "reason")).Value = reason
    lr.Range(1, ColIndex(lo, "evidence_id")).Value = evidenceId
    lr.Range(1, ColIndex(lo, "url")).Value = url
    lr.Range(1, ColIndex(lo, "status")).Value = "OPEN"
End Sub
