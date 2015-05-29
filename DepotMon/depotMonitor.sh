#!/bin/bash
PATH="/usr/local/bin:$PATH"
eval `/usr/local/bin/config_pkg -sh -a lio`
cd /home/appelte1/T2VanderbiltStorageTools/DepotMon
/usr/local/bin/python reportDepotStatus.py $1
