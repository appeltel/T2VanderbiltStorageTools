#!/bin/bash
###############################################################################
#    _   ___ ___ ___ ___
#   /_\ / __/ __| _ \ __|
#  / _ \ (_| (__|   / _|
# /_/ \_\___\___|_|_\___|
#
# - John G. Mora <john.mora@accre.vanderbilt.edu> - written 5/16/2011
################################################################################

#if [ -z $X509_CADIR ]; then
#echo "No grid environment sourced. Exiting."
#exit 1
#fi

#echo -e "exit status -- 142: timeout, 1: bad, 0: good"
echo

dd if=/dev/zero of=/tmp/testfile.bin.$USER bs=1M count=100 1>/dev/null 2>/dev/null
chmod 777 /tmp/testfile.bin.$USER
alarm() { perl -e 'alarm shift; exec @ARGV' "$@"; }

# add color stuff
reportbad() {
if [ $STATUS -eq 0 ]; then
STATUS="\033[1;32mOK("$STATUS")\033[0;34m"
else
STATUS="\033[1;31m"$STATUS"\033[0;34m"
fi
}

boldwhite="\e[36;1m"
reset="\e[0m"

# todo: add a function to generate a clean file if it doesn't exist, to be called from the functions below

srmp() {
for i in $SRM; do
alarm 30 srm-ping srm://$i.accre.vanderbilt.edu:6288/srm/v2/server 1>/dev/null 2>/dev/null ; STATUS="$?"
echo -e "#  srm-ping srm://$i.accre.vanderbilt.edu:6288/srm/v2/server"
reportbad
echo -e "$i srm-ping exit code: $STATUS"
done
}

gftpls() {
for i in $GFTP; do
alarm 20 uberftp $i.accre.vanderbilt.edu "ls /lio/lfs/store/grid_sanity/dummy1" 1>/dev/null 2>/dev/null ; STATUS="$?"
echo -e "#  uberftp $i.accre.vanderbilt.edu 'ls /lio/lfs/store/grid_sanity/dummy1'"
reportbad
echo -e "$i uberftp ls exit code: $STATUS"
done
}

lcgls() {
for i in $SRM; do
alarm 20 lcg-ls -l -b -D srmv2 srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/dummy1 1>/dev/null 2>/dev/null ; STATUS="$?"
echo -e "#  lcg-ls -l -b -D srmv2 srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/dummy1"
reportbad
echo -e "$i lcg-ls exit code: $STATUS"
done
}


srmls() {
for i in $SRM; do
alarm 20 srm-ls srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/dummy1 1>/dev/null 2>/dev/null ; STATUS="$?"
echo -e "#  srm-ls srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/dummy1"
reportbad
echo -e "$i srm-ls exit code: $STATUS"
done
}

gftpput() {
dd if=/dev/zero of=/tmp/testfile.bin.$USER bs=1M count=100 1>/dev/null 2>/dev/null
for i in $GFTP; do
TMPFILE="$RANDOM"
alarm 20 globus-url-copy file:/tmp/testfile.bin.$USER gsiftp://$i.accre.vanderbilt.edu:2811/lio/lfs/store/grid_sanity/write_tests/testfile.bin.$TMPFILE 1>/dev/null 2>/dev/null ; STATUS="$?"
echo -e "# globus-url-copy file:/tmp/testfile.bin.$USER gsiftp://$i.accre.vanderbilt.edu:2811/lio/lfs/store/grid_sanity/write_tests/testfile.bin."$TMPFILE
reportbad
echo -e "$i globus-url-copy PUT exit code: $STATUS"
done
}

srmrm() {
for i in $SRM; do
echo -e "#  srm-rm srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/write_tests/testfile.bin.$TMPFILE"
alarm 20 srm-rm srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/write_tests/testfile.bin.$TMPFILE 1>/dev/null 2>/dev/null ; STATUS="$?"
reportbad
echo -e "srm-rm $i exit code: $STATUS"
done
}

