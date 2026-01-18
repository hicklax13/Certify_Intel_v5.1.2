Option Explicit

Public Sub DiffSnapshotsToEvents()
    Dim snapLo As ListObject: Set snapLo = GetTable(SH_SNAP, T_SNAP)
    Dim evtLo As ListObject: Set evtLo = GetTable(SH_EVENTS, T_EVENTS)

    Dim dictLast As Object: Set dictLast = CreateObject("Scripting.Dictionary")
    Dim dictPrev As Object: Set dictPrev = CreateObject("Scripting.Dictionary")

    Dim r As ListRow
    For Each r In snapLo.ListRows
        Dim url As String: url = CStr(r.Range(1, ColIndex(snapLo, "url")).Value)
        Dim h As String: h = CStr(r.Range(1, ColIndex(snapLo, "text_hash")).Value)
        If url = "" Then GoTo NextR
        If Not dictLast.Exists(url) Then
            dictLast.Add url, h
        Else
            dictPrev(url) = dictLast(url)
            dictLast(url) = h
        End If
NextR:
    Next r

    Dim k As Variant
    For Each k In dictPrev.Keys
        If dictPrev(k) <> dictLast(k) Then
            Dim lr As ListRow: AppendRow evtLo, lr
            lr.Range(1, ColIndex(evtLo, "event_id")).Value = NewId("EVT")
            lr.Range(1, ColIndex(evtLo, "event_type")).Value = "EVIDENCE_CHANGED"
            lr.Range(1, ColIndex(evtLo, "severity")).Value = "medium"
            lr.Range(1, ColIndex(evtLo, "url")).Value = CStr(k)
            lr.Range(1, ColIndex(evtLo, "detected_at_utc")).Value = NowUtcIso()
            lr.Range(1, ColIndex(evtLo, "prev_text_hash")).Value = dictPrev(k)
            lr.Range(1, ColIndex(evtLo, "new_text_hash")).Value = dictLast(k)
            lr.Range(1, ColIndex(evtLo, "summary")).Value = "Evidence content changed"
            lr.Range(1, ColIndex(evtLo, "status")).Value = "OPEN"
        End If
    Next k
End Sub

Public Sub EvaluateAlerts()
    ' Minimal: placeholder. Alerts can be expanded with additional rule keys.
    Dim alLo As ListObject: Set alLo = GetTable(SH_ALERTS, T_ALERTS)
    Dim evtLo As ListObject: Set evtLo = GetTable(SH_EVENTS, T_EVENTS)
    Dim r As ListRow
    For Each r In alLo.ListRows
        If UCase$(CStr(r.Range(1, ColIndex(alLo, "enabled")).Value)) <> "TRUE" Then GoTo NextR
        If CStr(r.Range(1, ColIndex(alLo, "rule_key")).Value) = "EVIDENCE_CHANGED_ANY" Then
            If CountOpenEvidenceChanged(evtLo) > 0 Then r.Range(1, ColIndex(alLo, "last_fired_at_utc")).Value = NowUtcIso()
        End If
NextR:
    Next r
End Sub

Private Function CountOpenEvidenceChanged(ByVal evtLo As ListObject) As Long
    Dim n As Long
    Dim r As ListRow
    For Each r In evtLo.ListRows
        If UCase$(CStr(r.Range(1, ColIndex(evtLo, "event_type")).Value)) = "EVIDENCE_CHANGED" And UCase$(CStr(r.Range(1, ColIndex(evtLo, "status")).Value)) = "OPEN" Then
            n = n + 1
        End If
    Next r
    CountOpenEvidenceChanged = n
End Function
