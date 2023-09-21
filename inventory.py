"""
Tool for calling lio_du on specified directories, storing results
into text files, and parsing those files to generate reports.
"""
import datetime
import json
import os.path
import re
import subprocess
import time

LSTORE_DEFAULT_SERVER = 'lstore://10.0.13.241:6711:lio'
OUTPUT_DEFAULT_DIR = '/var/www/autocms/inventory/'

HTML_PAGESTART_FMTSTR = """\
<html>
<head>
<title>T2 Vanderbilt Storage Inventory</title>
<meta http-equiv="refresh" content="7200">
<style>
  table, th, td {{border: 1px solid black; padding: 0.4em; }}
  table {{ border-collapse: collapse; }}
</style>
</head>
<body>
Page generated at: {gentime} <br /><br />
"""

HTML_PAGEEND_FMTSTR = """\
</body>
</html>
"""


def main():
    """
    Check specified directories with lio_du, create reports, generate
    summary page and publish
    """
    make_daily_report('@:/cms/store/user/', 'cms.store.user')
    make_daily_report('@:/cms/store/', 'cms.store')
    generate_report(['cms.store', 'cms.store.user'])


def generate_report(
        prefixes,
        output_dir=None,
        output_name='index.html',
        comparisons=(1, 3, 7)
    ):
    """
    Look in the output_dir for inventory files for the current day with
    prefixes as given in a list. Creates a webpage with a report of usage
    from each specified inventory.
    """
    if output_dir is None:
        output_dir = OUTPUT_DEFAULT_DIR
    report = []
    report.append(HTML_PAGESTART_FMTSTR.format(
        gentime=str(datetime.datetime.now())
    ))

    for prefix in prefixes:
        data = fetch_inventory_data(prefix, 0, output_dir)
        comp_data = []
        for day in comparisons:
            comp_data.append(fetch_inventory_data(prefix, day, output_dir))
        report.append(generate_inventory_table(data, comparisons, comp_data))

    report.append(HTML_PAGEEND_FMTSTR.format())

    with open(os.path.join(output_dir, output_name), 'w') as stream:
        stream.write(''.join(report))


def fetch_inventory_data(prefix, days_old, output_dir):
    """
    Fetch inventory data by reading the file for the specified
    number of days ago (can be zero), prefix, and output directory.
    """
    target = datetime.datetime.now() - datetime.timedelta(days=days_old)
    datestr = target.strftime('%Y-%m-%d')
    filename = prefix + '.' + datestr + '.json'
    filepath = os.path.join(output_dir, filename)
    with open(filepath) as stream:
        data = json.loads(stream.read())
    return data


def generate_inventory_table(data, comparisons=(), comp_data=()):
    """
    Generate an HTML table from json inventory data file.
    Optionally include comparison dates and comparison data
    """
    report = []
    ra = report.append

    ra("""\
    <div>
      <h2>{0} Inventory</h2>
      Generated at {1}<br />
      """.format(
            data['directory'],
            datetime.datetime.fromtimestamp(data['timestamp'])
        )
    )
    ra("""\
      <table>
        <tr>
          <td><b>Directory</b></td>
          <td>&nbsp;</td>
          <td><b>Size</b></td>
          <td style="width:200px;"><b>Percent of Total</b></td>
      """)
    for day in comparisons:
        ra('      <td><b>{0} Day Change</b></td>\n'.format(day))
    ra("""\
          <td>&nbsp;</td>
          <td><b>File Count</b></td>
          <td style="width:200px;"><b>Percent of Total</b></td>
      """)
    for day in comparisons:
        ra('      <td><b>{0} Day Change</b></td>\n'.format(day))
    ra('        <tr>\n')

    inv = data['inventory']
    inv.sort(key=lambda x: x[1], reverse=True)
    totalsize = sum(x[1] for x in inv)
    totalcount = sum(x[2] for x in inv)
    comp_totalsize = []
    comp_totalcount = []
    for comp in comp_data:
        comp_totalsize.append(sum(x[1] for x in comp['inventory']))
        comp_totalcount.append(sum(x[2] for x in comp['inventory']))
    for entry in inv:
        if entry[2]:
            ra(
                inventory_table_line(
                    entry,
                    totalsize,
                    totalcount,
                    comparisons=comparisons,
                    comp_data=comp_data
                )
            )

    ra("""\
      <tr style="font-weight:bold;">
        <td>TOTAL</td>
        <td>&nbsp;</td>
        <td>{size}T</td>
        <td>N/A</td>\n""".format(size=str(round(totalsize / 1000**4, 2)))
    )
    for idx, day in enumerate(comparisons):
        change = totalsize - comp_totalsize[idx]
        if change > 0:
            ra(
                '      <td style="color:red;">{0}T</td>\n'
                .format(round(change / 1000**4, 2))
            )
        elif change < 0:
            ra(
                '      <td style="color:blue;">+{0}T</td>\n'
                .format(-round(change / 1000**4, 2))
            )
        else:
            ra('      <td>0T</td>\n')

    ra("""\
        <td>&nbsp;</td>
        <td>{count}</td>
        <td>N/A</td>\n""".format(count=totalcount)
    )
    for idx, day in enumerate(comparisons):
        change = totalcount - comp_totalcount[idx]
        if change > 0:
            ra(
                '      <td style="color:red;">{0}</td>\n'
                .format(change)
            )
        elif change < 0:
            ra(
                '      <td style="color:blue;">+{0}</td>\n'
                .format(-change)
            )
        else:
            ra('      <td>0</td>\n')


    ra("""\
      </tr>
    </table>
    </div>\n"""
    )
    return ''.join(report)


