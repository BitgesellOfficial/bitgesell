; Bitgesell Core Windows NSIS Installer Script
; Based on Bitcoin Core's NSIS installer pattern

Name "Bitgesell Core ${VERSION}"

RequestExecutionLevel highest
SetCompressor /SOLID lzma
SetDateSave off
Unicode true

; General Symbol Definitions
!define REGKEY "SOFTWARE\$(^Name)"
!define COMPANY "Bitgesell Core project"
!define URL https://bitgesell.ca/

; MUI Symbol Definitions
!define MUI_ICON "${PROJECT_ROOT}\share\pixmaps\BGL.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${PROJECT_ROOT}\share\pixmaps\nsis-wizard.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
!define MUI_HEADERIMAGE_BITMAP "${PROJECT_ROOT}\share\pixmaps\nsis-header.bmp"
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_STARTMENUPAGE_REGISTRY_ROOT HKLM
!define MUI_STARTMENUPAGE_REGISTRY_KEY ${REGKEY}
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME StartMenuGroup
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "Bitgesell Core"
!define MUI_FINISHPAGE_RUN "$WINDIR\explorer.exe"
!define MUI_FINISHPAGE_RUN_PARAMETERS $INSTDIR\bin\BGL-qt.exe
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "${PROJECT_ROOT}\share\pixmaps\nsis-wizard.bmp"
!define MUI_UNFINISHPAGE_NOAUTOCLOSE

; Included files
!include Sections.nsh
!include MUI2.nsh
!include x64.nsh

; Variables
Var StartMenuGroup

; Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuGroup
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Installer languages
!insertmacro MUI_LANGUAGE English

; Installer attributes
OutFile "${INSTALLER_OUT}"
InstallDir $PROGRAMFILES64\Bitgesell
CRCCheck force
XPStyle on
BrandingText " "
ShowInstDetails show
VIProductVersion ${VERSION_COMMA}
VIAddVersionKey ProductName "Bitgesell Core"
VIAddVersionKey ProductVersion "${VERSION}"
VIAddVersionKey CompanyName "${COMPANY}"
VIAddVersionKey CompanyWebsite "${URL}"
VIAddVersionKey FileVersion "${VERSION}"
VIAddVersionKey FileDescription "Installer for Bitgesell Core"
VIAddVersionKey LegalCopyright "Copyright (C) 2009-2025 The Bitgesell Core developers"
InstallDirRegKey HKCU "${REGKEY}" Path
ShowUninstDetails show

; Installer sections
Section -Main SEC0000
    SetOutPath $INSTDIR
    SetOverwrite on

    SetOutPath $INSTDIR\bin
    File "${DEPLOY_DIR}\bin\BGL-qt.exe"
    File "${DEPLOY_DIR}\bin\BGLd.exe"
    File "${DEPLOY_DIR}\bin\BGL-cli.exe"
    File "${DEPLOY_DIR}\bin\BGL-tx.exe"
    File "${DEPLOY_DIR}\bin\BGL-wallet.exe"

    SetOutPath $INSTDIR
    File /oname=COPYING.txt "${PROJECT_ROOT}\COPYING"
    File /oname=readme.txt "${PROJECT_ROOT}\doc\README_windows.txt"
    File "${PROJECT_ROOT}\share\examples\BGL.conf"

    SetOutPath $INSTDIR\share\rpcauth
    File "${PROJECT_ROOT}\share\rpcauth\*.*"

    SetOutPath $INSTDIR\doc
    File /r /x Makefile* "${PROJECT_ROOT}\doc\*.*"

    WriteRegStr HKCU "${REGKEY}\Components" Main 1
SectionEnd