gftpget() {
for i in $GFTP; do
alarm 20 globus-url-copy gsiftp://$i.accre.vanderbilt.edu:2811/lio/lfs/store/grid_sanity/dummy1 file:/tmp/testfile.bin.$USER 1>/dev/null 2>/dev/null ; STATUS="$?"
echo -e "#  globus-url-copy gsiftp://$i.accre.vanderbilt.edu:2811/lio/lfs/store/grid_sanity/dummy1 file:/tmp/testfile.bin.$USER"
reportbad
echo -e "$i globus-url-copy GET from $i exit code: $STATUS"
done
}

srmls() {
for i in $SRM; do
alarm 120 srm-ls srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/ 1>/dev/null 2>/dev/null ; STATUS="$?"
echo -e "#  srm-ls srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/"
reportbad
echo -e "$i srm-ls exit code: $STATUS"
done
}

lcgcppull() {
for i in $SRM; do
echo -e "#  lcg-cp -v -b -V cms -D srmv2 srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/dummy1 file:////tmp/testfile.bin.$USER.$i"
alarm 20 lcg-cp -v -b -V cms -D srmv2 srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/dummy1 file:////tmp/testfile.bin.$USER.$i 1>/dev/null 2>/dev/null ; STATUS="$?"
reportbad
echo -e "$i lcg-cp FROM $i exit code: $STATUS"
done
}

lcgcp() {
dd if=/dev/zero of=/tmp/testfile.bin.$USER bs=1M count=100 1>/dev/null 2>/dev/null
TMPFILE="$RANDOM"
for i in $SRM; do
echo -e "#  lcg-cp -v -b -V cms -D srmv2 file:////tmp/testfile.bin.$USER srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/write_tests/testfile.bin.$TMPFILE"
alarm 20 lcg-cp -v -b -V cms -D srmv2 file:////tmp/testfile.bin.$USER srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/write_tests/testfile.bin.$RANDOM 1>/dev/null 2>/dev/null ; STATUS="$?"
reportbad
echo -e "$i lcg-cp TO $i exit code: $STATUS"
done
}

srmcp() {
dd if=/dev/zero of=/tmp/testfile.bin.$USER bs=1M count=100 1>/dev/null 2>/dev/null
for i in $SRM; do
TMPFILE="$RANDOM"
echo -e "#  srmcp -srm_protocol_version=2 file:////tmp/testfile.bin.$USER srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/write_tests/testfile.bin.$TMPFILE"
alarm 20 srmcp -srm_protocol_version=2 file:////tmp/testfile.bin.$USER srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/write_tests/testfile.bin.$TMPFILE 1>/dev/null 2>/dev/null ; STATUS="$?"
reportbad
echo -e "srmcp TO $i exit code: $STATUS"
done
}

srmcppull() {
for i in $SRM; do
echo -e "#  srmcp -srm_protocol_version=2 srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/dummy1 file:////tmp/testfile.bin.$USER.$i"
alarm 20 srmcp -srm_protocol_version=2 srm://$i.accre.vanderbilt.edu:6288/srm/v2/server?SFN=/lio/lfs/store/grid_sanity/dummy1 file:////tmp/testfile.bin.$USER.$i 1>/dev/null 2>/dev/null ; STATUS="$?"
reportbad
echo -e "$i srmcp FROM $i exit code: $STATUS"
done
}

getgsi() {
for i in $GFTP; do
#echo -e "#  snmpget -Oq -v 1 -c public $i.vampire UCD-SNMP-MIB::extOutput.1"
GSI="`snmpget -Oq -v 1 -c public $i.vampire UCD-SNMP-MIB::extOutput.1 | cut -d ' ' -f 2`"
echo -e "$i reports $GSI used GridFTP slots"
done
}

