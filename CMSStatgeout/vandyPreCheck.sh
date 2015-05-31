#!/bin/bash

# Print the status of LFS to a log file.  Will be tweaking the function of this script,
# eventually it will roll LFS if LFS is missing

debug() { echo $*; }
nodebug() { true; }

DEBUG=nodebug
$DEBUG "Debug 0"

LOG_FILE="/scratch/cms-stageout-logs/vandyPreCheck/$(date +%Y)/$(date +%m)/$(date +%d)/$(hostname)/${PBS_JOBID:-NO_PBS_ID}-$(date +%s).log"
( 
umask 000
mkdir -p $(dirname $LOG_FILE)
)

touch $LOG_FILE
chmod a+r $LOG_FILE

# If we're running non-interactively, log to a log file
if [ ! -t 0 ]; then
    exec 3>&1 4>&2 >${LOG_FILE} 2>&1
    DEBUG=debug
fi


if [ -d /lio/lfs/cms/store/user ];
then
    echo -e "\n$(date) LFS is present"  >${LOG_FILE}
#    echo -e "\n$(date) LFS is present"  
    retval=0
else
    echo -e "\n$(date) LFS is NOT THERE" >${LOG_FILE}
#    echo -e "\n$(date) LFS is NOT THERE" 
    retval=1
fi

exit $retval
