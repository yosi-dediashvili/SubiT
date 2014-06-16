from exceptions import InvalidProviderName

class RequestsManager(object):

    def perform_request(domain, url, data, type, more_headers):
    	raise NotImplementedError

    def perform_request_next(domain, url, data, type, more_headers): 
    	raise NotImplementedError

    _instances = {}
    @classmethod
    def get_instance(cls, provider_name):
    	"""
    	A RequestsManager factory that given the same provider name will return
    	the same RequestsManager instance. 

    	This currently isn't a thread safe factory, so in case where to 
    	different threads trying to receive a RequestsManager for a 
    	provider_name that hasn't already been initialzied, will get in to a 
    	race condition, in which they might end up with different instances.

    	>>> a = RequestsManager.get_instance("a")
    	>>> b = RequestsManager.get_instance("a")
    	>>> id(a) == id(b)
    	True
    	>>> b = RequestsManager.get_instance("b")
    	>>> id(b) == id(a)
    	False
    	>>> b = RequestsManager.get_instance("a")
    	>>> id(a) == id(b)
    	True
    	>>> RequestsManager.get_instance("")
        Traceback (most recent call last):
            ...
        InvalidProviderName: provider_name can not be empty.
        >>> RequestsManager.get_instance(1)
        Traceback (most recent call last):
            ...
        InvalidProviderName: provider_name must be a string.
    	"""
    	if not provider_name:
    		raise InvalidProviderName("provider_name can not be empty.")
    	if not isinstance(provider_name, str):
    		raise InvalidProviderName("provider_name must be a string.")

    	if not provider_name in cls._instances:
    		cls._instances[provider_name] = cls()
    	return cls._instances[provider_name]