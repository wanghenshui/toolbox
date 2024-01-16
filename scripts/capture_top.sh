#!/bin/bash
readonly PROGNAME=$(basename $0)
readonly ARGS="$@"

function check_number(){
    local ID=$1
    if [ -n "$(echo $1| sed -n "/^[0-9]\+$/p")" ];then 
	return 0
    else 
	echo 'Number Error' 
	return 1
    fi 
}


function usage() {
    cat << EOF
    usage: $PROGNAME name email
    set git config name and email and default setting
EOF
}

function main() {
    if [ $# -ne 1 ]; then
        usage
        exit
    fi

    second=$1
    check_number $second
    if [ $? -ne 0  ] ; then
        usage
        exit
    fi

    while [ true ]
    do
        top -n1 -b | sed -n '8, $p' | sort -r -n -k 10,10 > top-output.txt
        sleep $second
    done
}

main $ARGS
