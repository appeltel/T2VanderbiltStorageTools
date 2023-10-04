#!/accre/admin/bin/adm-python
"""
This script checks all of the xrootd servers directly
to ensure a small file can be read and creates a JSON'
formatted report of the results.
"""
import json
import logging
import os
import subprocess
import sys
import time
import uuid


XROOTD_SERVERS = {
    'sea': 'xrootd-se1-vanderbilt.sites.opensciencegrid.org',
    'seb': 'xrootd-se2-vanderbilt.sites.opensciencegrid.org',
    'sec': 'xrootd-se3-vanderbilt.sites.opensciencegrid.org',
    'sed': 'xrootd-se4-vanderbilt.sites.opensciencegrid.org',
#    'see': 'xrootd-se5-vanderbilt.sites.opensciencegrid.org',
    'sef': 'xrootd-se6-vanderbilt.sites.opensciencegrid.org',
    'seg': 'xrootd-se7-vanderbilt.sites.opensciencegrid.org',
#    'seh': 'xrootd-se8-vanderbilt.sites.opensciencegrid.org',
    'se20': 'xrootd-se20-vanderbilt.sites.opensciencegrid.org',
    'se21': 'xrootd-se21-vanderbilt.sites.opensciencegrid.org',
    'se22': 'xrootd-se22-vanderbilt.sites.opensciencegrid.org',
    'se23': 'xrootd-se23-vanderbilt.sites.opensciencegrid.org',
    'se24': 'xrootd-se24-vanderbilt.sites.opensciencegrid.org',
    'se25': 'xrootd-se25-vanderbilt.sites.opensciencegrid.org',
    'se26': 'xrootd-se26-vanderbilt.sites.opensciencegrid.org',
    'se27': 'xrootd-se27-vanderbilt.sites.opensciencegrid.org',
    'vm-cms-xrootd-srv1': 'xrootd-hv1-vanderbilt.sites.opensciencegrid.org',
    'vm-cms-xrootd-srv2': 'xrootd-hv2-vanderbilt.sites.opensciencegrid.org',
    'vm-cms-xrootd1': 'xrootd-redir1-vanderbilt.sites.opensciencegrid.org',
    'vm-cms-xrootd2': 'xrootd-redir2-vanderbilt.sites.opensciencegrid.org'
}

# Some xrootd servers don't have a hostname that matches their ACCRE
# internal network name according to nagios so we allow some aliases
# for servers that diverge here
ALIASES = {
    'vm-cms-xrootd1': ['xrootd-srv1'],
    'vm-cms-xrootd2': ['xrootd-srv2'],
    'vm-cms-xrootd-srv1': ['xrootd-redir1-vanderbilt'],
    'vm-cms-xrootd-srv2': ['xrootd-redir2-vanderbilt']
}

OUTPUT_FILE = '/var/www/autocms/xrootdchecker/xrootd.json'
TEST_FILE_LFN = '/store/XROOTDCHECKER-VANDY-LFS.txt'
TEST_FILE_CONTENTS = 'XROOTD OK\n'

logging.basicConfig(
    format='%(asctime)s  %(levelname)s:%(message)s',
    filename='xrootdchecker.log',
    level=logging.INFO
)


def ensure_voms_proxy():
    proc = subprocess.Popen(
        ['/usr/bin/voms-proxy-info', '-exists', '-valid 3:0'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL
    )
    stdout, stderr = proc.communicate(timeout=30)
    if proc.returncode != 0:
        logging.info('Renewing grid certificate')
        proc = subprocess.Popen(
        ['/usr/bin/voms-proxy-init', '--voms', 'cms', '-hours', '72'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL
        )
        stdout, stderr = proc.communicate(timeout=30)
        if proc.returncode != 0:
            msg = (
                'voms-proxy-init failed with exit code {0}: {1}.'
                .format(proc.returncode, stderr)
            )
            logging.error(msg)
            sys.exit(1)


def check_server(gridname):
    """
    Returns a tuple of exitcode, stderr
    if file contents mismatch, will return exitcode -1
    """
    tmpfile = f'/tmp/{uuid.uuid4()}'
    arglist = [
        '/usr/bin/xrdcp',
        f'root://{gridname}:1094/{TEST_FILE_LFN}',
        tmpfile
    ]
    proc = subprocess.Popen(
        arglist, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, stdin=subprocess.DEVNULL
    )
    try:
        stdout, stderr = proc.communicate(timeout=120)
    except subprocess.TimeoutExpired:
        try:
            os.remove(tmpfile)
        except FileNotFoundError:
            pass
        return -1, 'xrdcp command timeout (120 seconds)'
    if proc.returncode != 0:
        try:
            os.remove(tmpfile)
        except FileNotFoundError:
            pass
        return proc.returncode, stderr.decode('utf-8')

    read_file_contents = open(tmpfile).read()
    if read_file_contents != TEST_FILE_CONTENTS:
        os.remove(tmpfile)
        return -1, 'Corrupted file read'

    os.remove(tmpfile)
    return 0, ''
    


def main():
    logging.info('Running xrootd checker...')
    try:
        ensure_voms_proxy()
        results = {}
        for server in XROOTD_SERVERS:
            logging.info(f'Checking server {server}')
            code, msg = check_server(XROOTD_SERVERS[server])
            results[server] = {
                'gridname': XROOTD_SERVERS[server],
                'status': code,
                'error_message': msg,
                'timestamp': time.time()
            }
            if server in ALIASES:
                for alias in ALIASES[server]:
                    results[alias] = results[server]
        open(OUTPUT_FILE, 'w').write(json.dumps(results, indent=2))
    except Exception as e:
        logging.exception('Xrootd checker failed')


if __name__ == '__main__':
    main()
