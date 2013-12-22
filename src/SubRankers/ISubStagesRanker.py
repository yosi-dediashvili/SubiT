from itertools import groupby
from Utils import WriteDebug, FormatMovieName, IsSeries, GetSeriesParams, RemoveSeriesNumbering

class ISubStagesRanker(object):
    """ Interface for SubStages (MovieSubStage and VersionSubStage) rankers. 
        method are of type classmethod, because there's no need to store 
        instances of them.
    """
    @classmethod
    def rankMovieSubStages(cls, movie_sub_stages, query):
        """ Rank a list of MovieSubStages using a query string. The string is 
            taken from the QuerySubStage, so it can either be a file name, or 
            a user query.

            The Function calls the class implementation for two functions:
            rankMovieSubStagesByMovieName() and rankMovieSubStagesByVerSum(). 
            The result is a combination between these two functions.

            The function return a tuple of the ranked MovieSubStages, and a 
            boolean to indicate wether the first MovieSubStage in the list is a 
            first match for the query or not.
        """
        movie_sub_stages_ranked           = []
        first_movie_sub_stages_is_certain = False

        (movie_sub_stages_ranked_by_moviename, first_moviename_certain) = \
            cls.rankMovieSubStagesByMovieName(movie_sub_stages, query)

        if first_moviename_certain:
            WriteDebug('[%s] First movie_name is certain' % cls)
            # If the first item is certain, we need to check if there are more 
            # MovieSubStages with the same MovieName parameter, and if so, we 
            # need to compare also the VerSum parameters. Otherwise, if there's 
            # only one MovieSubStage with that MovieName, we'll consider him to 
            # be a certain result
            movie_sub_stages_groups = \
                groupby(movie_sub_stages_ranked_by_moviename, 
                        lambda movie_sub_stage: movie_sub_stage.movie_name)
            all_groups_items = [list(g) for k, g in movie_sub_stages_groups]
            first_group_items = all_groups_items[0]

            if len(first_group_items) > 1:
                WriteDebug('[%s] First group is more than one item long, we need to check the vesrions_sum to...' % cls)
                (movie_sub_stages_ranked_by_versum, first_versum_certain) = \
                    cls.rankMovieSubStagesByVersionsSum(first_group_items, query)

                first_movie_sub_stages_is_certain = first_versum_certain
                # We need to append the ranked version of the first group, so
                # we append the movie_sub_stages in two stages.
                for movie_sub_stage in movie_sub_stages_ranked_by_versum:
                    movie_sub_stages_ranked.append(movie_sub_stage)
                for movie_sub_stages in all_groups_items[1:]:
                    for movie_sub_stage in movie_sub_stages:
                        movie_sub_stages_ranked.append(movie_sub_stage)
            elif len(first_group_items) == 1:
                WriteDebug('[%s] Only one MovieSubStage is avaliable with that movie_name, there is not need to check versions_sum' % cls)
                first_movie_sub_stages_is_certain = True
                        
        if not movie_sub_stages_ranked:
            movie_sub_stages_ranked = movie_sub_stages_ranked_by_moviename
            WriteDebug('[%s] first movie is not certain' % cls)
        
        return (movie_sub_stages_ranked, first_movie_sub_stages_is_certain)

    @classmethod
    def rankMovieSubStagesByMovieName(cls, movie_sub_stages, query):
        """ Rank a list of MovieSubStages using the query string against the 
            movie_name parameter on each MovieSubStage. Also, the function 
            checks wether the query is an episode, by performing several regex
            check against the name, and if so, it treats the episode numbering
            in a different method than the whole query threat.


            The function return a tuple of the ranked MovieSubStages, and a 
            boolean to indicate wether the first MovieSubStage in the list is 
            a first match for the query or not.
        """
        # Array of movie name (element for each word). The array is 
        # of set type, for more complex operations on lists
        movie_name = set(FormatMovieName(query))
        # Will contain the ranked order of the movies
        movies_list = movie_sub_stages
        # Will mark that the first item in movies_list 
        # is an exact match.
        first_is_certain = False

        try:
            def cmp_name(movie_sub_stage):
                """ Compare between the given movie_sub_stage.movie_name and 
                    the movie_name parameter. The comparison is made by 
                    subsraction of the set object of the two parameters 
                """
                movie_sub_stage_name = set()
                if IsSeries(query):
                    (stage_season, stage_episode) = \
                        GetSeriesParams(movie_sub_stage.movie_name)
                    (query_season, query_episode) = \
                        GetSeriesParams(query)
                    if (stage_season == query_season and 
                        stage_episode == query_episode):
                        movie_sub_stage_name = set(FormatMovieName\
                            (RemoveSeriesNumbering(movie_sub_stage.movie_name)))
                        _movie_name = set(FormatMovieName\
                            (RemoveSeriesNumbering(query)))
                        WriteDebug('[%s] comparing series names: %s, %s' % (cls, movie_sub_stage_name, _movie_name))
                        return len(movie_sub_stage_name - _movie_name)
                    else:
                        WriteDebug('[%s] series dont match: %s, %s' % cls, movie_sub_stage.movie_name, query)
                        WriteDebug('Proceeding to default rank')

                
                movie_sub_stage_name = \
                    set(FormatMovieName(movie_sub_stage.movie_name))
                WriteDebug('[%s] comparing movie names: %s, %s' % (cls, movie_sub_stage_name, movie_name))
                return len(movie_sub_stage_name - movie_name)
            # Store the ranked list. The sort is based on the rank given by 
            # cmp_name. 0 means highest (will be placed first).
            movies_list = sorted(movies_list, key = cmp_name)
            # After ranking the list, we check for exact match in first item
            WriteDebug('Checking if the first result [%s] is a certain match' % movies_list[0].info())
            first_is_certain = cmp_name(movies_list[0]) == 0
            WriteDebug('[%s] First item is certain by MovieSubStage.movie_name? %s' % (cls, first_is_certain))
        except Exception as eX:
            WriteDebug('[%s] Failure raised while ranking the MovieSubStages.movie_name results: %s' % (cls, eX))
                
        return (movies_list, first_is_certain)

    @classmethod
    def rankMovieSubStagesByVersionsSum(cls, movie_sub_stages, query):
        """ Rank a list of MovieSubStages using the query string against the 
            versions_sum parameter on each MovieSubStage.

            The function return a tuple of the ranked MovieSubStages, and a 
            boolean to indicate wether the first MovieSubStage in the list is 
            a first match for the query or not.
        """
        raise NotImplemented('ISubStagesRanker.rankMovieSubStagesByVerionsSum')
    
    @classmethod
    def rankVersionSubStages(cls, version_sub_stages, query):
        """ Rank a list of VersionSubStages using a query string. The string is 
            taken from the QuerySubStage, so it can either be a file name, or a 
            user query.

            The function return a tuple of the ranked VersionSubStages, and a 
            boolean to indicate wether the first VersionSubStages in the list 
            is a first match for the query or not.
        """
        raise NotImplemented('ISubStagesRanker.rankVersionSubStages')