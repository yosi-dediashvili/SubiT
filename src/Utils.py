_DEBUG = True
_IS_RUNNING_FROM_SOURCE = True

import sys

def IsPython3():
    """ Check if the major version of python is 3, return True if so, otherwise
        will return False 
    """
    return sys.version_info[0] == 3

if IsPython3():
    import http.client
else:
    import httplib

import os
import platform
import re
import zipfile
from io import BytesIO
import time

# reduce function moved to functools in python3, while in python2 the 
# function is avaliable directlt
if IsPython3():
    from functools import reduce

class HttpRequestTypes:
    GET  = 'GET'  #Retrieve only
    POST = 'POST' #Post data (Retrieve Optional)
    HEAD = 'HEAD' #Check response (same response as get, but without the data)

def LaunchInConsole():
    """ Will launch the console mode of SubiT under windows platform, will do
        nothing if we're not under windows, and if the cli exe is missing
    """
    if not IsWindowPlatform():
        WriteDebug('Not in windows, skipping start in console mode')

    console_exe_path = os.path.join(GetProgramDir(), 'SubiT-cli.exe')
    if not os.path.exists(console_exe_path):
        WriteDebug('SubiT-cli.exe is missing from: %s' % console_exe_path)
        return

    if len(sys.argv) > 1:
        os.execl(console_exe_path, console_exe_path, '"%s"' % sys.argv[1])
    else:
        os.execl(console_exe_path, console_exe_path)

def IsInConsoleMode():
    """ Check wether we're running in console mode under windows platform, will
        Return True if so, on other platforms will return True always. The check
        is made using the sys.argv[0] value
    """
    if not IsWindowPlatform():
        WriteDebug('We are not under windows platform, returning True for ConsoleMode')
        return True
    exe_name = sys.argv[0]
    is_in_console = exe_name.endswith('SubiT-cli.exe')
    WriteDebug('is_in_console is %s' % is_in_console)
    return is_in_console

def ShouldLaunchInConsoleMode():
    if IsInConsoleMode():
        WriteDebug('We are already in console mode')
        return False

    from Interaction import InteractionTypes, getDefaultInteractorByConfig
    _interaction_type = getDefaultInteractorByConfig()
    if _interaction_type in \
        [InteractionTypes.Console, InteractionTypes.ConsoleSilent]:
        WriteDebug('We are under console interactor, returning True')
        return True
    else:
        WriteDebug('We are not under console interactor, returning False')
        return False

# ============================================================================ #
# Series handling
# ============================================================================ #
def IsSeries(query):
    """ Check wether the query has indication of beeing a series, by checking
        to see wether it has a season and episode numbering 
    """
    return bool(GetSeriesParams(query))

def GetSeriesRegexes():
    """ Return our regexes for series numbering """
    return [# foo.S03E12.HDTV or foo.s04.e15.HDTV
            's(?P<season>\d{1,2})[ \-\.]?e(?P<episode>\d{1,2})',                                            
            # foo.Season.05.Episode.06.HDTV
            'season[ \.\-\_]?(?P<season>\d{1,2})[ \.\-\_]?episode[ \.\-\_]?(?P<episode>\d{1,2})',   
            # foo.4x15.HDTV
            '(?P<season>\d{1,2})x(?P<episode>\d{1,2})']

def RemoveSeriesNumbering(query):
    """ Remove the series numbering string from the whole query name. We use
        our regular regex patterns for series matching in order to remove the 
        strings from the query. The query parameter is converted to lower case
        before we look for matches. Consider calling FormatMovieName before 
        using the result of this function.
    """
    series_regexes = GetSeriesRegexes()
    result = query.lower()

    WriteDebug('Removing series params from: %s' % result)
    for regex in series_regexes:
        result = re.sub(regex, '', result)
    WriteDebug('Series params removed, the result is: %s' % result)
    return result

