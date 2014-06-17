from exceptions import InvalidProviderName

class RequestsManager(object):

    def perform_request(self, domain, url, 
        data = '', type = HttpRequestTypes.GET, more_headers = {}):
        """
        Locks the requests mutex, and after that, sends the request. If the 
        mutex is already lock, the function will block until the mutex is 
        released, and we manage to lock it.
        """
        raise NotImplementedError

    def perform_request_next(self, domain, url, 
        data = '', type = HttpRequestTypes.GET, more_headers = {}):
        """
        Perform a request without locking the mutex.
        """
        return self._perform_request(domain, url, data, type, more_headers)

    def _perform_request(self, domain, url, data, type, more_headers = {}, 
        retry = False, is_redirection = False):
        """ 
        Performs http requests. We are using fake user-agents. Use the data arg
        in case you send a "POST" request. Also, you can specify more headers 
        by supplying a dict in the more_headers arg
    
        Url should start with "/". If not, the function adds it.
        """
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
        raise NotImplementedError