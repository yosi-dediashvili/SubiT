# Set the debug flag to true in order to receive WriteDebug messages. When 
# building SubiT, this value should be true. It will not effect the Release
# version, because the minifier will remove the WriteDebug lines from the 
# source, but if it will be set to False, the Debug version will not display
# the WriteDebug messages.
_DEBUG = True

import sys
import httplib
import os
import platform
import re
import zipfile
from io import BytesIO
import time    
from urllib2 import Request, urlopen

import UserAgents

class HttpRequestTypes:
    GET  = 'GET'  #Retrieve only
    POST = 'POST' #Post data (Retrieve Optional)
    HEAD = 'HEAD' #Check response (same response as get, but without the data)

def LaunchInConsole():
    """ Will launch the console mode of SubiT under windows platform, will do
        nothing if we're not under windows, and if the cli exe is missing
    """
    WriteDebug('LaunchInConsole() called')

    if not IsWindowPlatform():
        WriteDebug('Not in windows, skipping start in console mode')
        return

    console_exe_path = os.path.join(GetProgramDir(), 'SubiT-cli.exe')
    
    if not os.path.exists(console_exe_path):
        WriteDebug('SubiT-cli.exe is missing from: %s' % console_exe_path)
        return
    
    WriteDebug('Launching in console. See you soon')

    if len(sys.argv) > 1:
        argument = ' '.join(x if x.startswith('-') else '"%s"' % x 
                            for x in sys.argv[1:])
        WriteDebug('Passing args to the exe: %s' % argument)
        os.execl(console_exe_path, '"%s"' % console_exe_path, argument)
    else:
        os.execl(console_exe_path, '"%s"' % console_exe_path)

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
    """ Checks wether we need to launch the console mode of SubiT. We check if
        we are not already in Console, and wether we are running in Windows
        (return True) or not (return False).
    """
    if IsInConsoleMode():
        WriteDebug('We are already in console mode')
        return False
    if IsWindowPlatform():
        WriteDebug('We are in windows, so we should launch console')
        return True
    else:
        WriteDebug('We are in windows, so we should not launch console')
        return False


def SplitToFileAndDirectory(path):
    """ Will split the given path into a tuple of (Directory, FileName). """
    return os.path.split(path)

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

def GetSubtitlesExtensions(with_dot = True):
    """Return all the extensions associated to subtitle files as it apear in 
    the config file. Extensions are in lower case."""
    from Settings.Config import SubiTConfig
    _ext = SubiTConfig.Singleton().Global.subtitles_extensions
    if not with_dot:
        _ext = list(map(lambda e: e.lstrip('.'), _ext))
    return _ext

def GetMoviesExtensions(with_dot = True):
    """Return all the extensions associated to movie files as it apear in 
    the config file. Extensions are in lower case."""
    from Settings.Config import SubiTConfig
    _ext = SubiTConfig.Singleton().Association.extensions_keys
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

def DownloadSubAsBytesIO(domain, url, referer = None, cookies = None):
    """ Download a url, and return as file-like object (Bytes). Use the referer
        parameter if the site require such parameter in the header in order to
        download the file
    """


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
    if cookies:
        request_headers.update({"Cookie" : cookies})

    file_request = Request(full_url, headers = request_headers)
    try:
        url_opened = urlopen(file_request)
        file_content.write(url_opened.read())
    except Exception as eX:
        WriteDebug('Failed getting file: %s->%s' % (full_url, eX))
        return None
    return file_content