def GetSeriesParams(query):
    """ Return the parameters of a series, Season and Episode, the result is 
        a tuple of (Season, Episode), each item is an integer. The query is 
        converted to lower case before the search.
    """
    query = query.lower()
    series_regexes = GetSeriesRegexes()
    
    result = []
    WriteDebug('Retriving series param from: %s' % query)
    for regex in series_regexes:
        # We might end up with result being None because takefirst returns None
        # if there are no items in an iterable.
        result = takefirst(getregexresults(regex, query, False))
        WriteDebug('Regex of %s got us: %s' % (regex, result))
        if result:
            # We convert result to list in order to change the items inside it
            result = list(result)
            # Convert to integers
            WriteDebug('Got result from regex, converting to integers')
            if result[0].isdigit():
                result[0] = int(result[0])
            if result[1].isdigit():
                result[1] = int(result[1])
            WriteDebug('Finished converting the regex results to integers')
            break
    WriteDebug('Series params retrivied, the result is: %s' % result)
    
     
    # result might be None (as it's says earlier in the function), so we can
    # get exception if result is None and we try to convert it to tuple.
    if result is None:
        return tuple([])
    else:
        return tuple(result)
# ============================================================================ #
# ============================================================================ #


def GetSubtitleSavingExtension(original_file_name = ''):
    """ Return the extension that we need to add to the subtitle file that we
        are saving after download. The value is returned from the configuration
        file under Global.subtitles_saving_extension. On failure, the function
        will return the default extension [.srt]. If the original_file_name is 
        specified, the funciton will append the extension to the file name (if 
        the file name didnt contained the extension already)
    """
    from Settings.Config import SubiTConfig
    WriteDebug('Retriving subtitle extension for file saving')
    ext = SubiTConfig.Singleton().getStr\
        ('Global', 'subtitles_saving_extension', '.srt')
    WriteDebug('The subtitle extensions for files is: %s' % ext)

    if not original_file_name.lower().endswith(ext):
        original_file_name += ext
    WriteDebug('original_file_name is now: %s' % original_file_name)
    
    return original_file_name

def GetSubtitleDownloadDirectory(dir_by_flow = None, interactive = False):
    """ Get the full path for the subtitle download directory. the argument
        dir_by_flow specify the directory in which the movie file exists.
        The function might return None if dir_by_flow is missing, and the value
        of Global.always_use_default_directory in the configuration is set to 
        False.
    """
    from Settings import DEFAULT_DIRECTORY_DEFAULT_VAL
    from Settings.Config import SubiTConfig

    from Logs import WARN as WARN_LOGS
    from Logs import DIRECTION as DIRC_LOGS

    download_directory = None
    conf_default_directory = SubiTConfig.Singleton().getStr\
        ('Global', 'default_directory', DEFAULT_DIRECTORY_DEFAULT_VAL)
    conf_always_use_default_dir = SubiTConfig.Singleton().getBoolean\
        ('Global', 'always_use_default_directory', False)

    if conf_default_directory == DEFAULT_DIRECTORY_DEFAULT_VAL:
        WriteDebug('conf_default_directory is: [%s], giving os.getcwd() [%s]' % (conf_default_directory, os.getcwd()))
        conf_default_directory = os.getcwd()
    elif not os.path.exists(conf_default_directory):
        WriteDebug('conf_default_directory [%s] is missing, giving os.getcwd() [%s]' % (conf_default_directory, os.getcwd()))
        conf_default_directory = os.getcwd()

    # The result of these 4 lines is simple. If dir_by_flow exists, and the conf
    # of always_use_default_dir is False, we return the dir_by_flow, if it's True
    # we return the conf_default_directory. In any other case, we return None
    if os.path.exists(dir_by_flow):
        WriteDebug('Setting download_directory to be dir_by_flow [%s]' % dir_by_flow)
        download_directory = dir_by_flow
    if conf_always_use_default_dir:
        WriteDebug('Setting download_directory to be conf_default_directory [%s]' % conf_default_directory)
        download_directory = conf_default_directory

    if not download_directory and interactive:
        import Interaction
        Interactor  = Interaction.getInteractor()
        writeLog = Interactor.writeLog

        while not download_directory:
            user_dir_choice = Interactor.getDestinationDirectoryInput\
                (conf_default_directory, DIRC_LOGS.INSERT_LOCATION_FOR_SUBTITLE_DOWNLOAD)
            if os.path.exists(user_dir_choice):
                WriteDebug('User enter legit path, using it: %s' % user_dir_choice)
                download_directory = user_dir_choice
            else:
                WriteDebug('User enter non-legit path [%s], asking again!' % user_dir_choice)
                writeLog(WARN_LOGS.ERROR_DIRECTORY_DOESNT_EXISTS % user_dir_choice)
    elif not download_directory:
        WriteDebug('To avoid problems, setting download_directory to conf_default_directory: %s' % conf_default_directory)
        download_directory = conf_default_directory

    return download_directory

