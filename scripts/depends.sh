#!/usr/bin/env bash

ESC_SEQ="\x1b["
 COL_RESET=$ESC_SEQ"39;49;00m"
 DARKGRAY=$ESC_SEQ"30;01m"
 LIGHTRED=$ESC_SEQ"31;01m"
 LIGHTGREEN=$ESC_SEQ"32;01m"
 # LIGHTGREEN=$ESC_SEQ"37;11m"
 YELLOW=$ESC_SEQ"33;01m"
 LIGHTBLUE=$ESC_SEQ"34;01m"
 LIGHTPURPLE=$ESC_SEQ"35;01m"
 LIGHTCYAN=$ESC_SEQ"36;01m"
 WHITE=$ESC_SEQ"37;01m"
 BLACK=$ESC_SEQ"30;11m"
 RED=$ESC_SEQ"31;11m"
 GREEN=$ESC_SEQ"32;11m"
 ORANGE=$ESC_SEQ"33;11m"
 BLUE=$ESC_SEQ"34;11m"
 PURPLE=$ESC_SEQ"35;11m"
 CYAN=$ESC_SEQ"36;11m"
 LIGHTGRAY=$ESC_SEQ"37;11m"

#!/bin/bash

function hide_output {
		OUTPUT=$(tempfile)
		$@ &> $OUTPUT
		E=$?
		if [ $E != 0 ]; then
		echo
		echo FAILED: $@
		echo -----------------------------------------
		cat $OUTPUT
		echo -----------------------------------------
		exit $E
		fi

		rm -f $OUTPUT
}

