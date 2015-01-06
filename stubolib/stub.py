class StubData(object):
     
    def __init__(self, requestBody, responseBody, method="POST", status=200):
        self.payload = dict(request=dict(method=method,
                                         bodyPatterns=[dict(contains=[requestBody])]),
                            response=dict(status=status,
                                          body=responseBody))
        
    def __eq__(self, other):
        if type(other) is type(self):
            return self.payload == other.payload
        return False   
    
    def __ne__(self, other):
        return not self.__eq__(other) 
    
    def request(self):
        return self.payload['request']
    
    def response(self):
        return self.payload['response']
    
    def response_status(self):
        return self.payload['response']['status']
    
    def set_response_body(self, body):
        self.response()['body'] = body 
         
    def response_body(self):
        response = self.response().get('body')
        if response and isinstance(response, basestring):
            response = [response]
        return response    
    
    def delay_policy(self):
        """Returns ``delay policy name``""" 
        return self.response().get('delayPolicy')
             
    def set_delay_policy(self, policy):
         self.response()['delayPolicy'] =  policy      
    
    def request_method(self):
        return self.payload['request']['method']
        
    def contains_matchers(self):
        return self.payload['request']['bodyPatterns'][0]['contains']
    
    def set_contains_matchers(self, matchers):
        self.request()['bodyPatterns'][0]['contains'] = matchers
        
    def number_of_matchers(self):
        return len(self.contains_matchers())
    
    def args(self):
        return self.payload.get('args', {})    
    
    def recorded(self):
        return self.payload.get('recorded')
             
    def set_recorded(self, recorded):
         self.payload['recorded'] = recorded  
         
    def module(self):
        return self.payload.get('module', {})
    
    def set_module(self, module):
         self.payload['module'] = module
         
    def space_used(self):
        return len(unicode(self.payload)) 
    
    def __str__(self):
       return unicode(self.payload)     