#!/usr/bin/env bash

PROGNAME="$(basename $0)"
readonly PROGNAME
PROGDIR="$(readlink -m $(dirname $0))"
readonly PROGDIR
ARGS="$@"
readonly ARGS

CRONTAB_BACKUP=${PWD}/crontab.bak
readonly CRONTAB_BACKUP

function usage() {

    cat << EOF
    usage: $PROGNAME options
    Program comment/uncomment specific cron string in crontab
    OPTIONS:
       $PROGNAME comment   logrotate
                        #* * * * * /usr/sbin/logrotate /etc/logrotate.conf
       $PROGNAME uncomment logrotate
                        * * * * * /usr/sbin/logrotate /etc/logrotate.conf
EOF
}
function main(){

        crontab -l |tee ${CRONTAB_BACKUP}
        cmd_string=$2
        if [[ $1 == 'comment' ]];then
                sed -i "/${cmd_string}/s/^/#/" ${CRONTAB_BACKUP}
                echo "comment"
        elif [[ $1 == 'uncomment' ]];then
                sed -i "/${cmd_string}/s/^#//" ${CRONTAB_BACKUP}
        else
                usage
        fi
        crontab ${CRONTAB_BACKUP}
}

main "$@"