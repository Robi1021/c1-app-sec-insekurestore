import json
import os

from app.auth import auth, authenticated, response
from app.aws_utils import Aws
from app.io_cmd import (
    delete,
    ext_check,
    get_download_url,
    read,
    write,
)
from app.static import serve_static

aws = Aws(os.environ['S3_BUCKET'])


def index(event, context):
    try:
        to_serve = event['pathParameters']['file']
    except Exception:
        to_serve = 'index.html'
    return serve_static(to_serve)


def do_auth(event, context):
    body = json.loads(event['body'])
    token = auth(body['username'], body['password'])
    resp = {'token': token}
    if token:
        return response(resp, 200)
    else:
        return response(resp, 401)


@authenticated
def is_valid(event, context):
    body = json.loads(event['body'])
    resp = ext_check(body['name'], aws)
    return response(resp, 200)


@authenticated
def list_bucket(event, context):
    resp = {'items': aws.list_bucket()}
    return response(resp, 200)


@authenticated
def read_file(event, context):
    resp = read(event['queryStringParameters']['file'], aws)
    return response(resp, 200)


@authenticated
def write_file(event, context):
    body = json.loads(event['body'])
    resp = write(body['file'], body['content'], aws)
    return response(resp, 200)


@authenticated
def get_file(event, context):
    resp = get_download_url(
        event['queryStringParameters']['file'],
        event['queryStringParameters']['options'], aws)
    return response(resp, 200)


@authenticated
def delete_file(event, context):
    body = json.loads(event['body'])
    resp = delete(body['file'], aws)
    return response(resp, 200)
