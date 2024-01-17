#!/usr/bin/env bash
while true; do
  ans=`curl -s 'http://159.75.70.9:8081/pull?u=000002833073102FC37580D25D2067BF'`
  a=`echo $ans | jq ".a"|jq ".[]"`
  t=`echo $ans | jq -r .t`
  b=`./check3 $(echo $a | awk '{printf "%s ",$0}')`
  curl -s "http://159.75.70.9:8081/push?t=$t&a=$b"
done