def GetSubtitlesExtensions(with_dot = True):
    """Return all the extensions associated to subtitle files as it apear in 
    the config file. Extensions are in lower case."""
    from Settings.Config import SubiTConfig
    _ext = SubiTConfig.Singleton().getList('Global', 'subtitles_extensions', 
                                           ['.srt', '.sub', '.idx'])
    _ext = list(map(str.lower, _ext))
    if not with_dot:
        _ext = list(map(lambda e: e.lstrip('.'), _ext))
    return _ext

def GetMoviesExtensions(with_dot = True):
    """Return all the extensions associated to movie files as it apear in 
    the config file. Extensions are in lower case."""
    from Settings.Config import SubiTConfig
    _ext = SubiTConfig.Singleton().getList('Association', 'extensions_keys', 
                                           ['.mkv', '.avi', '.wmv', '.mp4'])
    _ext =  list(map(str.lower, _ext))
    if not with_dot:
        _ext = list(map(lambda e: e.lstrip('.'), _ext))
    return _ext
        
def PerformRequest(domain, url, data = '', type = HttpRequestTypes.GET, 
                   more_headers = '', retry = False, is_redirection = False):
    """ 
        Performs http requests. We are using fake user-agents. Use the data arg
        in case you send a "POST" request. Also, you can specify more headers 
        by supplying a dict in the more_headers arg
    """
    import UserAgents

    response = ''
    try:
        httpcon = None
        if IsPython3():
            httpcon = http.client.HTTPConnection( domain, timeout=10 )
        else:
            httpcon = httplib.HTTPConnection(domain, timeout = 10)

        headers = {}
        # Each packet we send will have this params (good for hiding)
        if not retry:
            headers = { 'Connection'        : r'keep-alive',
                        'User-Agent'        : UserAgents.getAgent(),
                        'X-Requested-With'  : r'XMLHttpRequest',
                        'Content-Type'      : r'application/x-www-form-urlencoded',
                        'Accept-Charset'    : r'utf-8;q=0.7,*;q=0.3',
                        'Accept-Language'   : r'en-US,en;q=0.8',
                        'Cache-Control'     : r'max-age=0' }
        else:
            # The Fake User Agent 
            headers = { 'User-Agent' : UserAgents.getAgent() } 
    
        # In case of specifiyng more headers, we add them
        if (len(more_headers)):
            headers.update(more_headers)
        
        WriteDebug('Sending request for: %s' % (domain + url))
        httpcon.request( type, url, str(data), headers )     
        got_response = httpcon.getresponse()
        response = got_response.read()
        # In order to avoid decoding problems, we just convert the bytes to 
        # str. The problem is that when we do that, the str preserve the 
        # preceding 'b' of the bytes type, so we remove it, and the single 
        # quotes and the start and the end of the string
        try:
            response = response.decode('utf-8', errors='replace')
        except:
            response = str(response)[2:-1]
        response = response.replace('\r', '').replace('\n', '')
        # When we get and empty response, it might be a sign that we got a 
        # redirection and therefor we check the current url against the 
        # requested one. Also, if is_redirection is true, it means that we 
        # already got redirection, and therefor we stop the procedure
        if not response and not is_redirection:
            new_url = got_response.msg.dict['location']
            if url not in new_url:
                WriteDebug('Got Redirection: %s->%s' % (url, new_url))
                # Because the location gives us the full address including the 
                # protocol and the domain, we remove them in order to get the 
                # relative url
                new_url = new_url.replace('http://', '').replace(domain, '')
                return PerformRequest(domain, new_url, is_redirection=True)
    except Exception as eX:
        WriteDebug('Failed Getting: %s->%s [%s]' % (domain, url, eX))

    return response

