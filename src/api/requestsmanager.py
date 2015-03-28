import logging
import utils
logger = logging.getLogger("subit.api.requestsmanager")

from exceptions import InvalidProviderName


__all__ = ['RequestsManager', 'get_manager_instance']


class RequestsManager(object):
    def __init__(self):
        from threading import Lock
        self._requests_mutex = Lock()

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '<%s>' % type(self).__name__

    def perform_request_text(self, url, data = '', more_headers = {}):
        """
        A simple helper method. Executes perform_request, and than stripes away
        any white spaces (e.g., "\\r\\n\\t").
        """
        from api.utils import strip_white_spaces
        response = self.perform_request(url, data, more_headers)
        return strip_white_spaces(response)

    def perform_request(
        self, url, data = '', more_headers = {}, response_headers = []):
        """
        Locks the requests mutex, and after that, sends the request. If the
        mutex is already lock, the function will block until the mutex is
        released, and we manage to lock it.
        """
        logger.debug("perform_request got called.")
        with self._requests_mutex:
            return self._perform_request(
                url, data, more_headers, response_headers)

    def perform_request_next(
        self, url, data = '', more_headers = {}, response_headers = []):
        """
        Perform a request without locking the mutex.
        """
        logger.debug("perform_request_next got called.")
        return self._perform_request(url, data, more_headers, response_headers)

    def _perform_request(
        self, url, data = '', more_headers = {}, response_headers = []):
        """
        Performs a simple http requests. We are using fake user-agents. If the
        data arg is provided, a POST request will be sent instead of GET. Also,
        you can specify more headers by supplying a dict in the more_headers
        arg. 

        The data is returned as-is using the requests module.
        """
        logger.debug(
            "_perform_request got called with: '%s', '%s', %s" %
            (url, data, more_headers))
        from useragents import get_agent
        import requests

        try:
            headers = {'User-Agent': get_agent()}
            # In case of specifying more headers, we add them
            headers.update(more_headers)

            logger.debug("Request headers: %s" % headers)

            response_content = ''
            returned_headers = {}
            # Try 3 times.
            for error_count in range(1, 4):
                try:
                    logger.debug(
                        "Sending request for the %d time." % error_count)
                    if data:
                        response = requests.post(url, headers=headers, data=data, timeout=10)
                    else:
                        response = requests.get(url, headers=headers, timeout=10)

                    assert response.ok
                    response_content = response.content

                    # Iterate over the requested headers. This way, if no header
                    # was specified, we perform nothing, instead of first 
                    # iterating over the returned headers and checking whether
                    # they're in the response_header.
                    for header in response_headers:
                        if header in response.headers:
                            header_value = response.headers[header]
                            logger.debug("Adding response header: %s=%s"
                                % (header, header_value))
                            returned_headers[header] = header_value
                    # If we got the response, break the loop.
                    break
                except Exception as error:
                    logger.debug("Request failed: %s" % error)
                    # Sleep some time before we request it again.
                    from time import sleep
                    sleep(2)

        except Exception as eX:
            logger.error("Request flow failed: %s" % eX)

        logger.debug("Response length is: %d" % len(response_content))

        if not response_headers:
            return response_content
        else:
            return (response_content, returned_headers)

    def download_file(self, url, data = '', more_headers = {}):
        """
        Downloads the file from the given URL. Returns the name for the 
        downloaded file, and the file buffer itself.

        Tries to extract the file name from the Content-Disposition header, 
        otherwise, the last portion of the URL is returned.
        """
        content, headers = self.perform_request_next(
            url,
            data,
            more_headers,
            response_headers = ["Content-Disposition"])

        if not content:
            from api.exceptions import FailedDownloadingSubtitleBuffer
            raise FailedDownloadingSubtitleBuffer(
                "Failed downloading: %s" % url)

        # Extract the file name from the headers.
        file_name = ""
        if not "Content-Disposition" in headers or \
            'filename' not in headers["Content-Disposition"]:
            
            logger.debug("Failed getting the file name for the download.")
            splitted_url = url.rsplit('/', 1)
            if len(splitted_url) == 2:
                file_name = splitted_url[1]
        else:
            file_name = utils.take_first(utils.get_regex_results(
                headers["Content-Disposition"],
                "(?<=filename\=\").*(?=\")"))

        logger.debug("Downloaded file name is: %s" % file_name)

        return (file_name, content)


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
