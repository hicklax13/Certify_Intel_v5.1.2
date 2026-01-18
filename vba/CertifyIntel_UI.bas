Option Explicit

Public Sub SetupUI()
    Dim ws As Worksheet: Set ws = ThisWorkbook.Worksheets(SH_DASH)
    On Error Resume Next
    ws.Shapes("btnRunPipeline").Delete
    ws.Shapes("btnRunTests").Delete
    On Error GoTo 0

    Dim shp As Shape
    Set shp = ws.Shapes.AddShape(msoShapeRoundedRectangle, 30, 28, 140, 32)
    shp.Name = "btnRunPipeline"
    shp.TextFrame2.TextRange.Text = "Run Pipeline"
    shp.OnAction = "RunPipeline"

    Set shp = ws.Shapes.AddShape(msoShapeRoundedRectangle, 180, 28, 160, 32)
    shp.Name = "btnRunTests"
    shp.TextFrame2.TextRange.Text = "Run Self Tests"
    shp.OnAction = "RunSelfTests"
End Sub
