from itertools import groupby

from SubRankers.ISubStagesRanker import ISubStagesRanker

from Utils import WriteDebug
from Utils import FormatMovieName

class ByFullNameSubStagesRanker(ISubStagesRanker):
    """ SubStagesRanker that ranks the MovieSubStages using pure comparison 
        of the parameters. The comparison is made (most of the time) using the 
        set object in python.
    """
    @classmethod
    def rankMovieSubStagesByVersionsSum(cls, movie_sub_stages, query):
        # Array of movie name (element for each word). The array 
        # is of set type, for more complex operations on lists
        movie_name = set(FormatMovieName(query))
        # Will contain the ranked order of the movies
        movies_list = movie_sub_stages
        # Will mark that the first item in movies_list 
        # is an exact match.
        first_is_certain = False

        try:
            def cmp_name(movie_sub_stage):
                """ Compare between the given movie_sub_stage.VerSum and the 
                    movie_name parameter. The comparison is made by the
                    intersection_update of the set object of the two parameters 
                """
                movie_sub_stage_versum = \
                    set(FormatMovieName(movie_sub_stage.versions_sum))
                WriteDebug('[%s] cmp_name: %s, %s' % (cls, movie_sub_stage_versum, movie_name))
                movie_sub_stage_versum.intersection_update(movie_name)
                WriteDebug('[%s] cmp rank: %s' % (cls, len(movie_sub_stage_versum)))
                return len(movie_sub_stage_versum)
            # Store the ranked list. The sort is based on the rank given by 
            # cmp_name. 0 means lowest (will be placed last).
            movies_list = sorted(movies_list, key = cmp_name, reverse = True)
            # After ranking the list, we check for exact match in first item
            first_versum = FormatMovieName(movies_list[0].versions_sum)
            first_is_certain = cmp_name(movies_list[0]) == len(first_versum)
            WriteDebug('[%s] First item is certain by MovieSubStage.versions_sum? %s' % (cls, first_is_certain))
        except Exception as eX:
            WriteDebug('[%s] Failure raised while ranking the movie_sub_stages.versions_sum results: %s' % (cls, eX))
                
        return (movies_list, first_is_certain)

    @classmethod
    def rankVersionSubStages(cls, version_sub_stages, query):    
        # Array of movie name (element for each word). The array 
        # is of set type, for more complex operations on lists
        movie_name = set(FormatMovieName(query))
        # Will contain the ranked order of the versions list
        version_sub_stages_list = version_sub_stages
        # Will mark that the first item in version_sub_stages_list
        # is an exact match.
        first_is_certain = False

        try:
            def cmp_name(version_sub_stage):
                """ Compare between the given version_sub_stage.version_sum and 
                    the movie_name parameter. The comparison is made by the
                    intersection_update of the set object of the two parameters 
                """
                version_sub_stage_versum = \
                    set(FormatMovieName(version_sub_stage.version_sum))
                WriteDebug('[%s] cmp_name: %s, %s' % (cls, version_sub_stage_versum, movie_name))
                version_sub_stage_versum.intersection_update(movie_name)
                WriteDebug('[%s] cmp rank: %s' % (cls, len(version_sub_stage_versum)))
                return len(version_sub_stage_versum)

            # Store the ranked list. The sort is based on the rank given by 
            # cmp_name. 0 means lowest (will be placed last).
            version_sub_stages_list = \
                sorted(version_sub_stages_list, key = cmp_name, reverse = True)
            # After ranking the list, we check for exact match in first item
            first_versum = FormatMovieName(version_sub_stages_list[0].version_sum)
            first_is_certain = cmp_name(version_sub_stages_list[0]) == len(first_versum)
            WriteDebug('[%s] First item is certain by VersionSubStage.version_sum? %s' % (cls, first_is_certain))
        except Exception as eX:
            WriteDebug('[%s] Failure raised while ranking the VersionSubStages.version_sum results: %s' % (cls, eX))
                
        return (version_sub_stages_list, first_is_certain)