import os.path, time
import re
import sys

def main():

    inputpath = './'
    counter = sys.argv[1] 

    store = dict()
    user = dict()
    group = dict()
    hidata = dict()
    data = dict()
    mc = dict()
    himc = dict()
    unmerged = dict()

    with open(inputpath + 'store.inv.' + counter) as input_store:
        lines_store = input_store.read().splitlines()
    store[0] = parseLioDu(lines_store)

    with open(inputpath + 'store.user.inv.' + counter) as input_user:
        lines_user = input_user.read().splitlines()
    user[0] = parseLioDu(lines_user)
    with open(inputpath + 'store.group.inv.' + counter) as input_group:
        lines_group = input_group.read().splitlines()
    group[0] = parseLioDu(lines_group)
    with open(inputpath + 'store.hidata.inv.' + counter) as input_hidata:
        lines_hidata = input_hidata.read().splitlines()
    hidata[0] = parseLioDu(lines_hidata)
    with open(inputpath + 'store.data.inv.' + counter) as input_data:
        lines_data = input_data.read().splitlines()
    data[0] = parseLioDu(lines_data)
    with open(inputpath + 'store.mc.inv.' + counter) as input_mc:
        lines_mc = input_mc.read().splitlines()
    mc[0] = parseLioDu(lines_mc)
    with open(inputpath + 'store.himc.inv.' + counter) as input_himc:
        lines_himc = input_himc.read().splitlines()
    himc[0] = parseLioDu(lines_himc)
    with open(inputpath + 'store.unmerged.inv.' + counter) as input_unmerged:
        lines_unmerged = input_unmerged.read().splitlines()
    unmerged[0] = parseLioDu(lines_unmerged)

    prevDays = (1,3,7)

    for age in prevDays:

      if os.path.isfile(inputpath + 'store.inv.' + str(int(counter)-age)):
          with open( inputpath + 'store.inv.' + str(int(counter)-age) ) as old_store:
              lines_store = old_store.read().splitlines()    
          store[age] = parseLioDu(lines_store)
          loadOldSize(store[0],store[age],age)
          loadOldCount(store[0],store[age],age)

      if os.path.isfile(inputpath + 'store.user.inv.' + str(int(counter)-age)):
          with open( inputpath + 'store.user.inv.' + str(int(counter)-age) ) as old_user:
              lines_user = old_user.read().splitlines()    
          user[age] = parseLioDu(lines_user)
          loadOldSize(user[0],user[age],age)
          loadOldCount(user[0],user[age],age)
      if os.path.isfile(inputpath + 'store.group.inv.' + str(int(counter)-age)):
          with open( inputpath + 'store.group.inv.' + str(int(counter)-age) ) as old_group:
              lines_group = old_group.read().splitlines()
          group[age] = parseLioDu(lines_group)
          loadOldSize(group[0],group[age],age)
          loadOldCount(group[0],group[age],age)
      if os.path.isfile(inputpath + 'store.hidata.inv.' + str(int(counter)-age)):
          with open( inputpath + 'store.hidata.inv.' + str(int(counter)-age) ) as old_hidata:
              lines_hidata = old_hidata.read().splitlines()
          hidata[age] = parseLioDu(lines_hidata)
          loadOldSize(hidata[0],hidata[age],age)
          loadOldCount(hidata[0],hidata[age],age)
      if os.path.isfile(inputpath + 'store.data.inv.' + str(int(counter)-age)):
          with open( inputpath + 'store.data.inv.' + str(int(counter)-age) ) as old_data:
              lines_data = old_data.read().splitlines()
          data[age] = parseLioDu(lines_data)
          loadOldSize(data[0],data[age],age)
          loadOldCount(data[0],data[age],age)
      if os.path.isfile(inputpath + 'store.mc.inv.' + str(int(counter)-age)):
          with open( inputpath + 'store.mc.inv.' + str(int(counter)-age) ) as old_mc:
              lines_mc = old_mc.read().splitlines()
          mc[age] = parseLioDu(lines_mc)
          loadOldSize(mc[0],mc[age],age)
          loadOldCount(mc[0],mc[age],age)
      if os.path.isfile(inputpath + 'store.himc.inv.' + str(int(counter)-age)):
          with open( inputpath + 'store.himc.inv.' + str(int(counter)-age) ) as old_himc:
              lines_himc = old_himc.read().splitlines()
          himc[age] = parseLioDu(lines_himc)
          loadOldSize(himc[0],himc[age],age)
          loadOldCount(himc[0],himc[age],age)
      if os.path.isfile(inputpath + 'store.unmerged.inv.' + str(int(counter)-age)):
          with open( inputpath + 'store.unmerged.inv.' + str(int(counter)-age) ) as old_unmerged:
              lines_unmerged = old_unmerged.read().splitlines()
          unmerged[age] = parseLioDu(lines_unmerged)
          loadOldSize(unmerged[0],unmerged[age],age)
          loadOldCount(unmerged[0],unmerged[age],age)       

    constructStatusPage(store[0],user[0], group[0], hidata[0], data[0], mc[0], himc[0], unmerged[0],sys.argv[2],prevDays)

