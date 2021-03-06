# Accessing Amazon S3 without CLI or SDK

### Overview 

This project offers a reference for calling Amazon S3 REST API without using the AWS CLI or SDK. 
It supports [Signature Version 4](https://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html) 
for signing AWS requests to S3 API.  Sometimes, a client environment is restricted and 
is unallowed to install any external packages or modules. In such a case, installing AWS CLI 
or an AWS SDK such as Boto3 for Python is not feasible. Assuming Python runtime is available (which 
is the case in most Unix-like OS environments), the `s3.py` program from this project can be modified 
and executed to invoke various S3 APIs. 

### Amazon S3 API Invoked

The following S3 APIs are called from the program: 
- PutObject
- GetObject
- ListObjects
- ListBuckets
- CreateBucket
- DeleteBucket

More APIs can be added easily to `s3.py` by referencing the REST API syntax 
[documented here](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html).

### Installation 

> **Note**: `s3.py` has been tested with Python 2.7 and Python 3.7. Please report any issues running the 
code. 

1. Configure required environment variables 
```bash
export AWS_ACCESS_KEY_ID=[your access key id]
export AWS_SECRET_ACCESS_KEY=[your access key secret]
export AWS_S3_BUCKET=[your bucket name]
```
2. Clone this repo or download s3.py file, and copy to your Linux machine
3. Run the program as `python s3.py` or `python2.7 s3.py` 

### License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
- Copyright 2020 &copy; Sachin Hamirwasia