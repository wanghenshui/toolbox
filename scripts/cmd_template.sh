#!/usr/bin/env bash

PROGNAME="$(basename $0)"
readonly PROGNAME
PROGDIR="$(readlink -m $(dirname $0))"
readonly PROGDIR
ARGS="$@"
readonly ARGS

function usage() {
    cat <<- EOF
    usage: $PROGNAME options
   
    Program deletes files from filesystems to release space.
    It gets config file that define fileystem paths to work on, and whitelist rules to
    keep certain files.
    OPTIONS:
       -c --config              configuration file containing the rules. use --help-config to see the syntax.
       -n --pretend             do not really delete, just how what you are going to do.
       -t --test                run unit test to check the program
       -v --verbose             Verbose. You can specify more then one -v to have more verbose
       -x --debug               debug
       -h --help                show this help
          --help-config         configuration help
   
    Examples:
       Run all tests:
       $PROGNAME --test all
       Run specific test:
       $PROGNAME --test test_string.sh
       Run:
       $PROGNAME --config /path/to/config/$PROGNAME.conf
       Just show what you are going to do:
       $PROGNAME -vn -c /path/to/config/$PROGNAME.conf
EOF
}



function cmdline() {
    local arg=
    for arg
    do
        local delim=""
        case "$arg" in
            #translate --gnu-long-options to -g (short options)
            --config)         args="${args}-c ";;
            --pretend)        args="${args}-n ";;
            --test)           args="${args}-t ";;
            --help-config)    usage_config && exit 0;;
            --help)           args="${args}-h ";;
            --verbose)        args="${args}-v ";;
            --debug)          args="${args}-x ";;
            #pass through anything else
            *) [[ "${arg:0:1}" == "-" ]] || delim="\""
                args="${args}${delim}${arg}${delim} ";;
        esac
    done
    #Reset the positional parameters to the short options
    eval set -- $args
    while getopts "nvhxt:c:" OPTION
    do
         case $OPTION in
         v)
             readonly VERBOSE=1
             ;;
         h)
             usage
             exit 0
             ;;
         x)
             readonly DEBUG='-x'
             set -x
             ;;
         t)
             RUN_TESTS=$OPTARG
             verbose VINFO "Running tests"
             ;;
         c)
             readonly CONFIG_FILE=$OPTARG
             ;;
         n)
             readonly PRETEND=1
             ;;
        esac
    done
    if [[ $recursive_testing || -z $RUN_TESTS ]]; then
        [[ ! -f $CONFIG_FILE ]] \
            && eexit "You must provide --config file"
    fi
    return 0
}


main() {
    cmdline $ARGS
}
main

