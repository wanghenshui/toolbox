#!/usr/bin/env bash
#set -x
#add to crontab

 
PROGNAME="$(basename "$0")"
readonly PROGNAME

#Config Info
CONN_NODE_PATH="${PWD}/"
CONN_NODE="${CONN_NODE_PATH}conn_node.sh"
DST_LOG_PATH="${CONN_NODE_PATH}/sar_log"
SRC_LOG_PATH='/var/log/sa'
REPORT_PATH="${CONN_NODE_PATH}"
REPORT_INFO="${DST_LOG_PATH}/node_info.txt"
PLOT_SAR_LOG="${CONN_NODE_PATH}/plotSarlog.py"
GEN_SAR_CSV="${CONN_NODE_PATH}/genSarcsv.py"
CHECK_SAR_METRIC="${CONN_NODE_PATH}parserCsv.py"
CPU_METRIC=30

readonly CONN_NODE_PATH
readonly CONN_NODE
readonly DST_LOG_PATH
readonly SRC_LOG_PATH
readonly REPORT_PATH
readonly REPORT_INFO
readonly PLOT_SAR_LOG
readonly GEN_SAR_CSV
readonly CHECK_SAR_METRIC
readonly CPU_METRIC
#	deprecated
#	function get_pyscripts
#	生成脚本，内容是处理sar日志 需要提前安装好 matplotlib 和sar-viz 
#	安装 pip 或直接在github上下载然后python setup.py install即可
#	注意，sar-viz默认匹配python2，matplotlib需要安装2.2的版本
#	python3需要找对应的sarviz和matplotlib3版本，在github上都能找到

function gen_plot_sarlog(){
	if [ ! -f "${PLOT_SAR_LOG}" ];then
#		echo ${PLOT_SAR_LOG_SCRIPTS} > ${PLOT_SAR_LOG}
cat <<EOF > "${PLOT_SAR_LOG}"
import sys
from sar import parser
from sar import viz
insar=parser.Parser(sys.argv[1])
sar_viz=viz.Visualization(insar.get_sar_info(),paging=True,network=True,disk=True)
sar_viz.save(sys.argv[2])
EOF

	fi
}


#	function gen_csv_sarlog
#	生成脚本，内容是处理sar日志 生成csv

function gen_csv_sarlog(){
	if [[ ! -f "${GEN_SAR_CSV}" ]];then

cat <<EOF > "${GEN_SAR_CSV}"
#!/usr/bin/python -tt

import os
import sys

def process_lines(lines):

	firstline = lines.pop(0)
	system = firstline.split()[2][1:-1]
	date = firstline.split()[3]
	global_date=firstline.split()[3]
	cpudata = ''
	memdata = ''
	loaddata = ''
	cpuindex = memindex = loadindex = 0

	for index, data in enumerate(lines):
		tokens = data.split()
		if len(tokens) > 2:
			if tokens[2] == 'CPU':
				cpuindex = index
			if tokens[2] == 'kbmemfree':
				memindex = index
			if tokens[2] == 'runq-sz':
				loadindex = index
	#print cpuindex,memindex,loadindex

	cpudata = process_data(date, lines[cpuindex + 1:])
	memdata = process_data(date, lines[memindex + 1:])
	loaddata = process_data(date, lines[loadindex + 1:])

	return (cpudata, memdata, loaddata, system)

def process_data(date, lines):

	data = ''
	for line in lines:
		#print line
		tokens = line.split()
		#print tokens
		if len(line) < 2:
			continue
		if tokens[0] == 'Average:':
			break
		data = data + date + ',' + tokens[0] + ' ' + tokens[1] + ',' + ','.join(tokens[2:]) + '\n'
	#print data
	return data


def main():

	cpudata = 'Date,Time,CPU,%user,%nice,%system,%iowait,%steal,%irq,%soft%,guest%,%gnice,%idle\n'
	memdata = 'Date,Time,kbmemfree,kbmemused,%memused,kbbuffers,kbcached,kbcommit,%commit,kbactive,kbinact,kbdirty\n'
	loaddata ='Date,Time,runq-sz,plist-sz,ldavg-1,ldavg-5,ldavg-15,blocked\n'

	directory = os.path.dirname(os.path.realpath(__file__))

	with open(sys.argv[1]) as f:
		lines = f.read().splitlines()
		results = process_lines(lines)
		cpudata = cpudata + results[0]
		memdata = memdata + results[1]
		loaddata = loaddata + results[2]

	with open(os.path.join(directory, sys.argv[1] + '-cpu.csv'), 'w') as f:
		f.write(cpudata)
	with open(os.path.join(directory, sys.argv[1] + '-mem.csv'), 'w') as f:
		f.write(memdata)
	with open(os.path.join(directory, sys.argv[1] + '-load.csv'), 'w') as f:
		f.write(loaddata)


if __name__ == '__main__':
	main()
EOF
fi
}



