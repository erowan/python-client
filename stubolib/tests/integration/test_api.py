import unittest
from stubolib.testing import DummyModel
from stubolib.stub import StubData

# These integration tests use a testing stub in the stubo server
# which defaults to 'localhost:8001'. Set env var STUBO_DC to change the 
# location and set STUBO_USER & STUBO_PASSWORD for basic auth. 

class TestStubo(unittest.TestCase):
    
    def setUp(self):  
        from stubolib.api import Stubo
        import os
        self.dc = os.getenv('STUBO_DC', 'localhost:8001')
        user = os.getenv('STUBO_USER')
        password = os.getenv('STUBO_PASSWORD')
        self.auth = None
        if user and password:
            self.auth = (user, password)
        
        self.scenario = 'testing'
        self.session_name = '{0}_delme'.format(self.scenario)
        stubo = Stubo(self.dc, auth=self.auth)
        stubo.delete_stubs(scenario=self.scenario)
        response = stubo.begin_session(scenario=self.scenario,
                                       session=self.session_name, mode='record')
        stub = StubData('hello', 'goodbye')
        response = stubo.put_stub(session=self.session_name, json=stub.payload)
        assert response.status_code == 200, 'unable to create test fixture in stubo'  
        response = stubo.end_session(scenario=self.scenario,
                                     session=self.session_name)    
                                                                   
    def tearDown(self):
        from stubolib.api import Stubo
        stubo = Stubo(self.dc, auth=self.auth)
        stubo.delete_stubs(scenario=self.scenario, force=True)
               
    def _get_stubo(self, **kwargs):
        from stubolib.api import Stubo
        return Stubo(dc=self.dc, auth=self.auth, **kwargs)
    
    def test_ctor(self):
        stubo = self._get_stubo()
        self.assertEqual(stubo.dc, self.dc)
               
    def test_get_status(self):
        stubo = self._get_stubo()
        response = stubo.get_status()
        self.assertEqual(response.status_code, 200)
        payload = response.json()['data']
        self.assertEqual(payload['cache_server']['status'], "ok")
        self.assertEqual(payload['database_server']['status'], "ok")
        
    def test_get_status_with_unknown_scenario(self):
        stubo = self._get_stubo()
        response = stubo.get_status(scenario='bogus')
        self.assertEqual(response.status_code, 200)
        payload = response.json()['data']
        self.assertEqual(payload['sessions'], [])
        
    def test_get_status_with_scenario(self):
        stubo = self._get_stubo()
        response = stubo.get_status(scenario='testing')
        payload = response.json()['data']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload['sessions'], [[self.session_name, u'dormant']])
        
    def test_begin_session_playback(self):
        stubo = self._get_stubo()
        response = stubo.begin_session(scenario=self.scenario, session=self.session_name,
                                       mode='playback')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['status'], 'playback')
        
    def test_begin_session_record_dup_error(self):
        from stubolib.api import StuboError
        stubo = self._get_stubo()
        with self.assertRaises(StuboError):
            stubo.begin_session(scenario=self.scenario, 
                                session=self.session_name, mode='record')
    
    def test_begin_session_record(self):
        stubo = self._get_stubo()
        stubo.delete_stubs(scenario=self.scenario)
        response = stubo.begin_session(scenario=self.scenario,
                                       session=self.session_name, mode='record')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['status'], 'record')
        
    def test_end_session(self):
        stubo = self._get_stubo()
        response = stubo.end_session(scenario=self.scenario,
                                     session=self.session_name)
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(response.json()['data']["message"], "Session ended")
        
    def test_get_response_not_playback(self):
        from stubolib.api import StuboError
        stubo = self._get_stubo()
        with self.assertRaises(StuboError):
            stubo.get_response(session=self.session_name, data='hello')
            
    def test_get_response(self):
        stubo = self._get_stubo()
        stubo.begin_session(scenario=self.scenario, session=self.session_name, 
                            mode='playback')
        response = stubo.get_response(session=self.session_name, data='hello')
        self.assertEqual(response.content, 'goodbye') 
        self.assertEqual(response.headers['content-type'],
                         'text/html; charset=UTF-8')  
        
    def test_get_response_not_found(self):
        from stubolib.api import StuboError
        stubo = self._get_stubo()
        stubo.begin_session(scenario=self.scenario, session=self.session_name, 
                            mode='playback')
        with self.assertRaises(StuboError):
            stubo.get_response(session=self.session_name, data='xxx')
                            
    def test_put_stub_legacy(self):
        stubo = self._get_stubo() 
        stubo.delete_stubs(scenario=self.scenario)
        response = stubo.begin_session(scenario=self.scenario,
                                       session=self.session_name, mode='record')
        payload = u'||textMatcher||hello||response||goodbye'
        response = stubo.put_stub(session=self.session_name, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('error' not in response.json())
        
    def test_put_stub(self):
        stubo = self._get_stubo() 
        stubo.delete_stubs(scenario=self.scenario)
        response = stubo.begin_session(scenario=self.scenario,
                                       session=self.session_name, mode='record')
        stub = StubData('hello', 'goodbye')
        response = stubo.put_stub(session=self.session_name, json=stub.payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('error' not in response.json())    
        
    def test_get_delay_policy(self):
        stubo = self._get_stubo()  
        response = stubo.get_delay_policy(name='foo') 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'], {}) 
        
    def test_put_delete_delay_policy(self):
        stubo = self._get_stubo()  
        import uuid
        delay = str(uuid.uuid4())
        response = stubo.put_delay_policy(name=delay, delay_type='fixed', 
                                          milliseconds=2000)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'],
            {"status": "new", "message": "Put Delay Policy Finished", 
             "delay_type": "fixed", "name": "{0}".format(delay)})
        
        response = stubo.delete_delay_policy(name=delay) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'], 
            {"message": "Deleted 1 delay policies from [u'{0}']".format(delay)}) 
        
    def test_get_export(self):
        stubo = self._get_stubo()  
        response = stubo.get_export(scenario=self.scenario)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'].get('scenario'), self.scenario)

    def test_export_and_exec_cmds(self):
        # export testing
        stubo = self._get_stubo()  
        response = stubo.get_export(scenario=self.scenario)
        self.assertEqual(response.status_code, 200)   
        
        # exec cmds file found in the url location of exported testing.tar.gz
        payload = response.json()['data']
        archive = [x[1] for x in payload.get('links') if x[0] == "testing.tar.gz"]
        response = stubo.exec_cmds(cmdfile=archive[0])
        self.assertEqual(response.status_code, 200) 
        
    def test_user_args(self):
        stubo = self._get_stubo()  
        stubo.delete_stubs(scenario=self.scenario)
        session_name = self.session_name+"_template"
        response = stubo.begin_session(scenario=self.scenario,
                                       session=session_name, mode='record')
        matcher = """
        <rollme>                        
           <OriginDateTime>{{roll_date("2014-09-10", as_date(rec_date), as_date(play_date))}}T00:00:00Z</OriginDateTime>
        </rollme>
        """
        response = """
        <response>
        <putstub_arg>{% raw putstub_arg %}</putstub_arg>
        <getresponse_arg>{% raw getresponse_arg %}</getresponse_arg>
        </response>
        """
        stub = StubData(matcher, response)
        response = stubo.put_stub(session=session_name, json=stub.payload,
                                  rec_date='2014-09-10',
                                  putstub_arg='x')
        assert response.status_code == 200, 'unable to create test fixture in stubo'  
        response = stubo.end_session(scenario=self.scenario,
                                     session=session_name)  
        
        stubo.begin_session(scenario=self.scenario, session=session_name, 
                            mode='playback')
        request = """
        <rollme><OriginDateTime>2014-09-12T00:00:00Z</OriginDateTime></rollme>
        """
        response = stubo.get_response(session=session_name,
                                      data=request,
                                      play_date='2014-09-12',
                                      getresponse_arg='y',
                                      tracking_level='full') 
        self.assertEqual("""<response>
        <putstub_arg>x</putstub_arg>
        <getresponse_arg>y</getresponse_arg>
        </response>""".strip(), response.content.strip())               

              
            
            
        
        