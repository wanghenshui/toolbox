#!/bin/bash
#set -x
#add to crontab
#https://stackoverflow.com/questions/610839/how-can-i-programmatically-create-a-new-cron-job
function main(){
	(crontab -l ; echo "0 * * * * $@ ") | sort - | uniq - | crontab -
}
main $@ 