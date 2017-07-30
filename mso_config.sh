#!/bin/sh
#if it does't work, dos2unix file and chmod 
echo "--------------------------------------------------------"
echo "|MSO ip config script ,and use for version 5.1 6.0 6.1 |"
echo "|                                                      |"
echo "|I don't check the Parameter Validity , so be carefull |"
echo "--------------------------------------------------------"
echo "eth0 `ifconfig eth0 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"
echo "eth1 `ifconfig eth1 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"
echo "TSC IP enter eth0 OR eth1 :"
read eth
MSO_IP=`ifconfig $eth | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g | sed s/[[:space:]]//g`

echo "system id"
read systemid

echo "DMR mode 1 for DMR and 0 for PDT :"
read DMR

echo "CallMode 4 for DMR and 3 for PDT-P3 :"
read CallMode
datename=$(date +%Y%m%d-%H%M%S) 
cur='/opt/local/bin/VOS/cur/data'
if [ -e $cur/VOS.Config.db ] ; then
cp $cur/VOS.Config.db $cur/VOS.Config.db.$datename.bak
else
echo "db doesn't exist"
exit
fi	
echo "---------------sqlite3 running--------------"
sqlite3 $cur/VOS.Config.db <<EOF
/*Log counts*/
insert or replace INTO Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS", "LOGVIEW/MAXCOUNT","10","");

update Tbl_Config set value = replace (value,'20.0.2.2','$MSO_IP');

/*system id*/
update Tbl_Config set Value='$systemid'           where  Tag='MSO'and Key='SystemID';

/* DMR */
update Tbl_Config set Value='$DMR'           where  Tag='MSO'and Key='DMRCmptMode';

/* Call Mode*/
update Tbl_Config set Value='$CallMode'      where  Tag='SAG' and Key='SYS_MODE';

/*SAG*/
update Tbl_Config set value = replace (value,'192.168.20.96','$MSO_IP');

/*SPGP*/
update Tbl_Config set value = replace (value,'192.168.20.18','$MSO_IP');
update Tbl_Config set value="$MSO_IP:6000" where tag = "SPGP" and key = "MsoIp";

/*AISGW*/
update Tbl_Config set value="$MSO_IP:5062" where tag = "AISGW" and key = "AISGWIP";

/*GPSS*/
update Tbl_Config set value="2/false/$MSO_IP:29876/$MSO_IP:0" where tag = "VOS/SERVICES/IServices/GPSS" and key = "56";

/*vauc*/
update Tbl_Config set value="2/false/$MSO_IP:5002/$MSO_IP:8002" where tag = "VOS/SERVICES/IServices/V_AuC" and key = "4";
update Tbl_Config set value="$MSO_IP:3696" where tag = "V_AuC" and key = "AucUDPAddr";
update Tbl_Config set value="$MSO_IP:5500" where tag = "V_AuC" and key = "KdmcUDPAddr";
update Tbl_Config set value="$MSO_IP:3696" where tag = "V_AuC" and key = "LocalUDPAddr";
EOF

echo "CRT config: enter TSC_IP and TSC_ID "
echo "Ctrl C for quit"

num=1
while [[ 1 ]]; do
	echo "TSC_IP :"
	read TSC_IP
	echo "TSC_ID :"
	read TSC_ID

	sqlite3 $cur/VOS.Config.db <<EOF
	/*CRT*/
	update Tbl_Config set value="2/false/$MSO_IP:6088/$TSC_IP:8000" where tag = "VOS/SERVICES/IServices/CRT" and key = "4:$num";
	update Tbl_Config set key="4:$TSC_ID" where tag = "VOS/SERVICES/IServices/CRT" and value = "2/false/$MSO_IP:6088/$TSC_IP:8000";
	--replace INTO Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS/SERVICES/IServices/CRT", "4:$TSC_ID", "2/false/$MSO_IP:6088/$TSC_IP:8000","");
EOF
num=$num+1
done

echo '----------------finished------------------'