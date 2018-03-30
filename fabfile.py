#! /usr/bin/python2.7
# __*__ coding: utf-8 __*__

from fabric.api import *


env.hosts = [
        '172.16.236.111',
        '172.16.236.112',
        '172.16.236.113'
        ]
env.user = 'appuser'
env.password = '4rfv5tgb^YHN'
env.port = 22

def ls():
    with cd ('/tmp'):
        run('ls -l')

@hosts('172.16.236.113')
def mk():
    with cd('/tmp'):
        run('touch aaa')