class T2Directory:
    def __init__(self,name,count,size):
        self.name = name
        self.count = count
        self.size = size
        self.oldsize = dict()
        self.oldcount = dict()
    def printHTMLTable(self,file,totalsize,totalcount,prevDays):
        sizestr = str( round( self.size / 1000**4,2 ) )
        sizepercent = str( round( self.size / totalsize * 100,2 ) )
        countpercent = str( round( float(self.count) / float(totalcount) * 100,2 ) )
        truncname = (self.name[:15] + '...') if len(self.name) > 18 else self.name
        if self.name == 'TOTAL':
          file.write('<tr style="font-weight:bold;"><td>' + truncname + '</td>')
        else:
          file.write('<tr><td>' + truncname + '</td>')
        file.write('<td>&nbsp;</td>\n')
        file.write('<td>' + sizestr + 'T</td>\n')
        if self.name == 'TOTAL':
          file.write('<td>N/A</td>')
        else:
          file.write('<td><div style="float:left; width:55%; background: #FFFFFF; border: 1px solid black;')
          file.write('padding:2px;">')
          file.write('<div style="width:'+sizepercent+'%; background: #000000;">&nbsp;</div>\n')
          file.write('</div>&nbsp;'+sizepercent+'%</td>\n')
        for age in prevDays:
          if age in self.oldsize:
            if int(self.oldsize[age]) < int(self.size) :
              file.write('<td style="color:blue;">+')
            if int(self.oldsize[age]) > int(self.size) :
              file.write('<td style="color:red;">')
            if int(self.oldsize[age]) == int(self.size) :
              file.write('<td>')
            change = str( round( (self.size-self.oldsize[age]) / 1000**4,2 ) )
            file.write(change+'T </td>\n')
          else:
            file.write('<td> N/A </td>\n')   
        file.write('<td>&nbsp;</td>\n')
        file.write('<td>' + str(self.count) + '</td>\n')
        if self.name == 'TOTAL':
          file.write('<td>N/A</td>')
        else:
          file.write('<td><div style="float:left; width:55%; background: #FFFFFF; border: 1px solid black;')
          file.write('padding:2px;">')
          file.write('<div style="width:'+countpercent+'%; background: #000000;">&nbsp;</div>\n')
          file.write('</div>&nbsp;'+countpercent+'%</td>\n')
        for age in prevDays:
          if age in self.oldcount:
            if int(self.oldcount[age]) < int(self.count) :
              file.write('<td style="color:blue;">+')
            if int(self.oldcount[age]) > int(self.count) :
              file.write('<td style="color:red;">')
            if int(self.oldcount[age]) == int(self.count) :
              file.write('<td>')
            change = str(  int(self.count)-int(self.oldcount[age]) )
            file.write(change+'</td>\n')
          else:
            file.write('<td> N/A </td>\n')   
        file.write('</tr>\n')

def loadOldSize(new, old, age ):
    for ndir in new:
        for odir in old:
            if ndir.name == odir.name:
                ndir.oldsize[age] = odir.size

