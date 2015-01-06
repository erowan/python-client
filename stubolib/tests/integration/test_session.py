# These integration tests use a testing stub in the stubo server
# defined as 'dc' below
import unittest
from stubolib.testing import DummyModel

dc = 'localhost:8001'

class TestSession(unittest.TestCase):
    
    def setUp(self):  
        self.scenario = 'testing'
        self.session_name = '{0}_delme'.format(self.scenario)
        self.stubo_server = 'http://{0}'.format(dc)
             
    def tearDown(self):
        from stubolib.api import Stubo
        stubo = Stubo(dc)
        stubo.delete_stubs(scenario=self.scenario, force=True)
               
    def _get_session(self, **kwargs):
        from stubolib.session import Session
        return Session(dc, self.scenario, self.session_name, **kwargs)
    
    def test_ctor(self):
        session = self._get_session()
        self.assertEqual(session.scenario, self.scenario)
        
    def test_record(self):
        session = self._get_session()
        with session.record():
            response = session.get_requests_session().post(
                "http://httpbin.org/post", data="hello world")            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(session._calls), 1)
            import json
            payload = json.loads(session._calls[0].response_body)
            self.assertEqual(payload.get('data'), 'hello world')
            
    def test_play_scenario_not_found(self):
        from stubolib.api import StuboError
        session = self._get_session()
        with self.assertRaises(StuboError):
            with session.play():
                session.get_requests_session().post(
                      "http://httpbin.org/post", data="hello world") 
                
    def test_record_and_play(self):
        session = self._get_session()
        with session.record():
            response = session.get_requests_session().post(
                  "http://httpbin.org/post", data="hello world")             
            self.assertEqual(response.status_code, 200)
            
        with session.play():
            response = session.get_requests_session().post(
                  "http://httpbin.org/post", data="hello world")           
            self.assertEqual(response.status_code, 200) 
            
    def test_record_or_play(self):
        session = self._get_session()
        with session.record_or_play():
            response = session.get_requests_session().post(
                 "http://httpbin.org/post", data="hello world")              
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(session._calls), 1)
            
    def test_record_with_exit(self):
        import json
        session = self._get_session(user_exit=dict(name='foo'))
        with session.record():
            response = session.get_requests_session().post(
                "http://httpbin.org/post", data="hello world")            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(session._calls), 1) 
            payload = json.loads(session._calls[0].response_body)
            self.assertEqual(payload.get('data'), 'hello world')
        response = session.stubo.get_stublist(scenario=self.scenario)   
        self.assertEqual(response.json()['stubs'][0].get('module'),
                         dict(name='foo'))
                     
                   
                                    
           
            