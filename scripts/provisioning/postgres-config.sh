#!/usr/bin/env bash

function apt-get() {
  while fuser -s /var/lib/dpkg/lock;
    do echo 'apt-get is waiting for the lock release ...';
    sleep 1;
  done;
  /usr/bin/apt-get "$@";
}

sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

apt-get update

apt-get -y install postgresql-13 postgresql-13 postgresql-client-13


##################################  Enabling external access to Database #############################
echo "listen_addresses = '*'" >> /etc/postgresql/13/main/postgresql.conf
echo 'host    all             all             192.168.33.10/24        md5' >> /etc/postgresql/13/main/pg_hba.conf
service postgresql restart

##################################  Creating stork Database #############################

sudo -u postgres psql -c "create database api_users;"
sudo -u postgres psql -c "create user mahdy with encrypted password 'postgres';"
sudo -u postgres psql -c "grant all privileges on database api_users to mahdy;"