def GetFile(subtitle_file_io, path, file_name):
    """ 
        Get subtitle file from BytesIO object. subtitle_file_io is file like
        object that contains either a single subtitle file or a zip file. 
        path specify the directory in whice the subtitle will be saved. The 
        file_name specify the name for the subtitle. If the subtitle_file_io is 
        a zip file, will extract all the subtitles under it, otherwise, will 
        save the file in the given location.

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
    
    file_is_zip = zipfile.is_zipfile(subtitle_file_io)
    
    if file_is_zip:
        try:
            with zipfile.ZipFile(subtitle_file_io, 'r') as zfile:
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
                subtitle_file_io.seek(0)
                content = subtitle_file_io.getvalue()
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

LATIN_TO_DECIMAL = { 'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100,
                     'd': 500, 'm': 1000 }

LATIN_MAPPING = [('cd', 4 * 'c'),
                 ('xl', 4 * 'x'),
                 ('iv', 4 * 'i'),
                 ('d', 5 * 'c'),
                 ('l', 5 * 'x'),
                 ('v', 5 * 'i'),
                 ('cm', 9 * 'c'),
                 ('xc', 9 * 'x'),
                 ('ix', 9 * 'i')]

LATIN_BIG_NUMS = [('m', 1000), ('c', 100), ('x', 10), ('i', 1)]

def IsLatinNumber(number):
    """ Will check if the number string might be a latin (roman) number. """
    latin_chars = LATIN_TO_DECIMAL.keys()
    number = str(number).lower()

    for i in number:
        if i not in  latin_chars:
            return False
    return True

def IsArabicNumber(number):
    """ Will check if the number string is an integer (arabic one). """
    try:
        int(number)
        return True
    except:
        return False

def FromLatinToArabicNumber(latin_number):
    """ Will convert to the latin (roman) number to it's arabic representation
        as an integer. On failure, will return None.
    """
    WriteDebug('FromLatinToArabicNumber: %s' % latin_number)
    latin_number = latin_number.lower()
    if not IsLatinNumber(latin_number):
        return None

    for (short_ver, long_ver) in LATIN_MAPPING:
        latin_number = latin_number.replace(short_ver, long_ver)

    latin_number = '+'.join(list(latin_number))

    for (character, word) in LATIN_BIG_NUMS:
        latin_number = latin_number.replace(character, str(word))

    if latin_number == '':
        latin_number = '0'

    return eval(latin_number)

def FromArabicToLatinNumber(arabic_number):
    """ Will convert to the arabic number to it's latin (roman) representation
        as an str, in lower-case. On failure, will return None.
    """
    WriteDebug('FromArabicToLatinNumber: %s' % arabic_number)
    if not (IsArabicNumber(arabic_number)):
        return None

    latin_number = ''

    for (character, word) in LATIN_BIG_NUMS:
        latin_number += (arabic_number / word) * character
        arabic_number %= word

    for (short_ver, long_ver) in reversed(LATIN_MAPPING):
        latin_number = latin_number.replace(long_ver,short_ver)

    return latin_number

def FormatMovieName\
        (movie_name, to_list = True, splitters = './ -:',
         separator = '|', convert_latin = True):
    """ Will format the movie name to SubiT's standard format, 
        ie: "<movie name> [ver_0] [ver_[1] [ver_n]" 

        If to_list is true, will return the name as a list, using the splitters
        given. Otherwise, will return the movie_name after replacing the
        splitters with the separator. If convert_latin is True, the latin
        numbers appearing in the string will be converted to their arabic
        representation. For example: 'men in black ii' will be 'men in black 2'
        and so on.

        The string returned are in lower case format.
    """

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

    result_list = result.split(separator)
    if convert_latin:
        def _convert(i):
            if IsLatinNumber(i):
                i_tmp = FromLatinToArabicNumber(i)
                if type(i_tmp) is int:
                    return str(i_tmp)
            return i
        result_list = map(_convert, result_list)

    WriteDebug('result_list is: %s' % result_list)

    if to_list:
        return result_list
    else:
        return ' '.join(result_list)
        
def restart(args = None, override_sys = False):
    """Restart the program with params if args is exists"""
    WriteDebug('argv is: %s' % sys.argv)
    WriteDebug('args is: %s' % args)
   
    if args and (len(sys.argv) <= 1 or override_sys):
        WriteDebug('Restarting with args: %s' % args)
        os.execl(sys.executable, '"%s"' % sys.executable, '"%s"' % args)
    elif len(sys.argv) > 1:
        argument = ' '.join(x if x.startswith('-') else '"%s"' % x 
                            for x in sys.argv[1:])
        WriteDebug('Restarting with argv: %s' % argument)
        os.execl(sys.executable, '"%s"' % sys.executable, argument)
    else:
        WriteDebug('Restarting without args!')
        os.execl(sys.executable, '"%s"' % sys.executable)

def sleep(secs_to_sleep):
    """Sleep the thread"""
    time.sleep(secs_to_sleep)

def exit(secs_to_sleep = 0, return_value = 0):
    """Exit the program"""
    WriteDebug('Exiting in %s seconds' % secs_to_sleep)
    if secs_to_sleep:
        sleep(secs_to_sleep)
    os._exit(return_value)


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

def Is64BitWindows():
    """ Check if the OS is windows in his 64 bit version. """
    return IsWindowPlatform() and '64' in platform.machine()
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
    return _DEBUG

import inspect
def WriteDebug( message ):
    """ Write debug log - will only be written if the DEBUG flag is True. 
        
        KEEP IN MIND: Calling the function must be made in a one line style,
        the reason for this is that we use the minifier to remove some code 
        when we're not in DEBUG mode, and it looks for lines starting with 
        "WriteDebug(" and remove them, so if you spread the call on several 
        lines, the result will be unpredicted.
    """
    # The Python optimizer will make sure that the function won't be compiled 
    # if _DEBUG is set to False.
    if DEBUG():
        # The message format is: [time] => [file] => [message]
        frame = inspect.stack()[1]
        file_name = inspect.getsourcefile(frame[0])
        message = '[%s] => %s => %s' % (time.strftime('%I:%M:%S'), file_name, message)
        try:
            print(message)
            #open(os.path.join('d:\\', 'subit.log'), 'a').write(message + '\r\n')
        except:
            try:
                print(message.encode('utf-8', 'ignore').decode('ascii', 'ignore'))
            except: pass
    else:
        pass

def CurrentTime():
    """ Return the value of time.time() as int. """
    return int(time.time())

def CurrentTimePrintable():
    """ Return the value of time.ctime(). """
    return time.ctime()