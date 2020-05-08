# Accessing Amazon S3 without an SDK

### Overview 

This project offers a reference of calling Amazon S3 REST API without using an SDK. 
It supports [Signature Version 4](https://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html) 
for signing AWS requests to S3 API.  Sometimes, a client environment is restricted and 
is unallowed to install external packages or modules. In such a case, installing AWS CLI 
or an AWS SDK such as Boto3 is not feasible. Assuming Python runtime is available (which 
is the case in most Unix-like OS environments), the s3.py program can be modified and 
executed to invoke various S3 APIs. 

### S3 API Invoked

The followin S3 APIs are called from the program: 
- PutObject
- GetObject
- ListObjects
- ListBuckets
- CreateBucket

### Installation 

> **Note**: `s3.py` is written for Python 2.7, as it uses urllib2. If you have Python 3 
installed, you must run the program using the older runtime. 

1. Configure required environment variables 
```bash
export AWS_ACCESS_KEY_ID=[your access key id]
export AWS_SECRET_ACCESS_KEY=[your access key secret]
export AWS_S3_BUCKET=[your bucket name]
```
2. Clone this repo or download s3.py file, and copy to your Linux machine
3. Run the program as `python s3.py` or `python2.7 s3.py` 


