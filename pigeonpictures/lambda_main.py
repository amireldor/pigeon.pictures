"""
AWS Lambda entry point.
Make the pigeon be fetched, save output to S3.
"""

import boto3
from pigeonpictures import settings
from .main import fetch_urls, create_writer


def run(event=None, context=None):
    html = prepare_html()
    write_to_s3(html)


def prepare_html():
    urls = fetch_urls()
    writer = create_writer()
    return writer.render(urls)


def write_to_s3(html):
    s3 = boto3.resource("s3")
    write_to_me = s3.Object(settings.S3_BUCKET_NAME, "index.html")
    response = write_to_me.put(
        Body=html, ACL="public-read", ContentType="text/html", CacheControl="max-age=0"
    )
    print(response)


if __name__ == "__main__":
    run()
