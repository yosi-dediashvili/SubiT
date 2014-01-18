import Utils
WriteDebug = Utils.WriteDebug

if Utils.IsPython3():
    from urllib.parse import urlencode
else:
    from urllib import urlencode

import time

from Utils import HttpRequestTypes
from SubProviders.ISubProvider import ISubProvider

from SubStages.MovieSubStage import MovieSubStage
from SubStages.VersionSubStage import VersionSubStage

class TOREC_PAGES:
    TICKET   = r'/ajax/sub/guest_time.asp'  # Ticket for sub request
    DOWNLOAD = r'/ajax/sub/downloadun.asp'  # Request of specific sub file
    SEARCH   = r'/ssearch.asp'              # Search for movies
    SUBTITLE = r'/sub.asp'                  # Retrieve movie's subtitles
    DOMAIN   = r'www.torec.net'             # Domain...

from .HashCodesHamster import Hamster
    
class TOREC_REGEX:
    # Parser for the TOREC_PAGES.SUBTITLE results
    SUBS_VERSIONS_PARSER  = \
        '(?<=\<option value\=\")([A-F0-9]+)?(?:\" style\="background-color:' \
        '[#a-z0-9;]+"\>\s*)(.*?)(?=\<\/option\>)'

    # Parser for the TOREC_PAGES.SEARCH results
    SEARCH_RESULTS_PARSER = \
        '(?<=<a href\=\"/sub\.asp\?sub\_id\=)(?P<MovieCode>\d{1,6}?)(?:\"\>)'  \
        '(?P<MovieName>.*?)(?:\<\/a\>.*?\</span\>\</td\>\<td\>\<bdo dir\='     \
        '\"ltr\"\>\<span style\=\"font-weight:normal;font-family:Tahoma;text'  \
        '-decoration:none;color:black;font-size:12px;\"\>&nbsp;)(?P<VerSum>'   \
        '.*?)(?:\<\/span\>\<\/bdo\>\<\/tr\>\<\/table\>\<div\ style\=\"text\-'  \
        'align\:center\;margin\:0\ auto\;margin\-top\:20px\;\"\>\<a href\=\"/' \
        'sub\.asp\?sub\_id\=(?P=MovieCode)\")'
    
class TorecProvider(ISubProvider):
    PROVIDER_NAME = 'Hebrew - www.torec.net'
    PROVIDER_PNG = 'icon-subprovider-torec.png'

    @staticmethod
    def buildsubrequest(sub_id, guest_code, time_waited, sub_code ):
        """ Function to build well-formatted get request for subtitle. """
        values = {
            # sub_id, same for all sub versions
            'sub_id'        : sub_id,       
            # Are we guests (Not logged in)?
            'sh'            : 'yes',        
            # Ticket from TOREC_PAGES.TICKET
            'guest'         : guest_code,   
            # Specify the number of seconds we waited between the ticket 
            # request and this request (we cant fake this 8 secs is minimum)
            'timewaited'    : time_waited,  
            # Code for the specific sub_version
            'code'          : sub_code      
        }
        return urlencode( values )

#==============================================================================
#   
#==============================================================================
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findMovieSubStageList(cls, query_sub_stage):
        """
        Send request for the given movie/file name, and return array of found 
        movies, with versions summary for each movie.
        """
        moviename = query_sub_stage.query
        searchresult = Utils.PerformRequest( 
            TOREC_PAGES.DOMAIN, 
            TOREC_PAGES.SEARCH, 
            'search={0}'.format(moviename.replace(' ', '+')), 
            HttpRequestTypes.POST, 
            '')
        
        results = Utils.getregexresults(
            TOREC_REGEX.SEARCH_RESULTS_PARSER, searchresult)
        results = dict(
            map(lambda x: [
                        #moviecode
                        x[0],                            
                        [
                            # moviename (remove the hebrew title if it's 
                            # present - the format is <eng_title> / <heb_title>)
                            x[1].split('/')[1].lstrip() if '/' in x[1] else x[1], 
                            # versions
                            x[2]                                
                        ]], results))
        # Return a MovieSubStage constructed from each element.
        return list(map(
            lambda x: 
                MovieSubStage(cls.PROVIDER_NAME, 
                              x[1][0], 
                              x[0], 
                              x[1][1]), 
                results.items()))

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findVersionSubStageList(cls, movie_sub_stage):
        """
        Send requests for versions for the given movie sub stage.
        """
        sub_id = movie_sub_stage.movie_code
        sub_page = Utils.PerformRequest(
            TOREC_PAGES.DOMAIN, 
            TOREC_PAGES.SUBTITLE + '?sub_id={0}'.format( sub_id ), 
            '', 
            HttpRequestTypes.GET, 
            '')
        
        results = map(
            lambda i: 
                [i[0], i[1].lower()],
            list(Utils.getregexresults(
                TOREC_REGEX.SUBS_VERSIONS_PARSER, sub_page))
        )
                
        return list(map(lambda x: 
            VersionSubStage(cls.PROVIDER_NAME, x[1], x[0], sub_id), results))
        
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def getSubtitleContent(cls, version_sub_stage):
        """
        The function will try to retrieve the content of the subtitle 
        represented by the version_sub_stage. 

        The function initiates the Hamster in order to retrieve url for the 
        requested subtitle. If the downloaded subtitle turns out to be a fake
        subtitle provided by Torec, then, we will try again, until we reach the
        max limit.
        """
        sub_id      = version_sub_stage.movie_code
        sub_code    = version_sub_stage.version_code
        sleep_time  = 14
        hamster     = Hamster(sub_id)
        # The fake subtitle file is inside a zip file. The size of the zip file
        # is ~3KB. We set  our limit to 4KB just in case...
        fake_file_size_limit = 4096
        max_fake_downloads = 5

        def _try_download():
            fake_downloads_count = 0
            # Run until we reach maximum fake downloads
            while fake_downloads_count < max_fake_downloads:
                sub_url = ''
                # Until we get a legit sub_url value.
                while sub_url == '':
                    (sleep_time, guest_code) = hamster.getCode()
                    # Build the sub request data
                    sub_req = TorecProvider.buildsubrequest( 
                        sub_id, guest_code , sleep_time, sub_code)
                    # Retrieve the result (the url to the subtitle)
                    sub_url = Utils.PerformRequest(
                        TOREC_PAGES.DOMAIN, TOREC_PAGES.DOWNLOAD, 
                        sub_req, HttpRequestTypes.POST,
                        # Torec made it harder to bypass their defense. We need 
                        # to inject their cookie to the download request in 
                        # order ot get a legit subtitle file.
                        {'Cookie' : 'Torec%5FNC%5Fs=1600;'})

                file_io = Utils.DownloadSubAsBytesIO(
                    TOREC_PAGES.DOMAIN, sub_url, TOREC_PAGES.DOMAIN, None)
                file_size = len(file_io.getvalue())
                # If it's not the fake one.
                if file_size > fake_file_size_limit:
                    WriteDebug('Received real subtitle from Torec!')
                    return file_io
                # If it's a fake, increase the counter.
                else:
                    WriteDebug('Received fake subtitle from Torec!')
                    fake_downloads_count = fake_downloads_count + 1

        file_io = _try_download()
        return file_io
