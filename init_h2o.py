#! /usr/bin/python2.7
# __*__ coding: utf-8 __*__

import os
import sys
import re


def h2o_install():
    j_cmd = 'nohup java -jar --spring.datasource.password=1qaz2wsx#EDC \
            --spring.datasource.url=jdbc:mysql://localhost:3306/model?useUnicode=true&characterEncoding=UTF-8 '
    if int(run(" [ -d '/opt/Install' ] && echo 1 || echo 0")) == 1:
        run('cd Install && git pull && cd ..')
    else:
        os.system('git clone http://172.16.234.61/DPAAS/Install.git')
    os.system('mkdir -p /home/appuser/h2o/{login,unwar,war}')
    os.system('cp ./Install/h2o/sh/* /home/appuser/h2o/')
    os.system('java -jar /opt/Install/h2o/jar/service-discovery-0.0.1-SNAPSHOT.jar')
    time.sleep(15)
    for i in for i in os.listdir('.'):
        if os.path.isfile(i):
            os.system('{0} {1} {2}.log 2>&1 &'.format(j_cmd, i, i))
            print('start program successfully')
    os.system('cp -f ./Install/h2o/nginx.conf /etc/nginx/')
    os.system('tar -zxvf ./Install/h2o/webself.tar.gz -C /usr/share/nginx/html')
    os.system('systemctl reload nginx')

if __name__ == '__main__':
    h2o_install()