bdii() {
#echo -e "#  ldapsearch -h lcg-bdii.cern.ch -p 2170 -x -b Mds-Vo-name=local,o=grid '(&(objectClass=GlueCE)(|(GlueCEAccessControlBaseRule=VO:CMS)(GlueCEAccessControlBaseRule=VOMS:/CMS/Role=production)))' GlueSiteUniqueID -LLL | perl -p -00 -e 's/\n //g;'|grep -i 'Mds-Vo-name=VANDERBILT,'"
OUT="`ldapsearch -h lcg-bdii.cern.ch -p 2170 -x -b Mds-Vo-name=local,o=grid '(&(objectClass=GlueCE)(|(GlueCEAccessControlBaseRule=VO:CMS)(GlueCEAccessControlBaseRule=VOMS:/CMS/Role=production)))' GlueSiteUniqueID -LLL | perl -p -00 -e 's/\n //g;'|grep -i 'Mds-Vo-name=VANDERBILT,' | wc -l`"
echo -e "LCG BDII reports ${OUT} of 4 entries - http://bit.ly/iFXRyN"
echo

#echo -e "#  ldapsearch -h is.grid.iu.edu -p 2170 -x -b Mds-Vo-name=local,o=grid '(&(objectClass=GlueCE)(|(GlueCEAccessControlBaseRule=VO:CMS)(GlueCEAccessControlBaseRule=VOMS:/CMS/Role=production)))' GlueSiteUniqueID -LLL | perl -p -00 -e 's/\n //g;'|grep -i 'Mds-Vo-name=VANDERBILT,'"
OUT="`ldapsearch -h is.grid.iu.edu -p 2170 -x -b Mds-Vo-name=local,o=grid '(&(objectClass=GlueCE)(|(GlueCEAccessControlBaseRule=VO:CMS)(GlueCEAccessControlBaseRule=VOMS:/CMS/Role=production)))' GlueSiteUniqueID -LLL | perl -p -00 -e 's/\n //g;'|grep -i 'Mds-Vo-name=VANDERBILT,' | wc -l`"
echo -e "OSG BDII reports $OUT of 4 entries (this should match CERN count)"
echo
}

# /usr/lib64/nagios/plugins/doalarm 1 /usr/scheduler/torque/bin/qstat.bin -Q ; echo $?
qstat() {
echo "Checking vmpsched first:"
alarm 10 /usr/scheduler/torque/bin/qstat.bin -Q -f 1>/dev/null 2>/dev/null; STATUS="$?"
echo -e "# /usr/scheduler/torque/bin/qstat.bin -Q -f"
reportbad
echo -e "qstat exit code: $STATUS"
}

cacheqstat() {
if [ ! -f /tmp/qstat.cache ]; then
echo "Not running on vmps65, please run this script from vmps65"
exit 0
fi
LASTCAC="`date -r /tmp/qstat.cache`"
echo "Cache last updated: $LASTCAC"
echo
}

# Removing ce2 per Eric A. - klb, 9/4/2014
#CE="ce1 ce2"
CE="ce1"

runchecks() {
date
echo "============================= Checking for possible job scheduler issues ============================="
qstat
#cacheqstat
#submitjobs $CE
echo
echo "=============== Checking GridFTP slots via loadbalancer ==============="
getgsi $GFTP
echo
echo "============================= Checking SEs with GridFTP commands  ============================="
gftpls $GFTP
gftpput $GFTP
gftpget $GFTP
echo
echo "============================= Checking for Bestman/SRM server on $SRM ============================="
srmp $SRM
echo
echo "============================= Checking $SRM for Bestman-specific file-transfer issues ============================="
lcgls $SRM
lcgcp $SRM
lcgcppull $SRM
}

prod() {
SRM="se1"
#GFTP="`ssh ${USER}@se1 grep -v \"^#\" /opt/osg/bestman.OLD/accre-plugin/gsiftp.servers.txt | awk '{ print $1 }'`"
#GFTP="`wget --user=vandycms --password=vandycms --no-check-certificate https://se1.accre.vanderbilt.edu:8080/se-status/gsiftp.servers.txt -q -O - | grep -v \"^#\" | awk '{ print $1 }'`"
#GFTP="`echo $GFTP | sed 's/.accre.vanderbilt.edu//g' | sed 's+gsiftp://++g'`"
GFTP="se4 se6 se7 se8 se9 se11"
runchecks
}

prod
echo
echo "============================= Checking for BDII visibility ============================="
bdii
