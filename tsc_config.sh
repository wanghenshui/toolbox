#!/bin/sh
#if it does't work, dos2unix file and chmod 

echo "--------------------------------------------------------"
echo "|TSC ip config script ,and use for version 5.1 6.0 6.1 |"
echo "--------------------------------------------------------"

#######
#tool
#######

print_usage(){
	echo ""
	echo "./tsc_config.sh |	 | -a[all] | -s[show] | -h[help] |"
	echo "usage:"
	echo "  /tsc_config.sh TO CONFIG ALL"
	echo "  /tsc_config.sh -a ./tsc_config.sh -a TO CONFIG ALL"
	echo "  /tsc_config.sh -s OR ./tsc_config.sh show SEE CONFIGURATION"
	echo "  /tsc_config.sh -h OR ./tsc_config.sh help SEE THIS HELP"
	echo "special usage: ./tsc_config.sh key value "
	echo "	like: ./tsc_config.sh DMR 1 "
	echo "	like: ./tsc_config.sh TSC_IP 20.0.0.10 "
	echo "	key: TSC_IP TSC_ID MSO_IP DMR"
	exit
}

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

config(){
## normal config
	echo "eth0 `ifconfig eth0 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"
	echo "eth1 `ifconfig eth1 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"

	read -p "TSC IP enter eth0 OR eth1: " eth
	if [[ $eth == "eth1" || $eth == "eth0" ]] ; then
		#eth${sed -n "/^[0-9]\+$/p"}
		TSC_IP=`ifconfig $eth | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g | sed s/[[:space:]]//g`
	else
		TSC_IP='20.0.0.2'
		echo "device  error ,exit !"
		exit
	fi

	while true; do
		read -p "Please enter TSC_ID: " TSC_ID
		check_number $TSC_ID
		[ $? -eq 0 ] && break
	done

	while true; do
		read -p "Please enter MSO_IP: " MSO_IP
		check_ip $MSO_IP
		[ $? -eq 0 ] && break
	done

	read -p "DMR mode 1 for dmr and 0 for pdt :" DMR
	check_number $DMR
	if [ $? -ne 0  ] ; then
		DMR=0
	fi

	if [ $DMR -gt 1 ] ; then
		DMR=0
		echo "input ERROR and set with PDT"
	fi
}

show_config(){
	#dup
		echo	"--------------------show configuration----------------"
		DMR=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config where  Tag='TSC'and Key='DMRCmptMode'")
		OM_SERVER_IP=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config where  Tag='Agent'and Key='OM_SERVER_IP'")
		OM_SLAVE_IP=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config where  Tag='Agent'and Key='OM_SLAVE_IP'")
		AGETN_TSC_IP=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config  where  Tag='Agent'and Key='AGENT_IP'")
		AGENT_TSC_ID=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config  where  Tag='Agent'and Key='TSC_ID'")
		TSC_TSC_ID=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config  where  Tag='TSC'and Key='TSC_ID'")
		TRT=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config  where  Tag='VOS/SERVICES/IServices/TRT' and Key='36:28672'")
		
		echo "OM_SERVER_IP " $OM_SERVER_IP
		echo "OM_SLAVE_IP  " $OM_SLAVE_IP
		echo "AGETN_TSC_IP " $AGETN_TSC_IP
		echo "AGENT_TSC_ID " $AGENT_TSC_ID
		echo "TSC_ID       " $TSC_TSC_ID
		echo "TSC:MSO_IP   " $TRT
		echo "DMR MODE     " $DMR
		echo	"-------------------------------------------------------"
		exit
}
#######
#entry
#######
if [ $# -ge 3 ]; then
	print_usage
fi


if [ $# -eq 2 ]; then
### $2 is key and $3 is value
	echo "------------------sqlite3 selecting---------------------"
	DMR=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config where  Tag='TSC'and Key='DMRCmptMode'")
	MSO_IP=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config where  Tag='Agent'and Key='OM_SERVER_IP'")
	TSC_IP=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config  where  Tag='Agent'and Key='AGENT_IP'")
	TSC_ID=$(sqlite3 $cur/VOS.Config.db "select Value from Tbl_Config  where  Tag='Agent'and Key='TSC_ID'")

	
	if [ $1 == "TSC_IP" ]; then
		TSC_IP=$2
		echo "TSC_IP changed" $TSC_IP
	elif [ $1 == "TSC_ID" ] ;then
		TSC_ID=$2
		echo "TSC_ID changed" $TSC_ID
	elif [ $1 == "MSO_IP" ] ;then
		MSO_IP=$2
		echo "MSO_IP changed" $MSO_IP
	elif [ $1 == "DMR" ] ;then
		DMR=$2
		echo "DMR changed" $DMR
	else
		echo "key not define! exit"
		print_usage
	fi
elif [ $# == 1 ];then
	if [[ $1 == "show" || $1 = "-s" ]];then
		show_config
	elif [[ $1 == "--help" || $1 == "-h" || $1 == "help" ]];then
		print_usage
	elif [[ $1 == "all" || $1 = "-a" ]];then
		config
	else
		echo "./tsc_config.h -h for help"
		exit
	fi
elif [ $# == 0 ];then
	config
else
	print_usage
fi

if [ -e $cur/VOS.Config.db ] ; then
	cp $cur/VOS.Config.db $cur/VOS.Config.db.$datename.bak
else
	echo "db doesn't exist"
	exit
fi	

echo "--------------------------------------------------------"
		echo "TSC_IP " $TSC_IP
		echo "TSC_ID " $TSC_ID
		echo "MSO_IP " $MSO_IP
		echo "DMR MODE" $DMR
echo "--------------------------------------------------------"	
echo "------------------sqlite3 updating----------------------"
sqlite3 $cur/VOS.Config.db <<EOF
insert or replace into Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS", "LOGVIEW/MAXCOUNT","10","");
--update Tbl_Config set Value='0xff004f1f' where Tag='VOS' and Key='LOG/LOGLEVEL'
update Tbl_Config set Value='2/true/$TSC_IP:8000/$MSO_IP:6088' where Tag='VOS/SERVICES/IServices/TRT'  and Key='23:0';
update Tbl_Config set Value='2/true/$TSC_IP:8002/$MSO_IP:5002' where Tag='VOS/SERVICES/IServices/TRT' and Key='36:28672';
/*TSC ÐÞ¸Ä*/
update Tbl_Config set Value='$TSC_ID'          where  Tag='TSC'and Key='TSC_ID';
update Tbl_Config set Value='$DMR'           where  Tag='TSC'and Key='DMRCmptMode';
update Tbl_Config set Value='$TSC_IP:0' where  Tag='TSC'and Key='TSC_ExtraNetIP';
/* Agent ÅäÖÃÐÞ¸Ä*/
update Tbl_Config set Value='$MSO_IP' where  Tag='Agent'and Key='OM_SERVER_IP';
update Tbl_Config set Value='$MSO_IP' where  Tag='Agent'and Key='OM_SLAVE_IP';
update Tbl_Config set Value='$TSC_IP'  where  Tag='Agent'and Key='AGENT_IP';
update Tbl_Config set Value='$TSC_ID'        where  Tag='Agent'and Key='TSC_ID';
EOF

echo "-------------------------finished-----------------------"
