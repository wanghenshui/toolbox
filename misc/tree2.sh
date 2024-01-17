#!/usr/bin/env bash
while true; do
  ans=`curl -s 'http://159.75.70.9:8081/pull?u=000002833073102FC37580D25D2067BF'`
  a=`echo $ans | jq ".a[0]"`
  t=`echo $ans | jq -r .t`
  b=$[a*a+a]
  a=$b
  curl -s "http://159.75.70.9:8081/push?t=$t&a=$a"
done
