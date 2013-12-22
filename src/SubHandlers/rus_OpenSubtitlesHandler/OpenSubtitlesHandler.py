import xmlrpclib
import os
import struct

import SubiT
import SubResult
import Utils

from SubHandlers.ISubHandler import ISubHandler


class OPENSUBTITLES_PAGES:
    DOMAIN      = 'www.opensubtitles.org'
    API_SERVER  = 'http://api.opensubtitles.org/xml-rpc'

class OpenSubtitlesHandler(ISubHandler):
    HANDLER_NAME    = 'rus@www.opensubtitles.org'
    TOKEN           = None
    SERVER          = None
#    USER_AGENT      = 'SubiTApp %s' % SubiT.VERSION
    USER_AGENT      = 'SubiTApp 1.1.0'
    MovieSearchDict = {'sublanguageid'  : 'rus',
                       'moviehash'      : 0,
                       'moviebytesize'  : 0,
                       'imdbid '        : 0,
                       'query'          : 0 }

    #===========================================================================
    # OpenSubtitles flow for our needs is:
    #    1. If it's a file, send query with Hash Calc
    #    2. If there's no match, Send query with the given movie name
    #    2. Extract distinct list of IMDB's ids for the movies
    #    3. For earch id, group all avaliable movie releases (For VerSum)
    #    4. Using the results, create list of SubMovie items
    #-----------------------------
    #SubMovie Format: MovieCode -> IDMovieImdb
    #                 MovieName -> MovieName   
    #                 VerSum    -> MovieReleaseName
    #===========================================================================
    @staticmethod
    def findmovieslist( subSearch ):
        IDMovieImdb      = 'IDMovieImdb'
        MovieReleaseName = 'MovieReleaseName'
        MovieName        = 'MovieName'
        
        movienamequery = None
        queryresult    = None
        subMovies      = []

        #If it's a real file, we calculate relevant values
        if os.path.exists(subSearch.Path): 
            filesize = os.path.getsize(subSearch.Path)
            filehash = OpenSubtitlesHandler.HashFile(subSearch.Path)
            #format the query for exact match only
            movienamequery = OpenSubtitlesHandler.FormatQuery({'moviehash'      : filehash,
                                                               'moviebytesize'  : str(filesize)})
            queryresult = OpenSubtitlesHandler.GetServer().SearchSubtitles(OpenSubtitlesHandler.GetToken(), 
                                                                           [movienamequery])['data']
            queryresult = queryresult if queryresult is not False else None
        #==================================================
        
        #If we got NoneFile query, or Hash query returned nothing
        if queryresult is None:
            movienamequery = OpenSubtitlesHandler.FormatQuery({ 'query' : subSearch.Query })
            queryresult = OpenSubtitlesHandler.GetServer().SearchSubtitles(OpenSubtitlesHandler.GetToken(), 
                                                                           [movienamequery])['data']
            queryresult = queryresult if queryresult is not False else None
        #==================================================   
        
        #At Last, If we got results
        if queryresult is not None:
                imdbids      = list(set(map(lambda x: (x[IDMovieImdb], x[MovieName]), 
                                            queryresult)).difference()) #Create array of [ImdbId,MovieName]
                for id in imdbids:
                    movienameset = set(id[1].replace('.', ' ').lower().split()) #Set of moviename
                    #No need to go deep on this, simply concatination of all the 
                    #keywords from the releases (without the movie name itsetlf)
                    versums = ' / '.join(reduce(lambda t, c: t.union(c).difference(movienameset),
                                                map(lambda y: set(y[MovieReleaseName].lower().lstrip(':').replace('.', ' ').split()), 
                                                    filter(lambda x: x[IDMovieImdb] == id[0], queryresult))))
                    subMovies.append(SubResult.SubMovie(*id, versum=versums))                

        return subMovies


    #===========================================================================
    # OpenSubtitles flow is quite simple: Query With IMDB's ID, and and map each
    # result to SubVersion Object.
    #-----------------------------
    #SubVersion Format: VerCode   -> IDSubtitleFile
    #                   VerSum    -> MovieReleaseName
    #                   MovieCode -> IDMovieImdb
    #===========================================================================
    @staticmethod
    def findversionslist( subMovie ):
        IDSubtitleFile   = 'IDSubtitleFile'
        MovieReleaseName = 'MovieReleaseName'
        IDMovieImdb      = 'IDMovieImdb'
        subVersions      = []
        
        versionsquery = OpenSubtitlesHandler.FormatQuery({'imdbid' : subMovie.MovieCode})
        queryresult = OpenSubtitlesHandler.GetServer().SearchSubtitles(OpenSubtitlesHandler.GetToken(),
                                                                [versionsquery])['data']
        if queryresult is not False:
            subVersions = map( lambda x: SubResult.SubVersion(  x[IDSubtitleFile], x[MovieReleaseName],
                                                                x[IDMovieImdb]), queryresult)                                      
        return subVersions
    
    @staticmethod
    def getsuburl( subVersion ):
        IDSubtitleFile  = 'IDSubtitleFile'
        ZipDownloadLink = 'ZipDownloadLink'
        domain  = None
        url     = None
        
        subpathquery = OpenSubtitlesHandler.FormatQuery({'imdbid' : subVersion.MovieCode})
        queryresult  = OpenSubtitlesHandler.GetServer().SearchSubtitles(OpenSubtitlesHandler.GetToken(),
                                                                        [subpathquery])['data']
        if queryresult is not False:
            url     = filter(lambda x: x[IDSubtitleFile] == subVersion.VerCode, queryresult)[0][ZipDownloadLink]
            domain  = OPENSUBTITLES_PAGES.DOMAIN
        
        return (domain, url)
        
#===============================================================================
# Class Helpers -> Season Handling
#===============================================================================
    @staticmethod
    def GetToken():
        if not OpenSubtitlesHandler.TOKEN:
            OpenSubtitlesHandler.TOKEN = OpenSubtitlesHandler.GetServer().LogIn(0, 0, 0, 
                                                   OpenSubtitlesHandler.USER_AGENT)['token']
        return OpenSubtitlesHandler.TOKEN
    
    @staticmethod        
    def GetServer():
        if OpenSubtitlesHandler.SERVER is None:
            OpenSubtitlesHandler.SERVER = xmlrpclib.Server(OPENSUBTITLES_PAGES.API_SERVER)
        return OpenSubtitlesHandler.SERVER
    
    @staticmethod
    def FormatQuery( values ):
        query = {}
        query.update(OpenSubtitlesHandler.MovieSearchDict)
        query.update(values)
        return query
    
    @staticmethod
    def HashFile( filepath ): 
        try:  
            longlongformat = 'q'  # long long 
            bytesize = struct.calcsize(longlongformat) 
                    
            f = open(filepath, "rb") 
                
            filesize = os.path.getsize(filepath) 
            hash = filesize 
                
            if filesize < 65536 * 2: 
                   return "SizeError" 
             
            for x in range(65536/bytesize): 
                    buffer = f.read(bytesize) 
                    (l_value,)= struct.unpack(longlongformat, buffer)  
                    hash += l_value 
                    hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                     

            f.seek(max(0,filesize-65536),0) 
            for x in range(65536/bytesize): 
                    buffer = f.read(bytesize) 
                    (l_value,)= struct.unpack(longlongformat, buffer)  
                    hash += l_value 
                    hash = hash & 0xFFFFFFFFFFFFFFFF 
             
            f.close() 
            returnedhash =  "%016x" % hash 
            return returnedhash 
        except(IOError): 
                return "IOError"