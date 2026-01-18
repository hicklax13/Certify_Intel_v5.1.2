Option Explicit

Public Sub FetchEvidenceAndExtract()
    Dim entLo As ListObject: Set entLo = GetTable(SH_INPUT, T_ENTITIES)
    Dim evidLo As ListObject: Set evidLo = GetTable(SH_INPUT, T_EVID)
    Dim candLo As ListObject: Set candLo = GetTable(SH_INPUT, T_CANDS)
    Dim snapLo As ListObject: Set snapLo = GetTable(SH_SNAP, T_SNAP)

    Dim timeoutMs As Long: timeoutMs = 15000

    Dim r As ListRow
    For Each r In entLo.ListRows
        Dim entityId As String: entityId = CStr(r.Range(1, ColIndex(entLo, "entity_id")).Value)
        Dim domain As String: domain = CStr(r.Range(1, ColIndex(entLo, "domain")).Value)
        If entityId = "" Or domain = "" Then GoTo NextEnt

        Dim url As String: url = "https://" & domain & "/"
        Dim sourceKey As String: sourceKey = "Company_Site"
        Dim reason As String
        If Not SourceAllowlisted(sourceKey, LCase$(domain), reason) Then
            CreateReviewTask entityId, "evidence", "high", "ALLOWLIST_FAIL:" & reason, "", url
            GoTo NextEnt
        End If

        Dim status As Long, txt As String
        txt = HttpGetText(url, timeoutMs, status)
        If status <> 200 Or txt = "" Then
            CreateReviewTask entityId, "evidence", "high", "FETCH_FAIL_HTTP_" & CStr(status), "", url
            GoTo NextEnt
        End If

        Dim evidId As String: evidId = NewId("EVID")
        AppendEvidence evidLo, evidId, entityId, sourceKey, "TIER1", url, Left$(txt, 500)
        AppendSnapshot snapLo, entityId, sourceKey, url, txt, status
        ExtractFromText candLo, entityId, "SEG_MM", url, "TIER1", evidId, txt

NextEnt:
    Next r
End Sub

Private Sub AppendEvidence(ByVal evidLo As ListObject, ByVal evidId As String, ByVal entityId As String, ByVal sourceKey As String, ByVal tier As String, ByVal url As String, ByVal snippet As String)
    Dim lr As ListRow: AppendRow evidLo, lr
    lr.Range(1, ColIndex(evidLo, "evidence_id")).Value = evidId
    lr.Range(1, ColIndex(evidLo, "entity_id")).Value = entityId
    lr.Range(1, ColIndex(evidLo, "source_key")).Value = sourceKey
    lr.Range(1, ColIndex(evidLo, "tier")).Value = tier
    lr.Range(1, ColIndex(evidLo, "url")).Value = url
    lr.Range(1, ColIndex(evidLo, "fetched_at")).Value = NowUtcIso()
    lr.Range(1, ColIndex(evidLo, "snippet")).Value = snippet
    lr.Range(1, ColIndex(evidLo, "content_hash")).Value = ""
    lr.Range(1, ColIndex(evidLo, "text_hash")).Value = Sha64(snippet)
    lr.Range(1, ColIndex(evidLo, "domain_calc")).Value = DomainFromUrl(url)
    lr.Range(1, ColIndex(evidLo, "allowlist_ok")).Value = "TRUE"
End Sub

Private Sub AppendSnapshot(ByVal snapLo As ListObject, ByVal entityId As String, ByVal sourceKey As String, ByVal url As String, ByVal txt As String, ByVal httpStatus As Long)
    Dim lr As ListRow: AppendRow snapLo, lr
    lr.Range(1, ColIndex(snapLo, "snapshot_id")).Value = NewId("SNAP")
    lr.Range(1, ColIndex(snapLo, "url")).Value = url
    lr.Range(1, ColIndex(snapLo, "domain")).Value = DomainFromUrl(url)
    lr.Range(1, ColIndex(snapLo, "source_key")).Value = sourceKey
    lr.Range(1, ColIndex(snapLo, "entity_id")).Value = entityId
    lr.Range(1, ColIndex(snapLo, "fetched_at_utc")).Value = NowUtcIso()
    lr.Range(1, ColIndex(snapLo, "http_status")).Value = httpStatus
    lr.Range(1, ColIndex(snapLo, "content_hash")).Value = ""
    lr.Range(1, ColIndex(snapLo, "text_hash")).Value = Sha64(txt)
    lr.Range(1, ColIndex(snapLo, "text_len")).Value = Len(txt)
    lr.Range(1, ColIndex(snapLo, "notes")).Value = "snapshot"
