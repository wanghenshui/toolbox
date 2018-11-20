#!/bin/bash
#set -x
#add to crontab

#输入实例，获取实例的节点id和名字和角色
#遍历登录
#登录，取回最新的sa 文件，重命名为节点-角色-id
#调用分析脚本，生成pdf


#Config Info
CONN_NODE_PATH="/home/rds/wqw/"
CONN_NODE=${CONN_NODE_PATH}"conn_node.sh"
DST_LOG_PATH=${PWD}'/sar_log'
SRC_LOG_PATH='/var/log/sa'
REPORT_PATH=${PWD}
PLOT_SAR_LOG=${PWD}'/plotSarlog.py'

#	function get_pyscripts
#	生成脚本，内容是处理sar日志 需要提前安装好 matplotlib 和sar-viz 
#	安装 pip 或直接在github上下载然后python setup.py install即可
#	注意，sar-viz默认匹配python2，matplotlib需要安装2.2的版本
#	python3需要找对应的sarviz和matplotlib3版本，在github上都能找到

function gen_plot_sarlog(){
	if [ ! -f ${PLOT_SAR_LOG} ];then
#		echo ${PLOT_SAR_LOG_SCRIPTS} > ${PLOT_SAR_LOG}
cat <<EOF > ${PLOT_SAR_LOG}
import sys
from sar import parser
from sar import viz
insar=parser.Parser(sys.argv[1])
sar_viz=viz.Visualization(insar.get_sar_info(),paging=True,network=True,disk=True)
sar_viz.save(sys.argv[2])
EOF

	fi
}

#	function chmod_low_CryptPWD
#	权限问题，把文件权限调低通过登录验证
function chmod_low_CryptPWD(){
  chmod 000 ${CONN_NODE_PATH}CryptPWD/*
  chmod 777 ${CONN_NODE}
}

#	function prepare_log_path 

function prepare_log_path(){

	rm -rf ${DST_LOG_PATH}
	mkdir ${DST_LOG_PATH}
}
#	function process_log 
#	
#	@param $1 nodeId
function process_log(){

	#last_day=$(date -d last-day +%Y%m%d)
	#step 1 pull log from node
#	for nodeId in $1; do
		#for file_ in /var/log/sa/*; do
			#file_time=$(stat ${file_} | grep Modify | awk '{print $2}' | sed 's/-//g')
			#if [ ${last_day} \< ${file_time} ] ;then
	nodeId=$1
	#binary
	file_=${SRC_LOG_PATH}'/sa'$(date +%d)
	#sar usually missed, pass
	#file_r=${SRC_LOG_PATH}'/sar'$(date +%d)
	${CONN_NODE} connect ${nodeId} pull ${file_} ${DST_LOG_PATH}/${nodeId}.${file_##*/}.b
	sar -A -f ${DST_LOG_PATH}/${nodeId}.${file_##*/}.b > ${DST_LOG_PATH}/${nodeId}.${file_##*/}.log
	rm -rf ${DST_LOG_PATH}/${nodeId}.${file_##*/}.b
	#${CONN_NODE} connect ${nodeId} pull ${file_r} ${DST_LOG_PATH}/${nodeId}.${file_r##*/}.log
	
	#step 2 build report
	python ${PLOT_SAR_LOG} ${DST_LOG_PATH}/${nodeId}.${file_##*/}.log ${DST_LOG_PATH}/${nodeId}.${file_##*/}.log.pdf
}

#	function zip report
#	tar, chmod for download 
function zip_report(){
	#TODO:step 3 tar, chmod for download 
	datename=$(date +%Y%m%d-%H%M%S)
	tar -czvf ${REPORT_PATH}/report.${datename}.tar.gz ${DST_LOG_PATH}/*.pdf
	chmod 777 ${REPORT_PATH}/report.*
}

#	function #	function pull_log_from_node
#	
#	@param $1 instanceId
#   @ret   nodesid, nodesid_name,role
function get_nodeId_from_instanceId()
{
	${CONN_NODE} showNodesId $1 |awk '{print $1,$3,$7}' | sed '1,2d'|head -n -2;
}

#	function usage
#	miss instanceID then notice IT
function usage(){
	if [ $# -ne 1 ];then
		echo -e "\033[31m Usage: ./auto_gen_report dbinstanceID   \033[0m"
		exit
	fi
}


function main(){
	usage $@
	chmod_low_CryptPWD
	prepare_log_path
	gen_plot_sarlog
	nodes=$(get_nodeId_from_instanceId $1 )
	#第一列是nodeid 第二列是id名称 第三列是角色
	for nd in $(echo ${nodes} | tr ' '  '\n' |sed -n '1~3p');do
		process_log ${nd} 
	done	
	zip_report
}

main $@ 
