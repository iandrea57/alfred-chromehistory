#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
chrome history v0.1

Author: iandrea57
Host: https://github.com/iandrea57
'''

import sqlite3
import datetime
import cgi
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

DEBUG_MODE = False #debug mode
HISTORY_DB_PATH = os.path.expanduser('~') + '/Library/Application Support/Google/Chrome/Default/History'  #you can command `chrome://version/` in chrome to find the path

class History:
    '''
    This is chrome history class, field from table: urls
    contains field: id, url, title, visit_count, last_visit_time
    '''

    id = 0
    url = ''
    title = ''
    visit_count = 0
    last_visit_time = None
    def __init__(self, id, url, title, visit_count, last_visit_time):
        self.id = id
        if url is not None:
            self.url = url
        if title is not None:
            self.title = title
        self.visit_count = visit_count
        self.last_visit_time = datetime.datetime.fromtimestamp(last_visit_time/1000000-11644473600)

    def __str__(self):
        '''
        in DEBUG_MODE:  return all field value
        normally:       return workflow_xml item format info
        '''
        if DEBUG_MODE:
            return 'id=%d, url=%s, title=%s, visit_count=%d, last_visit_time=%s' % (self.id, self.url, self.title, self.visit_count, self.last_visit_time)
        else:
            return '<item uid="desktop" arg="' + cgi.escape(self.url) + '" valid="yes"><title>' + cgi.escape(self.title) + '</title><subtitle>' + cgi.escape(str(self.last_visit_time) + '  ' + self.url) + '</subtitle><icon>icon.png</icon></item>'


def backup_db(path):
    '''
    backup chrome's History database file daily (named 'History.bak.%y-%m-%d', previous backup file will be removed)
    '''
    time_day_str = datetime.datetime.now().strftime('%Y-%m-%d')
    backup_suffix = '.bak'
    backup_path = path + backup_suffix + "." + time_day_str
    if not os.path.exists(backup_path):
        os.system('rm ' + path.replace(' ', '\\ ') + backup_suffix + '.*')
        os.system('cp -a ' + path.replace(' ', '\\ ') + ' ' + backup_path.replace(' ', '\\ '))
    return backup_path


def get_conn(path):
    '''
    get sqlite3 database connect
    '''
    conn = None
    if path is not None and os.path.exists(path) and os.path.isfile(path):
        conn = sqlite3.connect(path)
        conn.text_factory = str
        if DEBUG_MODE:
            print 'sqlite connect path', path
    return conn


def get_cursor(conn):
    '''
    get sqlite3 database cursor
    '''
    if conn is not None:
        return conn.cursor()
    else:
        return None


def fetchall(conn, sql, data=None):
    '''
    fetchall data from sqlite3 database by sql and param
    '''
    result = None
    if sql is not None and sql != '':
        cursor = get_cursor(conn)
        if cursor is not None:
            if DEBUG_MODE:
                print('execute sql:[{}], param:[{}]'.format(sql, data))
            if data is not None:
                cursor.execute(sql, data)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
    return result


def build_history_list(result):
    '''
    build chrome history data list from sqlite3 query result arrays
    '''
    history_list = []
    if result is not None and len(result) > 0:
        for row in result:
            history_list.append(History(row[0], row[1], row[2], row[3], row[4]))
    return history_list


def print_history_list(history_list):
    '''
    print chrome history list
    in DEBUG_MODE:  print all field value
    normally:       print workflow_xml item format info
    '''
    if DEBUG_MODE:
        for history in history_list:
            print history
    else:
        workflow_xml = '<?xml version="1.0"?><items>'
        for history in history_list:
            workflow_xml += str(history)
        workflow_xml += '/<items>'
        print workflow_xml


def query(keyword):
    '''
    query chrome history list with keyword and print result
    '''
    like_string = '%' + keyword + '%'
    path = backup_db(HISTORY_DB_PATH)
    conn = get_conn(path)
    result = fetchall(conn, 'select id, url, title, visit_count, last_visit_time from urls where url like ? or title like ? order by visit_count desc, last_visit_time desc, id desc limit 50', (like_string, like_string))
    history_list = build_history_list(result)
    print_history_list(history_list)


if __name__ == '__main__':
    if DEBUG_MODE:
        query(u'wiki')
    else:
        query(u'{query}')