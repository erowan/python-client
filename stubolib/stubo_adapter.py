"""
stubo_adapter.py
~~~~~~~~~~

Contains an implementation of an HTTP adapter for Requests that calls
Stubo get/response URL when in 'playback' mode and 'records' the 
actual response of a real request when in 'record' mode.
"""
import urlparse
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth

class StuboAdapter(HTTPAdapter):
    """
    A Stubo-aware Transport Adapter for Python Requests. The central
    portion of the API.

    :param session: The Stubo Session to use for this request.
    """

    auth_token = None

    def __init__(self, session, auth_token=None, **kwargs):
        self.session = session
        self.auth_token = auth_token
        super(StuboAdapter, self).__init__(**kwargs)
            
    def get_stubo_headers(self, request):
        parts = urlparse.urlsplit(request.url)
        info = {
          'Stubo-Request-URI'    : request.url,
          'Stubo-Request-Host'   : parts.netloc,
          'Stubo-Request-Method' : request.method, 
        }
        if parts.path:
            info["Stubo-Request-Path"] = parts.path 
        if parts.query:
            info["Stubo-Request-Query"] = parts.query          
        return info      
            
        
    def send(self, request, **kwargs):
        """
        Sends a PreparedRequest object.

        :param request: The Requests :class:`PreparedRequest <PreparedRequest>` object to send.
        """
        headers = self.get_stubo_headers(request)
        if self.session.mode == 'record':
            self.session.record_request(request, headers)                                 
        else:
            request.headers.update(headers)
            request.url = self.proxify(request.url) 
            if self.auth_token:
                # just basic auth at the moment
                HTTPBasicAuth(self.auth_token[0], self.auth_token[1])(request)
                         
        return super(StuboAdapter, self).send(request, **kwargs)


    def build_response(self, request, response):
        """
        Builds a Response object from a urllib3 response. 

        :param request: The Requests :class:`PreparedRequest <PreparedRequest>` object sent.
        :param response: The urllib3 response.
        """
        resp = super(StuboAdapter, self).build_response(request, response)
        if self.session.mode == 'record':
            self.session.record_response(resp)    
        return resp

    def proxify(self, original_url):
        """
        Take a raw url string and turn it into a valid Stubo get/response URL.
        
        Before:
            http://foo.example.com/path
        After:
            http://<stubo_host>/stubo/api/get/response
        """
        parts = urlparse.urlsplit(original_url)
        new_host = self.session.stubo.dc
        if parts.username or parts.password:
            new_host = "{0}:{1}@{2}".format(parts.username, parts.password,
                                            new_host)
        return urlparse.urlunsplit((parts.scheme, new_host, 
            'stubo/api/get/response', 
            'session={0}'.format(self.session.session_name), 
            ''))
