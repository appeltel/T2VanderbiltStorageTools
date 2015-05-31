#!/bin/sh

# Remove script.
# Return 0 for success and -1 for failure.
#
# Usage vandyRm.sh source-file dest-file
#

debug() { echo $*; }
nodebug() { true; }

DEBUG=nodebug

#Number of retries
RETRIES="1 2 3"
#Sleep command
SLEEP="sleep 1"

fn_lio_retry() 
{
  local retval
  for retry in ${RETRIES}; do
     echo -e "$(date) [retry=${retry}] $*"      
     eval $*  #Use eval to get quoted strings to expand properly
     retval=$?
     #retval=1
     #echo "forced fail=${retval}"
     if (( (retval == 0) )); then
        return ${retval}
     fi

     ${SLEEP}
  done

  return ${retval}
}

LOG_FILE="/scratch/cms-stageout-logs/vandyRm/$(date +%Y)/$(date +%m)/$(date +%d)/$(hostname)/${SLURM_JOB_ID:-NO_SLURM_ID}-$(date +%s).log"
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
export PATH=/usr/local/bin:$PATH
. /etc/profile.d/setpkgs.sh

# Builds the argument list
DST_FILE=$1

$DEBUG "Debug 1: Get DN from the Cert"

# Gets the DN from the cert
for v in $X509_USER_PROXY  /tmp/x509_u`/usr/bin/id -u`; do 
    DN=`voms-proxy-info -file $v -identity | sed 's,\(/CN=\(proxy\|[0-9]\{10\}\)\)*$,,'`
    break
done
if [ -z "$DN" ]; then
    DN=`/usr/bin/openssl x509 -noout -in $X509_USER_CERT -subject 2>/dev/null | /usr/bin/cut -d' ' -f2-`
fi

$DEBUG "Debug 2: Check that the DN was set"

# Tests that the DN was set
if [ -z "$DN" ]; then
    echo "Error: no cert info"
    echo -e "Error: no cert info\n---------------------" 
    if [ "$2" == "verbose" ]; then
      cat $LOG_FILE 1>&3
    fi
    exit -1;
fi

$DEBUG "Debug 3: Check for valid CMS path (/cms/store/...)"

#=== new - check if file is a LFN, and if so convert to PFN
if [[ ${DST_FILE:0:6} == /store ]]; then
     DST_FILE=/cms${DST_FILE}
fi

#=== new - if people are adding /lio/lfs still for some reason
#          then strip it out
if [[ ${DST_FILE:0:8} == /lio/lfs ]]; then
     DST_FILE=${DST_FILE:8}
fi

#=== new - if the PFN is not /cms/store, don't allow access
if [[ ${DST_FILE:0:10} != /cms/store ]]; then
     echo "Illegal destination file name, only transfer to /cms/store permitted"
     if [ "$2" == "verbose" ]; then
       cat $LOG_FILE 1>&3
     fi
     exit 13
fi

$DEBUG "Debug 4: Set up LIO tools"

setpkgs -a lio

$DEBUG "Debug 5: Check for file existence"

DST_FILE_NAME=${DST_FILE##*/}
fn_lio_retry lio_ls @:${DST_FILE} 2> /dev/null | /usr/bin/tail -n 1 | /bin/grep "${DST_FILE_NAME}"
STAT_CHECK_RESULT=$?
if [ $STAT_CHECK_RESULT -ne 0 ]; then
  echo "File is already gone"
  if [ "$2" == "verbose" ]; then
    cat $LOG_FILE 1>&3
  fi
  exit 2
fi

$DEBUG "Debug 6: Get the DN for the file"

FILE_DN=$(fn_lio_retry lio_getattr -al user.cms_user_x509 -new_obj \"\" -end_obj \"\" -attr_fmt \"%s#%s\" ${DST_FILE} | grep -v retry | grep x509 | sed 's/^user.cms_user_x509#//')
retval=$?
# Tests if the attribute call was successful
if [ $retval -ne 0 ] ; then
  echo "Unable to access the cms_user_x509 attribute for ${DST_FILE}"
  if [ "$2" == "verbose" ]; then
    cat $LOG_FILE 1>&3
  fi
  exit $retval
fi

$DEBUG "Debug 7: Check that the DNs match"

if [[ "x$FILE_DN" != "x$DN"  ]]; then
  echo "Error user DN doesn't match file DN"
  echo "FileDN: $FILE_DN"
  echo "UserDN: $DN"
  if [ "$2" == "verbose" ]; then
    cat $LOG_FILE 1>&3
  fi
  exit -1;
fi

$DEBUG "Debug 8: remove file from LStore"


REMOVE_CMD="lio_rm @:${DST_FILE}"
echo -e "\n$(date) REMOVE_CMD: '${REMOVE_CMD}'" 
$REMOVE_CMD  2>&1
REMOVE_CMD_STATUS=$?

# Returns the exit code for the lstore command

if [ "$2" == "verbose" ]; then
  cat $LOG_FILE 1>&3
fi

exit $REMOVE_CMD_STATUS
