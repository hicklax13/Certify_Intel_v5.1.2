Option Explicit

Public Function DomainFromUrl(ByVal url As String) As String
    Dim re As Object, m As Object
    Set re = CreateObject("VBScript.RegExp")
    re.Pattern = "^(?:https?://)?([^/]+)"
    re.IgnoreCase = True
    If re.Test(url) Then
        Set m = re.Execute(url)(0)
        DomainFromUrl = LCase$(m.SubMatches(0))
    Else
        DomainFromUrl = ""
    End If
End Function

Public Function SourceAllowlisted(ByVal sourceKey As String, ByVal domain As String, ByRef reason As String) As Boolean
    Dim lo As ListObject: Set lo = ThisWorkbook.Worksheets("Sources_Allowlist").ListObjects(T_SRC)
    Dim r As ListRow
    For Each r In lo.ListRows
        If CStr(r.Range(1, lo.ListColumns("source_key").Index).Value) = sourceKey Then
            If UCase$(CStr(r.Range(1, lo.ListColumns("enabled").Index).Value)) <> "TRUE" Then
                reason = "SOURCE_DISABLED": SourceAllowlisted = False: Exit Function
            End If
            Dim aDomain As String: aDomain = LCase$(CStr(r.Range(1, lo.ListColumns("domain").Index).Value))
            If aDomain <> "" And domain <> aDomain Then
                reason = "DOMAIN_NOT_ALLOWED": SourceAllowlisted = False: Exit Function
            End If
            reason = "OK"
            SourceAllowlisted = True
            Exit Function
        End If
    Next r
    reason = "SOURCE_NOT_FOUND"
    SourceAllowlisted = False
End Function
