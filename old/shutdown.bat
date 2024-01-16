@echo vm suspending  

cd /d "C:\Program Files (x86)\VMware\VMware VIX\"
vmrun.exe suspend "D:\newxp\newxp.vmx"

@echo shutting down

shutdown -s -t 5

@echo off