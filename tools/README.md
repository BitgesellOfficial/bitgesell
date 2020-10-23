# 🛠 BGL-Standup Linux Script
This script installs the latest stable version of BGL Core, Uncomplicated Firewall (UFW), enables automatic updates for good security practices.


## Installation Instructions
* `StandUp.sh` can be used on a Ubuntu/Debian and has been tested on Ubuntu 18.04/20.04 and Debian 11 (Bullseye).


In order to run this script you need to be logged in as root, and enter in the commands listed below.
The `$` represents a terminal command prompt; do not actually type in a `$`.

1. Give the root user a password:

   `$ sudo passwd`

2. Switch to the root user:

   `$ su - root`

3. Create the file for the script:

   `$ nano standup.sh`

   - Nano is a text editor that works in a terminal, you need to paste the entire contents of the StandUp.sh into your terminal after running the above command. Then you can type:
      - `control x` (this starts to exit nano)
      - `y`         (this confirms you want to save the file)
      - `return`    (just press enter to confirm you want to save and exit)

4. Make sure the script is executable:

   `$ chmod +x standup.sh`




5. Run the script with the optional arguments like:

      `$ ./standup.sh "BGLTYPE" "UFW_STATUS" "SSH_KEY" "SYS_SSH_IP" "USERPASSWORD" "UACOMMENT"`
   -  The `BGLTYPE` options are  "mainnet", "pruned mainnet", "testnet", "pruned testnet", default is "mainnet".
   - If you supply `UFW_STATUS` to "enabled" it enables the firewall to only allow incoming connections for SSH (optional - if you do not want to enable one add "" as an argument)
   -  If you supply a `SSH_KEY` in the arguments, you will be able to easily access your node via SSH using your rsa pubkey (optional - if you do not want to add one add "" as an argument)
   -  If you add `SYS_SSH_IP`, you host will only accept SSH connections from those IPs (optional - if you do not want to add one add "" as an argument)
   -  The `USERPASSWORD` is used for a user called `standup` (optional - if you do not want to add one add "" as an argument)
   -  Supply `UACOMMENT` if you want to add user agent comment for node (optional - if you do not want to add one add "" as an argument)
   
   If you do not want to add any arguments and run everything as per the defaults simply run:
  `$ ./standup.sh`
  
By default the script sets up a mainnet node. BGL Core is set up as `systemd` service so that it starts automatically after crashes or reboots. 

You should check the *BGL-Standup* logs to ensure that the installation went correctly:

   `$ cat /root/standup.err`
   
   `$ cat /root/standup.log`

