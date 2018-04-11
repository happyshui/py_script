#! /usr/bin/python2.7
# __*__ coding: utf-8 __*__

import os
import sys
from optparse import OptionParser
from subprocess import Popen, PIPE
import shlex
import time
import MySQLdb
import re
import shutil
import tarfile
import stat
import logging
import pwd


logger = None
MySQL_DATA_DIR = '/mysql/'
MySQL_CONF_DIR = '/etc'


def opt():
    parser = OptionParser('Usage: %prog -f -b -p')
    parser.add_option('-f', '--tarfile',
            dest='tarfile',
            action='store',
            default='/opt/mysql-5.7.21-1.el7.x86_64.rpm-bundle.tar',
            help='file /opt/mysql-5.7.21-1.el7.x86_64.rpm-bundle.tar')
    parser.add_option('-b', '--bashfile',
            dest = 'bashfile',
            action = 'store',
            default = '/opt/createmycnf.sh',
            help = 'file /opt/createmycnf')
    parser.add_option('-p', '--mysqlpwd',
            dest = 'mysqlpwd',
            action = 'store',
            default = '1qaz2wsx#EDC',
            help = 'password 1qaz2wsx#EDC')
    options, args = parser.parse_args()
    return options, args

def setOwner():
    list = []
    with open('/etc/passwd', 'r') as f:
        for line in f:
            matchmysql = re.search(r'mysql', line, re.I)

    if matchmysql:
        os.system('chown -R mysql:mysql {0}'.format(MySQL_DATA_DIR))

    else:
        os.system('useradd -M -s /sbin/nologin mysql')
        os.system('chown -R mysql:mysql {0}'.format(MySQL_DATA_DIR))

    for i in pwd.getpwnam('mysql'):
        list.append(i)
    mysqluid = list[2]
    mysqlgid = list[3]
    print mysqluid, mysqlgid
    if not (os.stat(MySQL_DATA_DIR).st_uid == mysqluid and os.stat(MySQL_DATA_DIR).st_gid == mysqlgid):
        print('chown mysql datadir or installdir not ok')
        sys.exit(1)
    if not (os.stat(MySQL_DATA_DIR+'data').st_uid == mysqluid and os.stat(MySQL_DATA_DIR+'data').st_gid == mysqlgid):
        print('chown mysql datadir or installdir not ok')
        sys.exit(1)
    if not (os.stat(MySQL_DATA_DIR+'logs').st_uid == mysqluid and os.stat(MySQL_DATA_DIR+'logs').st_gid == mysqlgid):
        print('chown mysql datadir or installdir not ok')
        sys.exit(1)
    if not (os.stat(MySQL_DATA_DIR+'tmp').st_uid == mysqluid and os.stat(MySQL_DATA_DIR+'tmp').st_gid == mysqlgid):
        print('chown mysql datadir or installdir not ok')
        sys.exit(1)

def makeDIR():
    if os.path.exists('/mysql/data'):
        print('dir is exist')
    else:
        try:
            os.makedirs('/mysql/data')
            os.makedirs('/mysql/logs')
            os.makedirs('/mysql/tmp')
        except Exception, e:
            print(e)

def extract():
    if os.path.exists('/opt/mysql-5.7.21-1.el7.x86_64.rpm-bundle.tar'):
        print('mysql tarfile is /opt/')
    else:
        print('wget mysql rpm begin')
        os.system('wget https://cdn.mysql.com//Downloads/MySQL-5.7/mysql-5.7.21-1.el7.x86_64.rpm-bundle.tar -o /opt/mysql-5.7.21-1.el7.x86_64.rpm-bundle.tar')
        print('wget mysql rpm end')
    tar = tarfile.open('/opt/mysql-5.7.21-1.el7.x86_64.rpm-bundle.tar')
    tar.extractall()
    tar.close()

def install_MySQL():
    os.system('rm -rf mysql*minimal*.rpm')
    os.system('rm -rf mysql*embedded*.rpm')
    os.system('yum localinstall /opt/mysql-community-*.rpm -y')
    cnf = '/etc/my.cnf'
    if os.path.exists(cnf):
        os.system('cat /etc/my.cnf')
    else:
        print(cnf + ' do not esixts')
        sys.exit(1)

def mycnfCreate(bashfile):
    cnf = '/etc/my.cnf'
    if os.path.exists(cnf):
        os.system('rm -rf /etc/my.cnf')
        os.system('rm -rf /etc/my.cnf.rpm*')
    cmd = "/bin/bash {0}".format(bashfile)
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    p.communicate()
    p.returncode

def checkInstall():
    if not os.path.exists('/mysql/data/ibdata1'):
        print('mysql not install')
        sys.exit(1)

    with open('/var/log/mysqld.log') as f:
        flist = [i for i in f if i]
        fstr = ''.join(flist)
        re_error = re.compile(r'\s\[error\]\s', re.I | re.M)
        errorlist = re_error.findall(fstr)

    if errorlist:
        print('error.log error count:' + str(len(errorlist)))
        print('mysql not install')
        sys.exit(1)
    else:
        print('install mysql ok')

def mysqlStart():
    os.system('systemctl restart mysqld')

def connMySQL():
    str1 = ''.join([x for x in open('/var/log/mysqld.log').readlines() if re.search('A temporary password',x,re.I)])
    cnf = '/etc/my.cnf'
    if os.path.exists(cnf):
        host = 'localhost'
        user = 'root'
        dbname = 'mysql'
        passwd = str1.split(': ')[1]
        usocket = MySQL_DATA_DIR + '/tmp/mysql.sock'
        try:
            conn = MySQLdb.connect(host=host, user=user, db=dbname, passwd=passwd)
        except Exception, e:
            print(e)
            sys.exit(1)
        cur = conn.cursor()
        return cur

def execSQL(mysqlpwd):
    sql = 'alter user root@localhost identified by {0}'.format(mysqlpwd)
    cur = connMySQL()
    cur.execute(sql)


if __name__ == '__main__':
    options, args = opt()
    try:
        cmd = args[0]
    except IndexError:
        print('{0} follow a command').format(__file__)
        print('{0} -h').format(__file__)
        sys.exit(1)

    if (options.tarfile and os.path.isfile(options.tarfile)) and (options.bashfile and os.path.isfile(options.bashfile)) and (options.mysqlpwd):
        mysqlfile = options.tarfile
        bashfile = options.bashfile
        mysqlpwd = options.mysqlpwd
    else:
        print('{0} -h').format(__file__)
        sys.exit(1)

    if cmd == 'create':
        makeDIR()
        print('step1: makeDIR completed')
        extract()
        print('step2: extract completed')
        setOwner()
        print('step3: setOwner completed')
        install_MySQL()
        print('step4: Install MySQL completed')
        mycnfCreate(bashfile)
        print('step5: cnfcreate completed')
        mysqlStart()
        print('step6: MySQL Start completed')
        checkInstall()
        print('step7: checkInstall completed')
        execSQL(mysqlpwd)
        print('step8: change pwd completed')

        print('mysql install finish')
