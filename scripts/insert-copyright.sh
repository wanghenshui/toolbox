#!/bin/bash
# insert copyright info to fix lint error
ls | awk -F ' ' '{print $NF}' |grep -E ".cc|.h|.cpp|.hpp|.hxx" |while read file
do 
  sed -i '1i// Copyright (c) 2019-present,xxx  Authors' $file
done
