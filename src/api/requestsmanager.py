__all__ = ['RequestsManager', 'get_manager_instance']


import logging
logger = logging.getLogger("subit.api.requestsmanager")

from exceptions import InvalidProviderName


class RequestsManager(object):
    class HttpRequestTypes:
        GET  = 'GET'
        POST = 'POST'
        HEAD = 'HEAD'

    def __init__(self):
        from threading import Lock
        self._requests_mutex = Lock()

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '<%s>' % type(self).__name__

    def perform_request(self, domain, url,
        data = '', type = HttpRequestTypes.GET, more_headers = {}):
        """
        Locks the requests mutex, and after that, sends the request. If the
        mutex is already lock, the function will block until the mutex is
        released, and we manage to lock it.
        """
        logger.debug("perform_request got called.")
        with self._requests_mutex:
            return self._perform_request(domain, url, data, type, more_headers)

    def perform_request_next(self, domain, url,
        data = '', type = HttpRequestTypes.GET, more_headers = {}):
        """
        Perform a request without locking the mutex.
        """
        logger.debug("perform_request_next got called.")
        return self._perform_request(domain, url, data, type, more_headers)

    def _perform_request(self, domain, url, data, type, more_headers = {},
        retry = False, is_redirection = False):
        """
        Performs http requests. We are using fake user-agents. Use the data arg
        in case you send a "POST" request. Also, you can specify more headers
        by supplying a dict in the more_headers arg

        Url should start with "/". If not, the function adds it.
        """
        logger.debug(
            "_perform_request got called with: '%s', '%s', %s, %s, %s, %s, %s" % 
            (domain, url, data, type, more_headers, retry, is_redirection))
        from useragents import get_agent
        import httplib

        response = ''
        if not url.startswith("/"):
            url = "/" + url
        try:
            httpcon = httplib.HTTPConnection(domain, timeout = 10)

            headers = {'User-Agent' : get_agent()}
            # Each packet we send will have this params (good for hiding)
            if not retry:
                headers.update({
                    'Connection'        : r'keep-alive',
                    'X-Requested-With'  : r'XMLHttpRequest',
                    'Content-Type'      : r'application/x-www-form-urlencoded',
                    'Accept-Charset'    : r'utf-8;q=0.7,*;q=0.3',
                    'Accept-Language'   : r'en-US,en;q=0.8',
                    'Cache-Control'     : r'max-age=0'})

            # In case of specifiyng more headers, we add them
            if (len(more_headers)):
                headers.update(more_headers)
            logger.debug("Request headers: %s" % headers)

            got_response = None
            response    = None
            # Try 3 times.
            for error_count in range(1, 4):
                try:
                    logger.debug(
                        "Sending request for the %d time." % error_count)
                    # Before each request, we need to try and connect, because
                    # we're probably not connected (that's way the exception
                    # that we're catching was raised).
                    httpcon.connect()
                    httpcon.request(type, url, str(data), headers)
                    got_response = httpcon.getresponse()
                    response = got_response.read()
                    # If we got the response, break the loop.
                    break
                except Exception as error:
                    logger.debug("Request failed: %s" % error)
                    # Sleep some time before we request it again.
                    from time import sleep
                    sleep(2)
                    # Close it (we're calling connect() again inside the try).
                    httpcon.close()


            # In order to avoid decoding problems, we just convert the bytes to
            # str. The problem is that when we do that, the str preserve the
            # preceding 'b' of the bytes type, so we remove it, and the single
            # quotes and the start and the end of the string
            if got_response:
                try:
                    response = response.decode('utf-8', errors='replace')
                except:
                    response = str(response)[2:-1]
                response = response.replace('\r', '').replace('\n', '')
            # When we get and empty response, it might be a sign that we got a
            # redirection and therefor we check the current url against the
            # requested one. Also, if is_redirection is true, it means that we
            # already got redirection, and therefor we stop the procedure
            if got_response and not response and not is_redirection:
                logger.debug("Got no response, checking if it's redirection.")
                location = got_response.msg.dict['location']
                logger.debug("location value is: %s" % location)
                if url not in location or url == '/':
                    logger.debug("url is different, redirecting.")
                    # Because the location gives us the full address including
                    # the protocol and the domain, we remove them in order to
                    # get the relative url
                    location = \
                        location.replace('http://', '').replace(domain, '')
                    return self._perform_request(
                        domain, location, data, type, is_redirection=True)
                else:
                    logger.debug("No redirection was made.")
        except Exception as eX:
            logger.error("Request flow failed: %s" % eX)

        logger.debug("Response length is: %d" % len(response or ''))
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
