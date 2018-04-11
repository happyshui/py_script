#! /usr/bin/python2.7
# __*__ coding: utf-8 __*__

from fabric.api import *
from fabric.main import main
from fabric.colors import *
from fabric.context_managers import *
from fabric.contrib.console import confirm
import os
import sys
import re


env.hosts = [
        '172.16.236.111',
#        '172.16.236.112',
#        '172.16.236.113'
        ]
# env.user = 'appuser'
env.user = 'root'
# env.password = '4rfv5tgb^YHN'
env.password = 'jry123!QAZ'
env.port = 22
env.roledefs = {
        'ambari_master': ['172.16.236.111', ],
        'ambari_agent': ['172.16.236.112', '172.16.236.113', ],
        'h2o': ['172.16.236.111',]
        }

def update_ambari_repo():
    # run('wget -nv http://public-repo-1.hortonworks.com/ambari/centos7/2.x/updates/2.5.1.0/ambari.repo -O /etc/yum.repos.d/ambari.repo')
    run('wget -nv http://public-repo-1.hortonworks.com/ambari/centos7/2.x/updates/2.5.1.0/ambari.repo -O /opt/ambari.repo')
    run('yum -y install gcc pcre-devel zlib-devel openssl openssl-devel nginx git java-1.8.0-openjdk')
    run('systemctl start nginx')

@roles('h2o')
def h2o_install():
    with cd('/opt'):
        if int(run(" [ -d '/opt/Install' ] && echo 1 || echo 0")) == 1:
            run('cd Install && git pull && cd ..')
        else:
            run('git clone http://172.16.234.61/DPAAS/Install.git')
        run('mkdir -p /home/appuser/h2o/{login,unwar,war}')
        run('cp ./Install/h2o/sh/* /home/appuser/h2o/')
        run('java -jar /opt/Install/h2o/jar/service-discovery-0.0.1-SNAPSHOT.jar')
        time.sleep(15)
        run('for i in `ls ./Install/h2o/jar/*.jar | grep -v "service-discovery"`; do java -jar ./Install/h2o/jar/$i \&; done')
        if os.system('nohup java -jar --spring.datasource.password=1qaz2wsx#EDC \
                --spring.datasource.url=jdbc:mysql://localhost:3306/model?useUnicode=true&characterEncoding=UTF-8 \
                {0} >> {1}.log 2>&1 &'.format(jar_file, jar_file)) == 0:
            print('start program successfully')
        run('cp -f ./Install/h2o/nginx.conf /etc/nginx/')
        run('tar -zxvf ./Install/h2o/webself.tar.gz -C /usr/share/nginx/html')
        run('systemctl reload nginx')

def task_install():
    # execute(update_ambari_repo)
    execute(h2o_install)
