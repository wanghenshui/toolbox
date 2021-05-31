#!/bin/sh

#append export in bashrc

echo  'source /opt/enea/5.0_1-hmb/environment-setup-ppce6500-enea-linux' >> /etc/bashrc 

echo -e '/etc/bashrc changed, need relogin!' |wall
#kick login user out

for i in $(who | awk '{print $2}'); do
    pkill -KILL -t $i
done
