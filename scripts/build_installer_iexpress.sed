; IExpress SED file (example) to wrap Install_CertifyIntel.bat into a one-click EXE
; Usage (run in elevated cmd or normal cmd):
;   iexpress /N build_installer_iexpress.sed
;
; Output: CertifyIntel_Installer.exe in the same folder.

[Version]
Class=IEXPRESS
SEDVersion=3

[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=
DisplayLicense=
FinishMessage=
TargetName=%CD%\CertifyIntel_Installer.exe
FriendlyName=Certify Intel Installer
AppLaunched=Install_CertifyIntel.bat
PostInstallCmd=
AdminQuietInstCmd=
UserQuietInstCmd=
SourceFiles=SourceFiles

[SourceFiles]
SourceFiles0=%CD%

[SourceFiles0]
%CD%\Install_CertifyIntel.bat=
%CD%\Install_CertifyIntel.ps1=
%CD%\Certify_Intel_ExcelOnly_v3_dashboard_ops_ready.xlsx=
%CD%\JsonLite.bas=
%CD%\CertifyIntel_Core.bas=
%CD%\CertifyIntel_HTTP.bas=
%CD%\CertifyIntel_Allowlist.bas=
%CD%\CertifyIntel_Review.bas=
%CD%\CertifyIntel_Discovery_Bing.bas=
%CD%\CertifyIntel_FetchExtract.bas=
%CD%\CertifyIntel_Versions.bas=
%CD%\CertifyIntel_EventsAlerts.bas=
%CD%\CertifyIntel_UI.bas=
%CD%\CertifyIntel_SelfTests.bas=
%CD%\CertifyIntel_RunPipeline.bas=
%CD%\Install_Instructions.docx=

[Strings]
InstallPrompt=
FinishMessage=