Section -post SEC0001
    WriteRegStr HKCU "${REGKEY}" Path $INSTDIR
    SetOutPath $INSTDIR
    WriteUninstaller $INSTDIR\uninstall.exe
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory $SMPROGRAMS\$StartMenuGroup
    CreateShortcut "$SMPROGRAMS\$StartMenuGroup\Bitgesell Core.lnk" $INSTDIR\bin\BGL-qt.exe
    CreateShortcut "$SMPROGRAMS\$StartMenuGroup\Bitgesell Core (testnet).lnk" "$INSTDIR\bin\BGL-qt.exe" "-testnet" "$INSTDIR\bin\BGL-qt.exe" 1
    CreateShortcut "$SMPROGRAMS\$StartMenuGroup\Uninstall Bitgesell Core.lnk" $INSTDIR\uninstall.exe
    !insertmacro MUI_STARTMENU_WRITE_END
    WriteRegStr HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Bitgesell Core" DisplayName "Bitgesell Core"
    WriteRegStr HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Bitgesell Core" DisplayVersion "${VERSION}"
    WriteRegStr HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Bitgesell Core" Publisher "${COMPANY}"
    WriteRegStr HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Bitgesell Core" URLInfoAbout "${URL}"
    WriteRegStr HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Bitgesell Core" DisplayIcon $INSTDIR\bin\BGL-qt.exe
    WriteRegStr HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Bitgesell Core" UninstallString $INSTDIR\uninstall.exe
    WriteRegDWORD HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Bitgesell Core" NoModify 1
    WriteRegDWORD HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Bitgesell Core" NoRepair 1
    WriteRegStr HKCR "bitgesell" "URL Protocol" ""
    WriteRegStr HKCR "bitgesell" "" "URL:Bitgesell"
    WriteRegStr HKCR "bitgesell\DefaultIcon" "" $INSTDIR\bin\BGL-qt.exe
    WriteRegStr HKCR "bitgesell\shell\open\command" "" '"$INSTDIR\bin\BGL-qt.exe" "%1"'
SectionEnd

; Macro for selecting uninstaller sections
!macro SELECT_UNSECTION SECTION_NAME UNSECTION_ID
    Push $R0
    ReadRegStr $R0 HKCU "${REGKEY}\Components" "${SECTION_NAME}"
    StrCmp $R0 1 0 next${UNSECTION_ID}
    !insertmacro SelectSection "${UNSECTION_ID}"
    GoTo done${UNSECTION_ID}
next${UNSECTION_ID}:
    !insertmacro UnselectSection "${UNSECTION_ID}"
done${UNSECTION_ID}:
    Pop $R0
!macroend

; Uninstaller sections
Section /o -un.Main UNSEC0000
    Delete /REBOOTOK $INSTDIR\bin\BGL-qt.exe
    Delete /REBOOTOK $INSTDIR\bin\BGLd.exe
    Delete /REBOOTOK $INSTDIR\bin\BGL-cli.exe
    Delete /REBOOTOK $INSTDIR\bin\BGL-tx.exe
    Delete /REBOOTOK $INSTDIR\bin\BGL-wallet.exe
    RMDir /REBOOTOK $INSTDIR\bin
    Delete /REBOOTOK $INSTDIR\COPYING.txt
    Delete /REBOOTOK $INSTDIR\readme.txt
    Delete /REBOOTOK $INSTDIR\BGL.conf
    RMDir /r /REBOOTOK $INSTDIR\share
    RMDir /r /REBOOTOK $INSTDIR\doc
    DeleteRegValue HKCU "${REGKEY}\Components" Main
SectionEnd

Section -un.post UNSEC0001
    DeleteRegKey HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Bitgesell Core"
    Delete /REBOOTOK "$SMPROGRAMS\$StartMenuGroup\Uninstall Bitgesell Core.lnk"
    Delete /REBOOTOK "$SMPROGRAMS\$StartMenuGroup\Bitgesell Core.lnk"
    Delete /REBOOTOK "$SMPROGRAMS\$StartMenuGroup\Bitgesell Core (testnet).lnk"
    Delete /REBOOTOK "$SMSTARTUP\BGL.lnk"
    Delete /REBOOTOK $INSTDIR\uninstall.exe
    Delete /REBOOTOK $INSTDIR\debug.log
    Delete /REBOOTOK $INSTDIR\db.log
    DeleteRegValue HKCU "${REGKEY}" StartMenuGroup
    DeleteRegValue HKCU "${REGKEY}" Path
    DeleteRegKey /IfEmpty HKCU "${REGKEY}\Components"
    DeleteRegKey /IfEmpty HKCU "${REGKEY}"
    DeleteRegKey HKCR "bitgesell"
    RmDir /REBOOTOK $SMPROGRAMS\$StartMenuGroup
    RmDir /REBOOTOK $INSTDIR
    Push $R0
    StrCpy $R0 $StartMenuGroup 1
    StrCmp $R0 ">" no_smgroup
no_smgroup:
    Pop $R0
SectionEnd

; Installer functions
Function .onInit
    InitPluginsDir
    ${If} ${RunningX64}
        SetRegView 64
    ${Else}
        MessageBox MB_OK|MB_ICONSTOP "Cannot install 64-bit version on a 32-bit system."
        Abort
    ${EndIf}
FunctionEnd

; Uninstaller functions
Function un.onInit
    ReadRegStr $INSTDIR HKCU "${REGKEY}" Path
    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuGroup
    !insertmacro SELECT_UNSECTION Main ${UNSEC0000}
FunctionEnd
