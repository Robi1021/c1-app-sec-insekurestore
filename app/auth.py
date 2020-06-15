import functools
import json
from datetime import (
    datetime,
    timedelta,
)

import app.db as db

import jwt

import pymysql

secret = 't0ps3cret!'


def response(message, status_code):
    return {
        'statusCode': status_code,
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'origin, authorization',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        },
    }


def check_credentials(user, pswd):
    result = None
    try:
        sql = ('SELECT * from login_tbl WHERE '
               'username=\'{}\' and password=\'{}\'').format(
                   user, pswd)
        conn = pymysql.connect(db.DBHOST,
                               user=db.DB_USERNAME,
                               passwd=db.DB_PASSWORD,
                               db=db.DB_NAME,
                               port=int(db.DBPORT),
                               connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(sql)
            result = cur.fetchone()
        conn.close()
    except Exception as exp:
        print('[ERROR] - {}'.format(exp))
    return result


def auth(username, password):
    token = ''
    if not check_credentials(username, password):
        return token
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(seconds=1800)}
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token.decode('utf-8')


def authenticated(func):
    @functools.wraps(func)
    def auth_check(event, context):
        try:
            headers = event['headers']
            if 'Authorization' in headers:
                auth_header = headers['Authorization'].split()
                res = jwt.decode(auth_header[1], secret, algorithms=['HS256'])
                if res['username']:
                    try:
                        return func(event, context)
                    except Exception as ex1:
                        return response({'error': str(ex1)}, 500)
        except Exception as exp:
            return response({
                'error': 'Unauthorized',
                'message': str(exp)}, 401)
    return auth_check
