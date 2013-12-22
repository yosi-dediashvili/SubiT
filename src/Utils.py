#!/usr/bin/python
#import http
import httplib
import os
import tempfile
import re
import gzip
import zipfile
#import io
#StringIO = io.StringIO
from StringIO import StringIO
import uuid
import sys
import time

import UserAgents
import Logs 
from Settings import Registry

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

MOVIE_EXT   = Registry.getExtList()
SUB_EXT     = [ '.srt', '.sub' ]

DEBUG = True

class HttpRequestTypes:
    GET  = 'GET'  #Retrieve only
    POST = 'POST' #Post data (Retrieve Optional)
    HEAD = 'HEAD' #Check response (same response as get, but without the data)


#===============================================================================
# performs http request, url-> the url without the domain, type-> GET/POST
# retry is needed for subtitle downloading. in some cases, the download 
# is corrupted, with some bytes missing, with this method, it's working
#===============================================================================
def performrequest( domain, url, data, type, more_headers, retry = False ):
    httpcon = httplib.HTTPConnection( domain )
    headers = {}
    #each packet we send will have this params (good for low-profile)
    if not retry:
        headers =   {
                        'Connection'        : r'keep-alive',
                        'User-Agent'        : UserAgents.getAgent(), #The Fake User Agent
                        'X-Requested-With'  : r'XMLHttpRequest',
                        'Content-Type'      : r'application/x-www-form-urlencoded',
                        'Accept'            : r'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Charset'    : r'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                        'Accept-Encoding'   : r'gzip,deflate,sdch',
                        'Accept-Language'   : r'en-US,en;q=0.8',
                        'Cache-Control'     : r'max-age=0'
                    }
    else:
        headers =   {
                        'User-Agent'        : UserAgents.getAgent() #The Fake User Agent
                    }
    
    #in case of specifiyng more headers
    if ( len(more_headers) ):
        headers.update(more_headers)

    httpcon.request( type, url, data, headers )     
    response = httpcon.getresponse( ).read()
    if retry:
        return response
    else:
        try:
            return gzip.GzipFile(fileobj=StringIO(response)).read().replace('\r\n', '')
        except IOError as ex:
            if ex.message == 'Not a gzipped file':
                return response
            else:
                raise ex

#===============================================================================
# Downloand the file from the given url, and saves it at the given location
# domain    = domain name
# url       = url inside the domain
# path      = directory in which the subtitle will be saved (after extraction), 
#             leave empty for current dir)
# file_name = name to give to the subtitle file after extraction. 
#    note: will use the original name if: 
#        a. file_name is empty 
#        b. there is more then one file in the archive
# 
# in case of success, returns true, else false
#===============================================================================
def getfile(domain, url, path, file_name):
    #temp location for the zip file
    file_location       = os.path.abspath(path)                     #Directory path
    dst_file            = os.path.join(file_location, file_name)    #Filename of the moviefile, with sub ext
    defaultextraction   = lambda zf: zf.extractall( file_location ) #Default extraction in case of failure
    
    writelog( INFO_LOGS.STARTING_SUBTITLE_DOWNLOAD_PROCEDURE )
    writelog(INFO_LOGS.DESTINATION_DIRECTORY_FOR_SUBTITLE % file_location)
    
    for retry in range(0,2):
        response    = performrequest( domain, url, '', 'GET', '', retry )
        random_name = os.path.join( tempfile.gettempdir(), str(uuid.uuid4()) + '.zip' ) 
        if (len(response)):       
            try:
                open(random_name, 'wb').write( response )

                with zipfile.ZipFile(random_name, 'r') as zfile:
                    try:
                        #Filter to relevant file extensions
                        filterednamelist = filter(lambda x: x.lower().endswith(tuple(SUB_EXT)), zfile.namelist())
                        #If Archive does'nt is lacking of subtitle files
                        if not filterednamelist:
                            writelog( WARN_LOGS.NO_SUBTITLE_FILES_IN_THE_ARCHIVE )
                        else:
                            #If we don't have one file in archive, we keep original filenames
                            if len(filterednamelist) > 1:
                                writelog( INFO_LOGS.GOT_SEVERAL_FILES_IN_THE_ARCHIVE )
                                #Extracting of the subtitles in the archive, one by one
                                for subfile in filterednamelist:
                                    open(os.path.join(file_location, subfile), 'wb').write(zfile.open(subfile).read())
                                    writelog( INFO_LOGS.EXTRACTED_SUBTITLE_FILE % subfile )
                            #Else mean we got one subtitle (because we already checked for empty...
                            else:
                                #Use the movie filename
                                open(dst_file, 'wb').write(zfile.open(filterednamelist[0]).read())
                                writelog( INFO_LOGS.EXTRACTED_SUBTITLE_FILE % file_name )
                            #On Finish
                            writelog( INFO_LOGS.SUCCESSFULL_EXTRACTION_FROM_ARCHIVE )
                    except:
                        writelog( WARN_LOGS.FAILED_SPECIAL_EXTRACTION_OF_SUBTITLE )
                        defaultextraction(zfile)
                        writelog( INFO_LOGS.SUCCESSFULL_EXTRACTION_FROM_ARCHIVE )
                break #We wont do another iteration if we get success
            except:
                writelog( WARN_LOGS.FAILED_EXTRACTING_SUBTITLE_FILE_FROM_ARCHIVE )
                if not retry: #at first try
                    writelog( INFO_LOGS.TRYING_ANOTHER_METHOD_FOR_DOWNLOADING_SUB )
        else:
            writelog(WARN_LOGS.FAILED_DOWNLOADING_SUBTITLE_ARCHIVE)            
    writelog(INFO_LOGS.FINISHED_SUBTITLE_DOWNLOAD_PROCEDURE)
    
    #Tempfile removal
    try:
        os.remove(random_name)
        return True
    except:
        time.sleep(1)
        try:
            os.remove(random_name)
            return True
        except:
            writelog( WARN_LOGS.FAILED_TEMP_ZIP_FILE_REMOVAL )
            return False
                

