#!/bin/sh
#if it does't work, dos2unix file and chmod 

if [[ $# == 1  ||  $# -ge 3 ]]; then
	echo
	echo "Usage: ./np_config"
	echo "config all issues  step by step"
	echo
	exit
fi

echo "--------------------------------------------------------"
echo "|                                                      |"
echo "|  NP config script ,and use for version 6.1           |"
echo "|                                                      |"
echo "--------------------------------------------------------"
#########################################tool##############################################

datename=$(date +%Y%m%d-%H%M%S) 
cur='/opt/local/bin/VOS/cur/data'
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
###########################################################################################

## normal config
echo "eth0 `ifconfig eth0 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"
echo "eth1 `ifconfig eth1 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"

read -p "NP_ExtranetIp enter eth0 OR eth1: " eth
if [[ $eth == "eth1" || $eth == "eth0" ]] ; then
	#eth${sed -n "/^[0-9]\+$/p"}
	NP_ExtranetIp=`ifconfig $eth | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g | sed s/[[:space:]]//g`
else
	NP_ExtranetIp='20.0.0.2'
	echo "device  error ,exit !"
	exit
fi

while true; do
	read -p "Please enter TSC_ID: " TSC_ID
	check_number $TSC_ID
	[ $? -eq 0 ] && break
done
ETSC1_ID=$[TSC_ID+61440]

while true; do
	read -p "Please enter OM_IP: " OM_IP
	check_ip $OM_IP
	[ $? -eq 0 ] && break
done

if [ -e $cur/VOS.Config.db ] ; then
	cp $cur/VOS.Config.db $cur/VOS.Config.db.$datename.bak
else
	echo "db doesn't exist"
	exit
fi	

echo "--------------------------------------------------------"
		echo "NP_ExtranetIp " $NP_ExtranetIp
		echo "ETSC1_ID " $ETSC1_ID
		echo "MSO_IP " $OM_IP
echo "--------------------------------------------------------"	
echo "------------------sqlite3 updating----------------------"
sqlite3 $cur/VOS.Config.db <<EOF
insert or replace into Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS", "LOGVIEW/MAXCOUNT","10","");
/* NP */
update Tbl_Config set Value='$ETSC1_ID'          where  Tag='Agent'and Key='ETSC1_ID';
update Tbl_Config set Value='$NP_ExtranetIp:0' where  Tag='NP'and Key='NP_ExtranetIp';
/* OM */
update Tbl_Config set Value='$OM_IP' where  Tag='Agent'and Key='OM_SERVER_IP';
update Tbl_Config set Value='$OM_IP' where  Tag='Agent'and Key='OM_SLAVE_IP';
update Tbl_Config set Value='$NP_ExtranetIp'  where  Tag='Agent'and Key='AGENT_IP';
EOF

echo "-------------------------finished-----------------------"