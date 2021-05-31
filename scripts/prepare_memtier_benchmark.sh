#!/bin/bash
set -x
yum install -y git
yum install -y libtools
git clone https://github.com/RedisLabs/memtier_benchmark.git
cd memtier_benchmark
yum install -y libevent2-devel
autoreconf -ivf
./configure --disable-tls
make -j32
make install