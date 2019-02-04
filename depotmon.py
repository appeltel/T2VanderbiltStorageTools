"""
Generate a tabular html page displaying depot status.

Usage: python reportdepotstatus.py outputfile
"""
import datetime
import os.path
import re
import subprocess
import sys

LSTORE_DEFAULT_SERVER = 'lstore://10.0.13.241:6711:lio'
OUTPUT_DEFAULT_DIR = '/var/www/autocms/depotmon/'

class Depot:
    """
    Information about a specific depot.
    """
    def __init__(self):
        self.usedspace = 0
        self.freespace = 0
        self.totalspace = 0
        self.updrives = 0
        self.nospacedrives = 0
        self.downdrives = 0
        self.totaldrives = 0
        self.ignore = False


def get_depot_log(server=None):
    """
    Return result of lio_rs -s as a list of lines.
    """
    if server is None:
        server = LSTORE_DEFAULT_SERVER
    proc = subprocess.Popen(
        ['lio_rs', '-s', '-c', server],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, err = proc.communicate(timeout=900)
    return out.decode('utf-8').splitlines()


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

        if drive[1] == 'UP' or drive[1] == 'NO_SPACE' :
          depots[d].usedspace += iec_string_to_bytes(drive[3])
          depots[d].freespace += iec_string_to_bytes(drive[4])
          depots[d].totalspace += iec_string_to_bytes(drive[3]) + iec_string_to_bytes(drive[4])

        if drive[1] == 'UP' :
          depots[d].updrives += 1
          depots[d].totaldrives += 1
        if drive[1] == 'NO_SPACE' :
          depots[d].nospacedrives += 1
          depots[d].totaldrives += 1
        if drive[1] == 'DOWN' :
          depots[d].downdrives += 1
          depots[d].totaldrives += 1
    return depots


def print_depot_status(depots):
    """Print depot status list to the screen, for debugging."""
    depotlist = depots.keys()
    depotlist = sorted(depotlist, key=lambda x: float(re.findall(r'\d+',x)[0]))
    for d in depotlist:
        status_str = str(d) + "  "
        if depots[d].totalspace > 0:
            status_str +=  str(int( 100 * depots[d].usedspace / depots[d].totalspace)  ) + '% used '
        else:
            status_str += '0% free '
        status_str += str(depots[d].updrives) + '/' + str(depots[d].totaldrives)
        status_str += ' drives UP'
        if depots[d].ignore:
            status_str += ' IGNORE'
        printr(status_str)


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
    updrives_total = 0
    nospacedrives_total = 0
    downdrives_total = 0
    drives_total = 0
    used_total = 0
    free_total = 0
    space_total = 0
    for d in depots.keys():
        updrives_total += depots[d].updrives
        nospacedrives_total += depots[d].nospacedrives
        downdrives_total += depots[d].downdrives
        drives_total += depots[d].updrives + depots[d].nospacedrives + depots[d].downdrives

        used_total += depots[d].usedspace
        free_total += depots[d].freespace
        space_total += depots[d].usedspace + depots[d].freespace
    uppercentdrives = round( 100.0 * updrives_total / drives_total, 1 )
    nospacepercentdrives = round( 100.0 * nospacedrives_total / drives_total, 1 )
    downpercentdrives = round( 100.0 * downdrives_total / drives_total, 1 )
    usedpercentspace = round( 100.0 * used_total / space_total, 1 )
    freepercentspace = round( 100.0 * free_total / space_total, 1 )
    html.write(str(updrives_total)+' drives UP, '+str(nospacedrives_total)+' drives FULL (NO_SPACE), and '+str(downdrives_total)+' drives DOWN out of '+str(updrives_total)+'+'+str(nospacedrives_total)+'+'+str(downdrives_total)+' = '+str(drives_total)+' TOTAL drives.<br /> \n')
    html.write('UP/TOTAL = '+str(uppercentdrives)+'%; FULL/TOTAL = '+str(nospacepercentdrives)+'%; DOWN/TOTAL = '+str(downpercentdrives)+'%. <br /><br /> \n')
    if usedpercentspace < 85:
        html.write('In the '+str(updrives_total+nospacedrives_total)+' UP and FULL drives, '+str(round(used_total/1000**4,1))+' TB USED and '+str(round(free_total/1000**4,1))+' TB FREE out of '+str(round(used_total/1000**4,1))+'+'+str(round(free_total/1000**4,1))+' = '+str(round((used_total+free_total)/1000**4,1))+' TOTAL space.<br /> \n')
        html.write('USED/TOTAL = <font color="blue">'+str(usedpercentspace)+'%</font>; FREE/TOTAL = '+str(freepercentspace)+'%. <br /><br /><br /> \n')
    else:
        html.write('In the '+str(updrives_total+nospacedrives_total)+' UP and FULL drives, '+str(round(used_total/1000**4,1))+' TB USED and '+str(round(free_total/1000**4,1))+' TB FREE out of '+str(round(used_total/1000**4,1))+'+'+str(round(free_total/1000**4,1))+' = '+str(round((used_total+free_total)/1000**4,1))+' TOTAL space.<br /> \n') 
        html.write('USED/TOTAL = <font color="red">'+str(usedpercentspace)+'%</font>; FREE/TOTAL = '+str(freepercentspace)+'%. <br /><br /><br /> \n')

    # make table of depots 
    html.write('<table style="border:1px solid black;width:98%;margin:0 auto;">\n')
    html.write('<tr>\n')
    
    row = 0
    depotlist = depots.keys()
    depotlist = sorted(depotlist, key=lambda x: float(re.findall(r'\d+',x)[0]))
    for d in depotlist:
        upfraction = float(depots[d].updrives) / float(depots[d].totaldrives)
        if depots[d].totalspace > 0:
            usedspace =  int( 100 * depots[d].usedspace / depots[d].totalspace)  
            usedspacestr =  str(usedspace  ) + '% used '
        else:
            usedspace = 0
            usedspacestr = 'No Usable Space'
        drivesup = str(depots[d].updrives) + '/' + str(depots[d].totaldrives)
        if upfraction == 0 or depots[d].totalspace == 0 or usedspace >= 0.96:
           html.write('<td style="background: #FF0000;border: 1px solid black;">\n')
        elif usedspace >= 0.92 and usedspace < 0.96:
           html.write('<td style="background: #FFBF00;border: 1px solid black;">\n')
        elif usedspace >= 0.88 and usedspace < 0.92:
           html.write('<td style="background: #FFFF00;border: 1px solid black;">\n')
        elif usedspace >= 0.84 and usedspace < 0.88:
           html.write('<td style="background: #BFFF00;border: 1px solid black;">\n')
        else:
           html.write('<td style="background: #00FF00;border: 1px solid black;">\n')

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
    if len(sys.argv) > 1:
        outfile = sys.argv[1]
    else:
        outfile = os.path.join(OUTPUT_DEFAULT_DIR, 'index.html')
    log = get_depot_log()
    depots = parse_depot_log(log)
    construct_status_page(depots,outfile)