def DownloadSubAsBytesIO(domain, url, referer = None):
    """ Download a url, and return as file-like object (Bytes). Use the referer
        parameter if the site require such parameter in the header in order to
        download the file
    """
    import UserAgents

    if IsPython3():
        from urllib.request import Request, urlopen
    else:
        from urllib2 import Request, urlopen
    # urlopen accepts only a url, so we need to join the domain and url
    # into a one string. Also, the type is needed, therefor the "http://"
    full_url = ''
    if url.startswith('http://'):
        full_url = url
    elif url.startswith('www.'):
        full_url = 'http://' + url
    else:
        full_url = 'http://%s' % domain + url
    WriteDebug('Getting file: %s' % full_url)

    file_content = BytesIO()
    # Set the referer to be the domain because some site will avoid our request
    # if we don't do that
    request_headers = {'User-Agent' : UserAgents.getAgent(),
                       # Set the referer to be the domain if None passed
                       'Referer' : referer or domain}
    file_request = Request(full_url, headers = request_headers)
    try:
        url_opened = urlopen(file_request)
        file_content.write(url_opened.read())
    except Exception as eX:
        WriteDebug('Failed getting file: %s->%s' % (full_url, eX))
        return None
    return file_content

def GetFile(domain, url, path, file_name, referer = None):
    """ 
        Downloand the file from the given url, and saves it at the given 
        location. The url is relative to the domain arg. path specify the 
        directory in whice the subtitle will be saved. The file_name specify 
        the name for the subtitle. If the file is downloaded is a zip file, 
        will extract all the subtitles under it, otherwise, will save the file 
        in the given location.

        Note: will use the original name if: 
            a. file_name is empty 
            b. there is more then one file in the archive

        In case of success, returns true, else false
    """
    from Logs import INFO as INFO_LOGS
    from Logs import WARN as WARN_LOGS
    from Logs import DIRECTION as DIRC_LOGS

    import Interaction
    writeLog = Interaction.getInteractor().writeLog
    
    is_success          = False
    subtitle_directory  = os.path.abspath(path)                     
    subtitle_full_path  = os.path.join(subtitle_directory, file_name)
    
    writeLog(INFO_LOGS.STARTING_SUBTITLE_DOWNLOAD_PROCEDURE)
    writeLog(INFO_LOGS.DESTINATION_DIRECTORY_FOR_SUBTITLE % subtitle_directory)
    
    downloaded_file = DownloadSubAsBytesIO(domain, url, referer)
    file_is_zip     = False
    if downloaded_file:
        file_is_zip = zipfile.is_zipfile(downloaded_file)
    
    if file_is_zip:
        try:
            with zipfile.ZipFile(downloaded_file, 'r') as zfile:
                # Get the file names of the subtitles in the archive. 
                # Filtering out any other file types
                filter_func = lambda x: x.lower().endswith(
                                                tuple(GetSubtitlesExtensions()))
                sub_filenames = myfilter(filter_func, zfile.namelist())
                if not sub_filenames:
                    writeLog( WARN_LOGS.NO_SUBTITLE_FILES_IN_THE_ARCHIVE)
                else:
                    # If we have more than one subtitle file in the archive, we 
                    # keep the original filenames that comes with the archive)
                    if len(sub_filenames) > 1:
                        writeLog(INFO_LOGS.GOT_SEVERAL_FILES_IN_THE_ARCHIVE )
                        for file_name in sub_filenames:
                            # Write the file with the original filename
                            file_path = os.path.join(subtitle_directory, file_name)
                            open(file_path, 'wb').write(zfile.open(file_name).read())
                            writeLog(INFO_LOGS.EXTRACTED_SUBTITLE_FILE % file_name)
                    else:
                        # If the file_name was empty, we keep the original also
                        if not file_name:
                            subtitle_full_path = os.path.join(subtitle_directory, 
                                                              sub_filenames[0])
                        sub_content = zfile.open(sub_filenames[0]).read()
                        open(subtitle_full_path, 'wb').write(sub_content)
                        writeLog(INFO_LOGS.EXTRACTED_SUBTITLE_FILE % 
                                 subtitle_full_path)
            # Notify successful extraction
            writeLog( INFO_LOGS.SUCCESSFULL_EXTRACTION_FROM_ARCHIVE )
            is_success = True
        except Exception as eX:
            WriteDebug('Failed constructing ZipFile object: %s' % eX)
            writeLog(WARN_LOGS.FAILED_EXTRACTING_SUBTITLE_FILE_FROM_ARCHIVE)
    # If the file is simple subtitle text file
    else:
        try:
            with open(subtitle_full_path, 'wb') as sub_file:
                downloaded_file.seek(0)
                content = downloaded_file.getvalue()
                sub_file.write(content)
        except Exception as eX:
            WriteDebug('Failed saving subtitle as simple text file: %s' % eX)
            writeLog(WARN_LOGS.FAILED_SAVING_SUBTITLE_SIMPLE_FILE)
        is_success = True
    return is_success
                
