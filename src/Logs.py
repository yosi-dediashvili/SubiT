""" 
    This File Contatins all the logs for the program. Any new log message 
    should be entered here. SubiT has four log types: WARN, INFO, DIRECTION
    and OTHER which is used for any additional log message.
"""

DELIMITER = '__||__'
def BuildLog(type_str, message):
        """ Build a log message (includes the deliminter and the msg type """
        return type_str + DELIMITER + message

# ============================================================================ #
class WARN:
    _TYPE_ = 'WARN'

    DO_DIR_NO_MISSING_SUBTITLE_FILES                = BuildLog(_TYPE_, 'All the files in: %s have subtitles, skipping')
    OS_CANT_GET_MOVIE_NAME_FOR_HASH_VALUE           = BuildLog(_TYPE_, 'Can\'t get movie name using the file hash')
    OS_CANT_GET_MOVIE_NAME_FOR_FILE_NAME            = BuildLog(_TYPE_, 'Can\'t get movie name using the file name')
    CANT_GET_RESULTS_FOR_MOVIE_NAME                 = BuildLog(_TYPE_, 'Can\'t get results for file name')
    CANT_GET_RESULTS_FOR_MOVIE_CODE                 = BuildLog(_TYPE_, 'Can\'t get results for movie code')
    FAILED_DOWNLOADING_SUBTITLE_ARCHIVE             = BuildLog(_TYPE_, 'Failure while downloading subtitle archive')
    NO_SUBTITLE_FILES_IN_THE_ARCHIVE                = BuildLog(_TYPE_, 'Archive contains no subtitle files')
    FAILED_SPECIAL_EXTRACTION_OF_SUBTITLE           = BuildLog(_TYPE_, 'Failure while extracting specific file from archive, extracting all')
    FAILED_TEMP_ZIP_FILE_REMOVAL                    = BuildLog(_TYPE_, 'Failure while deleting temp zip file')
    FAILED_EXTRACTING_SUBTITLE_FILE_FROM_ARCHIVE    = BuildLog(_TYPE_, 'Failure while extracting from the archive')
    FAILED_SAVING_SUBTITLE_SIMPLE_FILE              = BuildLog(_TYPE_, 'Failure saving a subtitle simple file')
    ERROR_DIRECTORY_DOESNT_EXISTS                   = BuildLog(_TYPE_, 'Error: %s doesn\'t exists')

class INFO:
    _TYPE_ = 'INFO'

    STARTING                                            = BuildLog(_TYPE_, 'Starting. . .')
    SELECTED_SUB_PROVIDER_IS                            = BuildLog(_TYPE_, 'Using: %s as subtitle provider')
    SETTING_PROVIDER                                    = BuildLog(_TYPE_, 'Setting Provider: %s')
    STARTING_PROCESSING_OF_SINGLE_INPUT                 = BuildLog(_TYPE_, 'Starting search for a SingleInput: %s')
    CURRENT_QUERY_BEING_PROCESSED_IS                    = BuildLog(_TYPE_, 'The current query that is being processed is: %s')
    STARTING_DO_FILE_PROCEDURE                          = BuildLog(_TYPE_, 'Searching subtitle for the movie: %s')
    STARTING_DO_DIR_PROCEDURE                           = BuildLog(_TYPE_, 'Searching subtitles for directory: %s')
    STARTING_SEARCH_FOR                                 = BuildLog(_TYPE_, 'Searching for: %s')
    #Movie name query logs
    SENDING_QUERY_FOR_MOVIES                            = BuildLog(_TYPE_, 'Searching for: %s')
    GOT_SEVERAL_RESULTS_FOR_MOVIES                      = BuildLog(_TYPE_, 'Got several results from the search')
    GOT_ONE_RESULT_FOR_MOVIES                           = BuildLog(_TYPE_, 'Got one result from the search')
    #OpenSubtitles Movie Name Query Log
    OS_SENDING_QUERY_USING_THE_FILE_HASH_VALUE          = BuildLog(_TYPE_, 'Sending query to www.OpenSubtitles.org using the file hash value')
    OS_SENDING_QUERY_USING_THE_FILE_NAME                = BuildLog(_TYPE_, 'Sending query to www.OpenSubtitles.org using the file name')
    OS_FOUND_MOVIE_NAME                                 = BuildLog(_TYPE_, 'Got movie name from www.OpenSubtitles.org')
    #Movie Ranking
    GOT_EXACT_MATCH_FROM_MOVIE_RANKING                  = BuildLog(_TYPE_, 'There is an exact match for the movie version')
    NO_EXACT_MATCH_FROM_MOVIE_RANKING                   = BuildLog(_TYPE_, 'There is no exact match for the movie version')
    #Subtitle versions logs
    SENDING_QUERY_FOR_SUB_VERSIONS_FOR_MOVIE            = BuildLog(_TYPE_, 'Sending query for subtitle version for the movie: %s')
    MOVIE_CODE_FOR_SUBVERSIONS_IS                       = BuildLog(_TYPE_, 'The movie code is: %s')
    GOT_SEVERAL_RESULTS_FOR_SUB_VERSIONS                = BuildLog(_TYPE_, 'Got several subtitles versions')
    GOT_ONE_RESULT_FOR_SUB_VERSIONS                     = BuildLog(_TYPE_, 'Got one subtitle version')
    #Ranking
    GOT_EXACT_MATCH_FROM_VERSIONS_RANKING               = BuildLog(_TYPE_, 'Got an absolute match for: %s')
    NO_EXACT_MATCH_FROM_VERSIONS_RANKING                = BuildLog(_TYPE_, 'Can\'t get an absolute match')
    NO_EXACT_MATCH_FROM_VERSIONS_RANKING_TAKING_FIRST   = BuildLog(_TYPE_, 'Can\'t get an absolute match - downloading the best match: %s')
    #Subtitle download
    STARTING_SUBTITLE_DOWNLOAD_PROCEDURE                = BuildLog(_TYPE_, 'Starting subtitle download procedure')
    SENDING_SUBTITLE_FILE_REQUEST_FOR_SUBTITLE          = BuildLog(_TYPE_, 'Sending subtitle file request for version: %s')
    TRYING_ANOTHER_METHOD_FOR_DOWNLOADING_SUB           = BuildLog(_TYPE_, 'Trying another method for subtitle download')
    DESTINATION_DIRECTORY_FOR_SUBTITLE                  = BuildLog(_TYPE_, 'Subtitle destination directory is: %s')
    GOT_SEVERAL_FILES_IN_THE_ARCHIVE                    = BuildLog(_TYPE_, 'Got several files in subtitle archive, keeping original file names')
    EXTRACTED_SUBTITLE_FILE                             = BuildLog(_TYPE_, 'Extracted: %s')
    SUCCESSFULL_EXTRACTION_FROM_ARCHIVE                 = BuildLog(_TYPE_, 'Subtitle successfully extracted from the archive')
    FINISHED_SUBTITLE_DOWNLOAD_PROCEDURE                = BuildLog(_TYPE_, 'Finished subtitle download procedure')

