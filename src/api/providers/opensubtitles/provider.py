import logging
logger = logging.getLogger("subit.api.providers.opensubtitles.provider")

from api.exceptions import InvalidIMDBIdFormat
from api.exceptions import InvalidOpenSubtitlesTitleFormat
from api.title import *
from api.providers.providersnames import ProvidersNames
from api.providers.iprovider import IProvider
from api.languages import Languages
from api.identifiersextractor import extract_identifiers

from api import utils


__all__ = ['OpenSubtitlesProvider']


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
        self.server = requests_manager

    def get_title_versions(self, title, version):

        # First, format the dictionary that will be sent to the server.
        query_params = {}
        query_params["query"]         = title.name
        query_params["imdbid"]        = title.imdb_id
        query_params["sublanguageid"] = \
            ','.join([l.iso_name for l in self.langauges])

        if isinstance(title, SeriesTitle):
            if title.season_number and title.episode_number:
                query_params["season"]    = title.season_number
                query_params["episode"]   = title.episode_number
            else:
                query_params["query"] += " %s" % title.episode_name

        subtitle_results = self.server.SearchSubtitles([query_params])
        if not subtitle_results or not subtitle_results['data']:
            logger.error("Failed querying for title %s." % title)
            return None

        subtitle_results = subtitle_results['data']

        # For each result, construct a ProviderVersion instance.
        for subtitle_result in subtitle_result:
            imdb_id = subtitle_result["IDMovieImdb"]
            imdb_id = opensubtitles_id_format_for_imdb(imdb_id)
            name = subtitle_result["MovieName"]
            year = subtitle_result["MovieYear"]

            if subtitle_result["kind"] == "movie":
                title = MovieTitle(name, year, imdb_id)
            elif subtitle_result["kind"] == "episode":
                season_number = int(subtitle_result["SeriesSeason"])
                episode_number = int(subtitle_result["SeriesEpisode"])
                episode_imdb_id = imdb_id
                imdb_id = subtitle_result["SeriesIMDBParent"]
                imdb_id = \
                    opensubtitles_id_format_for_imdb(series_imdb_id)
                name, episode_name = \
                    format_opensubtitles_episode_title_name(name)
                title = SeriesTitle(
                    name, season_number, episode_number, episode_imdb_id, 
                    episode_name, year, imdb_id)

            version_string = subtitle_result["MovieReleaseName"]
            identifiers = extract_identifiers(title, version_string)
            num_of_cds = int(subtitle_result["SubActualCD"])
            attributes = {
                "ZipDownloadLink" : subtitle_result["ZipDownloadLink"]
            }



    def download_subtitle_buffer(self, provider_version):
        logger.debug("Trying to download version: %s" % provider_version)
        download_url = provider_version.attributes["ZipDownloadLink"]
        
        content, headers = self.server.perform_request_next(
            download_url,
            response_headers = ["Content-Disposition"])

        # Either we receive None for the content, or OpenSubtitles's error 
        # message.
        if not content or content == "Incorrect download parameters detected":
            from api.exceptions import FailedDownloadingSubtitleBuffer
            raise FailedDownloadingSubtitleBuffer(
                "Failed downloading: %s" % download_url)

        # Extract the file name from the headers.
        file_name = ""
        if not "Content-Disposition" in headers:
            logger.debug("Failed getting the file name for the zip.")
        else:
            file_name = utils.take_first(utils.get_regex_results(
                "(?<=filename\=\").*(?=\")", 
                headers["Content-Disposition"]))
            logger.debug("Downloaded file name is: %s" % file_name)

        return (file_name, content)

    def languages_in_use(self):
        return self._languages_in_use

    def calculate_file_hash(self, file_path):
        """
        Calculates the hash value (OpenSubtitles algorithm) for the given file.
        The result is encoded as lowercase hex string. On failures, a tuple
        (None, None) is returned. On success, a tuple of (hash, file size) is
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
                raise BufferError("The file size is too small: %s" % file_size)

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
            return (returned_hash, file_size)
        except Exception as eX:
            logger.error("Failed calculating the hash: %s" % eX)
            return (None, None)

    def get_title_by_imdb_id(self, imdb_id):
        """
        Queries OpenSubtitles using the imdb_id. The ID should be in the format
        of IMDB, and not OpenSubtitles's one. i.e., 'tt<id>' and not '<id>'.
        If succeeded, the function returns either SeriesTitle or MovieTitle 
        depends on what was queried. On failures, None is returned. If the 
        imdb_id is malformed, exception is raised.
        """
        logger.debug("Getting title info with imdb id: %s" % imdb_id)
        opensubtitles_id = imdb_id_format_for_opensubtitles(imdb_id)

        response = self.server.GetIMDBMovieDetails(opensubtitles_id)
        if not response:
            logger.error("Got no response for the imdb id.")
            return None

        data = response['data']
        kind = data['kind']
        logger.debug("Movie kind is: %s" % kind)
        if kind == 'movie':
            title = MovieTitle(
                data['title'],
                int(data['year']),
                opensubtitles_id_format_for_imdb(data['id']))
            logger.debug("Resulted movie title is: %s" % title)
            return title
        elif kind == "episode":
            try:
                series_name, episode_name = \
                    format_opensubtitles_episode_title_name(data['title'])
            except Exception as eX:
                logger.error(
                    "Failed formatting the series title: %s" % data['title'])
                return None
            try:
                series_imdb_id = opensubtitles_id_format_for_imdb(
                    data['episodeof'].keys()[0].replace("_", ""))
            except Exception as eX:
                logger.error(
                    "Failed formatting the series imdb id: %s" % data)
                return None
            title = SeriesTitle(
                series_name, 
                int(data['season']),
                int(data['episode']),
                opensubtitles_id_format_for_imdb(data['id']),
                episode_name,
                int(data['year']),
                series_imdb_id)
            logger.debug("Resulted series title is: %s" % title)
            return title
        else:
            logger.error("Received invalid kind value: %s" % kind)
            return None

    def get_release_name_by_hash(self, file_hash, file_size):
        """
        Queries OpenSubtitles for release name information using the hash value 
        of the file, and the size, in bytes of the same file. If no result is 
        returned from the site, None is returned. Otherwise, the function 
        extracts all the MovieReleaseName values from the response, lower() all 
        of them, and returns the one appearing most.
        """
        logger.debug("Getting title info with hash: %s" % file_hash)

        release_names = self._sum_search_results(
            self._do_search_subtitles_with_hash(file_hash, file_size), 
            'MovieReleaseName',
            lambda v: v.strip().lower())

        logger.debug("release_names appearances is: %s" % release_names)
        # Select the release with most appearances.
        release_names_sorted = \
            sorted(release_names.iteritems(), key=lambda i: i[1], reverse=True)
        logger.debug("Sorted result is: %s" % release_names_sorted)
        return release_names_sorted[0][0]

    def get_title_by_hash(self, file_hash, file_size = 0):
        """
        Queries OpenSubtitles for title information using the hash value of the
        file, and possibly the size, in bytes of the same file. If not result
        is returned from the site, None is returned. Otherwise, the function
        construct a Title instance with parameters from the first result that
        was returned from the site.
        """
        logger.debug("Getting title info with hash: %s" % file_hash)
        response = self.server.CheckMovieHash2([file_hash])
        if not response or not response['data']:
            logger.error("Failed getting response for the hash.")
            return None

        opensubtitles_id = response['data'][file_hash][0]['MovieImdbID']
        return self.get_title_by_imdb_id(
            opensubtitles_id_format_for_imdb(opensubtitles_id))

    def get_title_by_query(self, query):
        """
         Then, it iterates over all the 
        results, and looks for the imdb id in each one, and selects the id that 
        appears the most, and sends it to the get_title_by_imdb_id method.
        """
        logger.debug("Getting title info with query: %s" % query)
        
        # A dictionary of {IMDB_ID:Appearances}
        imdb_ids = self._sum_search_results(
            self._do_search_subtitles_with_query(query), 'IDMovieImdb')

        if not imdb_ids:
            logger.error("None of the movies has ID tag.")
            return None

        logger.debug("ID appearances is: %s" % imdb_ids)
        # Select the id with most appearances.
        ids_sorted = \
            sorted(imdb_ids.iteritems(), key=lambda i: i[1], reverse=True)
        logger.debug("Sorted result is: %s" % ids_sorted)
        selected_id = ids_sorted[0][0]
        imdb_id = opensubtitles_id_format_for_imdb(selected_id)
        return self.get_title_by_imdb_id(imdb_id)

    def _do_search_subtitles_with_hash(self, file_hash, file_size):
        return self._do_search_subtitles(
            {"moviehash" : file_hash, "moviebytesize" : str(file_size)})

    def _do_search_subtitles_with_query(self, query):
        """
        Replaces any dot in the query with space (in order to avoid OS's search
        bug where they think that certain strings are extensions, for example, 
        if a string contains 'something.movie.something', it will think that the
        '.movie' is actually a '.mov' extension, and thus, remove it), and then 
        sends the query as-is to OpenSubtitles.
        """
        query = query.replace(".", " ")
        return self._do_search_subtitles({"query":query})

    def _do_search_subtitles(self, params):
        logger.debug("Sending query to SearchSubtitles: %s" % params)
        response = self.server.SearchSubtitles([params])
        if not response or not response['data']:
            logger.error("Failed getting response for the query.")
            return None

        data = response['data']
        logger.debug("Received %d results from the query." % len(data))
        return data

    def _sum_search_results(self, results, key, value_func=lambda v: v):
        keys_appearences = {}
        if not results:
            return keys_appearences

        for result in results:
            if key not in result:
                logger.debug("The key [%s] is missing from the results: %s" 
                    % (key, result))
                continue
            value = value_func(result[key])
            if value not in keys_appearences:
                keys_appearences[value] = 1
            else:
                keys_appearences[value] += 1
        return keys_appearences

def format_opensubtitles_episode_title_name(title_value):
    """
    Splits the title value in OpenSubtitles in case it's in the episode format,
    which is '"<SeriesName>" <EpisodeName>', into a tuple of the same format.
    Raises an exception if the value is not formed in that way.

    >>> format_opensubtitles_episode_title_name(\
        '"The Big Bang Theory" The Pork Chop Indeterminacy')
    ('The Big Bang Theory', 'The Pork Chop Indeterminacy')
    >>> format_opensubtitles_episode_title_name("The Big Bang Theory")
    Traceback (most recent call last):
        ...
    InvalidOpenSubtitlesTitleFormat: \
        The format is invalid: 'The Big Bang Theory'
    """
    import re
    results = re.findall('"(.+?)" (.+)', title_value)
    if len(results) != 1 or len(results[0]) != 2:
        raise InvalidOpenSubtitlesTitleFormat(
            "The format is invalid: '%s'" % title_value)

    return results[0]

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

def opensubtitles_id_format_for_imdb(opensubtitles_id):
    """
    Coverts from OpenSubtitles's imdb id format to IMDB's. Adds leading 
    zeroes in order to generate a 7 chars ids. Raises an exception if the 
    id value is larger than 7 digits.

    >>> opensubtitles_id_format_for_imdb("2341621")
    'tt2341621'
    >>> opensubtitles_id_format_for_imdb("13512")
    'tt0013512'
    >>> opensubtitles_id_format_for_imdb(51223151)
    Traceback (most recent call last):
        ...
    InvalidIMDBIdFormat: ID number is too large: 51223151
    """
    id_str = str(opensubtitles_id)
    if len(id_str) > 7:
        raise InvalidIMDBIdFormat("ID number is too large: %s" % id_str)

    id_str = id_str.rjust(7, "0")
    return "tt" + id_str