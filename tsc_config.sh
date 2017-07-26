#!/bin/sh
#if it does't work, dos2unix file and chmod 
echo "--------------------------------------------------------"
echo "|TSC ip config script ,and use for version 5.1 6.0 6.1 |"
echo "|                                                      |"
echo "|I don't check the Parameter Validity , so be carefull |"
echo "--------------------------------------------------------"
echo "eth0 `ifconfig eth0 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"
echo "eth1 `ifconfig eth1 | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g `"
echo "TSC IP enter eth0 OR eth1 :"
read eth
TSC_IP=`ifconfig $eth | grep 'inet ' | sed s/^.*addr://g | sed s/Bcast.*$//g | sed s/[[:space:]]//g`

echo "TSC_ID :"
read TSC_ID

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
INSERT INTO Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS", "LOGVIEW/MAXCOUNT","10","");
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

echo '----------------finished------------------'