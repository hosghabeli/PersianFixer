Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

argsStr = ""
For i = 0 To WScript.Arguments.Count - 1
    argsStr = argsStr & " """ & WScript.Arguments(i) & """"
Next

pythonw = "pythonw.exe"
If fso.FileExists("C:\Python314\pythonw.exe") Then
    pythonw = "C:\Python314\pythonw.exe"
End If

WshShell.Run """" & pythonw & """ """ & scriptDir & "\gui.py""" & argsStr, 0, False