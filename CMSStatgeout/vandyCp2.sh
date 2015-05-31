#!/bin/bash

# Copy script for copying from a local file to a destination file
# Return 0 for success 
#
# Usage vandyCp.sh [-v] source-file dest-file
#

debug() { echo $*; }
nodebug() { true; }

#Number of retries
RETRIES="1 2 3"
#Sleep command
SLEEP="sleep 1"


fn_lio_cp_retry() 
{
  local retval
  for retry in ${RETRIES}; do
     echo -e "\n$(date) [retry=${retry}] $*"      
     eval $*  #Use eval to get quoted strings to expand properly
     retval=$?
     #retval=1
     #echo "forced fail=${retval}"
     if (( (retval == 0) || (retval == 1) )); then
        return ${retval}
     fi

     ${SLEEP}
  done

  return ${retval}
}

fn_lio_retry() 
{
  local retval
  for retry in ${RETRIES}; do
     echo -e "\n$(date) [retry=${retry}] $*"      
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

DEBUG=nodebug
$DEBUG "Debug 0: Starting Script"

LOG_FILE="/scratch/cms-stageout-logs/vandyCp/$(date +%Y)/$(date +%m)/$(date +%d)/$(hostname)/${SLURM_JOB_ID:-NO_SLURM_ID}-$(date +%s).log"
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
SRC_FILE=$1
DST_FILE=$2

echo -e "\n\n+++++++++++++++++++++\n$(date) Command called:\n   '$0 $*'\n" \
"User: $(id -u -n)\nHost: $(hostname)\nSLURM_Job: ${SLURM_JOB_ID:-NO_SLURM_ID}" 

$DEBUG "Debug 0: Check if target is a directory, build correct destination path, check that target exists and destination does not"

# if the target is a directory or ends in /, we want to change the destination to
# be a concatenation of the target and the relative source filename, 
# see http://pubs.opengroup.org/onlinepubs/9699919799/utilities/cp.html

REL_SRC_FILE=${SRC_FILE##*/} 

if [ $(echo ${DST_FILE} | grep -c '/$') -eq 1 ] ; then
  DST_FILE=${DST_FILE}${REL_SRC_FILE}
else
  REL_DST_FILE=${DST_FILE##*/} 
  DST_IS_DIR=$(fn_lio_retry lio_ls ${DST_FILE} | grep -v retry | grep ${REL_DST_FILE} | grep -c '^d')
  if [ ${DST_IS_DIR} -eq 1 ]; then
    DST_FILE=${DST_FILE}/${REL_SRC_FILE}
  fi
fi

DST_EXISTS=$(fn_lio_retry lio_ls ${DST_FILE} | grep -v retry | grep -c ${REL_DST_FILE} )
if [ ${DST_EXISTS} -ge 1 ]; then
  echo "Error: Destination file ${DST_FILE} already exists. Remove existing file with \"vandyRm.sh\" and try again"
  exit 17
fi

if [ ! -f ${SRC_FILE} ]; then 
  echo "Error: Source file ${SRC_FILE} does not exist or is not a regular file."
  exit 2 
fi 

$DEBUG "Debug 1: Get DN from the cert"

for v in $X509_USER_PROXY  /tmp/x509_u`/usr/bin/id -u`; do 
    DN=`voms-proxy-info -file $v -identity | sed 's,\(/CN=\(proxy\|[0-9]\{10\}\)\)*$,,'`
    break
done
if [ -z "$DN" ]; then
    DN=`/usr/bin/openssl x509 -noout -in $X509_USER_CERT -subject 2>/dev/null | /usr/bin/cut -d' ' -f2-`
fi

$DEBUG "Debug 2: Test that the DN is set"

if [ -z "$DN" ]; then
    echo "Error: no cert info"
    echo -e "Error: no cert info\n---------------------" 
    if [ "$3" == "verbose" ]; then
      cat $LOG_FILE 1>&3
    fi
    exit -1;
fi

$DEBUG "Debug 3: Check that file path is valid for CMS data"

# check if file is a LFN, and if so convert to PFN
if [[ ${DST_FILE:0:6} == /store ]]; then
     DST_FILE=/cms${DST_FILE}
fi

# if people are adding /lio/lfs still for some reason
# then strip it out
if [[ ${DST_FILE:0:8} == /lio/lfs ]]; then
     DST_FILE=${DST_FILE:8}
fi

# if the PFN is not /cms/store, don't allow access
if [[ ${DST_FILE:0:10} != /cms/store ]]; then
     echo "Illegal destination file name, only transfer to /cms/store permitted"
     if [ "$3" == "verbose" ]; then
       cat $LOG_FILE 1>&3
     fi
     exit 13
fi

$DEBUG "Debug 4: Setup LIO utilities"

setpkgs -a lio

$DEBUG "Debug 5: Upload file to LStore"

if [[ ! -d $(dirname $DST_FILE) ]]; then
    mkdir -p $(dirname $DST_FILE)
fi
fn_lio_cp_retry lio_cp -d 1 ${SRC_FILE} @:${DST_FILE} 2>&1
retval=$?
echo "$(date) Return code: ${retval}"
 
# Tests if the upload was successful
# and attempts to repair soft errors
if [ $retval -ne 0 ] ; then
    echo "Error: non-zero return code from upload command\n---------------------" 
    # lio_cp should remove any file with an error on write
    # but in the case of a segmentation fault it will
    # leave a zero byte file. This must be removed or
    # fallback to srmv2 transfers will fail with
    # error "60303" file already exists
    if [ $retval == 139 ]; then
       lio_rm @:${DST_FILE}  
    fi
    # lio_cp error 1 sometimes represents a "soft" or recoverable 
    # error. In this case we attempt a full repair, and change the 
    # return value to that of the repair
    if [ $retval == 1 ]; then
       echo "FILE_REPAIR: Attempting repair of file..."
       fn_lio_retry lio_inspect -i 20 -r -f -werr -x -b 40mi -o inspect_full_repair @:${DST_FILE} 2>&1
       retval=$?
    fi
fi

# quit if the file was unrecoverable
if [ $retval -ne 0 ] ; then
    if [ "$3" == "verbose" ]; then
      cat $LOG_FILE 1>&3
    fi
    exit $retval
fi

$DEBUG "Debug 6: Set the owner DN"

# Sets the DN for the file

#fn_lio_retry lio_setattr -d 20 -log /tmp/log.out -i 20 -delim : -as \"user.cms_user_x509:${DN}\" ${DST_FILE} 2>&1
fn_lio_retry lio_setattr -i 20 -delim : -as \"user.cms_user_x509:${DN}\" ${DST_FILE} 2>&1
attrretval=$?
echo "$(date) Return code: ${attrretval}" 

CHECKSUM=$(adler32 ${SRC_FILE})
echo "$(date) Checksum: ${CHECKSUM}"
#fn_lio_retry lio_setattr  -d 20 -log /tmp/log.out -i 20 -delim : -as \"user.cms_user_adler32:${CHECKSUM}\" ${DST_FILE} 2>&1
fn_lio_retry lio_setattr -i 20 -delim : -as \"user.cms_user_adler32:${CHECKSUM}\" ${DST_FILE} 2>&1
echo "$(date) Return code: $?" 

$DEBUG "Debug 7: Check File Integrity"

echo -e "\n File Integrity Check:"
fn_lio_retry lio_inspect -i 20 -r -f -werr -x -b 40mi -o inspect_quick_repair @:${DST_FILE} 2>&1
if [ $? -ne 0 ]; then
   echo -e "\nFILE IS DAMAGED!!!"
   lio_rm @:${DST_FILE}   #rm the file on failure
   if [ "$3" == "verbose" ]; then
     cat $LOG_FILE 1>&3
   fi
   exit 100
fi

echo -e "$(date) Exiting $0\n---------------------" 

$DEBUG "Debug 8: Exit"

if [ "$3" == "verbose" ]; then
  cat $LOG_FILE 1>&3
fi 

exit $retval
