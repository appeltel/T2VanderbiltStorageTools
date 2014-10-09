import os.path, time
import re
import sys

def main():

    counter = sys.argv[1] 

    with open('/home/appelte1/T2VanderbiltStorageTools/FileInventory/store.inv.' + counter) as input_store:
        lines_store = input_store.read().splitlines()
    store = parseLioDu(lines_store)

    with open('/home/appelte1/T2VanderbiltStorageTools/FileInventory/store.user.inv.' + counter) as input_user:
        lines_user = input_user.read().splitlines()
    user = parseLioDu(lines_user)

    #debug
    #print "Inventory for store:\n"
    #printFileInventory(store)
    #print "\n\nInventory for store/user:\n"
    #printFileInventory(user)

    constructStatusPage(store,user,'/home/appelte1/web/fileInventory.html')

class T2Directory:
    def __init__(self,name,count,size):
        self.name = name
        self.count = count
        self.size = size
        self.size1day = -1.0
        self.size7day = -1.0
        self.size30day = -1.0
    def printHTMLTable(self,file,totalsize):
        sizestr = str( round( self.size / 1000**4,2 ) )
        percent = str( round( self.size / totalsize * 100,2 ) )
        file.write('<tr><td>' + self.name + '</td>')
        file.write('<td>' + sizestr + 'T</td>')
        file.write('<td>' + str(self.count) + '</td>\n')
        file.write('<td><div style="float:left; width:65%; background: #FFFFFF; border: 1px solid black;')
        file.write('padding:2px;">')
        file.write('<div style="width:'+percent+'%; background: #000000;">&nbsp;</div>\n')
        file.write('</div>&nbsp;'+percent+'%</td></tr>\n')

def parseLioDu(lines):
    dirs = list()
    for entry in lines:
        # skip lines not starting with a number
        if not re.match(r'^[\s]*[0-9]',entry): 
            continue
        val = entry.split()
        name = val[2].rstrip('/').split('/')[-1]
        dirs.append( T2Directory(name,val[1],IECStringToBytes(val[0])) )
        
    return dirs

def IECStringToBytes(string):
    val = float(re.findall(r'\d+\.\d+', string)[0])
    if( re.match(r'.*ki',string) ): val *= 1024 
    if( re.match(r'.*Mi',string) ): val *= 1024**2
    if( re.match(r'.*Gi',string) ): val *= 1024**3
    if( re.match(r'.*Ti',string) ): val *= 1024**4
    if( re.match(r'.*Pi',string) ): val *= 1024**5
    if( re.match(r'.*k$',string) ): val *= 1000 
    if( re.match(r'.*M$',string) ): val *= 1000**2
    if( re.match(r'.*G$',string) ): val *= 1000**3
    if( re.match(r'.*T$',string) ): val *= 1000**4
    if( re.match(r'.*P$',string) ): val *= 1000**5
    return val

def printFileInventory(dirs):

    dirs.sort(key=lambda x: x.size,reverse=True)
    for item in dirs:
        sizestr = str( round( item.size / 1000**4, 2 )  )
        print item.name + "\t" + sizestr + "T" 

def constructStatusPage(store,user,outfile):

    store.sort(key=lambda x: x.size,reverse=True)
    user.sort(key=lambda x: x.size,reverse=True)

    html = open(outfile,'w')
    
    html.write('<html>\n')
    html.write('<head>\n')
    html.write('<title>T2 Vanderbilt Storage Inventory</title>\n')
    html.write('<meta http-equiv="refresh" content="7200">\n')
    html.write('<style>table, th, td {border: 1px solid black; padding: 0.4em; }')
    html.write('table { border-collapse: collapse; } </style>')
    html.write('</head>\n')
    
    html.write('<body>\n')

    html.write("Inventory performed at: %s<br />\n" % time.ctime(os.path.getmtime('store.inv.' + sys.argv[1])))
    html.write('Page generated at: '+str(time.ctime())+'<br /><br />\n')

    html.write('<div style="float:left;width:48%">\n')
    html.write('<h2>/cms/store/ Inventory</h2><br />\n')
    html.write('Total Usage: ' + str(round(store[0].size/1000**4,2)) + 'T<br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td></tr>\n')
    for item in store:
        if item.name == 'TOTAL':
            continue
        item.printHTMLTable(html,store[0].size)
    html.write('</table></div>\n<div style="float:left;width:48%">\n')

    html.write('<h2>/cms/store/user/ Inventory</h2><br />\n')
    html.write('Total Usage: ' + str(round(user[0].size/1000**4,2)) + 'T<br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td></tr>\n')
    for item in user:
        if item.name == 'TOTAL':
            continue
        item.printHTMLTable(html,user[0].size)
    html.write('</table>\n')

    html.write('</div></body></html>\n')
             
    html.close()


main()
