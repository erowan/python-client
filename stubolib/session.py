from contextlib import contextmanager
import urlparse
import StringIO
import json
from datetime import datetime, date
import logging
from stubo_adapter import StuboAdapter
from api import (
    Stubo, requests, StuboError
)
from stub import StubData

log = logging.getLogger(__name__)

class HTTPCall(object):
    """Represents an HTTP request/response used for recording interactions 
    with an HTTP server"""
    def __init__(self, host=None):
        self.host = host
        self.request_method = self.request_url = self.request_body = None
        self.request_headers = {}
        self.response_status = self.response_reason = None
        self.response_headers = {}
        self.response_body = None
        self._url_parts = None
        
    def __str__(self):
        return "request: {request_method} {request_url} {request_body}, " \
          "{request_headers}\nresponse: {response_status}, {response_reason},"\
          "{response_body}, {response_headers}".format(**self.__dict__)
    
    def __repr__(self):
        return self.__str__() 
    
    @property
    def url_parts(self):
        if not self._url_parts:
            self._url_parts =  urlparse.urlsplit(self.request_url or '')
        return self._url_parts    
          
    
    @property
    def request_query_args(self):
        return urlparse.parse_qs(self.url_parts.query)
            

class Session(object):
    """Creates a Session for record or playback

    When in 'record' mode an instance records all http remote calls. 
    In 'playback' mode all http calls go to stubo. 

    """
    def __init__(self, dc, scenario, session_name, **kwargs):
        """Create a record for the given caller"""
        self._calls = []
        self._current_call = None
        self.requests_session = None
        self.scenario = scenario
        self.session_name = session_name 
        self.delete_stubs = kwargs.pop('delete_stubs', True)
        self.delete_stubs_force = kwargs.pop('delete_stubs_force', False)
        self.mode = kwargs.pop('mode', None)
        self.user_exit = kwargs.pop('user_exit', None)
        self.stubo = Stubo(dc, **kwargs)
        self.extras = kwargs
        self.started_ok = False
    
    def get_requests_session(self):
        self.requests_session = requests.Session()
        auth = self.stubo.get_auth()
        self.requests_session.mount('http://', StuboAdapter(session=self, 
                                                auth_token=auth))
        self.requests_session.mount('https://', StuboAdapter(session=self, 
                                                auth_token=auth))
        return self.requests_session
            
    def start(self):
        assert(self.mode)   
        if self.mode == 'record' and self.delete_stubs:
             self.stubo.delete_stubs(scenario=self.scenario, 
                                     force=self.delete_stubs_force)
        self.stubo.begin_session(scenario=self.scenario,
                                 session=self.session_name,
                                 mode=self.mode)  
        self.started_ok = True               

    def stop(self):
        """Called to stop recording an interaction"""
        if self.started_ok:
            if self.mode == 'record':
                for call_number, call in enumerate(self._calls):
                    stub = StubData(call.request_body, call.response_body,
                                    call.request_method, call.response_status)
                    if self.user_exit:
                        stub.set_module(self.user_exit)
                    
                    self.stubo.put_stub(session=self.session_name,
                                        json=stub.payload,
                                        **call.request_query_args)
            
            self.stubo.end_session(scenario=self.scenario,
                                   session=self.session_name,
                                   mode=self.mode)    

    @contextmanager
    def record_or_play(self, mode=None):
        self.mode = mode
        return self._run()
       
    @contextmanager
    def record(self):
        self.mode = 'record'
        return self._run()
    
    @contextmanager
    def play(self):
        self.mode = 'playback'
        return self._run() 
            
    def _run(self):
        try:
            if not self.mode:
                self.mode = self.discover_mode()  
            self.start()
            yield
        finally:
            self.stop()
    
    def get_session_mode(self):
        payload = self.stubo.get_status(session=self.session_name).json().get(
                                                                    'data')
        status = payload.get('session', {}).get('status', None)
        return status if status else 'notfound'
                                         
    def discover_mode(self):
        session_mode = self.get_session_mode()
        if session_mode == 'notfound':
            return 'record'
        elif session_mode == 'dormant':
            return 'playback'
        else:
            raise StuboError(400, "session '{0}' in '{1}' mode should be " \
                  "dormant".format(self.session_name, session_mode))                 
        
    def record_request(self, request, headers):
        new_call = HTTPCall(host=headers["Stubo-Request-Host"])
        new_call.request_method = request.method
        new_call.request_url = request.url
        new_call.request_body = request.body
        new_call.request_headers = request.headers
        self._current_call = new_call

    def record_response(self, http_response):
        new_call = self._current_call
        if not new_call:
            raise StuboError(400, "Called record response when no request was made.")
        new_call.response_status = http_response.status_code
        new_call.response_reason = http_response.reason
        new_call.response_headers = http_response.headers
        body = http_response.content
        new_call.response_body = body
        self._calls.append(new_call)
        self._current_call = None
        