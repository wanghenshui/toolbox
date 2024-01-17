#!/usr/bin/env bash
while true; do
  ans=`curl -s 'http://159.75.70.9:8081/pull?u=000002833073102FC37580D25D2067BF'`
  a=`echo $ans | jq ".a"|jq ".[]"`
  t=`echo $ans | jq -r .t`
  s=`echo $ans | jq ".a"|jq ".[]" | sort -n`
  v=$(echo $s | awk '{printf "%s ",$0}')
  b=$[-1 * ((-1 * ${v[0]} * ${v[1]} + ${v[2]} - ${v[3]}) * ${v[4]} + ${v[5]} - ${v[6]})]
  curl -s "http://159.75.70.9:8081/push?t=$t&a=$b"
done
