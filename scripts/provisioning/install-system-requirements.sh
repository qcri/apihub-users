#!/usr/bin/env bash

function apt-get() {
  while fuser -s /var/lib/dpkg/lock;
    do echo 'apt-get is waiting for the lock release ...';
    sleep 1;
  done;
  /usr/bin/apt-get "$@";

}

apt-get update -y
apt-get install -y python-pip

apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev git

# Install redis-server
apt-get install -y redis-server
