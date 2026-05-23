'═══ TrackMe Desktop Shortcut Creator ═══
' Double-click this file to create a shortcut on your Desktop

Option Explicit

Dim WshShell, strDesktop, strProjectPath, oShortcut

' Get the folder where this .vbs file is located
strProjectPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")

' ── Create start shortcut ──
Set oShortcut = WshShell.CreateShortcut(strDesktop & "\TrackMe.lnk")
oShortcut.TargetPath = strProjectPath & "\start_trackme.bat"
oShortcut.WorkingDirectory = strProjectPath
oShortcut.Description = "تتبع الدوام والمالية الشخصية"
oShortcut.IconLocation = "C:\Program Files\Google\Chrome\Application\chrome.exe,0"
oShortcut.WindowStyle = 7    ' Minimized
oShortcut.Save

' ── Create stop shortcut ──
Set oShortcut = WshShell.CreateShortcut(strDesktop & "\إيقاف TrackMe.lnk")
oShortcut.TargetPath = strProjectPath & "\stop_trackme.bat"
oShortcut.WorkingDirectory = strProjectPath
oShortcut.Description = "إيقاف تطبيق TrackMe"
oShortcut.IconLocation = "shell32.dll,28"
oShortcut.WindowStyle = 7
oShortcut.Save

' ── Create startup folder shortcut (auto-start with Windows) ──
On Error Resume Next
Dim strStartup
strStartup = WshShell.SpecialFolders("Startup")
Set oShortcut = WshShell.CreateShortcut(strStartup & "\TrackMe.lnk")
oShortcut.TargetPath = strProjectPath & "\start_trackme.bat"
oShortcut.WorkingDirectory = strProjectPath
oShortcut.Description = "تشغيل TrackMe تلقائياً عند بدء Windows"
oShortcut.IconLocation = "C:\Program Files\Google\Chrome\Application\chrome.exe,0"
oShortcut.WindowStyle = 7
oShortcut.Save

MsgBox "تم بنجاح!" & vbCrLf & vbCrLf & _
       "✓ أيقونة TrackMe على سطح المكتب" & vbCrLf & _
       "✓ أيقونة إيقاف TrackMe على سطح المكتب" & vbCrLf & _
       "✓ تشغيل تلقائي عند بدء Windows", _
       vbInformation, "TrackMe — تثبيت الأيقونات"
