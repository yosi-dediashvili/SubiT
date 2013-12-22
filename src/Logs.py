#===============================================================================
# This File Contatins all the logs for the program.
# Any new log message should be entered here
#===============================================================================
class LOGS:
	DELIMITER = '__||__'
	TYPE_TO_COLOR = {'WARN':'Red', 'INFO':'Green', 'DIRECTION':'Blue'}
	class WARN:
		DO_DIR_NO_MISSING_SUBTITLE_FILES 				= 'WARN__||__All the files in: %s have subtitles, skipping'
		CANT_GET_RESULTS_FOR_MOVIE_NAME 				= 'WARN__||__Can\'t get results for file name'
		CANT_GET_RESULTS_FOR_MOVIE_CODE 				= 'WARN__||__Can\'t get results for movie code'
		FAILED_DOWNLOADING_SUBTITLE_ARCHIVE 			= 'WARN__||__Failure while downloading subtitle archive'
		NO_SUBTITLE_FILES_IN_THE_ARCHIVE				= 'WARN__||__Archive contains no subtitle files'
		FAILED_SPECIAL_EXTRACTION_OF_SUBTITLE			= 'WARN__||__Failure while extracting specific file from archvie, extracting all'
		FAILED_TEMP_ZIP_FILE_REMOVAL					= 'WARN__||__Failure while deleting temp zip file'
		FAILED_EXTRACTING_SUBTITLE_FILE_FROM_ARCHIVE	= 'WARN__||__Failure while extracting from the archive'
		ERROR_DIRECTORY_DOESNT_EXISTS 					= 'WARN__||__Error: %s doesn\'t exists'

	class INFO:
		STARTING 											= 'INFO__||__Starting. . .'
		SELECTED_SUB_HANDLER_IS 							= 'INFO__||__Using: %s as subtitle provider'
		STARTING_DO_FILE_PROCEDURE 							= 'INFO__||__Searching subtitle for the movie: %s'
		STARTING_DO_DIR_PROCEDURE 							= 'INFO__||__Searching subtitles for directory: %s'
		STARTING_SEARCH_FOR         						= 'INFO__||__Searching for: %s'
		#Movie name query logs
		SENDING_QUERY_FOR_MOVIES        					= 'INFO__||__Searching for: %s'
		GOT_SEVERAL_RESULTS_FOR_MOVIES  					= 'INFO__||__Got several results from the search'
		GOT_ONE_RESULT_FOR_MOVIES       					= 'INFO__||__Got one result from the search'
		#Movie Ranking
		GOT_EXACT_MATCH_FROM_MOVIE_RANKING 					= 'INFO__||__There is an exact match for the moive version'
		NO_EXACT_MATCH_FROM_MOVIE_RANKING_TAKING_FIRST 		= 'INFO__||__There is no exact match for the moive version - downloading the best match'
		#Subtitle versions logs
		SENDING_QUERY_FOR_SUB_VERSIONS_FOR_MOVIE			= 'INFO__||__Sending query for subtitle version for the movie: %s'
		MOVIE_CODE_FOR_SUBVERSIONS_IS						= 'INFO__||__The movie code is: %s'
		GOT_SEVERAL_RESULTS_FOR_SUB_VERSIONS        		= 'INFO__||__Got several subtitles versions'
		GOT_ONE_RESULT_FOR_SUB_VERSIONS             		= 'INFO__||__Got one subtitle version'
		#Ranking
		GOT_EXACT_MATCH_FROM_VERSIONS_RANKING				= 'INFO__||__Got an absolute match for: %s'
		NO_EXACT_MATCH_FROM_VERSIONS_RANKING				= 'INFO__||__Can\'t get an absolute match'
		NO_EXACT_MATCH_FROM_VERSIONS_RANKING_TAKING_FIRST	= 'INFO__||__Can\'t get an absolute match -downloading the best match: %s'
		#Subtitle download
		STARTING_SUBTITLE_DOWNLOAD_PROCEDURE 				= 'INFO__||__Starting subtitle download procedure'
		SENDING_SUBTITLE_FILE_REQUEST_FOR_SUBTITLE  		= 'INFO__||__Sending subtitle file request for version: %s'
		TRYING_ANOTHER_METHOD_FOR_DOWNLOADING_SUB			= 'INFO__||__Trying another method for subtitle download'
		DESTINATION_DIRECTORY_FOR_SUBTITLE          		= 'INFO__||__Subtitle destination directory is: %s'
		GOT_SEVERAL_FILES_IN_THE_ARCHIVE            		= 'INFO__||__Got several files in subtitle archive, keeping original file names'
		EXTRACTED_SUBTITLE_FILE								= 'INFO__||__Extracted: %s'
		SUCCESSFULL_EXTRACTION_FROM_ARCHIVE 				= 'INFO__||__Subtitle successfully extracted from the archive'
		FINISHED_SUBTITLE_DOWNLOAD_PROCEDURE        		= 'INFO__||__Finished subtitle download procedure'
		#Finish
		FINISHED_DO_FILE_PROCEDURE  						= 'INFO__||__Finished working on file'
		FINISHED_DO_DIR_PROCEDURE   						= 'INFO__||__Finished working on directory'
		FINISHED 											= 'INFO__||__Finished'

	class DIRECTION:
        #Movie name query logs
		INSERT_MOVIE_NAME_FOR_QUERY 						= 'DIRECTION__||__Please insert  a movie name'
		CHOOSE_MOVIE_FROM_MOVIES    						= 'DIRECTION__||__Please choose one of the movies'
		#Subtitle versions query
		CHOOSE_VERSION_FROM_VERSIONS 						= 'DIRECTION__||__Please choose one subtitle from the versions'
		#Subtitle download
		INSERT_LOCATION_FOR_SUBTITLE_DOWNLOAD 				= 'DIRECTION__||__Please insert the destination for the subtitle file [Leave empty for: %s]'
