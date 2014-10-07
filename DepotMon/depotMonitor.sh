#!/bin/bash
PATH="/usr/local/bin:$PATH"
eval `/usr/local/bin/config_pkg -sh -a java`
eval `/usr/local/bin/config_pkg -sh -a lio`
cd /home/appelte1/DepotMon
/usr/local/lio/bin/lio_rs -s | grep -e "^[0-9]" > /home/appelte1/DepotMon/foo
/usr/local/bin/python reportDepotStatus.py
rm /home/appelte1/DepotMon/foo
