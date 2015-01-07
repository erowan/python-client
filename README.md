Stub-O-Matic Python Client
==========================

[![Build Status](https://travis-ci.org/Stub-O-Matic/python-client.png?branch=master)](https://travis-ci.org/Stub-O-Matic/python-client)

python client language binding

stubo api

- weakly typed API to stubo HTTP JSON API


session api

- be as transparent as possible
- provide context to hide begin/end session calls 
- intercept standard http calls with redirect to stubo for record and playback
- use stubo api internally
- support save of recording to local disk in addition to put/stub stubo server recording 


Example
=======

### Session Example

    from stubolib.session import Session
    session = Session(dc='localhost:8001', scenario='myscenario', 
                      session_name='myscenario_session')
    
    # stubo recording of yahoo http calls
    with session.record():
        response = session.get_requests_session().post(
                "http://weather.yahooapis.com/forecastrss", data='w=1234')
                
    # stubo playback of previously recorded yahoo http calls
    with session.play():
        response = session.get_requests_session().post(
                "http://weather.yahooapis.com/forecastrss", data='w=1234') 
    
    # let stubo work out what you want to do            
    with session.play():
        response = session.get_requests_session().post(
                "http://weather.yahooapis.com/forecastrss", data='w=1234')                          
         

### API Example  
        
     # A wrapper around the stubo api is provided 
     from stubolib.api import Stubo
     
     stubo = Stubo('localhost:8001')
     response = stubo.get_status(scenario='first')
     response = stubo.delete_stubs(scenario='first', mode='force')

Install
=======

(Linux)

    (env) $ git clone git@github.com:Stub-O-Matic/python-client.git
    (env) $ cd stubo_lib/python
    
    Create a python virtual env
    prereqs: virtualenv => $ pip install virtualenv
    
    $ virtualenv --no-site-packages env
    $ source ./env/bin/activate
    
    (env) $ python setup.py develop
    
TESTING
=======

You can run the test suite by running the following command 
(in the project root: stubo-lib)

        (env) $ nosetests stubolib

Use the ``-x`` flag to stop the tests at the first error::

        (env) $ nosetests stubolib -x
        
Or to run a specific test:

        (env) $ nosetests stubo.tests.integration.test_api:TestFoo.test_it          
        

Use the ``--with-coverage`` flag to display a coverage report after
running the tests, this will show you which files / lines have not
been executed when the tests ran::

        (env) $ nosetests stubolib --with-coverage --cover-package=stubolib

  