import xmlrpclib
import os
import struct

import SubiT
import SubResult
import Utils

from SubHandlers.ISubHandler import ISubHandler


class OPENSUBTITLES_LANGUAGES:
	HEBREW 	= 'heb'
	ENGLISH = 'eng'
	RUSSIAN = 'rus'

class OPENSUBTITLES_PAGES:
	DOMAIN      = 'www.opensubtitles.org'
	API_SERVER  = 'http://api.opensubtitles.org/xml-rpc'
	LANGUAGE	= OPENSUBTITLES_LANGUAGES.ENGLISH

class IOpenSubtitlesHandler(ISubHandler):
	HANDLER_NAME    = 'Base - www.opensubtitles.org'
	TOKEN           = None
	SERVER          = None
	USER_AGENT      = ''
	MovieSearchDict = {}

	def __init__(self):
		IOpenSubtitlesHandler.USER_AGENT = 'SubiTApp %s' % SubiT.VERSION
		IOpenSubtitlesHandler.MovieSearchDict = {   'sublanguageid'  : OPENSUBTITLES_PAGES.LANGUAGE,
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
			filehash = IOpenSubtitlesHandler.HashFile(path)  #calculated file hash
			#format the query for exact match only
			movienamequery = IOpenSubtitlesHandler.FormatQuery({'moviehash'      : filehash,
															   'moviebytesize'  : str(filesize)})
			#send the query
			queryresult = IOpenSubtitlesHandler.GetServer().SearchSubtitles(IOpenSubtitlesHandler.GetToken(), 
																		   [movienamequery])['data']
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

		movienamequery = IOpenSubtitlesHandler.FormatQuery({ 'query' : fileName })
		#send the query
		queryresult = IOpenSubtitlesHandler.GetServer().SearchSubtitles(IOpenSubtitlesHandler.GetToken(), 
																		   [movienamequery])['data']
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
			filehash = IOpenSubtitlesHandler.HashFile(subSearch.Path)
			#format the query for exact match only
			movienamequery = IOpenSubtitlesHandler.FormatQuery({'moviehash'      : filehash,
															   'moviebytesize'  : str(filesize)})
			queryresult = IOpenSubtitlesHandler.GetServer().SearchSubtitles(IOpenSubtitlesHandler.GetToken(), 
																		   [movienamequery])['data']
			queryresult = queryresult if queryresult is not False else None
		#==================================================
		
		#If we got NoneFile query, or Hash query returned nothing
		if queryresult is None:
			movienamequery = IOpenSubtitlesHandler.FormatQuery({ 'query' : subSearch.Query })
			queryresult = IOpenSubtitlesHandler.GetServer().SearchSubtitles(IOpenSubtitlesHandler.GetToken(), 
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
		
		versionsquery = IOpenSubtitlesHandler.FormatQuery({'imdbid' : subMovie.MovieCode})
		queryresult = IOpenSubtitlesHandler.GetServer().SearchSubtitles(IOpenSubtitlesHandler.GetToken(),
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
		
		subpathquery = IOpenSubtitlesHandler.FormatQuery({'imdbid' : subVersion.MovieCode})
		queryresult  = IOpenSubtitlesHandler.GetServer().SearchSubtitles(IOpenSubtitlesHandler.GetToken(),
																		[subpathquery])['data']
		if queryresult is not False:
			url     = filter(lambda x: x[IDSubtitleFile] == subVersion.VerCode, queryresult)[0][ZipDownloadLink]
			domain  = OPENSUBTITLES_PAGES.DOMAIN
		
		return (domain, url)
		
#===============================================================================
# Class Helpers -> Session Handling
#===============================================================================
	@staticmethod
	def GetToken():
		if not IOpenSubtitlesHandler.TOKEN:
			IOpenSubtitlesHandler.TOKEN = IOpenSubtitlesHandler.GetServer().LogIn(0, 0, 0, 
												   IOpenSubtitlesHandler.USER_AGENT)['token']
		return IOpenSubtitlesHandler.TOKEN
	
	@staticmethod        
	def GetServer():
		if IOpenSubtitlesHandler.SERVER is None:
			IOpenSubtitlesHandler.SERVER = xmlrpclib.Server(OPENSUBTITLES_PAGES.API_SERVER)
		return IOpenSubtitlesHandler.SERVER
	
	@staticmethod
	def FormatQuery( values ):
		query = {}
		query.update(IOpenSubtitlesHandler.MovieSearchDict)
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
			Utils.WriteDebug('Failed calculating hash, returning null')
			return ''