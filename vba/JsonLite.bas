Option Explicit
'==============================
' JsonLite - Minimal JSON Parser
'==============================

Public Function JsonParse(ByVal json As String) As Variant
    Dim p As Long: p = 1
    SkipWs json, p
    JsonParse = ParseValue(json, p)
End Function

Private Sub SkipWs(ByVal s As String, ByRef p As Long)
    Do While p <= Len(s)
        Dim ch As String: ch = Mid$(s, p, 1)
        If ch = " " Or ch = vbTab Or ch = vbCr Or ch = vbLf Then
            p = p + 1
        Else
            Exit Do
        End If
    Loop
End Sub

Private Function ParseValue(ByVal s As String, ByRef p As Long) As Variant
    SkipWs s, p
    If p > Len(s) Then Err.Raise 5, , "Unexpected end"
    Dim ch As String: ch = Mid$(s, p, 1)

    If ch = "{" Then
        Set ParseValue = ParseObject(s, p)
    ElseIf ch = "[" Then
        Set ParseValue = ParseArray(s, p)
    ElseIf ch = """" Then
        ParseValue = ParseString(s, p)
    ElseIf ch = "t" Or ch = "f" Then
        ParseValue = ParseBool(s, p)
    ElseIf ch = "n" Then
        ParseValue = ParseNull(s, p)
    Else
        ParseValue = ParseNumber(s, p)
    End If
End Function

Private Function ParseObject(ByVal s As String, ByRef p As Long) As Object
    Dim dict As Object: Set dict = CreateObject("Scripting.Dictionary")
    p = p + 1
    SkipWs s, p
    If Mid$(s, p, 1) = "}" Then p = p + 1: Set ParseObject = dict: Exit Function

    Do
        SkipWs s, p
        Dim key As String: key = ParseString(s, p)
        SkipWs s, p
        If Mid$(s, p, 1) <> ":" Then Err.Raise 5, , "Expected :"
        p = p + 1
        Dim val As Variant: val = ParseValue(s, p)
        dict.Add key, val
        SkipWs s, p
        Dim ch As String: ch = Mid$(s, p, 1)
        If ch = "}" Then p = p + 1: Exit Do
        If ch <> "," Then Err.Raise 5, , "Expected ,"
        p = p + 1
    Loop
    Set ParseObject = dict
End Function

Private Function ParseArray(ByVal s As String, ByRef p As Long) As Object
    Dim col As Object: Set col = CreateObject("System.Collections.ArrayList")
    p = p + 1
    SkipWs s, p
    If Mid$(s, p, 1) = "]" Then p = p + 1: Set ParseArray = col: Exit Function
    Do
        col.Add ParseValue(s, p)
        SkipWs s, p
        Dim ch As String: ch = Mid$(s, p, 1)
        If ch = "]" Then p = p + 1: Exit Do
        If ch <> "," Then Err.Raise 5, , "Expected ,"
        p = p + 1
    Loop
    Set ParseArray = col
End Function

Private Function ParseString(ByVal s As String, ByRef p As Long) As String
    If Mid$(s, p, 1) <> """" Then Err.Raise 5, , "Expected string"
    p = p + 1
    Dim out As String: out = ""
    Do While p <= Len(s)
        Dim ch As String: ch = Mid$(s, p, 1)
        If ch = """" Then p = p + 1: Exit Do
        If ch = "" Then
            p = p + 1
            ch = Mid$(s, p, 1)
            Select Case ch
                Case """" : out = out & """"
                Case ""  : out = out & ""
                Case "/"  : out = out & "/"
                Case "n"  : out = out & vbLf
                Case "r"  : out = out & vbCr
                Case "t"  : out = out & vbTab
                Case Else : out = out & ch
            End Select
        Else
            out = out & ch
        End If
        p = p + 1
    Loop
    ParseString = out
End Function

Private Function ParseBool(ByVal s As String, ByRef p As Long) As Boolean
    If Mid$(s, p, 4) = "true" Then p = p + 4: ParseBool = True: Exit Function
    If Mid$(s, p, 5) = "false" Then p = p + 5: ParseBool = False: Exit Function
    Err.Raise 5, , "Invalid bool"
End Function

Private Function ParseNull(ByVal s As String, ByRef p As Long) As Variant
    If Mid$(s, p, 4) = "null" Then p = p + 4: ParseNull = Null: Exit Function
    Err.Raise 5, , "Invalid null"
End Function

Private Function ParseNumber(ByVal s As String, ByRef p As Long) As Double
    Dim start As Long: start = p
    Do While p <= Len(s)
        Dim ch As String: ch = Mid$(s, p, 1)
        If InStr("0123456789+-.eE", ch) = 0 Then Exit Do
        p = p + 1
    Loop
    ParseNumber = CDbl(Mid$(s, start, p - start))
End Function
