from urllib import urlencode
from functools import partial
import logging
import requests

log = logging.getLogger(__name__)

class StuboApiVersion(object):
    V1 = 'stubo/api'

class StuboError(Exception):
    pass

class Stubo(object):
       
    def __init__(self, dc=None, api_version=None, ssl=False, **kwargs): 
        self.dc = dc or 'localhost:8001'
        self.ssl = ssl
        self.api_version = api_version or StuboApiVersion.V1
        self.defaults = kwargs or {}
        
    def get_auth(self):
        return self.defaults.get('auth')    

    def __getattr__(self, name):
        return partial(self, method=name)
    
    def _method_to_path(self, method):
        parts = method.partition('_')
        return '{0}/{1}'.format(parts[0], parts[-1])  
    
    def __call__(self, **kwargs):
        method = self._method_to_path(kwargs.pop('method'))
        data = kwargs.pop('data', None)
        json = kwargs.pop('json', None)
        if self.ssl:
            protocol = 'https'
        else:
            protocol = 'http'
        if kwargs:   
            # single param values only 
            params = urlencode(kwargs, True)
            url = "{protocol}://{dc}/{api_version}/{method}?{params}".format(
              protocol=protocol, dc=self.dc, api_version=self.api_version,
              method=method, params=params)
        else:
            url = "{protocol}://{dc}/{api_version}/{method}".format(
              protocol=protocol, dc=self.dc, api_version=self.api_version,
              method=method)
                          
        return self._post(url, data=data, json=json)      
            
    def _raise_on_error(self, response, url):
        status = response.status_code
        if status != 200 and response.headers.get('X-Stubo-Version') and \
            'application/json' in response.headers.get("Content-Type", {}):
            error = response.json().get('error')
            if error:
                # it's one of ours, reconstruct the error 
                raise StuboError(error.get('code'), error.get('message')) 

    def _post(self, url, data=None, json=None):
        log.debug(u'post url: {0}'.format(url))
        response = requests.post(url, data=data, json=json, **self.defaults)
        self._raise_on_error(response, url)  
        return response 