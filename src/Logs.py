#===============================================================================
# This File Contatins all the logs for the program.
# Any new log message should be entered here
#===============================================================================
class LOGS:
	class WARN:
		DO_DIR_NO_MISSING_SUBTITLE_FILES 	= 'Directory is not missing subtitles, skipping: %s'
	
		CANT_GET_RESULTS_FOR_MOVIE_NAME = 'Can\'t get results for file name'
		CANT_GET_RESULTS_FOR_MOVIE_CODE = 'Can\'t get results for movie code'
        
		FAILED_DOWNLOADING_SUBTITLE_ARCHIVE = 'Failure while downloading subtitle archive'
        
		FAILED_SPECIAL_EXTRACTION_OF_SUBTITLE         = 'Failure while extracting specific file from archvie, extracting all'
		FAILED_TEMP_ZIP_FILE_REMOVAL				  = 'Failure while deleting temp zip file'
		FAILED_EXTRACTING_SUBTITLE_FILE_FROM_ARCHIVE  = 'Failure while extracting from the archive'
		
		ERROR_DIRECTORY_DOESNT_EXISTS = 'Error: Directory doesn\'t exists: %s'
        
	class INFO:
		STARTING 					= 'Starting. . .'
		
		STARTING_DO_FILE_PROCEDURE 	= 'Starting to work on file'
		STARTING_DO_DIR_PROCEDURE 	= 'Starting to work on dir'
				
		STARTING_SEARCH_FOR         = 'Starting search for: %s'
		
		#Movie name query logs
		SENDING_QUERY_FOR_MOVIES        = 'Sending query for movies with: %s'
		GOT_SEVERAL_RESULTS_FOR_MOVIES  = 'Got several results for movies query'
		GOT_ONE_RESULT_FOR_MOVIES       = 'Got one result from movies query'
		
		#Movie Ranking
		GOT_EXACT_MATCH_FROM_MOVIE_RANKING 				= 'Got exact match from movies ranking'
		NO_EXACT_MATCH_FROM_MOVIE_RANKING_TAKING_FIRST 	= 'Got no exact match from movies ranking - taking first'
		
		#Subtitle versions logs
		SENDING_QUERY_FOR_SUB_VERSIONS_FOR_MOVIE	= 'Sending query for subtitle version for movie: %s'
		MOVIE_CODE_FOR_SUBVERSIONS_IS				= 'Movie code is: %s'
		GOT_SEVERAL_RESULTS_FOR_SUB_VERSIONS        = 'Got several results for subtitle versions'
		GOT_ONE_RESULT_FOR_SUB_VERSIONS             = 'Got one result for subtitle versions'
		
		#Ranking
		GOT_EXACT_MATCH_FROM_VERSIONS_RANKING				= 'Got certain match from versions ranking'
		NO_EXACT_MATCH_FROM_VERSIONS_RANKING				= 'Can\'t get certain match from versions ranking'
		NO_EXACT_MATCH_FROM_VERSIONS_RANKING_TAKING_FIRST	= 'Can\'t get certain match from versions ranking - taking first'
		
		#Subtitle download
		STARTING_SUBTITLE_DOWNLOAD_PROCEDURE 		= 'Starting subtitle download procedure'
		SENDING_SUBTITLE_FILE_REQUEST_FOR_SUBTITLE  = 'Sending subtitle file request for version with: %s'
		TRYING_ANOTHER_METHOD_FOR_DOWNLOADING_SUB	= 'Trying another method for subtitle download'
		DESTINATION_DIRECTORY_FOR_SUBTITLE          = 'Subtitle destination directory is: %s'
		GOT_SEVERAL_FILES_IN_THE_ARCHIVE            = 'Got several files in subtitle archive, keeping original file names'
		SUCCESSFULL_EXTRACTION_FROM_ARCHIVE 		= 'Subtitle successfully extracted from the archive'
		FINISHED_SUBTITLE_DOWNLOAD_PROCEDURE        = 'Finished subtitle download procedure'
		
		FINISHED_DO_FILE_PROCEDURE  = 'Finished to work on file'
		FINISHED_DO_DIR_PROCEDURE   = 'Finished to work on dir'
		FINISHED = 'Finished'
                
	class DIRECTION:
        #Movie name query logs
		INSERT_MOVIE_NAME_FOR_QUERY = 'Please insert movie name to query'
		CHOOSE_MOVIE_FROM_MOVIES    = 'Please choose one of the movies bellow'
		
		#Subtitle versions query
		CHOOSE_VERSION_FROM_VERSIONS = 'Please choose one subtitle from the versions bellow'
		
		#Subtitle download
		INSERT_LOCATION_FOR_SUBTITLE_DOWNLOAD = 'Please insert the destination for the subtitle file [Empty for: %s]'
        