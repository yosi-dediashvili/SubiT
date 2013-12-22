#!/usr/bin/python
import Utils

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
    TICKET   = r'/ajax/sub/guest_time.asp'  #Ticket for sub request
    DOWNLOAD = r'/ajax/sub/download.asp'    #Request of specific sub file
    SEARCH   = r'/ssearch.asp'              #Search for movies
    SUBTITLE = r'/sub.asp'                  #Retrieve movie's subtitles
    DOMAIN   = r'www.torec.net'             #Domain...

from .HashCodesHamster import Hamster
    
class TOREC_REGEX:
    #Parser for the TOREC_PAGES.SUBTITLE results
#    SUBS_VERSIONS_PARSER  = '(?<=\<option value\=\")([A-F0-9]+)?(?:\" style\="background-color:[#a-z0-9;]+"\> )(.*?)(?=\<\/option\>)'   
    SUBS_VERSIONS_PARSER  = '(?<=\<option value\=\")([A-F0-9]+)?(?:\" style\="background-color:[#a-z0-9;]+"\>\s*)(.*?)(?=\<\/option\>)'   


    
    #Parser for the TOREC_PAGES.SEARCH results
    SEARCH_RESULTS_PARSER = str(
                                
                                '(?<=<a\shref\=\"sub\.asp\?sub\_id\=)(?P<MovieCode>\d{1,6}?)(?:\"\>)(?P<MovieName>.*?)(?:\<\/a\>.*?' + 
                                '</span\>\</td\>\<td\>\<bdo dir\=\"ltr\"\>\<span style\=\"font-weight:normal;font-' +
                                'family:Tahoma;text-decoration:none;color:black;font-size:12px;\"\>&nbsp;)(?P<VerSum>.*?)(?:' +
                                '\<\/span\>\<\/bdo\>\<\/tr\>\<\/table\>\<div\ style\=\"text\-align\:center\;margin' + 
                                '\:0\ auto\;margin\-top\:20px\;\"\>\<a\ href\=\"sub\.asp\?sub\_id\=(?P=MovieCode)\")') 
    
class TorecProvider(ISubProvider):
    PROVIDER_NAME = 'Hebrew - www.torec.net'
    PROVIDER_PNG = 'icon-subprovider-torec.png'
    def __init__(self):
        Hamster()
#===========================================================================
# Function to build well-formatted get request for subtitle
#===========================================================================
    @staticmethod
    def buildsubrequest(sub_id, guest_code, time_waited, sub_code ):
        values ={
                    'sub_id'        : sub_id,       #sub_id, same for all sub versions
                    'sh'            : 'yes',        #Are we guests?
                    'guest'         : guest_code,   #Ticket from TOREC_PAGES.TICKET
                    'timewaited'    : time_waited,  #Specify the number of seconds we waited between 
                                                        #the ticket request and this request (we cant 
                                                        #fake this 8 secs is minimum)
                    'code'          : sub_code      #Code for the specific sub_version
                }
        return urlencode( values )

#==============================================================================
#   Send request for the given movie/file name, and return array of found movies, 
# with low-res versions on each movie result
#==============================================================================
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findMovieSubStageList(cls, query_sub_stage):
        moviename = query_sub_stage.query
        searchresult = Utils.PerformRequest( TOREC_PAGES.DOMAIN, 
                                             TOREC_PAGES.SEARCH, 
                                             'search={0}'.format(moviename.replace(' ', '+')), 
                                             HttpRequestTypes.POST, 
                                             '' )
        
        results = Utils.getregexresults(TOREC_REGEX.SEARCH_RESULTS_PARSER, searchresult)
        results = dict(map(lambda x: [x[0],                             #moviecode
                                                                        #moviename
                                      [x[1].split('/')[1].lstrip() if '/' in x[1] else x[1],       
                                       x[2]                             #versions
                                       ]], results))
        return list(map(lambda x: MovieSubStage(cls.PROVIDER_NAME, x[1][0], x[0], x[1][1]), results.items()))

    #Send request for the given sub_id, and return two-dim array with each
    #item as [0 = sub_code, 1=sub_version]
    
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findVersionSubStageList(cls, movie_sub_stage):
        sub_id = movie_sub_stage.movie_code
        sub_page = Utils.PerformRequest(TOREC_PAGES.DOMAIN, 
                                        TOREC_PAGES.SUBTITLE + '?sub_id={0}'.format( sub_id ), 
                                        '', 
                                        HttpRequestTypes.GET, 
                                        '')
        
        results = map(lambda i: [i[0], i[1].lower()],
                      list(Utils.getregexresults( TOREC_REGEX.SUBS_VERSIONS_PARSER, sub_page )))
                
        return list(map(lambda x: VersionSubStage(cls.PROVIDER_NAME, x[1], x[0], sub_id), results))
        
#==============================================================================
#   The Final stage - Retrieving the download code
#   sleep_time is needed in order to pass the test in the site - With each 
#     guest_code is simply hash representation of current time with each 
#     subtitle file request, tha guest_code is checked for time waited since 
#     the guest_code generated - 8 secs is the minimal time to wait in order 
#     to pass this test.
#   Logs Removed on purpose - in order to hide the core method
#==============================================================================
    
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def getSubtitleUrl(cls, version_sub_stage):
        sub_id      = version_sub_stage.movie_code
        sub_code    = version_sub_stage.version_code
        sleep_time  = 8
        sub_url     = ''    

        #In case we fail at the first time, the request is inside a loop
        #(keep in mind - possible endless loop, but who cares :})
        while sub_url == '':
            (sleep_time, guest_code) = Hamster.getCode()
            sub_req = TorecProvider.buildsubrequest( sub_id, guest_code , sleep_time, sub_code )
            sub_url = Utils.PerformRequest(TOREC_PAGES.DOMAIN, 
                                           TOREC_PAGES.DOWNLOAD, 
                                           sub_req, 
                                           HttpRequestTypes.POST, 
                                           '')
        return (TOREC_PAGES.DOMAIN, sub_url, TOREC_PAGES.DOMAIN)
