#!/bin/bash

port=3306
expirelogsdays=7
ip=$(ip a|awk -F "inet|/"  '/inet.*brd/ {print $2}'|awk -F'.' '{print $4}')
serverid=$ip

cat > /etc/my.cnf << EOF
[client]
port = $port
socket = /mysql/tmp/mysql.sock

[mysqld]
port = $port
user = mysql
datadir = /mysql/data
tmpdir = /mysql/tmp
pid-file = /mysql/tmp/mysql.pid
socket = /mysql/tmp/mysql.sock
character_set_server = utf8
open_files_limit = 65535
server-id = $serverid

query_cache_type = 0
query_cache_size = 0
sql_mode = ''

log-bin = /mysql/logs/mysql-bin
sync_binlog = 1
expire_logs_days = 7

innodb_undo_directory = /mysql/logs/undolog
innodb_undo_log_truncate = 1
innodb_undo_tablespaces = 4

EOF