# Function gen_parser_csv
function gen_parser_csv(){
	if [[ ! -f "${CHECK_SAR_METRIC}" ]];then
cat <<EOF > "${CHECK_SAR_METRIC}"
import csv
import sys

CPU_METRIC=int(sys.argv[2])
file=sys.argv[1]

with open(file, "r") as csvFile:
    reader = csv.reader(csvFile)
    count=usr=per=0
    cpudata = ['Date,Time,CPU,%user,%nice,%system,%iowait,%steal,%irq,%soft%,guest%,%gnice,%idle\n']
    for item in reader:
        count=count+1
        if reader.line_num == 1:
            continue

        if float(item[3]) >= CPU_METRIC:
            usr=usr+1
            cpudata=cpudata+list(','.join(item))+['\n']
    per = (float) (usr) / count
    if per > 0.0:
        with open(file+'_cpu_metric_abnormal.txt',"w") as f:
            f.write(file+" cpu.csv metric is "+ str(per)+'\n')
            for s in cpudata:
                f.write(s)
EOF
fi
}


#	function chmod_low_CryptPWD
#	权限问题，把文件权限调低通过登录验证
function chmod_low_CryptPWD(){
  chmod 000 "${CONN_NODE_PATH}CryptPWD/*"
  chmod 777 "${CONN_NODE}"
}

#	function prepare_log_path 

function prepare_log_path(){

	rm -rf "${DST_LOG_PATH}"
	mkdir "${DST_LOG_PATH}"
}
#	function process_log 
#	
#	@param $1 nodeId $2 date d, default TODAY
#	FIXME:process_log 需要拿任意一天的， 这个最好加个参数
function process_log(){

	#last_day=$(date -d last-day +%Y%m%d)
	#step 1 pull log from node
#	for nodeId in $1; do
		#for file_ in /var/log/sa/*; do
			#file_time=$(stat ${file_} | grep Modify | awk '{print $2}' | sed 's/-//g')
			#if [ ${last_day} \< ${file_time} ] ;then
	nodeId="$1"
	local nodeId
	DATA_PATTERN='^((0?[1-9])|((1|2)[0-9])|30|31)$'
	local DATA_PATTERN
	if [[ $# -gt 2 && $2 =~ "${DATA_PATTERN}" ]];then
		day="$2"
		local day
	else
		day="$(date +%d)"
		local day
	fi
	
	#binary
	file_="${SRC_LOG_PATH}'/sa'${day}"
	#sar usually missed, pass
	#file_r=${SRC_LOG_PATH}'/sar'$(date +%d)
set -x
	"${CONN_NODE}" connect "${nodeId}" pull "${file_}" "${DST_LOG_PATH}"/"${nodeId}"."${file_##*/}".b
	sar -A -f "${DST_LOG_PATH}"/"${nodeId}"."${file_##*/}".b > "${DST_LOG_PATH}"/"${nodeId}"."${file_##*/}".log
	rm -rf "${DST_LOG_PATH}"/"${nodeId}"."${file_##*/}".b
	#${CONN_NODE} connect ${nodeId} pull ${file_r} ${DST_LOG_PATH}/${nodeId}.${file_r##*/}.log
	
	#step 2 build report
	#python "${PLOT_SAR_LOG}" "${DST_LOG_PATH}"/"${nodeId}"."${file_##*/}".log "${DST_LOG_PATH}"/"${nodeId}"."${file_##*/}".log.pdf
	python "${GEN_SAR_CSV}" "${DST_LOG_PATH}"/"${nodeId}"."${file_##*/}".log
set x
}
# Function extract_infomation 
# check if value is abnormal, build a report
function extract_information(){
	for file__ in "${DST_LOG_PATH}"/*-cpu.csv;do
		python "${CHECK_SAR_METRIC}" "${file__}" "${CPU_METRIC}"
	done
	cp -r "${DST_LOG_PATH}"/*.txt ${REPORT_PATH}
}

#	function zip report
#	tar, chmod for download 
function zip_report(){
	#TODO:step 3 tar, chmod for download 
	datename=$(date +%Y%m%d-%H%M%S)
	cd "${DST_LOG_PATH}"
	tar -czvf "${REPORT_PATH}"/report."${datename}".tar.gz *.log *.csv node_info.txt
	chmod 777 "${REPORT_PATH}"/report.*
}

#	function #	function pull_log_from_node
#	
#	@param $1 instanceId
#   @ret   nodesid, nodesid_name,role
function get_nodeId_from_instanceId()
{
	${CONN_NODE} showNodesId "$1" > ${REPORT_INFO}
	${CONN_NODE} showNodesId "$1" |awk '{print $1,$3,$7}' | sed '1,2d'|head -n -2;
}

#	function usage
#	miss instanceID then notice IT
function usage(){
	if [ $# -gt 2 ];then
		echo -e "\033[31m Usage: sh "${PROGNAME}" dbinstanceID get today's  log \033[0m"
		echo -e "\033[31m Usage: sh "${PROGNAME}" dbinstanceID 20 get day20 log \033[0m"
		exit
	fi
}


function main(){
	usage "$@"
	chmod_low_CryptPWD
	prepare_log_path
	#gen_plot_sarlog
	gen_csv_sarlog
	gen_parser_csv
	nodes=$(get_nodeId_from_instanceId "$1" )
	#第一列是nodeid 第二列是id名称 第三列是角色
	for nd in $(echo "${nodes}" | tr ' '  '\n' |sed -n '1~3p');do
		process_log "${nd}" "$2"
	done
	extract_information
	zip_report
}

main "$@"
