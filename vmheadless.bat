@echo u17 starting

cd /d "C:\Program Files\Oracle\VirtualBox\"

VBoxManage.exe startvm u17 --type headless

@echo encrypt xp starting
cd /d "C:\Program Files (x86)\VMware\VMware VIX\"

vmrun.exe start "D:\newxp\newxp.vmx" nogui
@echo off