def getregexresults( pattern, content, with_groups = False):
    """ Query the content and returns list of all result, in case of multi-
        group pattern, will return a list of tuples (tuple for each group).
    """
    c_pattern = re.compile( pattern )
    results = []
    if with_groups:
        results = map(lambda i: i.groupdict(), re.finditer(c_pattern, content))
    else:
        results =  re.findall( c_pattern, content )
    return list(results)

def myfilter(filter_func, items, format_func = lambda i: i, take_first = False):
    """ Self implementation of the filter function, allowing to set different 
        value than the one given in items.
    """
    filtered_items = []
    for item in list(items):
        if filter_func(item):
            filtered_items.append(format_func(item))
    if not take_first:
        return filtered_items
    else:
        return takefirst(filtered_items)

def getlist(anything):
    """ Will try to convert the object to list. Return empty list on failure """
    try:
        return list(anything)
    except:
        return []

def takefirst(items):
    """ Function to return the first item in a list (will try to convert the 
        parameter to list if it's not. return None on failure.
    """
    first_item = None
    try:
        if type(items) != list:
            items = list(items)
    
        if len(items):
            first_item = items[0]
    except: 
        pass
    return first_item

def FormatMovieName(movie_name, to_list = True, splitters = './ -:'):
    """ Will format the movie name to SubiT's standard format, 
        ie: "<movie name> [ver_0] [ver_[1] [ver_n]" 
        also, if to_list is true, will return the name as a list, splitted 
        using the splitters given. Otherwise, will return the movie_name after
        replacing the splitters with space. The string returned are in lower
        case format.
    """
    separator = '|'

    # Replace all the splitters in the movie_name with the separator
    result = reduce(lambda name, splitter: name.replace(splitter, separator), 
                    splitters, movie_name.lower()).strip()
    # If we get two splitters or more together in the movie_name, we end up 
    # with the a separtor sequence instead of a single one. For example, if the
    # movie_name is "the.matrix: reloaded", the result after the reduce will be
    # "the|matrix||reloaded", so we use re.sub to replace a separator sequence
    # with a singal instance and after that strip the result with the separator
    # as the char in order to make sure that we dont leave some in the start or
    # end of the result.
    result = re.sub('\%s{2,}' % separator, separator, result)
    result = result.strip(separator)

    if to_list:
        return result.split(separator)
    else:
        return result.replace(separator, ' ')
        
HELP_ARGS = ['/?', '?', '--help', 'help']

def printhelp():
    print ('')
    print ('SubiT - Automated system for subtitle downloading')
    print ('Usage: SubiT.exe [Moviename | Filename | Directory]')
    print ('')
    print ('Moviename: movie name')
    print ('Filename:  name of movie file, with extension')
    print ('Directory: destination directory for storing the subtitle,')
    print ('           omitting this parameter will keep original subtitle filename')
    input()
    sys.exit()

def GetDirFileNameAndFullPath():
    params = ['','','']
    
    def win32_unicode_argv():
        """
        Uses shell32.GetCommandLineArgvW to get sys.argv as a list of Unicode
        strings.

        Versions 2.x of Python don't support Unicode in sys.argv on
        Windows, with the underlying Windows API instead replacing multi-byte
        characters with '?'.
        """

        from ctypes import POINTER, byref, cdll, c_int, windll
        from ctypes.wintypes import LPCWSTR, LPWSTR

        GetCommandLineW = cdll.kernel32.GetCommandLineW
        GetCommandLineW.argtypes = []
        GetCommandLineW.restype = LPCWSTR

        CommandLineToArgvW = windll.shell32.CommandLineToArgvW
        CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
        CommandLineToArgvW.restype = POINTER(LPWSTR)

        cmd = GetCommandLineW()
        argc = c_int(0)
        argv = CommandLineToArgvW(cmd, byref(argc))
        WriteDebug('argc: %s' % argc.value)
        if argc.value > 0:
            return [argv[i] for i in range(0, argc.value)]

    if IsWindowPlatform():
        sys.argv = win32_unicode_argv()
    
    WriteDebug('Parameters passed: %s' % sys.argv)
    WriteDebug('Parameters count:  %s' % len(sys.argv))

    if len(sys.argv) > 1:
        WriteDebug('Got Params!')
        if sys.argv[1].lower() in HELP_ARGS:
            WriteDebug('Got help param!')
            printhelp()
        elif len(sys.argv) == 2:
            WriteDebug('Got Two params!')
            WriteDebug('sys.argv[0]: %s' % sys.argv[0])
            WriteDebug('sys.argv[1]: %s' % sys.argv[1])
            if os.path.isfile(sys.argv[1]):
                WriteDebug('File passed!')
                params[:2] = list(os.path.split(sys.argv[1]))
                params[1] = os.path.splitext(params[1])[0] #File name without ext
                params[2] = sys.argv[1]
            elif os.path.isdir(sys.argv[1]):
                WriteDebug('Dir passed!')
                params[0] = sys.argv[1]
            else:
                WriteDebug('Query passed!')
                params[1] = sys.argv[1]
    return params

