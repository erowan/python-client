import unittest
import mock
from stubolib.testing import DummyModel

class TestStubo(unittest.TestCase):
    
    def setUp(self):
        self.requests = DummyRequests()
        self.requests_patch = mock.patch('stubolib.api.requests', self.requests)
        self.requests_patch.start()
    
    def tearDown(self):
        self.requests_patch.stop() 
        
    def _get_stubo(self, **kwargs):
        from stubolib.api import Stubo
        return Stubo(**kwargs)
    
    def test_bad_method(self):
        stubo = self._get_stubo()
        response = stubo.bogus()
        self.assertEqual(response.status_code, 404)           
   
    def test_method(self):
        stubo = self._get_stubo()
        response = stubo.get_status()
        self.assertEqual(response.json(), {"version": "5.6.4", "data": {"cache_server": {"status": "ok", "local": True}, "info": {"cluster": "rowan"}, "database_server": {"status": "ok"}}})
        self.assertEqual(self.requests.posts, [('http://localhost:8001/stubo/api/get/status', None)])
        
    def test_https(self):
        stubo = self._get_stubo(ssl=True)
        response = stubo.get_status()
        self.assertEqual(response.json(), {"version": "5.6.4", "data": {"cache_server": {"status": "ok", "local": True}, "info": {"cluster": "rowan"}, "database_server": {"status": "ok"}}})
        self.assertEqual(self.requests.posts, [('https://localhost:8001/stubo/api/get/status', None)])
        
    def test_dc(self):
        stubo = self._get_stubo(dc='www.stubo.com')
        response = stubo.get_status()
        self.assertEqual(response.json(), {"version": "5.6.4", "data": {"cache_server": {"status": "ok", "local": True}, "info": {"cluster": "rowan"}, "database_server": {"status": "ok"}}})
        self.assertEqual(self.requests.posts, [('http://www.stubo.com/stubo/api/get/status', None)])    
        

    def test_method_with_arg(self):
        stubo = self._get_stubo()
        response = stubo.get_status(scenario='first')
        self.assertEqual(response.json(), {"version": "5.6.4", "data": {"cache_server": {"status": "ok", "local": True}, "info": {"cluster": "rowan"}, "database_server": {"status": "ok"}, "sessions": [["first_1", "dormant"]]}})
        self.assertEqual(self.requests.posts, [('http://localhost:8001/stubo/api/get/status?scenario=first', None)])

    def test_stubo_error(self):
        from stubolib.api import StuboError
        stubo = self._get_stubo()
        with self.assertRaises(StuboError):
            stubo.get_response(session='foo', data='hello')
            
    def test_get_response_no_match(self):
        from stubolib.api import StuboError
        stubo = self._get_stubo()  
        with self.assertRaises(StuboError):
            response = stubo.get_response(session='bar', data='hello') 
            print 'response=', response 
             
        
class DummyRequests(object):
    
    responses = {
        '/stubo/api/get/status' : ("""
             {"version": "5.6.4", "data": {"cache_server": {"status": "ok", "local": true}, "info": {"cluster": "rowan"}, "database_server": {"status": "ok"}}}
         """, 200),
        '/stubo/api/get/status?scenario=first' : ("""         
            {"version": "5.6.4", "data": {"cache_server": {"status": "ok", "local": true}, "info": {"cluster": "rowan"}, "database_server": {"status": "ok"}, "sessions": [["first_1", "dormant"]]}}        
        """, 200),                 
         '/stubo/api/get/response?session=foo' : ("""
         {"version": "5.6.4", "error" : {"code" : 400, "message" : "session not found - localhost:foo"} }
         """, 400),   
        '/stubo/api/get/response?session=bar' : ("""
         {"version": "5.6.4", "error" : {"code" : 400, "message" : "E017:No matching response found"} }
         """, 400),                 
    }
    
    def __init__(self):
        self.posts = []
    
    def get(self, url):
        return self.post(url, method='GET')     
    
    def post(self, url, data=None, json=None, method='POST'):
        import urlparse
        import json
        parts = urlparse.urlparse(url)
        response = DummyModel(headers={}, content="")
        response.headers["Content-Type"] = 'application/json; charset=UTF-8'
        response.headers["X-Stubo-Version"] = '5.6.4'
        response.json = lambda: json.loads(response.content) 
        uri = '{0}?{1}'.format(parts.path, parts.query)  
        if uri in self.responses.keys():
            response.content, response.status_code = self.responses[uri]
        elif parts.path in self.responses.keys():
            response.content, response.status_code = self.responses[parts.path]    
        else:        
            response.status_code = 404
            response.headers["Content-Type"] = 'text/plain'
            response.content = 'HTTP 404: Not Found'
        self.posts.append((url, data))    
        return response 