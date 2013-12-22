""" The SubInputs module serves mostly the SubFlow object. The getSingleInput...
    function acts as an iterator by yielding objects of SingleInput type.
"""
import os

from SubInputs.SingleInput import SingleInput
from SubInputs.SubInputsUtils import GetMovieFilesInDirectory
from SubInputs.SubInputsUtils import IsMovieFileGotSubtitle
from SubInputs.SubInputsUtils import IsMovieFile

from Utils import WriteDebug

def getSingleInputsFromAllTypes(queries = [], files = [], directories = []):
    """ Get SingleInput instances for all the available types of inputs. The
        function simply calls the corresponding function for each type, and
        yield its results.
    """
    WriteDebug('Getting SingleInputs for directories: %s' % directories)
    for dir_single_input in getSingleInputsFromDirectories(directories, True):
        yield dir_single_input

    WriteDebug('Getting SingleInputs for files: %s' % files)
    for file_single_input in getSingleInputFromFiles(files):
        yield file_single_input

    WriteDebug('Getting SingleInputs for queries: %s' % queries)
    for query_single_input in getSingleInputsFromQueries(queries):
        yield query_single_input

def getSingleInputsFromDirectories(directories, recursive = False):
    """ Get SingleInput instances for the movie files inside the given 
        directories. If the recursive parameter is set to True, The function
        will return instances for files inside sub directories also. The 
        directories should have a full path.
    """
    for directory in directories:
        for single_input in getSingleInputsFromDirectory(directory, recursive):
            yield single_input

def getSingleInputsFromDirectory(directory, recursive = False):
    """ Get SingleInput instances for the movie files inside the given 
        directory. If the recursive parameter is set to True, The function
        will return instances for files inside sub directories also. The 
        directory should have a full path.
    """
    movie_files = GetMovieFilesInDirectory(directory, recursive)
    for file_single_input in getSingleInputFromFiles(movie_files):
        yield file_single_input
    

def getSingleInputFromFiles(files):
    """ Get SingleInput instances for the given files. The files should have a
        full path.
    """
    WriteDebug('Getting SingleInputs for the files: %s' % files)
    for file in files:
        if IsMovieFile(file):
            WriteDebug("file is a movie file.")
            if not IsMovieFileGotSubtitle(file):
                yield getSingleInputFromFile(file)
        else:
            WriteDebug("The file is not a movie file, skipping.")

def getSingleInputFromFile(file):
    """ The function will return an instance of SingleInput for the given file.
        The file should have a full path.
    """
    WriteDebug('Creating SingleInput instance from the file: %s' % file)
    directory = os.path.dirname(file)
    file_name, extension = os.path.splitext(os.path.basename(file))

    single_input = SingleInput\
        (file_name, True, directory, file_name, directory, file)
    WriteDebug('Created SingleInput instance from file.')

    return single_input

def getSingleInputsFromQueries(queries):
    """ Get SingleInput instance for the given queries. """
    WriteDebug('Getting SingleInputs for the queries: %s' % queries)
    for query in queries:
        yield getSingleInputFromQuery(query)

def getSingleInputFromQuery(query):
    """ The function will return an instance of SingleInput for the given query.
    """
    WriteDebug('Creating SingleInput instance from the query: %s' % query)
    # We are not adding any optional parameter.
    if os.path.exists(query):
        single_input = getSingleInputFromFile(query)
    else:
        single_input = SingleInput(query, False)
    WriteDebug('Created SingleInput instance from query.')

    return single_input