import re
import urllib
import requests
class NoEncodedPlusSession(requests.Session):
    def send(self, *a, **kw):
        # a[0] is prepared request
        a[0].url = a[0].url.replace(urllib.parse.quote("+"), "+")
        return requests.Session.send(self, *a, **kw)

r = NoEncodedPlusSession()

def make_mfc_request(payload, access='read', objects='items', request='search'):
  parameters = {
    'type': 'json',
    'access': access,
    'object': objects,
    'request': request,
    **payload
  }
  request = r.get('https://myfigurecollection.net/api_v2.php', params=parameters)
  return request

def text_to_plus(text):
  text = re.sub(' +',' ', text)
  return text.replace(' ', '+')

def figure_search(text, page=1):
  return make_mfc_request({'keywords': text_to_plus(text), 'page': page})

def get_pictures(username='', page=1):
  return make_mfc_request({'username': username, 'page': page}, objects='pictures', request='search')
