Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

argsStr = ""
For i = 0 To WScript.Arguments.Count - 1
    argsStr = argsStr & " """ & WScript.Arguments(i) & """"
Next

Function FindPython()
    Dim py, ver, candidate, localAppData, localPython, subFolder
    Dim vers: vers = Array("3.14", "3.13", "3.12", "3.11", "3.10", "3.9")

    ' 1. Check registry (HKCU then HKLM)
    On Error Resume Next
    For Each ver In vers
        Err.Clear
        py = WshShell.RegRead("HKCU\Software\Python\PythonCore\" & ver & "\InstallPath\WindowedExecutablePath")
        If Err.Number = 0 And fso.FileExists(py) Then FindPython = py: Exit Function
        
        Err.Clear
        py = WshShell.RegRead("HKCU\Software\Python\PythonCore\" & ver & "\InstallPath\")
        If Err.Number = 0 And fso.FileExists(py & "pythonw.exe") Then FindPython = py & "pythonw.exe": Exit Function

        Err.Clear
        py = WshShell.RegRead("HKLM\Software\Python\PythonCore\" & ver & "\InstallPath\WindowedExecutablePath")
        If Err.Number = 0 And fso.FileExists(py) Then FindPython = py: Exit Function

        Err.Clear
        py = WshShell.RegRead("HKLM\Software\Python\PythonCore\" & ver & "\InstallPath\")
        If Err.Number = 0 And fso.FileExists(py & "pythonw.exe") Then FindPython = py & "pythonw.exe": Exit Function
    Next
    On Error GoTo 0

    ' 2. Check %LOCALAPPDATA%\Programs\Python
    localAppData = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%")
    localPython = localAppData & "\Programs\Python"
    If fso.FolderExists(localPython) Then
        For Each subFolder In fso.GetFolder(localPython).SubFolders
            candidate = subFolder.Path & "\pythonw.exe"
            If fso.FileExists(candidate) Then FindPython = candidate: Exit Function
        Next
    End If

    ' 3. Check C:\PythonXX
    For Each ver In vers
        candidate = "C:\Python" & Replace(ver, ".", "") & "\pythonw.exe"
        If fso.FileExists(candidate) Then FindPython = candidate: Exit Function
    Next

    ' 4. Check %ProgramFiles%\PythonXX
    Dim pf: pf = WshShell.ExpandEnvironmentStrings("%ProgramFiles%")
    For Each ver In vers
        candidate = pf & "\Python" & Replace(ver, ".", "") & "\pythonw.exe"
        If fso.FileExists(candidate) Then FindPython = candidate: Exit Function
    Next

    ' 5. Check %ProgramFiles(x86)%\PythonXX
    Dim pfx86: pfx86 = WshShell.ExpandEnvironmentStrings("%ProgramFiles(x86)%")
    For Each ver In vers
        candidate = pfx86 & "\Python" & Replace(ver, ".", "") & "\pythonw.exe"
        If fso.FileExists(candidate) Then FindPython = candidate: Exit Function
    Next

    ' 6. Check official Python Launcher pyw.exe
    If fso.FileExists("C:\Windows\pyw.exe") Then FindPython = "C:\Windows\pyw.exe": Exit Function

    ' 7. Check if pythonw is in system PATH via where.exe
    On Error Resume Next
    Dim oExec: Set oExec = WshShell.Exec("where pythonw")
    If Not oExec Is Nothing Then
        If Not oExec.StdOut.AtEndOfStream Then
            candidate = Trim(oExec.StdOut.ReadLine())
            If fso.FileExists(candidate) Then FindPython = candidate: Exit Function
        End If
    End If
    On Error GoTo 0

    FindPython = ""
End Function

pythonwPath = FindPython()

If pythonwPath = "" Then
    msg = "خطا در اجرای PersianFixer:" & vbCrLf & vbCrLf & _
          "مفسر پایتون (Python 3.10 یا بالاتر) در سیستم شما شناسایی نشد." & vbCrLf & vbCrLf & _
          "برای استفاده از PersianFixer، لطفاً ابتدا پایتون را از سایت رسمی دانلود و نصب کنید." & vbCrLf & _
          "⚠️ نکته بسیار مهم: در صفحه اول نصب پایتون، حتماً گزینه:" & vbCrLf & _
          "   'Add python.exe to PATH'" & vbCrLf & _
          "را تیک بزنید." & vbCrLf & vbCrLf & _
          "آیا مایلید صفحه رسمی دانلود پایتون هم‌اکنون در مرورگر باز شود؟"
    res = MsgBox(msg, vbCritical + vbYesNo, "PersianFixer - پایتون یافت نشد")
    If res = vbYes Then
        WshShell.Run "https://www.python.org/downloads/"
    End If
    WScript.Quit 1
End If

On Error Resume Next
WshShell.Run """" & pythonwPath & """ """ & scriptDir & "\gui.py""" & argsStr, 0, False
If Err.Number <> 0 Then
    MsgBox "خطا در راه‌اندازی PersianFixer:" & vbCrLf & Err.Description, vbCritical, "PersianFixer"
End If
