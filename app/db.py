import os
import sys

import pymysql

DBHOST = os.environ['DB_HOST']
DBPORT = os.environ['DB_PORT']
DB_USERNAME = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']


def migrate(event, context):
    try:
        conn = pymysql.connect(DBHOST,
                               user=DB_USERNAME,
                               passwd=DB_PASSWORD,
                               db=DB_NAME,
                               port=int(DBPORT),
                               connect_timeout=5)
        queries = [('CREATE TABLE IF NOT EXISTS '
                    'login_tbl(ID INT PRIMARY KEY  '
                    'NOT NULL, USERNAME TEXT NOT NULL, '
                    'PASSWORD TEXT NOT NULL)'),
                   ('INSERT IGNORE INTO login_tbl'
                    '(id, username, password)'
                    ' VALUES(1, \'admin\', \'admin\')')]
        with conn.cursor() as cur:
            for sql in queries:
                cur.execute(sql)
        conn.commit()
        conn.close()
        return 'DB Migrated Sucessfully'
    except pymysql.MySQLError as exp:
        return 'MySQLError: {}'.format(exp)
    except Exception as exp:
        return 'ERROR: {}'.format(exp)
