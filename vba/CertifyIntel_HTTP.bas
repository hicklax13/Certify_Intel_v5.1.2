Option Explicit

Public Function HttpGetJson(ByVal url As String, ByVal headers As Object, ByVal timeoutMs As Long, ByRef httpStatus As Long) As String
    On Error GoTo EH
    Dim http As Object
    Set http = CreateObject("WinHTTP.WinHTTPRequest.5.1")
    http.Option(6) = True
    http.Open "GET", url, False
    http.SetTimeouts timeoutMs, timeoutMs, timeoutMs, timeoutMs
    Dim k As Variant
    If Not headers Is Nothing Then
        For Each k In headers.Keys
            http.SetRequestHeader CStr(k), CStr(headers(k))
        Next k
    End If
    http.Send
    httpStatus = CLng(http.Status)
    HttpGetJson = CStr(http.ResponseText)
    Exit Function
EH:
    httpStatus = 0
    HttpGetJson = ""
End Function

Public Function HttpGetText(ByVal url As String, ByVal timeoutMs As Long, ByRef httpStatus As Long) As String
    Dim headers As Object: Set headers = CreateObject("Scripting.Dictionary")
    HttpGetText = HttpGetJson(url, headers, timeoutMs, httpStatus)
End Function
