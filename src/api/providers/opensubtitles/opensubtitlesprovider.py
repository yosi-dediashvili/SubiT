import logging
logger = logging.getLogger("subit.api.providers.opensubtitles")

from api.exceptions import InvalidIMDBIdFormat

from api.providers.providersnames import ProvidersNames
from api.providers.iprovider import IProvider
from api.languages import Languages

from xmlrpclib import Server as XmlRpcServer


__all__ = ['OpenSubtitlesProvider']

API_URL = 'http://api.opensubtitles.org/xml-rpc'
USER_AGENT = "SubiTApp 3.0.0"
OK_STATUS = "200 OK"


class OpenSubtitlesServer(object):
    """
    A small wrapper for the XmlRpcServer. We store the token, and before each 
    call to a server method, we increase the default socket timeout, and also,
    apply a retry mechanism up to 3 failures.
    """
    def __init__(self):
        self.server = XmlRpcServer(API_URL)
        self.token = self.server.LogIn(0, 0, 0, USER_AGENT)['token']

    def __getattribute__(self, name):
        """
        Once called, we check if it's a specific names, if not, we assume that
        the names are xmlrpc's method names. So, instead of returning the real
        methods to the caller, we wrap the method with out function, and return
        it to the user. Once he calls the function, our wrapper gets called.
        """
        import socket
        if name not in ['server', 'token']:
            logger.debug("Returning a wrapper for: %s" % name)
            def func_wrapper(func):
                def func_exec(*args, **kwargs):
                    logger.debug("Calling %s" % name)
                    socket.setdefaulttimeout(10)
                    max_retries = 3
                    try:
                        for c in range(1, max_retries + 1):
                            try:
                                val = func(self.token, *args, **kwargs)
                                if val:
                                    break
                            except socket.error as eX:
                                logger.debug("Call failed: %d:%s" % (c, eX))
                                if c < max_retries:
                                    continue
                                else:
                                    raise eX
                        if val and val['status'] != OK_STATUS:
                            raise Exception("OpenSubtitles returned error: %s" 
                                % val['status'])
                    except Exception as eX:
                        logger.error("Failed calling %s: %s" % (name, eX))
                        return None
                    logger.debug("Succeeded calling %s: %s" % (name, val))
                    return val
                return func_exec
            attr = getattr(object.__getattribute__(self, 'server'), name)
            return func_wrapper(attr)
        else:
            return object.__getattribute__(self, name)


class OpenSubtitlesProvider(IProvider):
    provider_name = ProvidersNames.OPEN_SUBTITLES
    supported_languages = [Languages.ENGLISH]

    def __init__(self, languages, requests_manager):
        """
        The OpenSubtitles provider does not really uses the requests manager,
        so there is not real reason to store its reference.
        """
        self.langauges = languages
        self._languages_in_use = list(
            set(OpenSubtitlesProvider.supported_languages)
            .intersection(set(languages)))
        self.server = OpenSubtitlesServer()

    def get_title_versions(self, input):
        raise NotImplementedError(
            "OpenSubtitlesProvider.get_title_versions")

    def download_subtitle_buffer(self, provider_version):
        raise NotImplementedError(
            "OpenSubtitlesProvider.download_subtitle_buffer")

    def languages_in_use(self):
        return self._languages_in_use

    def calculate_file_hash(self, file_path):
        """
        Calculates the hash value (OpenSubtitles algorithm) for the given file.
        The result is encoded as lowercase hex string. On failures, None is 
        returned.
        """
        import struct
        from os.path import getsize
        logger.debug("Calculating hash value for: %s" % file_path)
        try:  
            long_long_format = 'q'  # long long 
            byte_size = struct.calcsize(long_long_format) 
                    
            file_size = getsize(file_path) 
            logger.debug("File size is: %d" % file_size)
            if file_size < 65536 * 2: 
                raise BufferError("The file size is too small: %s" % filesize)

            hash = file_size 
            with open(file_path, "rb") as f:
                for x in range(65536/byte_size): 
                    buffer = f.read(byte_size) 
                    (l_value,)= struct.unpack(long_long_format, buffer)  
                    hash += l_value 
                    hash = hash & 0xFFFFFFFFFFFFFFFF
                     
                f.seek(max(0,file_size-65536),0) 
                for x in range(65536/byte_size): 
                        buffer = f.read(byte_size) 
                        (l_value,)= struct.unpack(long_long_format, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF 

            returned_hash =  "%016x" % hash 
            logger.debug("Hash value is: %s" % returned_hash)
            return returned_hash 
        except Exception as eX:
            logger.error("Failed calculating the hash: %s" % eX)
            return None

    def get_title_by_imdb_id(self, imdb_id):
        """
        Queries OpenSubtitles using the imdb_id. The ID should be in the format
        of IMDB, and not OpenSubtitles's one. i.e., 'tt<id>' and not '<id>'.
        If succeeded, the function returns either SeriesTitle or MovieTitle 
        depends on what was queried. On failures, None is returned.
        """
        pass

    def get_title_by_hash(self, file_hash, file_size = 0):
        """
        Queries OpenSubtitles for title information using the hash value of the
        file, and possibly the size, in bytes of the same file. If not result
        is returned from the site, None is returned. Otherwise, the function
        construct a Title instance with parameters from the first result that
        was returned from the site.
        """
        pass

    def get_title_by_query(self, query):
        """
        Sends the query as-is to OpenSubtitles, and after it, applies the same 
        logic as the get_title_by_hash() method.
        """
        pass


def imdb_id_format_for_opensubtitles(imdb_id):
        """
        Coverts from IMDB'd format to OpenSubtitles's. Removes any leading zero
        also. Raises an exception if the imdb_id format is invalid.

        >>> imdb_id_format_for_opensubtitles("tt2341621")
        '2341621'
        >>> imdb_id_format_for_opensubtitles("tt0013512")
        '13512'
        >>> imdb_id_format_for_opensubtitles("zzzzzz")
        Traceback (most recent call last):
            ...
        InvalidIMDBIdFormat: The format is invalid: zzzzzz
        >>> imdb_id_format_for_opensubtitles("1512351")
        Traceback (most recent call last):
            ...
        InvalidIMDBIdFormat: The format is invalid: 1512351
        """
        import re
        id_items = re.findall("(tt)(\d+)", imdb_id)
        if len(id_items) != 1 or len(id_items[0]) != 2:
            raise InvalidIMDBIdFormat("The format is invalid: %s" % imdb_id)

        # We convert to int in order to remove any leading zeroes.
        return str(int(id_items[0][1]))