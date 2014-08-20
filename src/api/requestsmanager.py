__all__ = ['RequestsManager', 'get_manager_instance']


import logging
logger = logging.getLogger("subit.api.requestsmanager")

from exceptions import InvalidProviderName


class RequestsManager(object):
    def __init__(self):
        from threading import Lock
        self._requests_mutex = Lock()

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '<%s>' % type(self).__name__

    def perform_request(self, url, data = '', more_headers = {}):
        """
        Locks the requests mutex, and after that, sends the request. If the
        mutex is already lock, the function will block until the mutex is
        released, and we manage to lock it.
        """
        logger.debug("perform_request got called.")
        with self._requests_mutex:
            return self._perform_request(url, data, more_headers)

    def perform_request_next(self, url, data = '', more_headers = {}):
        """
        Perform a request without locking the mutex.
        """
        logger.debug("perform_request_next got called.")
        return self._perform_request(url, data, more_headers)

    def _perform_request(self, url, data = '', more_headers = {}):
        """
        Performs a simple http requests. We are using fake user-agents. If the
        data arg is provided, a POST request will be sent instead of GET. Also, 
        you can specify more headers by supplying a dict in the more_headers 
        arg. 

        The data is returned as-is using the urllib2.
        """
        logger.debug(
            "_perform_request got called with: '%s', '%s', %s" % 
            (url, data, more_headers))
        from useragents import get_agent
        import urllib2

        try:
            request = urllib2.Request(url)
            request.add_header("User-Agent", get_agent())
            request.add_header('Connection'      , r'keep-alive')
            request.add_header('X-Requested-With', r'XMLHttpRequest')
            request.add_header('Content-Type'    , r'application/x-www-form-urlencoded')
            request.add_header('Accept-Charset'  , r'utf-8;q=0.7,*;q=0.3')
            request.add_header('Accept-Language' , r'en-US,en;q=0.8')
            request.add_header('Cache-Control'   , r'max-age=0')

            # In case of specifiyng more headers, we add them
            for name, value in more_headers.iteritems():
                request.add_header(name, value)

            logger.debug("Request headers: %s" % request.headers)

            if data:
                request.add_data(data)

            response = ''
            # Try 3 times.
            for error_count in range(1, 4):
                try:
                    logger.debug(
                        "Sending request for the %d time." % error_count)
                    response_obj = urllib2.urlopen(request, timeout=10)
                    response = response_obj.read()
                    # If we got the response, break the loop.
                    break
                except Exception as error:
                    logger.debug("Request failed: %s" % error)
                    # Sleep some time before we request it again.
                    from time import sleep
                    sleep(2)

        except Exception as eX:
            logger.error("Request flow failed: %s" % eX)

        logger.debug("Response length is: %d" % len(response))
        return response

_instances = {}
def get_manager_instance(provider_name):
    """
    A RequestsManager factory that given the same provider name will return
    the same RequestsManager instance.

    If OpenSubtitles's provider is given, OpenSubtitles's request manager 
    instances is returned, and not the default RequestManager.

    This currently isn't a thread safe factory, so in case where to
    different threads trying to receive a RequestsManager for a
    provider_name that hasn't already been initialized, will get in to a
    race condition, in which they might end up with different instances.

    >>> a = get_manager_instance("a")
    >>> b = get_manager_instance("a")
    >>> id(a) == id(b)
    True
    >>> b = get_manager_instance("b")
    >>> id(b) == id(a)
    False
    >>> b = get_manager_instance("a")
    >>> id(a) == id(b)
    True
    >>> get_manager_instance("")
    Traceback (most recent call last):
        ...
    InvalidProviderName: provider_name can not be empty.
    >>> get_manager_instance(1)
    Traceback (most recent call last):
        ...
    InvalidProviderName: provider_name must be a string.
    >>> from api.providers import ProvidersNames
    >>> get_manager_instance(ProvidersNames.OPEN_SUBTITLES.full_name)
    <OpenSubtitlesRequestsManager ...>
    >>> get_manager_instance("some_name")
    <RequestsManager>
    """
    logger.debug("Getting instance for: %s" % provider_name)
    if not provider_name:
        raise InvalidProviderName("provider_name can not be empty.")
    if not isinstance(provider_name, str):
        raise InvalidProviderName("provider_name must be a string.")

    global _instances
    if not provider_name in _instances:
        logger.debug("Instance was yet to be created, creating one.")
        from api.providers import ProvidersNames
        if provider_name == ProvidersNames.OPEN_SUBTITLES.full_name:
            from api.providers.opensubtitles import OpenSubtitlesRequestsManager
            cls_type = OpenSubtitlesRequestsManager
        else:
            cls_type = RequestsManager
        logger.debug("Creating request manager instance of type: %s" % cls_type)
        _instances[provider_name] = cls_type()
    return _instances[provider_name]
