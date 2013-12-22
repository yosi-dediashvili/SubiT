import os
from Utils import GetMoviesExtensions
from Utils import GetSubtitlesExtensions
from Utils import WriteDebug

def IsMovieFile(file_full_path):
    """ Check if the given file is movie file using the file extension. The 
        function return True when the file extension matches the list in the
        config (by calling GetMoviesExtesions), otherwise, False.
    """
    WriteDebug('Checking if the file is a movie file: %s' % file_full_path)
    file, extension = os.path.splitext(file_full_path)
    if not extension:
        WriteDebug('file has no extension, returning False')
        return False

    movie_extensions = GetMoviesExtensions()
    # Convert to lower in order to match the casing of the movie_extensions.
    extension = extension.lower()

    WriteDebug('The extension is: %s' % extension)
    is_movie_ext = extension in movie_extensions
    if is_movie_ext:
        WriteDebug('The extension is in the movie_extensions list.')
    else:
        WriteDebug('The extension is not in the movie_extensions list.')
    return is_movie_ext

def IsMovieFileGotSubtitle(file_full_path):
    """ Check wether the given subtitle file got subtitle in his directory.
        Subtitle files are files with the extensions that appears in the config.
        The check is performed against both the upper and lower case format of
        the subtitle.
    """
    WriteDebug('Checking if the file got subtitle: %s' % file_full_path)
    sub_extensions = GetSubtitlesExtensions()
    
    file_dir, file_name = os.path.split(file_full_path)
    file_name_no_ext = os.path.splitext(file_name)[0].lower()

    # In order to avoid casing problem in linux platform, we can't just use the
    # regular os.path.exists function on the movie file (but with subtitle ext
    # instead of the movie ext) in order to check for existing subtitle file.
    # Instead, we take all the files in the directory, and filter out those 
    # that have the same name (in lower case) as the movie file, after that, we
    # compare their lower-case extension to those in the sub_extensions list.
    files_in_dir = [i.lower() for i in os.listdir(file_dir)]
    same_names_in_dir = filter(lambda i: file_name_no_ext in i, files_in_dir)

    for name in same_names_in_dir:
        name_ext = os.path.splitext(name)[1].lower()
        if name_ext in sub_extensions:
            WriteDebug('The movie file is not missing a subtitle: %s' % name)
            return True
    WriteDebug('The movie file is missing a subtitle')
    return False

def GetMovieFilesInDirectory(directory, recursive = False):
    """ Return all the movie files in the given directory. If the recursive
        parameter is set to True, the function will check all the directories
        under the given directory also. The return value is a list containing
        the full path to each movie file that was found in the directory.
    """
    movie_files = []

    WriteDebug('Getting movie files inside the directory: %s' % directory)

    def _append_if_movie(_full_path):
        if os.path.isfile(_full_path) and IsMovieFile(_full_path):
            WriteDebug('The file is a movie file, adding it: %s' % _full_path)
            movie_files.append(_full_path)

    if not recursive:
        WriteDebug('We got called with recursive set to False, using os.listdir')
        for dir_item in os.listdir(directory):
            item_full_path = os.path.join(directory, dir_item)
            _append_if_movie(item_full_path)
    else:
        WriteDebug('We got called with recursive set to True, using os.walk')
        for current_dir, directories, files in os.walk(directory):
            for file in files:
                file_full_path = os.path.join(current_dir, file)
                _append_if_movie(file_full_path)
                
    return movie_files

def GetDirectoriesInDirectory(directory, recursive = False):
    """ Return all the directories in the given directory. If the recursive
        parameter is set to True, the function will check all the directories
        under the given directory also. The return value is a list containing
        the full path to each directory that was found in the directory.
    """
    directories = []

    if not recursive:
        WriteDebug('We got called with recursive set to False, using os.listdir')
        for dir_item in os.listdir(directory):
            item_full_path = os.path.join(directory, dir_item)
            WriteDebug('Checking if the item is dir: %s' % item_full_path)
            if os.path.isdir(item_full_path):
                WriteDebug('Adding the item to the list: %s' % item_full_path)
                directories.append(item_full_path)
    else:
        WriteDebug('We got called with recursive set to True, using os.walk')
        for current_dir, dirs, files in os.walk(directory):
            for dir in dirs:
                dir_full_path = os.path.join(current_dir, dir)
                WriteDebug('Adding the dir to the list: %s' % dir_full_path)
                directories.append(dir_full_path)

    return directories

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