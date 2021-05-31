#!/bin/bash
ls |awk -F ' ' '{print $NF}'|while read line
do 
    cpplint $line
done
