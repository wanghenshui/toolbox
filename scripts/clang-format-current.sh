#!/usr/bin/env bash
ls |awk -F ' ' '{print $NF}'|while read line
do 
	clang-format $line -style=Google
done