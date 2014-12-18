from api.requestsmanager import RequestsManager

import logging
logger = logging.getLogger("subit.api.providers.opensubtitles.requestsmanager")

from xmlrpclib import Server as XmlRpcServer
from xmlrpclib import Error as XmlRpcError


__all__ = ['OpenSubtitlesRequestsManager']

API_URL = 'http://api.opensubtitles.org/xml-rpc'
USER_AGENT = "subit-api 1.0.0"
OK_STATUS = "200 OK"


class OpenSubtitlesRequestsManager(RequestsManager):
    """
    A small wrapper for the XmlRpcServer. We store the token, and before each 
    call to a server method, we increase the default socket timeout, and also,
    apply a retry mechanism up to 3 failures.
    """
    def __init__(self):
        super(RequestsManager, self).__init__()
        self.server = XmlRpcServer(API_URL)
        self.token = self.server.LogIn(0, 0, 0, USER_AGENT)['token']

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ("<OpenSubtitlesRequestsManager "
                "server='%(server)s', token='%(token)s'>" % 
                object.__getattribute__(self, '__dict__'))
            
    def __getattribute__(self, name):
        """
        Once called, we check if it's a specific names, if not, we assume that
        the names are xmlrpc's method names. So, instead of returning the real
        methods to the caller, we wrap the method with out function, and return
        it to the user. Once he calls the function, our wrapper gets called.
        """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            logger.debug("Returning a wrapper for: %s" % name)
            def func_wrapper(func):
                def func_exec(*args, **kwargs):
                    logger.debug("Calling %s" % name)
                    import socket
                    socket.setdefaulttimeout(10)
                    max_retries = 3
                    try:
                        for c in range(1, max_retries + 1):
                            try:
                                val = func(self.token, *args, **kwargs)
                                if val:
                                    break
                            except (socket.error, XmlRpcError) as eX:
                                logger.debug("Call failed: %d:%s" % (c, eX))
                                if c <= max_retries:
                                    continue
                                else:
                                    raise eX
                        if val and val['status'] != OK_STATUS:
                            raise Exception(
                                "OpenSubtitles returned error: %s" 
                                % val['status'])
                    except Exception as eX:
                        logger.error("Failed calling %s: %s" % (name, eX))
                        return None
                    logger.debug("Succeeded calling %s." % name)
                    return val
                return func_exec

            # Get the name from the server's instance.
            attr = getattr(object.__getattribute__(self, 'server'), name)
            return func_wrapper(attr)