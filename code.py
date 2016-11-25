import time, hmac, base64, hashlib, json, urllib, httplib
from urlparse import urlparse
import pandas as pd

class NotificationHub:
  def __init__(self, ConnectionString=None, HubName=None, debug=0):
    self.Endpoint    = None
    self.HubName     = HubName
    self.Debug       = debug

    parts = ConnectionString.split(';')
    for part in parts:
      if part.startswith('Endpoint'):
        self.Endpoint = 'https' + part[11:]
      if part.startswith('SharedAccessKeyName'):
        self.SasKeyName = part[20:]
      if part.startswith('SharedAccessKey'):
        self.SasKeyValue = part[16:]

  def get_expiry(self, secs):
    return int(round(time.time() + secs))

  def encode_base64(self, data):
    return base64.b64encode(data)

  def sign_string(self, to_sign):
    key = self.SasKeyValue.encode('utf-8')
    tos = to_sign.encode('utf-8')
    sig = hmac.HMAC(key, tos, hashlib.sha256)
    dig = sig.digest()
    enc = self.encode_base64(dig)
    return enc

  def sas_token(self, uri):
    target_uri = self.Endpoint + self.HubName + uri
    my_uri = urllib.quote(target_uri, '').lower()
    expiry = str(self.get_expiry(300))
    tos = my_uri + '\n' + expiry
    sig = urllib.quote(self.sign_string(tos))
    fmt = 'SharedAccessSignature sig={0}&se={1}&skn={2}&sr={3}'
    tok = fmt.format(sig, expiry, self.SasKeyName, my_uri)
    return tok

  def send_notification(self, message, msgtype='template'):
    rel_uri = '/messages?api-version=2013-10'
    url = self.Endpoint + self.HubName + rel_uri
    o = urlparse(url)
    headers = {
      'Content-Type': 'application/json;charset=utf-8',
      'ServiceBusNotification-Format': msgtype,
      'Authorization': self.sas_token(rel_uri),
      'Host': o.hostname,
      'Content-Length': len(message),
      'X-WNS-Type': 'wns/toast'
    }
    if self.Debug > 0:
      print "--- REQUEST ---"
      print "URI: " + url
      print "Headers: " + json.dumps(headers)
      print "--- END REQUEST ---"
    conn = httplib.HTTPSConnection(o.hostname, o.port)
    conn.set_debuglevel(self.Debug)
    conn.request('POST', url, message, headers)
    response = conn.getresponse()
    if self.Debug > 0:
      print "--- RESPONSE ---"
      print str(response.status) + " " + response.reason
      print response.read()
      print "--- END RESPONSE ---"
    conn.close()

def azureml_main(dataframe1 = None, dataframe2 = None):
    threshold = 400
    cs = '<SPECIFY CONNECTION STRING HERE>'
    hubname = 'iot-demo-notification-hub'
    nh = NotificationHub(cs, hubname, debug = 0)
    for index, row in dataframe1.iterrows():
      pred = row['Predicted_Value']
      price = row['Price']
      if pred > threshold:
        wns_payload = """<toast><visual><binding template=\"ToastText01\"><text id=\"1\">Alert!</text></binding></visual></toast>"""
        nh.send_notification(wns_payload, 'windows')
        break
    return dataframe1