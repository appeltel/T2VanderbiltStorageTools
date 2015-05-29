"""Generate a tabular html page displaying depot status.

Usage: python reportdepotstatus.py outputfile
"""

import sys
import re
import datetime
import subprocess


class Depot(object):
    """Information about a specific depot."""

    def __init__(self):
        self.freespace = 0
        self.totalspace = 0
        self.updrives = 0
        self.totaldrives = 0
        self.ignore = False


def get_depot_log():
    """Return result of lio_rs -s as a list of lines."""
    proc = subprocess.Popen(['/usr/local/lio/bin/lio_rs','-s'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=False)
    (out, err) = proc.communicate()
    return out.splitlines()


def iec_string_to_bytes(string):
    """Strip off IEC suffix and report appropriate number of bytes."""
    val = float(re.findall(r'\d+\.*\d*', string)[0])
    if re.match(r'.*ki',string): val *= 1024 
    if re.match(r'.*Mi',string): val *= 1024**2
    if re.match(r'.*Gi',string): val *= 1024**3
    if re.match(r'.*Ti',string): val *= 1024**4
    if re.match(r'.*k[^i]',string) or re.match(r'.*k$',string): val *= 1000 
    if re.match(r'.*M[^i]',string) or re.match(r'.*M$',string): val *= 1000**2
    if re.match(r'.*G[^i]',string) or re.match(r'.*G$',string): val *= 1000**3
    if re.match(r'.*T[^i]',string) or re.match(r'.*T$',string): val *= 1000**4
    return val


def parse_depot_log(log):
    """Parse a lio depot log, return a dictionary of Depots."""
    depots = {}
    for entry in log:
        # skip lines that don't begin in digits - these are headers, etc...
        if not re.match(r'^\d+',entry):
            continue
        drive = entry.split()
        d = drive[2]

        if not d in depots:
          depots[d] = Depot()

        depots[d].freespace += iec_string_to_bytes(drive[4])
        depots[d].totalspace += iec_string_to_bytes(drive[5])
        depots[d].totaldrives += 1
        if drive[1] == 'UP' :
          depots[d].updrives += 1
        if drive[1] == 'IGNORE':
          depots[d].ignore = True
          depots[d].updrives += 1
        if drive[1] == 'NO_SPACE' and iec_string_to_bytes(drive[5]) > 1e9 : 
          depots[d].updrives += 1
    return depots


def print_depot_status(depots):
    """Print depot status list to the screen, for debugging."""
    depotlist = depots.keys()
    depotlist = sorted(depotlist, key=lambda x: float(re.findall(r'\d+',x)[0]))
    for d in depotlist:
        status_str = str(d) + "  "
        if depots[d].totalspace > 0:
            status_str +=  str(int( 100 - 100 * depots[d].freespace / depots[d].totalspace)  ) + '% used '
        else:
            status_str += '0% free '
        status_str += str(depots[d].updrives) + '/' + str(depots[d].totaldrives)
        status_str += ' drives UP'
        if depots[d].ignore:
            status_str += ' IGNORE'
        print status_str


def construct_status_page(depots,outfile):
    """Construct tabular html display of depots from dictionary of Depots."""
    html = open(outfile,'w')
    
    html.write('<html>\n')
    html.write('<head>\n')
    html.write('<title>LStore Depot Status</title>\n')
    html.write('<meta http-equiv="refresh" content="900">\n')
    html.write('</head>\n')
    
    html.write('<body>\n')
    html.write('Page generated at: '+str(datetime.datetime.now())+'<br /><br />\n')

    # write totals
    drives_total = 0
    updrives_total = 0
    space_total = 0
    used_total = 0
    for d in depots.keys():
        drives_total += depots[d].totaldrives
        updrives_total += depots[d].updrives
        space_total += depots[d].totalspace
        used_total += depots[d].totalspace - depots[d].freespace
    html.write(str(updrives_total)+' drives UP out of '+str(drives_total)+' total drives.&nbsp;&nbsp;')
    html.write(str(round(used_total/1000**4,1))+' TB used out of ')
    html.write(str(round(space_total/1000**4,1))+' TB total space.<br /><br /><br />')

    # make table of depots 
    html.write('<table style="border:1px solid black;width:98%;margin:0 auto;">\n')
    html.write('<tr>\n')
    
    row = 0
    depotlist = depots.keys()
    depotlist = sorted(depotlist, key=lambda x: float(re.findall(r'\d+',x)[0]))
    for d in depotlist:
        upfraction = float(depots[d].updrives) / float(depots[d].totaldrives)
        if depots[d].totalspace > 0:
            usedspace =  int( 100 - 100 * depots[d].freespace / depots[d].totalspace)  
            usedspacestr =  str(usedspace  ) + '% used '
        else:
            usedspace = 0
            usedspacestr = 'No Usable Space'
        drivesup = str(depots[d].updrives) + '/' + str(depots[d].totaldrives)
        #if upfraction == 1 and not depots[d].ignore :
        if upfraction == 1 :
           html.write('<td style="background: #00FF00;border: 1px solid black;">\n')
        if upfraction >= 0.9 and upfraction < 1.0 :
           html.write('<td style="background: #BFFF00;border: 1px solid black;">\n')
        if upfraction >= 0.8 and upfraction < 0.9 :
           html.write('<td style="background: #FFFF00;border: 1px solid black;">\n')
        if upfraction >= 0.7 and upfraction < 0.8 :
           html.write('<td style="background: #FFBF00;border: 1px solid black;">\n')
        if upfraction < 0.7  :
           html.write('<td style="background: #FF0000;border: 1px solid black;">\n')
        
        html.write('<b>'+str(d)+'</b><br />\n') 
        if depots[d].ignore :
           html.write('<b>READ ONLY</b><br />\n') 
        html.write(usedspacestr+' ( ')
        html.write(str(round(depots[d].totalspace / 1000**4,1))+' TB total )\n' )
        html.write('<div style="width:95%; background: #FFFFFF; border: 1px solid black;')
        html.write('padding:2px;">')
        html.write('<div style="width:'+str(usedspace)+'%; background: #000000;">&nbsp;</div>\n')
        html.write('</div>\n')
        html.write(drivesup+' drives up\n')
        html.write('</td>\n')
        if row == 5:
           html.write('</tr><tr>\n')
        row += 1
        row = row % 6
    html.write('</tr></table>\n')
    html.write('</body</html>\n')
    html.close()


if __name__ == '__main__':
    outfile = sys.argv[1]
    log = get_depot_log()
    depots = parse_depot_log(log)
    construct_status_page(depots,outfile)
