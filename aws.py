from project_secrets import BUCKET_NAME, AWS_SECRET_KEY, AWS_ACCESS_KEY
import boto3
import uuid

client = boto3.client(
                    's3',
                    aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY
                    )

S3_LOCATION = f'https://{BUCKET_NAME}.s3.amazonaws.com/'


def upload_file_s3(file, acl="public-read"):
    try:
        filename = f'{uuid.uuid4()}_{file.filename}'

        client.upload_fileobj(
            file,
            BUCKET_NAME,
            filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("File upload didn't work", e)
        return e

    # returns the new img url
    return "{}{}".format(S3_LOCATION, filename)