End Sub

Private Sub ExtractFromText(ByVal candLo As ListObject, ByVal entityId As String, ByVal segId As String, ByVal url As String, ByVal tier As String, ByVal evidId As String, ByVal txt As String)
    Dim re As Object, m As Object
    Set re = CreateObject("VBScript.RegExp")
    re.IgnoreCase = True
    re.Global = False

    re.Pattern = "\$([0-9][0-9,]*)\s*(?:per\s*year|/year|annual)"
    If re.Test(txt) Then
        Set m = re.Execute(txt)(0)
        WriteCandidate candLo, entityId, segId, "pricing_acv", "", CDbl(Replace(m.SubMatches(0), ",", "")), "USD", 0.75, evidId, m.FirstIndex, m.FirstIndex + m.Length, tier, "PROMOTABLE", "regex"
    Else
        WriteCandidate candLo, entityId, segId, "pricing_acv", "UNKNOWN", "", "USD", 0.2, evidId, "", "", tier, "REVIEW_REQUIRED", "no explicit ACV"
        CreateReviewTask entityId, "pricing_acv", "medium", "NO_EXPLICIT_ACV", evidId, url
    End If
End Sub

Private Sub WriteCandidate(ByVal candLo As ListObject, ByVal entityId As String, ByVal segId As String, ByVal fieldKey As String, ByVal vText As String, ByVal vNum As Variant, ByVal units As String, ByVal conf As Double, ByVal evidId As String, ByVal s0 As Variant, ByVal s1 As Variant, ByVal tier As String, ByVal statusAuto As String, ByVal reason As String)
    Dim lr As ListRow: AppendRow candLo, lr
    lr.Range(1, ColIndex(candLo, "candidate_id")).Value = NewId("CAND")
    lr.Range(1, ColIndex(candLo, "entity_id")).Value = entityId
    lr.Range(1, ColIndex(candLo, "segment_id")).Value = segId
    lr.Range(1, ColIndex(candLo, "field_key")).Value = fieldKey
    lr.Range(1, ColIndex(candLo, "value_text")).Value = vText
    If Not IsEmpty(vNum) And CStr(vNum) <> "" Then lr.Range(1, ColIndex(candLo, "value_num")).Value = vNum
    lr.Range(1, ColIndex(candLo, "units")).Value = units
    lr.Range(1, ColIndex(candLo, "confidence")).Value = conf
    lr.Range(1, ColIndex(candLo, "evidence_id")).Value = evidId
    lr.Range(1, ColIndex(candLo, "span_start")).Value = s0
    lr.Range(1, ColIndex(candLo, "span_end")).Value = s1
    lr.Range(1, ColIndex(candLo, "tier")).Value = tier
    lr.Range(1, ColIndex(candLo, "status_auto")).Value = statusAuto
    lr.Range(1, ColIndex(candLo, "auto_reason")).Value = reason
    lr.Range(1, ColIndex(candLo, "status_final")).Value = IIf(statusAuto = "PROMOTABLE" And conf >= 0.7, "PROMOTED", "REVIEW_REQUIRED")
End Sub

Public Function Sha64(ByVal s As String) As String
    Dim h As Double, i As Long, c As Integer
    h = 1469598103934666#
    For i = 1 To Len(s)
        c = Asc(Mid$(s, i, 1))
        h = (h Xor c) * 1099511628211#
    Next i
    Sha64 = "fnv64:" & CStr(h)
End Function
