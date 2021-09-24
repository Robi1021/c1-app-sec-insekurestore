import base64
import subprocess
from pathlib import Path


def read(file_name, aws):
    aws.download_file(file_name)
    cnt_bytes = Path('/tmp/{}'.format(file_name)).read_bytes()
    data = str(base64.b64encode(cnt_bytes), 'utf-8')
    return {'content': data}


def get_download_url(file_name, options, aws):
    aws.download_file(file_name)
    cmd = 'ls -l "/tmp/{}" {}'.format(file_name, options)
    mime = subprocess.check_output(
        cmd,
        shell=True).decode('utf-8', errors='ignore')
    url = aws.get_signed_url('get_object', file_name)
    return {'url': url, 'mime': mime}


def ext_check(file_name, aws):
    ext = Path(file_name).suffix
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp',
               '.pdf', '.doc', '.docx', '.txt', '.csv']:
        url = aws.get_signed_url('put_object', file_name)
        return {'mime': 'ok', 'url': url}
    else:
        return {'mime': 'fail'}


def write(file_name, content, aws):
    loc = '/tmp/{}'.format(file_name)
    up_file = Path(loc)
    up_file.write_text(content)
    aws.upload_file(loc, up_file.name)
    return {'status': 'ok', 'location': str(up_file)}


def delete(file_name, aws):
    aws.delete_file(file_name)
    return {'status': 'ok'}
