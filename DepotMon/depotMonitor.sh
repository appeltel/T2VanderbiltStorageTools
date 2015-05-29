#!/bin/bash
PATH="/usr/local/bin:$PATH"
eval `/usr/local/bin/config_pkg -sh -a lio`
/usr/local/bin/python reportDepotStatus.py $1
