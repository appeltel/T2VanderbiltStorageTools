T2VanderbiltStorageTools
========================

This repository contains a few tools related to 
data storage at the Vanderbilt T2, and a sample 
crontab entry for running the tools automatically.

To administer these tools, just change the lines
in the sample crontab to reflect the appropriate 
directories and add the lines to your crontab.

### CMS Stageout Scripts

The CMS stageout scripts are called from WMAgent or 
CRAB when a job running at T2_US_Vanderbilt needs to 
stage out a file to the LSTore system at T2_US_Vanderbilt.
These scripts call the native LIO tools, perform 
retries as necessary, and log the behavior. 
The use of this system prevents having to transfer files
through gridftp which are already in temporary storage
at Vanderbilt worker nodes.

The stageout scripts produce a lot of logs in 
`/scratch/cms-stageout-logs/` and old logs need to be 
cleaned out periodically. The crontab lines supplied in the
`crontab.entry` file of this script perform this cleaning.

The production scripts are in `/usr/local/cms-stageout/`
and you must be a member of the `cms-admin` group to modify them.

The procedure below should be used to modify the production 
scripts, using `vandyCp2.sh` as an example:

1. Put your new version in `/usr/local/cms-stageout/vandyCpDev.sh`
make sure that the group of the file is `cms-admin`.

2. Make a copy of the old version for backup in case there is a problem.

3. Start an [AutoCMS](https://github.com/appeltel/AutoCMS) instance 
and configure it to run the `skim_test` every 10 minutes using the 
`vandyCpDev.sh` version of the script. Make sure that there are no 
problems for ~24 hours.

4. Copy the new script to the production version using 
`mv vandyCpDev.sh vandyCp2.sh`, rather than deleting the old version. 
This will prevent any errors from jobs currently using the script.


### Depot Monitor

The depot monitor simply runs through cron every 
15 minutes, and parses the output of 
`lio_rs` to create a web page that shows the overall
status and disk usage of each depot, and the number 
of drives that are currently up.

The color scheme assigned to indicate the health 
of each depot based on the number of drives that are 
UP was decided arbitrarily, with healthy depots in 
green and depots with many failed drives in red.

### File Inventory

The file inventory monitor walks the LStore filesystem
each evening (as configured by cron) using `lio_du`, and 
prints the summary of usage for the `/cms/store` and 
`/cms/store/user` directories to json formatted log files.
If `lio_du` fails it will retry a few times.
These log files are read by a python script that constructs 
a web page to show the current status and changes over previous 
days or weeks.

The json log files are never deleted and are placed in the
same location as the web page.