def restart(args = None, override_sys = False):
    """Restart the program with params if args is exists"""
    WriteDebug('argv is: %s' % sys.argv)
    WriteDebug('args is: %s' % args)
    
    if args and (len(sys.argv) <= 1 or override_sys):
        WriteDebug('Restarting with args: %s' % args)
        os.execl(sys.executable, sys.executable, '"%s"' % args)
    elif len(sys.argv) > 1:
        WriteDebug('Restarting with argv: %s' % sys.argv[1])
        os.execl(sys.executable, sys.executable, '"%s"' % sys.argv[1])
    else:
        WriteDebug('Restarting without args!')
        os.execl(sys.executable, sys.executable)

def sleep(secs_to_sleep):
    """Sleep the thread"""
    time.sleep(secs_to_sleep)

def exit(secs_to_sleep = 0):
    """Exit the program"""
    WriteDebug('Exiting in %s seconds' % secs_to_sleep)
    if secs_to_sleep:
        sleep(secs_to_sleep)
    os._exit(0)


# ============================================================================ #
# Platform checks
# ============================================================================ #
def GetSystemPlatform():
    """Return the system platform name"""
    return platform.system()

def IsWindowPlatform():
    """Return True if the system's OS is Windows, else False."""
    return GetSystemPlatform() == 'Windows'

def IsVistaOrLater():
    """Return True if the system is vista or later, else False."""
    value = False
    if IsWindowPlatform():
        vista_or_later_major = 6
        system_major_version = int(platform.version().split('.')[0])
        value =  system_major_version >= vista_or_later_major
    return value
# ============================================================================ #
# ============================================================================ #
    
def GetProgramDir():
    """ Return the location of SubiT. Because utils module is in the parent 
        dir, we get the programs location. The function also check wether we 
        running in freeze state (sys.frozen), and if so, extract teh dir from 
        the sys.executable location instead of the the __file__ location.
    """
    _file_path = ''
    _dir_path = ''
    if hasattr(sys, 'frozen'):
        WriteDebug('We are running in freeze state, getting sys.executable')
        _file_path = sys.executable
    else:
        WriteDebug('We are running in regular stage, getting __file__')
        _file_path = __file__
    WriteDebug('_file_path value is: %s' % _file_path)
    _dir_path = os.path.dirname(_file_path)
    WriteDebug('_dir_path value is: %s' % _dir_path)
    return _dir_path

def DEBUG():
    """ Return True if we are in debug mode, else False """
    global _DEBUG
    global _IS_RUNNING_FROM_SOURCE

    return _DEBUG or _IS_RUNNING_FROM_SOURCE

def WriteDebug( message ):
    """ Write debug log - will only be written if the DEBUG flag is True. 
        
        KEEP IN MIND: Calling the function must be made in a one line style,
        the reason for this is that we use the minifier to remove some code 
        when we're not in DEBUG mode, and i looks for lines starting with 
        [WriteDebug(] and remove them, so if you spread the call on several 
        lines, the result will be unpredicted.
    """
    # The Python optimizer will make sure that the function won't be compiled 
    # if _DEBUG is set to False.
    if DEBUG():
        message = '[%s] => %s' % (time.strftime('%I:%M:%S'), message)
        try:
            print(message)
        except:
            print(message.encode('utf-8', 'ignore').decode('ascii', 'ignore'))
    else:
        pass

def CurrentTime():
    """ Return the value of time.time() as int. """
    return int(time.time())

def CurrentTimePrintable():
    """ Return the value of time.ctime(). """
    return time.ctime()