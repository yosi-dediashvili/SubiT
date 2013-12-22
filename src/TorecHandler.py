#!/usr/bin/python
import urllib
import gzip
from StringIO import StringIO 
import time

import Utils
from Utils import HttpRequestTypes
from HashCodesHamster import Hamster
import Logs

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

class TOREC_PAGES:
    TICKET   = r'/ajax/sub/guest_time.asp'  #Ticket for sub request
    DOWNLOAD = r'/ajax/sub/download.asp'    #Request of specific sub file
    SEARCH   = r'/ssearch.asp'              #Search for movies
    SUBTITLE = r'/sub.asp'                  #Retrieve movie's subtitles
    DOMAIN   = r'www.torec.net'             #Domain...
    
class TOREC_REGEX:
    #Parser for the TOREC_PAGES.SUBTITLE results
    SUBS_VERSIONS_PARSER  = '(?<=\<option value\=\")([A-F0-9]+)?(?:\" style\="background-color:[#a-z0-9;]+"\> )(.*?)(?=\<\/option\>)'   
    
    #Parser for the TOREC_PAGES.SEARCH results
    SEARCH_RESULTS_PARSER = str(
                                '(?<=<a\shref\=\"sub\.asp\?sub\_id\=)(?P<subid>\d{1,6}?)(?:\"\>)(.*?)(?:\<\/a\>.*?' + 
                                '</span\>\</td\>\<td\>\<bdo dir\=\"ltr\"\>\<span style\=\"font-weight:normal;font-' +
                                'family:Tahoma;text-decoration:none;color:black;font-size:12px;\"\>&nbsp;)(.*?)(?:' +
                                '\<\/span\>\<\/bdo\>\<\/tr\>\<\/table\>\<div\ style\=\"text\-align\:center\;margin' + 
                                '\:0\ auto\;margin\-top\:20px\;\"\>\<a\ href\=\"sub\.asp\?sub\_id\=(?P=subid)\")') 
    
