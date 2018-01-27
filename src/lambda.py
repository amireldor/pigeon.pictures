"""
AWS Lambda entry point.
Make the pigeon be fetched, save output to S3.
"""

import boto3
import settings


def main():
    s3 = boto3.resource("s3")
    write_to_me = s3.Object(settings.S3_BUCKET_NAME, settings.S3_OBJECT_KEY)

    response = write_to_me.put(Body="This is a test")

    print(response)


if __name__ == "__main__":
    main()
