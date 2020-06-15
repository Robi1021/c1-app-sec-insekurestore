from pathlib import Path

MIMES = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.ico': 'image/vnd.microsoft.icon',
    '.txt': 'text/plain',
}


def serve_static(file):
    base_dir = Path(__file__).resolve().parents[1]
    serve = Path(base_dir / 'static' / file)
    try:
        mime = MIMES[serve.suffix]
    except Exception:
        mime = 'text/plain'
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': mime,
        },
        'isBase64Encoded': False,
        'body': serve.read_text(),
    }
