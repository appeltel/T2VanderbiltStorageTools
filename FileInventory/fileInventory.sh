#!/bin/bash

# Setup environment and working dir, initialize state
PATH="/usr/local/bin:$PATH"
eval `/usr/local/bin/config_pkg -sh -a lio`
if [ -f fileInventory.state ]; then 
  source fileInventory.state
else
  COUNTER=0
fi 

# Perform Inventory
/usr/local/lio/bin/lio_du -h -s @:/cms/store/ > store.inv.$COUNTER
STORE_RESULT=$?
echo "$(date) - performed inventory of /cms/store/ with exit code $STORE_RESULT" >> fileInventory.log
# retry on 2 line output or error code twice
if [[ $( wc -l < store.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/ > store.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 1: /cms/store/ with exit code $STORE_RESULT" >> fileInventory.log
fi
if [[ $( wc -l < store.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/ > store.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 2: /cms/store/ with exit code $STORE_RESULT" >> fileInventory.log
fi

# Seems to be some lio_du bug right now (5/31/2015) that 
# makes /cms/store/user/ report nothing, but /cms/store/user/*
# works.

/usr/local/lio/bin/lio_du -h -s @:/cms/store/user/* > store.user.inv.$COUNTER
USER_RESULT=$?
echo "$(date) - performed inventory of /cms/store/user/ with exit code $USER_RESULT" >> fileInventory.log
# retry on 2 line output or error code twice
if [[ $( wc -l < store.user.inv.$COUNTER ) -lt 3 || $USER_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/user/* > store.user.inv.$COUNTER
  USER_RESULT=$?
  echo "$(date) - Retry 1: /cms/store/user/ with exit code $USER_RESULT" >> fileInventory.log
fi
if [[ $( wc -l < store.user.inv.$COUNTER ) -lt 3 || $USER_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/user/* > store.user.inv.$COUNTER
  USER_RESULT=$?
  echo "$(date) - Retry 2: /cms/store/user/ with exit code $USER_RESULT" >> fileInventory.log
fi

# Report to webpage
/usr/local/bin/python reportFileInventory.py $COUNTER $1

#update and record state and exit
COUNTER=$(( $COUNTER + 1 ))
echo "COUNTER=$COUNTER" > fileInventory.state
