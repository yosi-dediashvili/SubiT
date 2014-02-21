import Utils

from xmlrpclib import Server as XmlRpcServer

import os
import struct
from functools import reduce

import SubiT
from SubStages.MovieSubStage import MovieSubStage
from SubStages.VersionSubStage import VersionSubStage


WriteDebug = Utils.WriteDebug

from SubProviders.ISubProvider import ISubProvider


class OPENSUBTITLES_LANGUAGES:
    HEBREW      = 'heb'
    ENGLISH     = 'eng'
    RUSSIAN     = 'rus'
    NORWEGIAN   = 'nor'
    SPANISH     = 'spa'
    TURKISH     = 'tur'
    SLOVAK      = 'slo'
    CZECH       = 'cze'
    GLOBAL      = 'all'

class OPENSUBTITLES_PAGES:
    DOMAIN      = 'www.opensubtitles.org'
    API_SERVER  = 'http://api.opensubtitles.org/xml-rpc'
    LANGUAGE    = OPENSUBTITLES_LANGUAGES.GLOBAL

class IOpenSubtitlesProvider(ISubProvider):
    PROVIDER_NAME   = 'Base - www.opensubtitles.org'
    PROVIDER_PNG    = 'icon-subprovider-opensubtitles.png'
    TOKEN           = None
    SERVER          = None
    USER_AGENT      = ''
    MovieSearchDict = {}

    def __init__(self):
        IOpenSubtitlesProvider.USER_AGENT = 'SubiTApp %s' % SubiT.VERSION
        IOpenSubtitlesProvider.MovieSearchDict = {   'sublanguageid'  : OPENSUBTITLES_PAGES.LANGUAGE,
                                                    'moviehash'      : 0,
                                                    'moviebytesize'  : 0,
                                                    'imdbid '        : 0,
                                                    'query'          : 0 }


    @staticmethod
    def findByHash(path, get_movie_name_only = False):
        """Find results using the hash value of the file"""
        MovieName   = 'MovieName'
        queryresult = None
        #is_episode  = False


        if os.path.exists(path):
            filesize = os.path.getsize(path)                #calculated file size
            filehash = IOpenSubtitlesProvider.HashFile(path)  #calculated file hash
            #format the query for exact match only
            movienamequery = IOpenSubtitlesProvider.FormatQuery({'moviehash'      : filehash,
                                                               'moviebytesize'  : str(filesize)})
            try:
                #send the query
                queryresult = IOpenSubtitlesProvider.GetServer().SearchSubtitles(IOpenSubtitlesProvider.GetToken(), 
                                                                               [movienamequery])['data']
            except Exception as eX:
                WriteDebug(eX)

            if queryresult is not False:
                is_episode = queryresult[0]['MovieKind'] == 'episode'
                if get_movie_name_only: 
                    if is_episode:
                        res = queryresult[0][MovieName]
                        queryresult = Utils.getregexresults('"(.*?)"', res)[0]
                    else:
                        queryresult = queryresult[0][MovieName] #set only the moviename
                else: queryresult = queryresult #set the whole result
            else:
                queryresult = None

        return queryresult#, is_episode

    @staticmethod
    def findByFileName(fileName, get_movie_name_only = False):
        """find results using the file name"""
        MovieName   = 'MovieName'
        #is_episode  = False

        movienamequery = IOpenSubtitlesProvider.FormatQuery({ 'query' : fileName })
        try:
            #send the query
            queryresult = IOpenSubtitlesProvider.GetServer().SearchSubtitles(IOpenSubtitlesProvider.GetToken(), 
                                                                           [movienamequery])['data']
        except Exception as eX:
            WriteDebug(eX)

        if queryresult is not False:
            is_episode = queryresult[0]['MovieKind'] == 'episode'
            if get_movie_name_only: 
                if is_episode:
                    res = queryresult[0][MovieName]
                    queryresult = Utils.getregexresults('"(.*?)"', res)[0]
                else:
                    queryresult = queryresult[0][MovieName] #set only the moviename
            else: queryresult = queryresult #set the whole result
        else:
            queryresult = None

        return queryresult

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
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findMovieSubStageList(cls, query_sub_stage):
        IDMovieImdb      = 'IDMovieImdb'
        MovieReleaseName = 'MovieReleaseName'
        MovieName        = 'MovieName'
        
        movienamequery = None
        queryresult    = None
        _movie_sub_stages = []

        #If it's a real file, we calculate relevant values
        if os.path.exists(query_sub_stage.full_path): 
            filesize = os.path.getsize(query_sub_stage.full_path)
            filehash = IOpenSubtitlesProvider.HashFile(query_sub_stage.full_path)
            #format the query for exact match only
            movienamequery = IOpenSubtitlesProvider.FormatQuery({'moviehash'      : filehash,
                                                               'moviebytesize'  : str(filesize)})

            try:
                queryresult = IOpenSubtitlesProvider.GetServer().SearchSubtitles(IOpenSubtitlesProvider.GetToken(), 
                                                                                [movienamequery])['data']
            except Exception as eX:
                WriteDebug(eX)

            queryresult = queryresult if queryresult is not False else None
        #==================================================
        
        #If we got NoneFile query, or Hash query returned nothing
        if queryresult is None:
            movienamequery = IOpenSubtitlesProvider.FormatQuery({ 'query' : query_sub_stage.query })

            try:
                queryresult = IOpenSubtitlesProvider.GetServer().SearchSubtitles(IOpenSubtitlesProvider.GetToken(), 
                                                                                [movienamequery])['data']
            except Exception as eX:
                WriteDebug(eX)
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
                    _versions_sum = ' / '.join(reduce(lambda t, c: t.union(c).difference(movienameset),
                                                map(lambda y: set(y[MovieReleaseName].lower().lstrip(':').replace('.', ' ').split()), 
                                                    filter(lambda x: x[IDMovieImdb] == id[0], queryresult))))

                    _movie_name = id[1]
                    _movie_code = id[0]
                    _movie_sub_stages.append(MovieSubStage\
                        (cls.PROVIDER_NAME, _movie_name, _movie_code, _versions_sum))
        return _movie_sub_stages


    #===========================================================================
    # OpenSubtitles flow is quite simple: Query With IMDB's ID, and and map each
    # result to SubVersion Object.
    #-----------------------------
    #SubVersion Format: VerCode   -> IDSubtitleFile
    #                   VerSum    -> MovieReleaseName
    #                   MovieCode -> IDMovieImdb
    #===========================================================================
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findVersionSubStageList(cls, movie_sub_stage):
        IDSubtitleFile   = 'IDSubtitleFile'
        MovieReleaseName = 'MovieReleaseName'
        IDMovieImdb      = 'IDMovieImdb'
        _version_sub_stages = []
        
        versionsquery = IOpenSubtitlesProvider.FormatQuery({'imdbid' : movie_sub_stage.movie_code})

        try:
            queryresult = IOpenSubtitlesProvider.GetServer().SearchSubtitles(IOpenSubtitlesProvider.GetToken(),
                                                                            [versionsquery])['data']
        except Exception as eX:
            WriteDebug(eX)

        if queryresult is not False:
            _version_sub_stages = map(lambda x: VersionSubStage(cls.PROVIDER_NAME, 
                x[MovieReleaseName],  x[IDSubtitleFile], x[IDMovieImdb]), queryresult)

        return list(_version_sub_stages)
    
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def getSubtitleContent(cls, version_sub_stage):
        IDSubtitleFile  = 'IDSubtitleFile'
        ZipDownloadLink = 'ZipDownloadLink'
        domain  = None
        url     = None
        
        subpathquery = IOpenSubtitlesProvider.FormatQuery({'imdbid' : version_sub_stage.movie_code})

        try:
            queryresult  = IOpenSubtitlesProvider.GetServer().SearchSubtitles(IOpenSubtitlesProvider.GetToken(),
                                                                            [subpathquery])['data']
        except Exception as eX:
                WriteDebug(eX)

        if queryresult is not False:
            url     = Utils.myfilter(lambda x: x[IDSubtitleFile] == version_sub_stage.version_code, queryresult,
                                     lambda f: f[ZipDownloadLink], True)
            domain  = OPENSUBTITLES_PAGES.DOMAIN
        
        return Utils.DownloadSubAsBytesIO(domain, url, domain, None)
        
#===============================================================================
# Class Helpers -> Session Handling
#===============================================================================
    @staticmethod
    def GetToken():
        if not IOpenSubtitlesProvider.TOKEN:
            IOpenSubtitlesProvider.TOKEN = IOpenSubtitlesProvider.GetServer().LogIn(0, 0, 0, 
                                                   IOpenSubtitlesProvider.USER_AGENT)['token']
        return IOpenSubtitlesProvider.TOKEN
    
    @staticmethod        
    def GetServer():
        if IOpenSubtitlesProvider.SERVER is None:
            IOpenSubtitlesProvider.SERVER = XmlRpcServer\
                (OPENSUBTITLES_PAGES.API_SERVER)
        return IOpenSubtitlesProvider.SERVER
    
    @staticmethod
    def FormatQuery( values ):
        query = {}
        query.update(IOpenSubtitlesProvider.MovieSearchDict)
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
        except:
            WriteDebug('Failed calculating hash, returning null')
            return ''