#===============================================================================
# Query the content and returns list of all result, in case of multi-group pattern, 
# will return a list of tuples (tuple for each group)
#===============================================================================
def getregexresults( pattern, content, with_groups = False):
    c_pattern = re.compile( pattern )

    if with_groups:
        return map(lambda i: i.groupdict(), re.finditer(c_pattern, content))
    return re.findall( c_pattern, content )

HELP_ARGS = ['/?', '?', '--help', 'help']


def printhelp():
    print ('')
    print ('SubiT - Auto Subtitles Downloader')
    print ('Usage: SubiT.exe [moviename | filename] [Directory]')
    print ('')
    print ('moviename: movie name')
    print ('filename:  name of movie file, with extension')
    print ('Directory: destination directory for storing the subtitle,')
    print ('           omitting this parameter will keep original subtitle filename')
    raw_input()
    sys.exit()

#params[0] is Dir
#params[1] is filename without ext    
def parseargs():
    params = ['','','']

    if len(sys.argv) > 1:
        if sys.argv[1].lower() in HELP_ARGS: 
            printhelp()
        elif len(sys.argv) == 2:
            if os.path.isfile(sys.argv[1]):
                params[:2] = list(os.path.split(sys.argv[1]))
                params[1] = os.path.splitext(params[1])[0] #File name without ext
                params[2] = sys.argv[1]
            elif os.path.isdir(sys.argv[1]):
                params[0] = sys.argv[1]
        else:
            printhelp()
    return params

def askuserforname():
    moviename = askuser( DIRC_LOGS.INSERT_MOVIE_NAME_FOR_QUERY, False )
    if(len(moviename) == 0):
        sys.exit()
    return moviename

GuiInstance = None

#Basic function to print messages (modification will be done later)
def writelog( message ):
    if DEBUG:
        print message
    GuiInstance.writelog( message )

def WriteDebug( message ):
    if DEBUG:
        print message

def askuser( question, canempty, withdialog=False ):
    return GuiInstance.getuserinput(question, canempty, withdialog)
    
def setmoviechoices( choices, message ):     
    GuiInstance.setmoviechoices(choices, message)
    
def setversionchoices( choices, message ):
    return GuiInstance.setversionchoices(choices, message)

def getselection( type ):
    return GuiInstance.getselection( type )
