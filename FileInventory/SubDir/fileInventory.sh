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
# hidata
/usr/local/lio/bin/lio_du -h -s @:/cms/store/hidata/ > store.hidata.inv.$COUNTER
STORE_RESULT=$?
echo "$(date) - performed inventory of /cms/store/hidata/ with exit code $STORE_RESULT" >> fileInventory.log
# retry on 2 line output or error code twice
if [[ $( wc -l < store.hidata.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/hidata/ > store.hidata.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 1: /cms/store/hidata/ with exit code $STORE_RESULT" >> fileInventory.log
fi
if [[ $( wc -l < store.hidata.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/hidata/ > store.hidata.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 2: /cms/store/hidata/ with exit code $STORE_RESULT" >> fileInventory.log
fi

# Seems to be some lio_du bug right now (5/31/2015) that makes 
#/cms/store/user/ report nothing, but /cms/store/user/* works.
# user
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

# group
/usr/local/lio/bin/lio_du -h -s @:/cms/store/group/ > store.group.inv.$COUNTER
STORE_RESULT=$?
echo "$(date) - performed inventory of /cms/store/group/ with exit code $STORE_RESULT" >> fileInventory.log
# retry on 2 line output or error code twice
if [[ $( wc -l < store.group.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/group/ > store.group.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 1: /cms/store/group/ with exit code $STORE_RESULT" >> fileInventory.log
fi
if [[ $( wc -l < store.group.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/group/ > store.group.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 2: /cms/store/group/ with exit code $STORE_RESULT" >> fileInventory.log
fi

# data
/usr/local/lio/bin/lio_du -h -s @:/cms/store/data/ > store.data.inv.$COUNTER
STORE_RESULT=$?
echo "$(date) - performed inventory of /cms/store/data/ with exit code $STORE_RESULT" >> fileInventory.log
# retry on 2 line output or error code twice
if [[ $( wc -l < store.data.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/data/ > store.data.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 1: /cms/store/data/ with exit code $STORE_RESULT" >> fileInventory.log
fi
if [[ $( wc -l < store.data.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/data/ > store.data.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 2: /cms/store/data/ with exit code $STORE_RESULT" >> fileInventory.log
fi

# mc
/usr/local/lio/bin/lio_du -h -s @:/cms/store/mc/ > store.mc.inv.$COUNTER
STORE_RESULT=$?
echo "$(date) - performed inventory of /cms/store/mc/ with exit code $STORE_RESULT" >> fileInventory.log
# retry on 2 line output or error code twice
if [[ $( wc -l < store.mc.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/mc/ > store.mc.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 1: /cms/store/mc/ with exit code $STORE_RESULT" >> fileInventory.log
fi
if [[ $( wc -l < store.mc.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/mc/ > store.mc.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 2: /cms/store/mc/ with exit code $STORE_RESULT" >> fileInventory.log
fi

# himc
/usr/local/lio/bin/lio_du -h -s @:/cms/store/himc/ > store.himc.inv.$COUNTER
STORE_RESULT=$?
echo "$(date) - performed inventory of /cms/store/himc/ with exit code $STORE_RESULT" >> fileInventory.log
# retry on 2 line output or error code twice
if [[ $( wc -l < store.himc.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/himc/ > store.himc.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 1: /cms/store/himc/ with exit code $STORE_RESULT" >> fileInventory.log
fi
if [[ $( wc -l < store.himc.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/himc/ > store.himc.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 2: /cms/store/himc/ with exit code $STORE_RESULT" >> fileInventory.log
fi

# unmerged
/usr/local/lio/bin/lio_du -h -s @:/cms/store/unmerged/ > store.unmerged.inv.$COUNTER
STORE_RESULT=$?
echo "$(date) - performed inventory of /cms/store/unmerged/ with exit code $STORE_RESULT" >> fileInventory.log
# retry on 2 line output or error code twice
if [[ $( wc -l < store.unmerged.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/unmerged/ > store.unmerged.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 1: /cms/store/unmerged/ with exit code $STORE_RESULT" >> fileInventory.log
fi
if [[ $( wc -l < store.unmerged.inv.$COUNTER ) -lt 3 || $STORE_RESULT -ne 0 ]]; then
  sleep 300
  /usr/local/lio/bin/lio_du -h -s @:/cms/store/unmerged/ > store.unmerged.inv.$COUNTER
  STORE_RESULT=$?
  echo "$(date) - Retry 2: /cms/store/unmerged/ with exit code $STORE_RESULT" >> fileInventory.log
fi


# produce store.inv.XXX
sed -n '1,2p' ./store.user.inv.$COUNTER > store.inv.$COUNTER
sed '$!d' ./store.user.inv.$COUNTER >> store.inv.$COUNTER
sed -i 's/TOTAL/\/cms\/store\/user\//g' store.inv.$COUNTER >> store.inv.$COUNTER
sed '$!d' ./store.group.inv.$COUNTER >> store.inv.$COUNTER
sed -i 's/TOTAL/\/cms\/store\/group\//g' store.inv.$COUNTER >> store.inv.$COUNTER
sed '$!d' ./store.hidata.inv.$COUNTER >> store.inv.$COUNTER
sed -i 's/TOTAL/\/cms\/store\/hidata\//g' store.inv.$COUNTER >> store.inv.$COUNTER
sed '$!d' ./store.data.inv.$COUNTER >> store.inv.$COUNTER
sed -i 's/TOTAL/\/cms\/store\/data\//g' store.inv.$COUNTER >> store.inv.$COUNTER
sed '$!d' ./store.mc.inv.$COUNTER >> store.inv.$COUNTER
sed -i 's/TOTAL/\/cms\/store\/mc\//g' store.inv.$COUNTER >> store.inv.$COUNTER
sed '$!d' ./store.himc.inv.$COUNTER >> store.inv.$COUNTER
sed -i 's/TOTAL/\/cms\/store\/himc\//g' store.inv.$COUNTER >> store.inv.$COUNTER
sed '$!d' ./store.unmerged.inv.$COUNTER >> store.inv.$COUNTER
sed -i 's/TOTAL/\/cms\/store\/unmerged\//g' store.inv.$COUNTER >> store.inv.$COUNTER
sed -n '2p' ./store.user.inv.$COUNTER >> store.inv.$COUNTER
# produce total size
declare -a vas
vas[0]=$( sed '$!d' ./store.user.inv.$COUNTER | awk '{print $1;}' )
vas[1]=$( sed '$!d' ./store.group.inv.$COUNTER | awk '{print $1;}' )
vas[2]=$( sed '$!d' ./store.hidata.inv.$COUNTER | awk '{print $1;}' )
vas[3]=$( sed '$!d' ./store.data.inv.$COUNTER | awk '{print $1;}' )
vas[4]=$( sed '$!d' ./store.mc.inv.$COUNTER | awk '{print $1;}' )
vas[5]=$( sed '$!d' ./store.himc.inv.$COUNTER | awk '{print $1;}' )
vas[6]=$( sed '$!d' ./store.unmerged.inv.$COUNTER | awk '{print $1;}' )
sizeAll=0
tmps=0
for it in ${!vas[*]}
do
  var=${vas[$it]}
  if [ "${var: -1}" == "K" ]; then
    tmps=$(bc <<<"${var: 0:(${#var}-1)}*0.001*0.001*0.001")
    sizeAll="${sizeAll} + ${tmps}"
  fi
  if [ "${var: -1}" == "M" ]; then
    tmps=$(bc <<<"${var: 0:(${#var}-1)}*0.001*0.001")
    sizeAll="${sizeAll} + ${tmps}"
  fi
  if [ "${var: -1}" == "G" ]; then
    tmps=$(bc <<<"${var: 0:(${#var}-1)}*0.001")
    sizeAll="${sizeAll} + ${tmps}"
  fi
  if [ "${var: -1}" == "T" ]; then
    tmps=$(bc <<<"${var: 0:(${#var}-1)}*1.0")
    sizeAll="${sizeAll} + ${tmps}"
  fi
  if [ "${var: -1}" == "P" ]; then
    tmps=$(bc <<<"${var: 0:(${#var}-1)}*1000")
    sizeAll="${sizeAll} + ${tmps}"
  fi
done
totalSize="$(echo "$sizeAll" | bc -l)"
# produce total file count
declare -a vac
vac[0]=$( sed '$!d' ./store.user.inv.$COUNTER | awk '{print $2;}' )
vac[1]=$( sed '$!d' ./store.group.inv.$COUNTER | awk '{print $2;}' )
vac[2]=$( sed '$!d' ./store.hidata.inv.$COUNTER | awk '{print $2;}' )
vac[3]=$( sed '$!d' ./store.data.inv.$COUNTER | awk '{print $2;}' )
vac[4]=$( sed '$!d' ./store.mc.inv.$COUNTER | awk '{print $2;}' )
vac[5]=$( sed '$!d' ./store.himc.inv.$COUNTER | awk '{print $2;}' )
vac[6]=$( sed '$!d' ./store.unmerged.inv.$COUNTER | awk '{print $2;}' )
countAll=0
for ic in ${!vac[*]}
do
  varc=${vac[$ic]}
  countAll="${countAll} + ${varc}"
done
totalCount="$(echo "$countAll" | bc -l)"
printf "%9sT  %10d  TOTAL\n" "$totalSize" "$totalCount" >> store.inv.$COUNTER


# Report to webpage
/usr/local/bin/python reportFileInventory.py $COUNTER $1

#update and record state and exit
COUNTER=$(( $COUNTER + 1 ))
echo "COUNTER=$COUNTER" > fileInventory.state