def loadOldCount(new, old, age ):
    for ndir in new:
        for odir in old:
            if ndir.name == odir.name:
                ndir.oldcount[age] = odir.count

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

def constructStatusPage(store,user,group,hidata,data,mc,himc,unmerged,outfile,prevDays):
    store.sort(key=lambda x: x.size,reverse=True)
    user.sort(key=lambda x: x.size,reverse=True)
    group.sort(key=lambda x: x.size,reverse=True)
    hidata.sort(key=lambda x: x.size,reverse=True)
    data.sort(key=lambda x: x.size,reverse=True)
    mc.sort(key=lambda x: x.size,reverse=True)
    himc.sort(key=lambda x: x.size,reverse=True)
    unmerged.sort(key=lambda x: x.size,reverse=True)

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

    #html.write('<div style="float:left;width:48%">\n')
    html.write('<div>\n')
    html.write('<h2>/cms/store/ Inventory</h2><br />\n')
#    html.write('<h3>Total File Size: ' + str(round(store[0].size/1000**4,2)) + 'T ' )
#    html.write('&emsp;&emsp;&emsp;')
#    html.write('Total File Count: '+str(store[0].count)+'</h3><br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('</tr>')
    for item in store:
        #if item.name == 'TOTAL':
        #    continue
        item.printHTMLTable(html,store[0].size,store[0].count,prevDays)
    html.write('</table></div>\n')

    html.write('<div>\n')
    html.write('<h2>/cms/store/user/ Inventory</h2><br />\n')
#    html.write('<h3>Total File Size: ' + str(round(user[0].size/1000**4,2)) + 'T ' )
#    html.write('&emsp;&emsp;&emsp;')
#    html.write('Total File Count:'+str(user[0].count)+'</h3><br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('</tr>')
    for item in user:
        #if item.name == 'TOTAL':
        #    continue
        item.printHTMLTable(html,user[0].size,user[0].count,prevDays)
    html.write('</table>\n')

#group
    html.write('<div>\n')
    html.write('<h2>/cms/store/group/ Inventory</h2><br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('</tr>')
    for item in group:
        item.printHTMLTable(html,group[0].size,group[0].count,prevDays)
    html.write('</table>\n')
#hidata
    html.write('<div>\n')
    html.write('<h2>/cms/store/hidata/ Inventory</h2><br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('</tr>')
    for item in hidata:
        item.printHTMLTable(html,hidata[0].size,hidata[0].count,prevDays)
    html.write('</table>\n')
#data
    html.write('<div>\n')
    html.write('<h2>/cms/store/data/ Inventory</h2><br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('</tr>')
    for item in data:
        item.printHTMLTable(html,data[0].size,data[0].count,prevDays)
    html.write('</table>\n')
#mc
    html.write('<div>\n')
    html.write('<h2>/cms/store/mc/ Inventory</h2><br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('</tr>')
    for item in mc:
        item.printHTMLTable(html,mc[0].size,mc[0].count,prevDays)
    html.write('</table>\n')
#himc
    html.write('<div>\n')
    html.write('<h2>/cms/store/himc/ Inventory</h2><br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('</tr>')
    for item in himc:
        item.printHTMLTable(html,himc[0].size,himc[0].count,prevDays)
    html.write('</table>\n')
#unmerged
    html.write('<div>\n')
    html.write('<h2>/cms/store/unmerged/ Inventory</h2><br />\n')
    html.write('<table>')
    html.write('<tr><td><b>Directory</b></td>')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>Size</b></td>')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('<td>&nbsp;</td>')
    html.write('<td><b>File Count</b></td>\n')
    html.write('<td style="width:200px;"><b>Percent of Total</b></td>\n')
    for age in prevDays:
      html.write('<td><b>'+str(age)+' Day Change</b></td>\n')
    html.write('</tr>')
    for item in unmerged:
        item.printHTMLTable(html,unmerged[0].size,unmerged[0].count,prevDays)
    html.write('</table>\n')


    html.write('</div></body></html>\n')
             
    html.close()

if __name__ == '__main__':
    main()