class DIRECTION:
    _TYPE_ = 'DIRECTION'

    #Movie name query logs
    LOADING_PLEASE_WAIT                     = BuildLog(_TYPE_, 'Loading, please wait.')
    INSERT_MOVIE_NAME_FOR_QUERY             = BuildLog(_TYPE_, 'Please enter a movie name.')
    CHOOSE_MOVIE_FROM_MOVIES                = BuildLog(_TYPE_, 'Please select a movie.')
    #Subtitle versions query
    CHOOSE_VERSION_FROM_VERSIONS            = BuildLog(_TYPE_, 'Please select a version.')
    #Subtitle download
    INSERT_LOCATION_FOR_SUBTITLE_DOWNLOAD   = BuildLog(_TYPE_, 'Please select the destination directory for the subtitle file.')

class FINISH:
    _TYPE_ = 'FINISH'

    #Finish
    FINISHED_PROCESSING_SINGLE_INPUT                    = BuildLog(_TYPE_, 'Finished processing a SingleInput: %s')
    FINISHED_DO_FILE_PROCEDURE                          = BuildLog(_TYPE_, 'Finished working on a movie file.')
    FINISHED_DO_DIR_PROCEDURE                           = BuildLog(_TYPE_, 'Finished working on directory.')
    FINISHED                                            = BuildLog(_TYPE_, 'Finished.')
    APPLICATION_WILL_NOW_EXIT                           = BuildLog(_TYPE_, 'Finished, application will now exit.')

class GUI_SPECIAL:
    _TYPE_ = 'GUI_SPECIAL'
    SEARCH_LINE_UPDATE = BuildLog(_TYPE_, '%s')

class OTHER:
    _TYPE_ = 'OTHER'


# ============================================================================ #

TYPE_TO_COLOR = {WARN._TYPE_        :'Red', 
                 INFO._TYPE_        :'White', 
                 DIRECTION._TYPE_   :'LightBlue', 
                 FINISH._TYPE_      :'LightGreen',
                 OTHER._TYPE_       :'LightGray'}

def MessageType(message):
    """ Will return the type of the message, the value is equal to the class
        _TYPE_ value.
    """
    try:
        return message.split(DELIMITER)[0]
    except:
        return OTHER._TYPE_

def MessageString(message):
    """ Will return the message without the message type and the delimiter """
    try:
        return message.split(DELIMITER)[1]
    except:
        return message

def MessageColor(message):
    """ Will return the color that is associated with that message. If failed
        to get the color, will try to return the color of OTHER """
    try:
        return TYPE_TO_COLOR[MessageType(message)]
    except:
        return TYPE_TO_COLOR[OTHER._TYPE_]
