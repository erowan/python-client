import logging
from argparse import ArgumentParser
import requests
from stubolib import session
 
log = logging.getLogger(__name__)

class Report(object):
    
    def __init__(self, stubo_dc, auth=None, user_exit=None):
        self.stubo_session =  session.Session(dc=stubo_dc, 
                                              scenario='py_example', 
                                              session_name='py_example_1', 
                                              auth=auth, 
                                              user_exit=user_exit)
    
    def run(self, requests_session):
        resp = requests_session.post("http://httpbin.org/post?x=y&a=b", 
                                     data="hello world")
        log.debug(resp.content)    
              
    def record(self):
        with self.stubo_session.record():
            self.run(self.stubo_session.get_requests_session())
            
    def play(self):
        with self.stubo_session.play():
            self.run(self.stubo_session.get_requests_session())    
            
    def record_or_play(self, mode=None):
        with self.stubo_session.record_or_play(mode=mode):
            self.run(self.stubo_session.get_requests_session())          

def run(stubo_dc, auth=None, user_exit=None):
    log.info('run python example 1')
    report = Report(stubo_dc, auth, user_exit=user_exit)
    log.info('straight http call without stubo')
    report.run(requests.Session())
    log.info('stubo recording of http call')
    report.record()
    log.info('stubo playback of previously recorded http call')
    report.play()
    log.info('let stubo work out what you want to do')
    report.record_or_play()   
       
          
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    parser = ArgumentParser(
          description="Stubo example 1"
        )  
    parser.add_argument('-dc', '--datacenter', dest='dc',
                        default='localhost:8001',  help="stubo data center") 
    parser.add_argument('-u', '--user', dest='user', help="stubo user name")
    parser.add_argument('-p', '--password', dest='password', 
                        help="stubo password")
    parser.add_argument('-e', '--exit', dest='exit', help="user exit name")
    args = parser.parse_args()
    auth = None
    if args.user and args.password:
        auth = (args.user, args.password)
    user_exit = None    
    if args.exit:
        user_exit = dict(name=args.exit)
                    
    run(args.dc, auth, user_exit)    