def inventory_table_line(
    entry,
    totalsize,
    totalcount,
    comparisons=(),
    comp_data=()
):
    """
    Generate an HTML table row for the given inventory data and optional
    comparisons.
    """
    name = entry[0].split('/')[-1]
    if not name:
        name = entry[0].split('/')[-2]
    size = entry[1]
    count = entry[2]

    truncname = (name[:15] + '...') if len(name) > 18 else name
    sizestr = str(round(size / 1000**4, 2))
    sizepercent = str(round(size / totalsize * 100, 2))
    countpercent = str(round(float(count) / float(totalcount) * 100, 2))

    result = []

    result.append("""\
      <tr>
        <td>{name}</td>
        <td>&nbsp;</td>
        <td>{size}T</td>
        <td>
          <div style="float:left; width:55%; padding:2px;
                      background: #FFFFFF; border: 1px solid black;">
            <div style="width:{sizeper}%; background: #000000;">&nbsp;</div>
          </div>
          &nbsp;{sizeper}%
        </td>\n""".format(
            name=truncname,
            size=sizestr,
            sizeper=sizepercent,
        )
    )
    for idx, day in enumerate(comparisons):
        change = size - _fetch_entry_size(name, comp_data[idx])
        if change > 0:
            result.append(
                '      <td style="color:red;">{0}T</td>\n'
                .format(round(change / 1000**4, 2))
            )
        elif change < 0:
            result.append(
                '      <td style="color:blue;">+{0}T</td>\n'
                .format(-round(change / 1000**4, 2))
            )
        else:
            result.append('      <td>0T</td>\n')

    result.append("""\
        <td>&nbsp;</td>
        <td>{count}</td>
        <td>
          <div style="float:left; width:55%; padding:2px;
                      background: #FFFFFF; border: 1px solid black;">
            <div style="width:{countper}%; background: #000000;">&nbsp;</div>
          </div>
          &nbsp;{countper}%
        </td>\n""".format(
            name=truncname,
            size=sizestr,
            count=count,
            sizeper=sizepercent,
            countper=countpercent
        )
    )
    for idx, day in enumerate(comparisons):
        change = count - _fetch_entry_count(name, comp_data[idx])
        if change > 0:
            result.append(
                '      <td style="color:red;">{0}</td>\n'
                .format(change)
            )
        elif change < 0:
            result.append(
                '      <td style="color:blue;">+{0}</td>\n'
                .format(-change)
            )
        else:
            result.append('      <td>{0}</td>\n'.format(change))

    result.append('     </tr>\n')

    return ''.join(result)


def _fetch_entry_size(name, data):
    for entry in data['inventory']:
        ename = entry[0].split('/')[-1]
        if not ename:
            ename = entry[0].split('/')[-2]
        if ename == name:
            return entry[1]
    return 0


def _fetch_entry_count(name, data):
    for entry in data['inventory']:
        ename = entry[0].split('/')[-1]
        if not ename:
            ename = entry[0].split('/')[-2]
        if ename == name:
            return entry[2]
    return 0


def make_daily_report(directory, filename, server=None, output_dir=None):
    """
    Run lio_du on the specified lstore directory, and make a
    corresponding json report in a file of the form
    "filename.YYYY-MM-DD.json"
    """
    if output_dir is None:
        output_dir = OUTPUT_DEFAULT_DIR
    if server is None:
        server = LSTORE_DEFAULT_SERVER

    datestr = datetime.datetime.now().strftime('%Y-%m-%d')
    filename += '.' + datestr + '.json'

    result = {
        'directory': directory,
        'inventory': run_lio_du(directory),
        'server': server,
        'timestamp': time.time()
    }

    with open(os.path.join(output_dir, filename), 'w') as stream:
        stream.write(json.dumps(result, indent=2))


def run_lio_du(directory, server=None, retries=3, timeout=9600):
    """
    Run a lio_du command on the specified directory and parse the
    results, returning a list of tuples of the form:
    ("directory_name", file size (in bytes), file count)
    """
    if server is None:
        server = LSTORE_DEFAULT_SERVER

    counter = 0
    success = False
    while counter < retries and not success:
        counter += 1
        proc = subprocess.Popen(
            ['lio_du', '-s', '-c', server, directory],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(timeout=timeout)
        lines = stdout.decode('utf-8').splitlines()
        if proc.returncode == 0 and len(lines) > 2:
            success = True

    if not success:
        raise Exception('lio_du failed after {} retries'.format(retries))

    result = []
    for line in lines[2:-2]:
        fields = line.split()
        name = fields[2]
        count = int(fields[1])
        size = int(fields[0])
        result.append((name, size, count))
    return result


def parse_iec_str(iec):
    """
    Return number of bytes as a float from an IEC format
    string
    """
    val = float(re.findall(r'\d+\.\d+', iec)[0])
    if( re.match(r'.*ki',iec) ): val *= 1024
    if( re.match(r'.*Mi',iec) ): val *= 1024**2
    if( re.match(r'.*Gi',iec) ): val *= 1024**3
    if( re.match(r'.*Ti',iec) ): val *= 1024**4
    if( re.match(r'.*Pi',iec) ): val *= 1024**5
    if( re.match(r'.*k$',iec) ): val *= 1000
    if( re.match(r'.*M$',iec) ): val *= 1000**2
    if( re.match(r'.*G$',iec) ): val *= 1000**3
    if( re.match(r'.*T$',iec) ): val *= 1000**4
    if( re.match(r'.*P$',iec) ): val *= 1000**5
    return val


if __name__ == '__main__':
    main()
