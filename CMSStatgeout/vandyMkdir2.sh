#!/bin/sh

# Mkdir script for creating a directory
# Return 0 for success and -1 for failure.
#
# Usage vandyMkdir.sh path
#

LOG_FILE="/scratch/cms-stageout-logs/vandyMkdir/$(date +%Y)/$(date +%m)/$(date +%d)/$(hostname)/${PBS_JOBID:-NO_PBS_ID}-$(date +%s).log"
( 
    umask 000
    mkdir -p $(dirname $LOG_FILE)
)

INTEGRITY_CHECK=/usr/local/lstore-client/bin/lst-integrity-check
export LSTORE_PROPS=/usr/local/lstore-client/config/properties.cms

touch $LOG_FILE
chmod a+r $LOG_FILE

# If we're running non-interactively, log to a log file
if [ ! -t 0 ]; then
    exec 3>&1 4>&2 >${LOG_FILE} 2>&1
    DEBUG=debug
fi
export PATH=/usr/local/bin:$PATH
. /etc/profile.d/setpkgs.sh
setpkgs -a lstore-client

# Builds the argument list
RAWPATH=$1

# Brings in the configuration file
#source /Users/brumgard/Documents/workspace/VandyStageOut/src/scripts/vandy.cfg
source /usr/local/cms-stageout/vandy.cfg

# check if bound for BFS or LFS
if [[ ${RAWPATH:0:4} == /cms ]]; then
    RAWPATH=/lio/lfs/${RAWPATH}
fi

DST_PREFIX=${RAWPATH:0:8}


if [[ "$DST_PREFIX" == /lio/lfs ]]; then
  mkdir -p $RAWPATH
  exit $?
else
  mkdir -p /lio/lfs/cms/${RAWPATH}
  # Gets the lstore path
  LSTORE_PATH=/`echo $RAWPATH | sed 's/store/\n/' | tail -n 1`

  # Makes the directory on lstore
  ${LSTCP} --debug-level 0 --mkdir --recursive ${LSTORE_HOST}:${LSTORE_PATH}

  # Returns the exit code for the lstore command
  exit $?
fi
