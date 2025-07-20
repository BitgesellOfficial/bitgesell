#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
export TZ=Etc/UTC
apt-get update && apt-get install -y tzdata
ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
dpkg-reconfigure --frontend noninteractive tzdata
#apt-get -y update
apt-get -y install apt-utils devscripts sudo #dpkg-dev
apt-get -y install libqrencode-dev qt5-default qttools5-dev-tools
