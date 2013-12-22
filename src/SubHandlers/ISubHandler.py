import Utils
import Logs
from itertools import groupby

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

class ISubHandler(object):
    """
    Interface for handling sub requests, implementation is to be made on each site.
    Keep in mind, implementation can have more function/classes, which will help 
    with the procedure."""
    
    #===========================================================================
    # The HANDLER_NAME will act as the identifier of the handler (Handler 
    # selection is made using this parameter)
    #===========================================================================
    HANDLER_NAME = 'ISubHandler.HANDLER_NAME'
    
    #===========================================================================
    # Init of the handler. Keep in mind, that on load time, the init is called
    # automatically, so that's the place to run all the stuff that are outside
    # of the SubFlow/SubResult.
    #===========================================================================
    def __init__(self):
        pass
    
    #===========================================================================
    # function to retrieve movies matching the given name (can return one result
    # also). The parameter can be anything from just the movie name to the whole
    # file name of the given movie.
    # ------------
    # return list of SubMovie
    #===========================================================================
    @staticmethod
    def findmovieslist( subSearch ):
        #return List<SubMovie>
        raise Exception('Not Implemented: ISubHandler.findmovieslist')
    
    #===========================================================================
    # function to retrieve movie versions for one movie. The parameter is one of 
    # the movies returned by the "findmovieslist".
    # ------------
    # return list of SubVersion
    #===========================================================================
    @staticmethod
    def findversionslist( subMovie ):
        #return List<SubVersion>
        raise Exception('Not Implemented: ISubHandler.findversionslist')
    
    #===========================================================================
    # function to retrieve the final url to the subtitle file. The parameter is
    # one of the versions from the "findversionslist".
    # -------------
    # return tuple of (domain, url) values
    #===========================================================================
    @staticmethod
    def getsuburl( subVersion ):
        #return (domain, url)
        raise Exception('Not Implemented: ISubHandler.getsuburl')
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    
    
#===============================================================================
# Ranking mechanizm, Feel free to implement any other logic if needed
#===============================================================================
    @staticmethod
    def findrelevantmovies( subSearch ):
        """Function Containg logic for ranking the movies from the search. 
        logic is same as the sub_versions ranking."""

        #Array of movie name (element for each word), we split also "-" char. The array is from set type, for more complex operations on lists
        movie_name          = set(Utils.FormatMovieName(subSearch.Query))
        #Will contain the ranked order of the movies
        movies_list         = subSearch.Results()
        #If the first item in movies_list will be an exact match, this value will be true
        first_is_certain    = False


        try:
            #In order for the groupby function to work, the items needs to be in the right order (ordered by the Movie name)
            #Notice that later on, if we are not getting an exact match from the groupby, no further ranking is made for the movies_list
            movies_list.sort(lambda c,n: cmp(c.MovieName.lower(),n.MovieName.lower()))
            #We group by the movie name
            for movie_group, movie_group_items in groupby(movies_list, lambda i: i.MovieName.lower()):
                #We take only groups which as a complete match to our movie name (all the words 
                #from the results gets filtered out when reducing it with the query). We will get only one group.
                if not set(Utils.FormatMovieName(movie_group)) - movie_name:
                    #Convert it to list
                    list_items = [i for i in movie_group_items]
                    Utils.WriteDebug('%s: Exact match for MovieName, ranking items. Total items: %s' % (movie_group, len(list_items)))
                    #Set our movie list to the current list
                    movies_list = list_items
                    #Do another rank, now with the VerSum values
                    movies_list.sort(   lambda c_ver, n_ver: 
                                        #If current item contains more words from the movie_name rank it higher than the previous item
                                        1 if
                                        len(set(Utils.FormatMovieName(n_ver.VerSum)) - movie_name)
                                        <
                                        len(set(Utils.FormatMovieName(c_ver.VerSum)) - movie_name)
                                        else -1)
                                        #=============================================================================================
                    
                    #After we done ranking all results, we check to see if the first item is an exact match.
                    #The test is done using only the VerSum value (because we already checked the MovieName value)
                    query_without_movie_name = movie_name - set(movie_group.split(' '))
                    
                    #If we got only one movie left - set first_is_certain to True
                    if len(movies_list) == 1:
                        first_is_certain = True
                    #If it is not an empty list and the VerSum is not indicating that we didn't extracted the sub_types
                    elif query_without_movie_name and VerSum != 'Sub types are not supported in this handler':
                        firstitem_ver   = set(Utils.FormatMovieName(movies_list[0].VerSum))
                        #Leave only items which are not in both lists
                        query_without_movie_name.difference_update( firstitem_ver )
                        #If firstitem_ver is empty set list, the "not" will return True, so we got exact match
                        first_is_certain = not query_without_movie_name

                    Utils.WriteDebug('First item is certain? %s' % first_is_certain)

                else:
                    Utils.WriteDebug('%s: No exact match for MovieName, filtering items out!' % movie_group)
        
            Utils.writelog(INFO_LOGS.GOT_EXACT_MATCH_FROM_MOVIE_RANKING if first_is_certain else 
                           INFO_LOGS.NO_EXACT_MATCH_FROM_MOVIE_RANKING)

        except Exception as eX:
            Utils.WriteDebug('Failure raised while ranking the movies results: %s' % eX.message)
        
        return (movies_list, first_is_certain)


    @staticmethod
    def findrelevantsubversions( file_name, subMovie ):
        """This function contains the logic for ranking the results returned from findversionslist function. 
           Logic is pretty much straight forward:
            1. On each item in the array remove the words appearing in the movie name 
            2. If the number of word left (words not apearing in the file_name) is larger or 
               equal to the previous item, put it bellow him, else, put it before him."""
    
        #Array of file name (element for each word), we split also "-" char. The array is from set type, for more complex operations on lists
        file_name           = set(Utils.FormatMovieName(file_name))
        #Will contain the ranked order of the versions list
        subversions_list    = subMovie.Versions()
        #If the first item in subversions_list will be an exact match, this value will be true
        first_is_certain    = False

        try:
            #Sorting logic...
            subversions_list.sort(  lambda c_ver, n_ver: 
                                    #If current item contains more words from the file_name rank it higher than the previous item
                                    1 if 
                                    len(file_name - set(Utils.FormatMovieName(n_ver.VerSum)))
                                    <
                                    len(file_name - set(Utils.FormatMovieName(c_ver.VerSum)))
                                    else -1)
                                    #============================================================================================

            
            #After ranking the list, we check the first item (if it's an exact match or not)
            #Create a set from the VerSum (in order to manipulate it)
            first_item = set(Utils.FormatMovieName(subversions_list[0].VerSum))
            #Filter out items in both sets
            first_item.difference_update(file_name)
            #If first_item is empty list (not will return True), it means we got full match
            first_is_certain = not first_item
            Utils.WriteDebug('First item is certain? %s' % first_is_certain)
        except Exception as eX:
            Utils.WriteDebug('Failure raised while ranking the subversions results: %s' % eX.message)
                
        return (subversions_list, first_is_certain)
    
