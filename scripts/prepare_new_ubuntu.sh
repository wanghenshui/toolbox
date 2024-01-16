#!/bin/bash 
set -x
apt install -y vim tmux gcc git g++ ibus-pinyin python3 python3-pip

echo "fuck rotate sensor"
systemctl stop iio-sensor-proxy.service
systemctl disable iio-sensor-proxy.service

echo "create symbol link"
ln -s /usr/bin/python3 /usr/bin/python
ln -s /usr/bin/pip3 /usr/bin/pip
