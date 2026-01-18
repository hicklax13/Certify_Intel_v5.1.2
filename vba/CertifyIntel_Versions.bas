Option Explicit

Public Sub PromoteToClaimVersions()
    Dim candLo As ListObject: Set candLo = GetTable(SH_INPUT, T_CANDS)
    Dim versLo As ListObject: Set versLo = GetTable(SH_VERSIONS, T_VERS)

    Dim r As ListRow
    For Each r In candLo.ListRows
        If UCase$(CStr(r.Range(1, ColIndex(candLo, "status_final")).Value)) <> "PROMOTED" Then GoTo NextR
        Dim evidId As String: evidId = CStr(r.Range(1, ColIndex(candLo, "evidence_id")).Value)
        If evidId = "" Then GoTo NextR

        Dim vText As String: vText = CStr(r.Range(1, ColIndex(candLo, "value_text")).Value)
        If UCase$(vText) = "UNKNOWN" Then GoTo NextR

        Dim lr As ListRow: AppendRow versLo, lr
        lr.Range(1, ColIndex(versLo, "version_id")).Value = NewId("VER")
        lr.Range(1, ColIndex(versLo, "claim_id")).Value = NewId("CLM")
        lr.Range(1, ColIndex(versLo, "entity_id")).Value = CStr(r.Range(1, ColIndex(candLo, "entity_id")).Value)
        lr.Range(1, ColIndex(versLo, "field_key")).Value = CStr(r.Range(1, ColIndex(candLo, "field_key")).Value)
        lr.Range(1, ColIndex(versLo, "value_type")).Value = "mixed"
        lr.Range(1, ColIndex(versLo, "value_num")).Value = r.Range(1, ColIndex(candLo, "value_num")).Value
        lr.Range(1, ColIndex(versLo, "value_text")).Value = vText
        lr.Range(1, ColIndex(versLo, "confidence")).Value = r.Range(1, ColIndex(candLo, "confidence")).Value
        lr.Range(1, ColIndex(versLo, "tier")).Value = r.Range(1, ColIndex(candLo, "tier")).Value
        lr.Range(1, ColIndex(versLo, "evidence_id")).Value = evidId
        lr.Range(1, ColIndex(versLo, "created_at_utc")).Value = NowUtcIso()
        lr.Range(1, ColIndex(versLo, "created_by")).Value = "pipeline"
        lr.Range(1, ColIndex(versLo, "reason")).Value = "auto_promotion"
        lr.Range(1, ColIndex(versLo, "status")).Value = "active"
NextR:
    Next r
End Sub
