import boto3


class Aws:
    def __init__(self, bucket):
        self.s3 = boto3.client('s3')
        self.bucket = bucket

    def get_signed_url(self, method, key):
        return self.s3.generate_presigned_url(
            ClientMethod=method,
            Params={
                'Bucket': self.bucket,
                'Key': key,
            },
        )

    def list_bucket(self):
        items = []
        bkt = self.s3.list_objects(Bucket=self.bucket)
        if 'Contents' in bkt:
            for item in bkt['Contents']:
                items.append(item['Key'])
        return items

    def download_file(self, key):
        try:
            self.s3.download_file(self.bucket, key, '/tmp/{}'.format(key))
        except Exception:
            pass

    def upload_file(self, file, key):
        self.s3.upload_file(file, self.bucket, key)

    def delete_file(self, key):
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
        except Exception:
            pass
