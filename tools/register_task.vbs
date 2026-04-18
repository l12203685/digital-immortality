Dim schService, xmlFile, taskName
Set schService = CreateObject("Schedule.Service")
Call schService.Connect()

xmlFile = "C:\Users\admin\workspace\digital-immortality\tools\stale_detector_scheduler.xml"
taskName = "Edward_StaleMemory_Check"

' Read XML file
Dim fso, xmlContent
Set fso = CreateObject("Scripting.FileSystemObject")
xmlContent = fso.OpenTextFile(xmlFile).ReadAll()

' Register task
Dim folder, registeredTask
Set folder = schService.GetFolder("\")

On Error Resume Next
' Try to delete existing task
folder.DeleteTask taskName, 0
On Error Goto 0

Set registeredTask = folder.RegisterTask(taskName, xmlContent, 6, Null, Null, 0)

If Err.Number = 0 Then
    WScript.Echo "Success: Task '" & taskName & "' registered"
    WScript.Quit 0
Else
    WScript.Echo "Error: " & Err.Description
    WScript.Quit 1
End If
