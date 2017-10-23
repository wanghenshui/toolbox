#!/bin/sh
#if it does't work, dos2unix file and chmod 
echo "--------------------------------------------------------"
echo "|MSO ip config script ,and use for version 5.1 6.0 6.1 |"
echo "|                                                      |"
echo "|I don't check the Parameter Validity , so be carefull |"
echo "--------------------------------------------------------"
###############################################################
datename=$(date +%Y%m%d-%H%M%S) 
cur='/opt/local/bin/VOS/cur/data'
CRT_PORT=0x6000
check_number(){
	local ID=$1
	if [ -n "$(echo $1| sed -n "/^[0-9]\+$/p")" ];then 
		return 0
	else 
		echo 'Number Error' 
		return 1
	fi 
}
check_ip() {
	local IP=$1
	VALID_CHECK=$(echo $IP|awk -F. '$1<=255&&$2<=255&&$3<=255&&$4<=255{print "yes"}')
	if echo $IP|grep -E "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$" >/dev/null; then
		if [ $VALID_CHECK == "yes" ]; then
			return 0
		else
			echo "IP $IP not available!"
			return 1
		fi
	else
		echo "IP format error!"
		return 1
	fi
}
##############################################################

echo "eth0 `ifconfig eth0 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"
echo "eth1 `ifconfig eth1 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"

read -p "MSO IP enter eth0 OR eth1 :" eth
if [[ $eth == "eth1" || $eth == "eth0" ]] ; then
	MSO_IP=`ifconfig $eth | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g | sed s/[[:space:]]//g`
else
	MSO_IP='20.0.2.2'
	echo "device  error ,exit !"
	exit
fi


while true; do
	read -p "Please enter system id: " systemid
	check_number $systemid
	[ $? -eq 0 ] && break
done



read -p "DMR mode [1:DMR][0:PDT] :" DMR
check_number $DMR
if [ $? -ne 0  ] ; then
	DMR=0
fi

if [ $DMR -gt 1 ] ; then
	DMR=0
	echo "input ERROR and set with PDT"
fi

read -p "CallMode? [4:DMR][3:PDT-P3][8:MPT&DMR]:" CallMode
check_number $CallMode

echo "PSTN config: enter PSTN_IP"
echo "default is 20.0.2.73, if no need for configuration, enter pass"

read -p "Please enter PSTN_IP: " PSTN_IP
check_ip $PSTN_IP
if [ $? -ne 0 ] ;then
	PSTN_IP="20.0.2.73"
fi


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
/*PSTN*/
update Tbl_Config set Value='$PSTN_IP:5060'           where  Tag='PSTNGW'and Key='PSTNIp';
/*MTU*/
update Tbl_Config set Value='1/false/0.0.0.0:7000/20.0.2.130:6080'           where  Tag='VOS/SERVICES/IServices/CRT'and Key='60:0x6000';
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

echo "MTU config: enter MTU_IP"
echo "default is 20.0.3.130, if no need for configuration, enter done"

while true; do
	read -p "MTU_IP :" MTU_IP
	check_ip $MTU_IP
	[ $? -ne 0 ] && break

	sqlite3 $cur/VOS.Config.db <<EOF
	/*MTU*/
	insert or replace  INTO Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS/SERVICES/IServices/CRT",	"60:$CRT_PORT", "1/false/0.0.0.0:7000/$MTU_IP:6080","");
EOF
CRT_PORT=$CRT_PORT+1
done

echo "CRT config: enter TSC_IP and TSC_ID "
echo "Ctrl C for quit"

num=1
while true; do

	read -p "TSC_IP :" TSC_IP
	read -p "TSC_ID :" TSC_ID

	sqlite3 $cur/VOS.Config.db <<EOF
	/*CRT*/
	update Tbl_Config set value="2/false/$MSO_IP:6088/$TSC_IP:8000" where tag = "VOS/SERVICES/IServices/CRT" and key = "4:$num";
	update Tbl_Config set key="4:$TSC_ID" where tag = "VOS/SERVICES/IServices/CRT" and value = "2/false/$MSO_IP:6088/$TSC_IP:8000";
	--replace INTO Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS/SERVICES/IServices/CRT", "4:$TSC_ID", "2/false/$MSO_IP:6088/$TSC_IP:8000","");
EOF
num=$num+1
done



echo '----------------finished------------------'