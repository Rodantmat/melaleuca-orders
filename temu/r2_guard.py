"""R2 free-tier guard. Import ok_to_upload(s3,bucket,add_bytes) before any upload; hard caps sit well under the free limits (10 GB storage, 1M class A ops/month)."""
import os, boto3
MAX_BYTES = 5 * 1024**3   # 5 GB = 50% of the 10 GB free storage
MAX_OBJECTS = 20000       # keeps class-A (writes/lists) far below 1M per month

def client():
    return boto3.client("s3", endpoint_url="https://%s.r2.cloudflarestorage.com" % os.environ["R2_ACCOUNT_ID"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"], region_name="auto")

def usage(s3, bucket):
    total = n = 0
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        for o in page.get("Contents", []):
            total += o["Size"]; n += 1
    return total, n

def ok_to_upload(s3, bucket, add_bytes):
    total, n = usage(s3, bucket)
    return (total + add_bytes) <= MAX_BYTES and (n + 1) <= MAX_OBJECTS
