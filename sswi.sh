#!/bin/sh
#if it does't work, dos2unix file and chmod 
echo "--------------------------------------------------------"
echo "|TSC ip config script ,and use for version 5.1 6.0 6.1 |"
echo "|                                                      |"
echo "|I don't check the Parameter Validity , so be carefull |"
echo "--------------------------------------------------------"
echo "eth0 `ifconfig eth0 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"
echo "eth1 `ifconfig eth1 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"
echo "TSBS IP enter eth0 OR eth1 :"
read eth
TSBS_IP=`ifconfig $eth | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g | sed s/[[:space:]]//g`

echo "TSBS_ID :(=2000+ TSC_ID)"
read TSBS_ID

echo "MSO IP :"
read MSO_IP

echo "DMR mode 1 for dmr and 0 for pdt :"
read DMR
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
insert or replace into Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS", "LOGVIEW/MAXCOUNT","10","");
--update Tbl_Config set Value='0xff004f1f' where Tag='VOS' and Key='LOG/LOGLEVEL'

update Tbl_Config set Value='$TSBS_IP:0' where  Tag='SSWI'and Key='SSWI_ExtranetIp';

update Tbl_Config set Value='$MSO_IP' where  Tag='Agent'and Key='OM_SERVER_IP';
update Tbl_Config set Value='$MSO_IP' where  Tag='Agent'and Key='OM_SLAVE_IP';
update Tbl_Config set Value='$TSBS_IP'  where  Tag='Agent'and Key='AGENT_IP';
update Tbl_Config set Value='$TSBS_ID'        where  Tag='Agent'and Key='TSBS_ID';
EOF

echo '----------------finished------------------'