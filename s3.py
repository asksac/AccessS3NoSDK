import sys, os, base64, datetime, hashlib, hmac
import logging
import urllib, urllib2, urlparse

http_logger = urllib2.HTTPHandler(debuglevel = 1)
opener = urllib2.build_opener(http_logger) # put your other handlers here too!
urllib2.install_opener(opener)

# sets logging level for urllib3 
#logging.basicConfig(level=logging.DEBUG)
#import http.client
#http.client.HTTPConnection.debuglevel = 1

REGION = 'us-east-1'
SERVICE = 's3'
SCHEME = 'http'

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def build_request(method='GET', host='s3.amazonaws.com', uri_path='/', query_string='', headers={}, body=None): 
  t = datetime.datetime.utcnow()
  amzdate = t.strftime('%Y%m%dT%H%M%SZ')
  datestamp = t.strftime('%Y%m%d') # Date in YYYYMMDD format, used in credential scope

  if (method in ['GET', 'DELETE', 'HEAD']): 
    body = ''
  elif not body: 
    body = ''
  payload_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()

  canonical_uri = uri_path
  canonical_querystring = query_string

  headers['host'] = host
  headers['x-amz-content-sha256'] = payload_hash
  headers['x-amz-date'] = amzdate

  canonical_headers = ''
  signed_headers = ''
  for k in sorted(headers.keys()): 
    canonical_headers += k.lower() + ':' + headers[k] +'\n'
    if not signed_headers:
      signed_headers += k
    else:
      signed_headers += ';' + k

  # create a signed authorization header using AWS Signature Version 4
  canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
  algorithm = 'AWS4-HMAC-SHA256'
  credential_scope = datestamp + '/' + REGION + '/' + SERVICE + '/' + 'aws4_request'
  string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
  signing_key = getSignatureKey(secret_key, datestamp, REGION, SERVICE)
  signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
  authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

  # add our new authorization header
  headers['authorization'] = authorization_header

  request_url = urlparse.urlunparse((SCHEME, host, uri_path, None, query_string, None))
  return (request_url, headers)

def submit_request(method, url, headers, body=None):
  if not body: 
    request = urllib2.Request(url, headers=headers)
  else: 
    request = urllib2.Request(url, data=body, headers=headers)

  request.get_method = lambda: method 
  response = urllib2.urlopen(request)
  return response

# -----

access_key = os.environ.get('AWS_ACCESS_KEY_ID')
secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
s3_bucket = os.environ.get('AWS_S3_BUCKET')

if access_key is None or secret_key is None or s3_bucket is None:
    print('One or more required environment variables not set (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET)')
    sys.exit()

host = s3_bucket + '.s3.us-east-1.amazonaws.com'
object_uri = '/test.txt'

# PutObject API call 
print('----- PutObject -----')
data = 'Welcome to amazing S3!'
(u, h) = build_request(method='PUT', host=host, uri_path=object_uri, body=data, 
                      headers={'x-amz-storage-class': 'REDUCED_REDUNDANCY'})
print('**Request URL = ' + u)
print('**Request Headers = ' + str(h))

res = submit_request('PUT', u, h, data)
print('**Response Code: ' + str(res.getcode()))
print('**Response Data: ' + res.read())

# GetObject API call 
print('----- GetObject -----')
(u, h) = build_request(method='GET', host=host, uri_path=object_uri)
print('**Request URL = ' + u)
print('**Request Headers = ' + str(h))

res = submit_request('GET', u, h)
print('**Response Code: ' + str(res.getcode()))
print('**Response Data: ' + res.read())

# ListObjects API call 
print('----- ListObjects -----')
(u, h) = build_request(method='GET', host=host, uri_path='/', query_string='MaxKeys=10', headers={})
print('**Request URL = ' + u)
print('**Request Headers = ' + str(h))

res = submit_request('GET', u, h)
print('**Response Code: ' + str(res.getcode()))
print('**Response Data: ' + res.read())
