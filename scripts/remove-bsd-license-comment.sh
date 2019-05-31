#!/bin/bash
# remove license info in source file
ls | awk -F ' ' '{print $NF}' |while read file
do 
    n=$(grep -n "BSD-style" $file | awk -F ':' '{print $1}')
    if [[ n != "" ]]
    then   
	    sed "$n,$(expr $n + 2)d" -i $file
    fi
done
