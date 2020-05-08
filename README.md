# Accessing Amazon S3 Without SDK

### Overview 

This project offers a reference of calling Amazon S3 REST APIs without using an SDK. 
Sometimes, the client environment is restricted and is unallowed to install external 
packages or modules. Assuming Python runtime is available (which is the case in most
Unix-like OS environments), the s3.py program can be modified and executed to invoke 
various S3 APIs. 

### Installation 

1. Configure required environment variables 
```bash
export AWS_ACCESS_KEY_ID=[your access key id]
export AWS_SECRET_ACCESS_KEY=[your access key secret]
export AWS_S3_BUCKET=[your bucket name]
```
2. Clone this repo or download s3.py file, and copy to your Linux machine
3. Run the program as `python s3.py`
