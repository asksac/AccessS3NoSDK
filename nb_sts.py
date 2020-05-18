import sys, os, datetime
import base64, hashlib, hmac
import logging
import xml.dom.minidom

if (sys.version_info > (3, 0)):
  # Python 3
  import urllib
  import urllib.request as urllibx
  import urllib.parse as urlparse
  from urllib.error import HTTPError
else:
  # Python 2
  import urllib
  import urllib2 as urllibx
  import urlparse
  from urllib2 import HTTPError

S3_DEFAULTS = dict(
  region = 'us-east-1', 
  name = 's3', 
  scheme = 'https',
  endpoint = 's3.us-east-1.amazonaws.com'
)

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def build_request(service=S3_DEFAULTS, method='GET', host=None, uri_path='/', query_params={}, headers={}, body=None): 
  t = datetime.datetime.utcnow()
  amzdate = t.strftime('%Y%m%dT%H%M%SZ')
  datestamp = t.strftime('%Y%m%d') # Date in YYYYMMDD format, used in credential scope

  if (method in ['GET', 'DELETE', 'HEAD']): 
    body = ''
  elif not body: 
    body = ''
  payload_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()

  if not host: host = service.get('endpoint')

  headers['host'] = host
  headers['x-amz-content-sha256'] = payload_hash
  headers['x-amz-date'] = amzdate

  canonical_uri = uri_path
  canonical_querystring = "&".join([ k + '=' + urllib.quote_plus(query_params[k]) for k in sorted(query_params.keys()) ])

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
  credential_scope = datestamp + '/' + service.get('region') + '/' + service.get('name') + '/' + 'aws4_request'
  string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
  signing_key = getSignatureKey(secret_key, datestamp, service.get('region'), service.get('name'))
  signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
  authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

  # add our new authorization header
  headers['authorization'] = authorization_header

  request_url = urlparse.urlunparse((service.get('scheme'), service.get('endpoint'), uri_path, None, canonical_querystring, None))
  return (request_url, headers)

def submit_request(method, url, headers, body=None):
  logging.debug('>> Request URL: [' + method + ' ' + url + ']')
  logging.debug('>> Request Headers: ' + str(headers))

  if not body: 
    request = urllibx.Request(url, headers=headers)
  else: 
    body_bytes = body.encode() # required in Python 3, default is utf-8
    request = urllibx.Request(url, data=body_bytes, headers=headers)

  request.get_method = lambda: method 
  try: 
    response = urllibx.urlopen(request)
    res_code = response.getcode()
    res_body = response.read().decode()
  except HTTPError as ex:
    err_reason = ex.reason
    res_code = ex.code
    res_body = ex.read().decode()
    logging.error('!! Response Error: ' + err_reason)

  if res_body.startswith('<?xml'):
    res_body_print = prettyXml(res_body)
  else:
    res_body_print = res_body

  logging.debug('<< Response Code: ' + str(res_code))
  logging.debug('<< Response Data: ' + res_body_print)
  return (res_code, res_body)

def prettyXml(txt):
  dom = xml.dom.minidom.parseString(txt)
  xml_pretty_str = dom.toprettyxml()
  return xml_pretty_str

# -----

sts_service = dict(
  region = 'us-east-1', 
  name = 'sts', 
  scheme = 'https',
  endpoint = 'sts.us-east-1.amazonaws.com'
)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

access_key = os.environ.get('AWS_ACCESS_KEY_ID')
secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

if access_key is None or secret_key is None:
    print('One or more required environment variables not set (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)')
    sys.exit()

# sets logging level for urllib
if sts_service.get('scheme') == 'https': 
  https_logger = urllibx.HTTPSHandler(debuglevel = 1)
  opener = urllibx.build_opener(https_logger) # put your other handlers here too!
  urllibx.install_opener(opener)
else: 
  http_logger = urllibx.HTTPHandler(debuglevel = 1)
  opener = urllibx.build_opener(http_logger) # put your other handlers here too!
  urllibx.install_opener(opener)

# GetObject API call 
print('----- GetSessionToken -----')
gst = dict(
  Version = '2011-06-15',
  Action = 'GetSessionToken', 
  DurationSeconds = '129600' 
)
(u, h) = build_request(service=sts_service, method='GET', query_params=gst)
(code, res) = submit_request('GET', u, h)

if (code == 200):
  dom = xml.dom.minidom.parseString(res)
  accesskeyid = dom.getElementsByTagName('AccessKeyId')[0].firstChild.nodeValue
  secretaccesskey = dom.getElementsByTagName('SecretAccessKey')[0].firstChild.nodeValue
  print('Access Key ID:' + accesskeyid)
  print('Secret Access Key:' + secretaccesskey)
  #ec = subprocess.call(['ls', '-al'])
  ec = subprocess.call(['tpconfig', '-update', '-storage_server', '<SERVER NAME>', '-stype', '<SERVER TYPE>', '-sts_user_id', accesskeyid, '-password', secretaccesskey])
  print('tpconfig returned code: ' + str(ec))

print('----- GetSessionToken -----\n\n')