function spinner() {
		local pid=$!
		local delay=0.025
		local spinstr='|/-\'
		while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
				local temp=${spinstr#?}
				printf " [%c]  " "$spinstr"
				local spinstr=$temp${spinstr%"$temp"}
				sleep $delay
				GREEN='\033[11;37m'
				NC='\033[0m' # No Color
				printf "${GREEN}\b\b\b\b\b\b"
		done
		printf "${GREEN}    \b\b\b\b"
    return 1
	exit 1
}

function spinnergreen() {
		local pid=$!
		local delay=0.025
		local spinstr='|/-\'
		while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
				local temp=${spinstr#?}
				printf " [%c]  " "$spinstr"
				local spinstr=$temp${spinstr%"$temp"}
				sleep $delay
				GREEN='\033[00;32m'
				NC='\033[0m' # No Color
				printf "${GREEN}\b\b\b\b\b\b"
		done
		printf "${GREEN}    \b\b\b\b"
    return 1
	exit 1
}

function spinnerblack() {
		local pid=$!
		local delay=0.025
		local spinstr='|/-\'
		while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
				local temp=${spinstr#?}
				printf " [%c]  " "$spinstr"
				local spinstr=$temp${spinstr%"$temp"}
				sleep $delay
				GREEN='\033[00;30m'
				NC='\033[0m' # No Color
				printf "${GREEN}\b\b\b\b\b\b"
		done
		printf "${GREEN}    \b\b\b\b"
    return 1
	exit 1
}


function bar() { 

echo -ne '\r'
sleep 0.7
echo -ne $LIGHTGRAY '#############             (33%)\r'
sleep 0.7
echo -ne $LIGHTGRAY '#######################   (100%)\r'
echo -ne '\n'
}


function apt_get_quiet {
		DEBIAN_FRONTEND=noninteractive hide_output sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" "$@" 
}




if ! locale -a | grep en_US.utf8 > /dev/null; then
# Generate locale if not exists
hide_output locale-gen en_US.UTF-8
fi

export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_TYPE=en_US.UTF-8

# Fix so line drawing characters are shown correctly in Putty on Windows. See #744.
export NCURSES_NO_UTF8_ACS=1


clear 

echo -e "$WHITE								


										               Made by Tyler for Bitgesell 
$COL_RESET"


# Check swap
echo -e "$LIGHTCYAN Checking for swap file...$COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTCYAN...$COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTCYAN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTCYAN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTCYAN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTCYAN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & bar


SWAP_MOUNTED=$(cat /proc/swaps | tail -n+2)
SWAP_IN_FSTAB=$(grep "swap" /etc/fstab)
ROOT_IS_BTRFS=$(grep "\/ .*btrfs" /proc/mounts)
TOTAL_PHYSICAL_MEM=$(head -n 1 /proc/meminfo | awk '{print $2}')
AVAILABLE_DISK_SPACE=$(df / --output=avail | tail -n 1)
if
[ -z "$SWAP_MOUNTED" ] &&
[ -z "$SWAP_IN_FSTAB" ] &&
[ ! -e /swapfile ] &&
[ -z "$ROOT_IS_BTRFS" ] &&
[ $TOTAL_PHYSICAL_MEM -lt 19000000 ] &&
[ $AVAILABLE_DISK_SPACE -gt 5242880 ]
then
echo -e "$LIGHTGREEN Adding a swap file...$COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTGREEN ...$COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHLIGHTGREEN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTGREEN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTGREEN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTCYAN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTCYAN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTCYAN $COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTCYAN This will take 10-30 seconds... $COL_RESET" & spinnergreen 

# Allocate and activate the swap file

dd if=/dev/zero of=/swapfile bs=2048 count=$[1024*1024] status=none
if [ -e /swapfile ]; then
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
fi


echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
fi

echo -e "$LIGHTGRAY...$COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTGRAY...$COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTGRAY...$COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTGRAY...$COL_RESET" & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
echo -e "$LIGHTGREEN $COL_RESET" 
echo -e "$LIGHTGREEN $COL_RESET" 
echo -e "$LIGHTGREEN $COL_RESET" 
echo -e "$LIGHTGREEN $COL_RESET" 
echo -e "$LIGHTGREEN done...$COL_RESET" & bar

sleep 0.7


echo -e "$LIGHTGRAY...$COL_RESET"

clear
 


sudo swapon --show  & spinner

sleep 1.5

clear

echo -e "$WHITE								

						

										                  Made by Tyler for Bitgesell 
$COL_RESET"

echo -e "$LIGHTGRAY Swap file made - now making dependencies... $COL_RESET"

echo -e
echo -e

echo -e "\e[39m\e[5m\e[92mInstalling dependencies Part 1/6\e[0m" 


sudo apt-get update -y >/dev/null 1>&1 & spinner & spinner & spinner & spinner & spinner & spinner

sudo apt-get upgrade -y >/dev/null 1>&1 & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen 

sudo apt-get update -y >/dev/null 1>&1 & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack
 
echo -e

echo -e "$LIGHTBLUE $COL_RESET" & bar




echo -e
echo -e

echo -e "\e[39m\e[5m\e[92mInstalling dependencies Part 2/6\e[0m" 

sudo apt-get install libprotobuf-dev protobuf-compiler libqrencode-dev unzip doxygen cmake nsis bc -y >/dev/null 2>&1  & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen

sudo apt-get install libminiupnpc-dev libzmq3-dev libgmp3-dev libqt5gui5 libqt5core5a libqt5dbus5 qttools5-dev qttools5-dev-tools libprotobuf-dev protobuf-compiler -y >/dev/null 2>&1 & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack

echo -e

echo -e "$LIGHTBLUE $COL_RESET " & bar





echo -e
echo -e
echo -e "\e[39m\e[5m\e[92mInstalling dependencies Part 3/6\e[0m" 

sudo apt-get install build-essential libtool autotools-dev automake pkg-config libssl-dev libevent-dev bsdmainutils -y >/dev/null 2>&1 & spinner & spinner & spinner & spinner & spinner & spinner

sudo apt-get install python3 libboost-system-dev libboost-filesystem-dev libboost-chrono-dev libboost-test-dev libboost-thread-dev libboost-all-dev libboost-program-options-dev -y >/dev/null 2>&1 & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen

sudo apt-get update -y >/dev/null 1>&1 & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack

echo -e


echo -e "$LIGHTBLUE $COL_RESET" & bar





echo -e
echo -e
echo -e "\e[39m\e[5m\e[92mInstalling dependencies Part 4/6\e[0m" 

sudo apt-get install libcurl4-openssl-dev -y >/dev/null 1>&1 & spinner & spinner & spinner & spinner & spinner & spinner

sudo apt-get install libminiupnpc-dev -y >/dev/null 1>&1 & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen 

sudo apt-get update -y >/dev/null 1>&1 & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack

echo -e

echo -e "$LIGHTBLUE $COL_RESET" & bar





echo -e
echo -e
echo -e "\e[39m\e[5m\e[92mInstalling dependencies Part 5/6\e[0m" 

sudo apt-get install software-properties-common >/dev/null 1>&1 & spinner & spinner & spinner & spinner & spinner

sudo add-apt-repository -y ppa:bitcoin/bitcoin >/dev/null 2>&1 & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen

sudo apt-get update >/dev/null 1>&1 & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen

sudo apt-get install libdb4.8-dev libdb4.8++-dev -y >/dev/null 1>&1 & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen
# sudo apt-get install libdb5.3-dev libdb5.3++-dev -y >/dev/null 1>&1 & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen

sudo apt-get update -y >/dev/null 1>&1 & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack

echo -e

echo -e "$LIGHTBLUE $COL_RESET" & bar






echo -e
echo -e
echo -e "\e[39m\e[5m\e[92mInstalling dependencies Part 6/6\e[0m" 

sudo apt-get install g++-mingw-w64-x86-64 -y >/dev/null 1>&1 & spinner & spinner & spinner & spinner & spinner & spinner

sudo update-alternatives --config x86_64-w64-mingw32-g++ <<< '1' >/dev/null 1>&1 & spinner & spinner & spinner & spinner & spinner & spinner

sudo apt-get install g++-mingw-w64-i686 -y >/dev/null 1>&1 & spinner & spinner & spinner & spinner & spinner & spinner

sudo update-alternatives --config i686-w64-mingw32-g++ <<< '1' >/dev/null 1>&1 & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen & spinnergreen

sudo apt-get update -y >/dev/null 1>&1 & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack & spinnerblack

echo -e

echo -e "$LIGHTBLUE $COL_RESET" & bar

sleep 1.5



clear

echo -e "$LIGHTGREEN 							












									                          YOUR SERVER IS READY !  :)

$COL_RESET"

sleep 2

clear

echo -e "$LIGHTGRAY ...$COL_RESET"


sleep 1.2



kill -INT 888 >/dev/null 2>&1

kill -9 888 >/dev/null 2>&1 

kill -INT 888 >/dev/null 2>&1 

kill -9 888 >/dev/null 2>&1 

PID=$! >/dev/null 2>&1 

sleep 0.2 >/dev/null 2>&1 

kill $PID >/dev/null 2>&1 

echo -e >/dev/null 2>&1 

clear





