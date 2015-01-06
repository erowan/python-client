import logging
from argparse import ArgumentParser
import requests
from stubolib.api import Stubo, StuboError
from stubolib.stub import StubData
 
log = logging.getLogger(__name__)

class APIExample(object):
    
    def __init__(self, stubo_dc, **kwargs):
        self.stubo =  Stubo(dc=stubo_dc, **kwargs) 
                                          
    def record(self, scenario, session_name):
        self.stubo.delete_stubs(scenario=scenario)
        response = self.stubo.begin_session(scenario=scenario,
                                       session=session_name, 
                                       mode='record')
        #stub = StubData('hello', 'goodbye')
        import json
        stub = StubData(json.dumps(dict(x='hello')), json.dumps(dict(y='goodbye')))
        response = self.stubo.put_stub(session=session_name, json=stub.payload)
        self.stubo.end_session(scenario=scenario,
                               session=session_name) 
        return response   
            
    def play(self, scenario, session_name):
        self.stubo.begin_session(scenario=scenario,
                                 session=session_name, 
                                 mode='playback')
        #response = self.stubo.get_response(session=session_name, data='hello')
        response = self.stubo.get_response(session=session_name, json=dict(x='hello'))
        self.stubo.end_session(scenario=scenario,
                               session=session_name)   
        return response               

def run(stubo_dc, **kwargs):
    try:
        log.info('run python example 1')
        example = APIExample(stubo_dc, **kwargs)
        scenario = 'pyapiexample'
        session_name = 'pyapiexample_1'
        #log.info('stubo recording of http call')
        #response = example.record(scenario, session_name)
        #log.info('record response: {0}'.format(response.json()))
        #log.info('stubo playback of previously recorded http call')
        response = example.play(scenario, session_name)
        log.info('playback response: {0}'.format(response.content))  
    except StuboError, e:
        log.error(e)    
 
       
          
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    parser = ArgumentParser(
          description="Stubo API example"
        )  
    parser.add_argument('-dc', '--datacenter', dest='dc',
                        default='localhost:8001',  help="stubo data center, defaults to localhost:8001") 
    parser.add_argument('-u', '--user', dest='user', help="stubo user name")
    parser.add_argument('-p', '--password', dest='password', 
                        help="stubo password")
    args = parser.parse_args()
    auth = None
    if args.user and args.password:
        auth = (args.user, args.password)                
        run(args.dc, auth=auth)
    else:
        run(args.dc)        