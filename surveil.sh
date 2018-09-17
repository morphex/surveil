#!/bin/bash
#
# Shell script to run surveil.py from Cron
#
# For example, enter
#
# @reboot /root/surveil/surveil.sh email-address
#
PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin:/usr/local/sbin
export PATH

cd /root/surveil
python3 ./surveil.py $1 &>>surveil.log



