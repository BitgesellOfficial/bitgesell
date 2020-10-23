#!/bin/bash

####
# 1. Set Initial Variables from command line arguments
####

# The arguments are read as per the below variables:
# ./standup.sh "BGLTYPE" "UFW_STATUS" "SSH_KEY" "SYS_SSH_IP" "USERPASSWORD" "UACOMMENT"

# If you want to omit an argument then input empty qoutes in its place for example:
# ./standup "mainnet" "" "" "" "aPasswordForTheUser" "userAgentComment"

# If you do not want to add any arguments and run everything as per the defaults simply run:
# ./standup.sh


# Can be one of the following: "mainnet", "pruned mainnet", "testnet", "pruned testnet", default is "mainnet"
BGLTYPE=$1

# Optional key for firewall status, can be the following: "enabled" - if you do not want to enable one add "" as an argument
UFW_STATUS=$2

# Optional key for automated SSH logins to standup non-privileged account - if you do not want to add one add "" as an argument
SSH_KEY=$3

# Optional comma separated list of IPs that can use SSH - if you do not want to add any add "" as an argument
SYS_SSH_IP=$4

# Optional password for the standup non-privileged account - if you do not want to add one add "" as an argument
USERPASSWORD=$5

# Optional key for node user agent comment  - if you do not want to add one add "" as an argument
UACOMMENT=$6

# Force check for root, if you are not logged in as root then the script will not execute
if ! [ "$(id -u)" = 0 ]
then

  echo "$0 - You need to be logged in as root!"
  exit 1

fi

# Output stdout and stderr to ~root files
exec > >(tee -a /root/standup.log) 2> >(tee -a /root/standup.log /root/standup.err >&2)

####
# 2. Bring Up To Date
####

echo "$0 - Starting updates; this will take a while!"

# Make sure all packages are up-to-date
apt-get update
apt-get upgrade -y
apt-get dist-upgrade -y
apt-get -y install wget sudo systemd vim-common


# Set system to automatically update
echo "unattended-upgrades unattended-upgrades/enable_auto_updates boolean true" | debconf-set-selections
apt-get -y install unattended-upgrades

echo "$0 - Updated Packages"

# get uncomplicated firewall and deny all incoming connections except SSH

if [ "${UFW_STATUS,,}" == "enabled" ]; then

   sudo apt-get -y install ufw
   ufw allow ssh
   ufw enable
   echo "$0 - UFW is enabled."

fi



####
# 3. Set Up User
####

# Create "standup" user with optional password and give them sudo capability
/usr/sbin/useradd -m -p `perl -e 'printf("%s\n",crypt($ARGV[0],"password"))' "$USERPASSWORD"` -g sudo -s /bin/bash standup
/usr/sbin/adduser standup sudo

echo "$0 - Setup standup with sudo access."

# Setup SSH Key if the user added one as an argument
if [ -n "$SSH_KEY" ]
then

   mkdir ~standup/.ssh
   echo "$SSH_KEY" >> ~standup/.ssh/authorized_keys
   chown -R standup ~standup/.ssh

   echo "$0 - Added .ssh key to standup."

fi

# Setup SSH allowed IP's if the user added any as an argument
if [ -n "$SYS_SSH_IP" ]
then

  echo "sshd: $SYS_SSH_IP" >> /etc/hosts.allow
  echo "sshd: ALL" >> /etc/hosts.deny
  echo "$0 - Limited SSH access."

else

  echo "$0 - WARNING: Your SSH access is not limited; this is a major security hole!"

fi

####
# 4. Install BGL
####

# Download BGL
echo "$0 - Downloading BGL; this will also take a while!"

# CURRENT BGL RELEASE:
# Change as necessary
export BITGESELL_VERSION="0.1.2"

sudo -u standup wget -P ~standup/ "https://bitgesell.ca/downloads/${BITGESELL_VERSION}/bitgesell_${BITGESELL_VERSION}_amd64.deb"



# Install BGL
echo "$0 - Installinging BGL."

sudo apt-get -y install ~standup/bitgesell_${BITGESELL_VERSION}_amd64.deb

# Start Up BGL
echo "$0 - Configuring BGL."

sudo -u standup /bin/mkdir ~standup/.bgl

# The only variation between mainnet and testnet is that testnet has the "testnet=1" variable
# The only variation between regular and pruned is that pruned has the "prune=550" variable, which is the smallest possible prune

RPCPASSWORD=$(xxd -l 8 -p /dev/urandom)

cat > ~standup/.bgl/bgl.conf << EOF
server=1
rpcuser=standup
rpcpassword=$RPCPASSWORD
rpcconnect=127.0.0.1
EOF

if [ -n "$UACOMMENT" ]
then

cat >> ~standup/.bgl/bgl.conf << EOF
uacomment=$UACOMMENT
EOF

fi

if [ "${BGLTYPE,,}" == "mainnet" ]; then

cat >> ~standup/.bgl/bgl.conf << EOF
txindex=1
EOF

elif [ "${BGLTYPE,,}" == "pruned mainnet" ]; then

cat >> ~standup/.bgl/bgl.conf << EOF
prune=550
EOF

elif [ "${BGLTYPE,,}" == "testnet" ]; then

cat >> ~standup/.bgl/bgl.conf << EOF
txindex=1
testnet=1
EOF

elif [ "${BGLTYPE,,}" == "pruned testnet" ]; then

cat >> ~standup/.bgl/bgl.conf << EOF
prune=550
testnet=1
EOF

else

cat >> ~standup/.bgl/bgl.conf << EOF
txindex=1
EOF

fi

cat >> ~standup/.bgl/bgl.conf << EOF
[test]
rpcport=18332
[main]
rpcport=8332
EOF



/bin/chown standup ~standup/.bgl/bgl.conf
/bin/chmod 600 ~standup/.bgl/bgl.conf



# Setup BGL as a service that requires
echo "$0 - Setting up BGL as a systemd service."

sudo cat > /etc/systemd/system/bgld.service << EOF
# It is not recommended to modify this file in-place, because it will
# be overwritten during package upgrades. If you want to add further
# options or overwrite existing ones then use
# $ systemctl edit bgld.service
# See "man systemd.service" for details.
[Unit]
Description=Bitgesell daemon

[Service]
ExecStart=/usr/bin/BGLd -conf=/home/standup/.bgl/bgl.conf
# Process management
####################
Type=simple
PIDFile=/run/bgld/bgld.pid
Restart=on-failure
# Directory creation and permissions
####################################
User=standup
Group=sudo
# /run/bgld
RuntimeDirectory=bgld
RuntimeDirectoryMode=0710
# Hardening measures
####################
# Provide a private /tmp and /var/tmp.
PrivateTmp=true
# Mount /usr, /boot/ and /etc read-only for the process.
ProtectSystem=full
# Disallow the process and all of its children to gain
# new privileges through execve().
NoNewPrivileges=true
# Use a new /dev namespace only populated with API pseudo devices
# such as /dev/null, /dev/zero and /dev/random.
PrivateDevices=true
# Deny the creation of writable and executable memory mappings.
MemoryDenyWriteExecute=true
[Install]
WantedBy=multi-user.target
EOF


echo "$0 - Starting bgld service"
sudo systemctl enable bgld.service
sudo systemctl start bgld.service


echo "$0 - BGL is setup as a service and will automatically start if your VPS reboots"
echo "$0 - You can manually stop BGL with: sudo systemctl stop bgld.service"
echo "$0 - You can manually start BGL with: sudo systemctl start bgld.service"
echo "$0 - You can follow BGL logs with: sudo journalctl -u bgld.service -f"

# Finished, exit script
exit 1

