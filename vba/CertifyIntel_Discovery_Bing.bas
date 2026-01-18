Option Explicit

Public Sub DiscoverCompetitors()
    Dim ws As Worksheet: Set ws = ThisWorkbook.Worksheets(SH_CONFIG)
    Dim provider As String: provider = UCase$(Trim$(CStr(ws.Range("B2").Value)))
    Dim apiKey As String: apiKey = Trim$(CStr(ws.Range("B3").Value))
    Dim query As String: query = Trim$(CStr(ws.Range("B4").Value))
    If query = "" Then query = "Certify Health competitors middle market healthcare"

    If provider <> "BING" Then
        CreateReviewTask "", "discovery", "medium", "UNKNOWN_PROVIDER:" & provider, "", ""
        Exit Sub
    End If
    If apiKey = "" Then
        CreateReviewTask "", "discovery", "high", "MISSING_API_KEY", "", ""
        Exit Sub
    End If

    Dim url As String
    url = "https://api.bing.microsoft.com/v7.0/search?q=" & EncodeUrl(query) & "&count=10"

    Dim headers As Object: Set headers = CreateObject("Scripting.Dictionary")
    headers.Add "Ocp-Apim-Subscription-Key", apiKey

    Dim status As Long, raw As String
    raw = HttpGetJson(url, headers, 15000, status)
    If status <> 200 Or raw = "" Then
        CreateReviewTask "", "discovery", "high", "DISCOVERY_HTTP_" & CStr(status), "", url
        Exit Sub
    End If

    Dim parsed As Variant
    On Error GoTo PARSE_FAIL
    parsed = JsonParse(raw)
    On Error GoTo 0

    Dim webPages As Object
    Set webPages = parsed("webPages")
    Dim values As Object
    Set values = webPages("value")

    Dim entLo As ListObject: Set entLo = GetTable(SH_INPUT, T_ENTITIES)
    Dim i As Long
    For i = 0 To values.Count - 1
        Dim item As Object: Set item = values(i)
        Dim nm As String: nm = CStr(item("name"))
        Dim link As String: link = CStr(item("url"))
        Dim domain As String: domain = DomainFromUrl(link)
        If domain <> "" Then UpsertEntity entLo, nm, domain
    Next i
    Exit Sub

PARSE_FAIL:
    CreateReviewTask "", "discovery", "high", "JSON_PARSE_FAILED", "", url
End Sub

Private Sub UpsertEntity(ByVal entLo As ListObject, ByVal canonicalName As String, ByVal domain As String)
    Dim r As ListRow
    For Each r In entLo.ListRows
        If LCase$(CStr(r.Range(1, ColIndex(entLo, "domain")).Value)) = LCase$(domain) Then
            r.Range(1, ColIndex(entLo, "canonical_name")).Value = canonicalName
            Exit Sub
        End If
    Next r

    Dim lr As ListRow: AppendRow entLo, lr
    lr.Range(1, ColIndex(entLo, "entity_id")).Value = NewId("ENT")
    lr.Range(1, ColIndex(entLo, "canonical_name")).Value = canonicalName
    lr.Range(1, ColIndex(entLo, "domain")).Value = domain
    lr.Range(1, ColIndex(entLo, "vertical")).Value = "UNKNOWN"
    lr.Range(1, ColIndex(entLo, "region")).Value = "UNKNOWN"
    lr.Range(1, ColIndex(entLo, "segment_id")).Value = "SEG_MM"
    lr.Range(1, ColIndex(entLo, "discovered_via")).Value = "BING_SEARCH"
    lr.Range(1, ColIndex(entLo, "discovered_at")).Value = NowUtcIso()
    lr.Range(1, ColIndex(entLo, "status")).Value = "ACTIVE"
End Sub

Private Function EncodeUrl(ByVal s As String) As String
    Dim i As Long, ch As String, out As String
    For i = 1 To Len(s)
        ch = Mid$(s, i, 1)
        Select Case Asc(ch)
            Case 48 To 57, 65 To 90, 97 To 122
                out = out & ch
            Case 32
                out = out & "+"
            Case Else
                out = out & "%" & Right$("0" & Hex(Asc(ch)), 2)
        End Select
    Next i
    EncodeUrl = out
End Function
