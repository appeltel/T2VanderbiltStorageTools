#!/bin/bash

# Setup environment and working dir, initialize state
PATH="/usr/local/bin:$PATH"
FI_HOME=/home/appelte1/T2VanderbiltStorageTools/FileInventory/
cd $FI_HOME
eval `/usr/local/bin/config_pkg -sh -a lio`
if [ -f $FI_HOME/fileInventory.state ]; then 
  source $FI_HOME/fileInventory.state
else
  COUNTER=0
fi 

# Perform Inventory
/usr/local/lio/bin/lio_du -h -s @:/cms/store/ > $FI_HOME/store.inv.$COUNTER
/usr/local/lio/bin/lio_du -h -s @:/cms/store/user/ > $FI_HOME/store.user.inv.$COUNTER
# Report to webpage
/usr/local/bin/python reportFileInventory.py $COUNTER

#update and record state and exit
COUNTER=$(( $COUNTER + 1 ))
echo "COUNTER=$COUNTER" > $FI_HOME/fileInventory.state