class TorecHandler:
    def __init__(self, guinstance):
        Utils.GuiInstance = guinstance
        
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
        return urllib.urlencode( values )

 #==============================================================================
 #   Send request for the given movie/file name, and return array of found movies, 
 # with low-res versions on each movie result
 #==============================================================================
    @staticmethod
    def getmovieslist( moviename ):
        searchresult = Utils.performrequest( TOREC_PAGES.DOMAIN, 
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
                                    
        if len(results) > 1:
            Utils.writelog( INFO_LOGS.GOT_SEVERAL_RESULTS_FOR_MOVIES )
        elif len(results) == 1:
            Utils.writelog( INFO_LOGS.GOT_ONE_RESULT_FOR_MOVIES ) 
        else:
            Utils.writelog( WARN_LOGS.CANT_GET_RESULTS_FOR_MOVIE_NAME )
        
        return results


    #Send request for the given sub_id, and return two-dim array with each 
	#item as [0 = sub_code, 1=sub_version]
    @staticmethod
    def getmovieversions(sub_id ):
        Utils.writelog( INFO_LOGS.MOVIE_CODE_FOR_SUBVERSIONS_IS % sub_id )
        sub_page = Utils.performrequest(TOREC_PAGES.DOMAIN, 
                                        TOREC_PAGES.SUBTITLE + '?sub_id={0}'.format( sub_id ), 
                                        '', 
                                        HttpRequestTypes.GET, 
                                        '')
        
        results = map(lambda i: [i[0], i[1].lower()],
                      list(Utils.getregexresults( TOREC_REGEX.SUBS_VERSIONS_PARSER, sub_page )))
        
        if len(results) > 1:
            Utils.writelog( INFO_LOGS.GOT_SEVERAL_RESULTS_FOR_SUB_VERSIONS )
        elif len(results) == 1:
            Utils.writelog( INFO_LOGS.GOT_ONE_RESULT_FOR_SUB_VERSIONS ) 
        else:
            Utils.writelog( WARN_LOGS.CANT_GET_RESULTS_FOR_MOVIE_CODE )
        
        return results
        
    
#===============================================================================
#    This function contains the logic for rangking the results returned from 
#	    getmovieversions function Logic is pretty much straight forward:
# 
#    On each item in the array remove the words appearing in the movie name 
#	(the first parameter) If the number of word left is larger or equal to 
#	the previous item, put it bellow him, else, put it before him.
#===============================================================================
    @staticmethod
    def findrelevantsubversions(moviename, sub_versions):
        #Create array from the movie name
        moviename = moviename.replace(' ', '.').split('.')
        for i in moviename: 
            if '-' in i: 
                for l in i.split('-'): moviename.append(l)
        
        #Convert the array to set
        moviename = set( map(str.lower, moviename) )
        #Sorting logic...
        sub_versions.sort( lambda c_ver, n_ver: 
                                    1 if 
                                        len( moviename - set( n_ver.VerSum.replace('-', ' ').split(' ') ) ) 
                                        <
                                        len( moviename - set( c_ver.VerSum.replace('-', ' ').split(' ') ) ) 
                                    else -1
                    )
    
        
        firstitem = set( sub_versions[0].VerSum.replace('-', ' ').split(' ') )
        firstitem.difference_update( moviename )    
        #Check if the first result is certain (full match)
        first_is_certain = ( len(firstitem) == 0 )
                
        return (sub_versions, first_is_certain)
    
    #===========================================================================
    # Containg logic for ranking the movies from the search. logic is same as the
    #    sub_versions ranking.
    #===========================================================================
    @staticmethod
    def findrelevantmovies(moviename, movieslist):
        #Create array from the movie name
        moviename = moviename.replace(' ', '.').split('.')
        for i in moviename: 
            if '-' in i: 
                for l in i.split('-'): moviename.append(l)
        
        #Convert the array to set
        moviename = set( map(str.lower, moviename) )
        #Sorting logic...
        movieslist.sort( lambda c_ver, n_ver: 
                                    1 if 
                                        len( moviename - set( map(str.strip, 
                                                                  n_ver.VerSum.replace('/', ' ').split(' ')) ) ) 
                                        <
                                        len( moviename - set( map(str.strip, 
                                                                  c_ver.VerSum.replace('/', ' ').split(' ')) ) ) 
                                    else -1
                    )
    
        
        firstitem = set( map(str.strip, movieslist[0].VerSum.replace('/', ' ').split(' ')) )
        firstitem.difference_update( moviename )    
        #Check if the first result is certain (full match)
        first_is_certain = ( len(firstitem) == 0 )
        
        Utils.writelog(INFO_LOGS.GOT_EXACT_MATCH_FROM_MOVIE_RANKING if first_is_certain else 
                       INFO_LOGS.NO_EXACT_MATCH_FROM_MOVIE_RANKING_TAKING_FIRST)
        
        return movieslist[0]
        
    
 #==============================================================================
 #   The Final stage - Retrieving the download code
 #   sleep_time is needed in order to pass the test in the site - With each 
 #     guest_code is simply hash representation of current time with each 
 #     subtitle file request, tha guest_code is checked for time waited since 
 #     the guest_code generated - 8 secs is the minimal time to wait in order 
 #     to pass this test.
 #   Logs Removed on purpose - in order to hide the core method
 #==============================================================================
    @staticmethod
    def getsuburl(sub_id, sub_code ):
        sleep_time = 8
        sub_url = ''    

        #In case we fail at the first time, the request is inside a loop 
		#(keep in mind - possible endless loop, but who cares :})
        while sub_url == '':
            (sleep_time, guest_code) = Hamster.getCode()
            sub_req = TorecHandler.buildsubrequest( sub_id, guest_code , sleep_time, sub_code )
            sub_url = Utils.performrequest(TOREC_PAGES.DOMAIN, 
                                           TOREC_PAGES.DOWNLOAD, 
                                           sub_req, 
                                           HttpRequestTypes.POST, 
                                           '')
        return sub_url