import Utils
import Logs

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

class ISubHandler:
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

    #===========================================================================
    # This function contains the logic for rangking the results returned from 
    # "findversionslist" function. 
    # Logic is pretty much straight forward:
    # On each item in the array remove the words appearing in the movie name 
    # (the first parameter) If the number of word left is larger or equal to 
    # the previous item, put it bellow him, else, put it before him.
    #===========================================================================
    @staticmethod
    def findrelevantsubversions( filename, subMovie ):
        subVersions = subMovie.Versions()
        #Create array from the movie name
        filename = filename.replace(' ', '.').split('.')
        for i in filename: 
            if '-' in i: 
                for l in i.split('-'): filename.append(l)
        
        #Convert the array to set
        filename = set( map(str.lower, filename) )
        #Sorting logic...
        subVersions.sort( lambda c_ver, n_ver: 
                                    1 if 
                                        len( filename - set( n_ver.VerSum
                                                              .replace('-', ' ')
                                                              .split(' ') ) ) 
                                        <
                                        len( filename - set( c_ver.VerSum
                                                              .replace('-', ' ')
                                                              .split(' ') ) ) 
                                    else -1
                    )
    
        firstitem = set( subVersions[0].VerSum.replace('-', ' ').split(' ') )
        firstitem.difference_update( filename )    
        #Check if the first result is certain (full match)
        first_is_certain = ( len(firstitem) == 0 )
                
        return (subVersions, first_is_certain)
    
    #===========================================================================
    # Function Containg logic for ranking the movies from the search. logic is 
    # same as the sub_versions ranking.
    #===========================================================================
    @staticmethod
    def findrelevantmovies( subSearch ):
        moviename = subSearch.Query
        movieslist = subSearch.Results()
        #Create array from the movie name
        moviename = moviename.replace(' ', '.').split('.')
        for i in moviename: 
            if '-' in i: 
                for l in i.split('-'): moviename.append(l)
        
        #Convert the array to set
        moviename = set( map(str.lower, moviename) )
        #Sorting logic [1 means take it one up, -1 means take one down]
        movieslist.sort( lambda c_ver, n_ver: 
                                    1 if
                                        #=======================================================
                                        #Check By MovieName of the items -> we check the value of
                                        #(MovieName - moviename) - if the items left on this element
                                        #are less then the next element, we say that the current 
                                        #element is better match then the next one.
                                        (
                                        len(set( map( str.strip, 
                                                      n_ver.MovieName.lower().replace('/', ' ').split(' ')
                                                    ) ) - moviename ) 
                                        <
                                        len(set( map( str.strip, 
                                                      c_ver.MovieName.lower().replace('/', ' ').split(' ')
                                                    ) ) - moviename )) 
                                        or
                                        #Check By VerSum of the items -> we check the value of 
                                        #(VerSum - moviename) - if the items left on this element
                                        #are less then the next element, we say that the current 
                                        #element is better match then the next one.
                                        (
                                        len( moviename - set( map( str.strip, 
                                                                   n_ver.VerSum.lower().replace('/', ' ').split(' ')
                                                                  ) ) ) 
                                        <
                                        len( moviename - set( map( str.strip, 
                                                                   c_ver.VerSum.lower().replace('/', ' ').split(' ')
                                                                  ) ) ) )
                                        #========================================================
                                    else -1
                    )
    
        
        firstitem_ver   = set( map(str.strip, movieslist[0].VerSum.lower().replace('/', ' ').split(' ')) )
        firstitem_ver.difference_update( moviename )    
        firstitem_name  = set( map(str.strip, movieslist[0].MovieName.lower().replace('/', ' ').split(' ')) )
        firstitem_name.difference_update( moviename )    
        
        #Check if the first result is certain (full match)
        first_is_certain = ( len(firstitem_ver) == 0 or len(firstitem_name) == 0)
        
        Utils.writelog(INFO_LOGS.GOT_EXACT_MATCH_FROM_MOVIE_RANKING if first_is_certain else 
                       INFO_LOGS.NO_EXACT_MATCH_FROM_MOVIE_RANKING_TAKING_FIRST)
        
        return movieslist[0]