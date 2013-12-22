from itertools import groupby

from SubRankers.ISubStagesRanker import ISubStagesRanker

from Utils import WriteDebug
from Utils import FormatMovieName

class ByPropertiesSubStagesRanker(ISubStagesRanker):
    """ SubStageRanker that ranks the results by using the video and audio
        properties. The ranker is written after a request from some users. 
    """
    # We store the properties in lower case, and that's how we'll check matches
    VideoProperties = ['480p', '720p', '1080p', '1080i', 'dvdrip', 'ts', 
                       'bluray', 'blu-ray', 'x264', 'hddvd', 'brrip', 
                       'hdrip', 'hdtv']
    AudioProperties = ['ac3', 'dts']

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
        # Store only the properties that apears in the movie_name
        total_props_in_movie_name = \
            set(cls.VideoProperties + cls.AudioProperties)
        total_props_in_movie_name.intersection_update(movie_name)
    
        try:
            def cmp_props(movie_sub_stage):
                """ Compare by using intersection_update on the props and the 
                    movie. The return value is the length of props apearing in 
                    both movie_name and movie_sub_stage.VerSum
                """
                movie_sub_stage_versum = \
                    set(FormatMovieName(movie_sub_stage.versions_sum))
                WriteDebug('[%s] cmp_props: %s, %s' % (cls, total_props_in_movie_name, movie_sub_stage_versum))
                total_props = total_props_in_movie_name.intersection\
                    (movie_sub_stage_versum)
                WriteDebug('[%s] cmp rank: %s' % (cls, len(total_props)))
                return len(total_props)

            movies_list = sorted(movies_list, key = cmp_props, reverse = True)
            # Because the rank is a ByProperties rank, we're satisfied even 
            # with one tag in the versions_sum
            first_is_certain = cmp_props(movies_list[0]) > 0
            WriteDebug('[%s] First item is certain by MovieSubStage.versions_sum? %s' % (cls, first_is_certain))
        except Exception as eX:
            WriteDebug('[%s] Failure raised while ranking the MovieSubStages.versions_sum results: %s' % (cls, eX))

        return (movies_list, first_is_certain)

    @classmethod
    def rankVersionSubStages(cls, version_sub_stages, query):    
        # Array of movie name (element for each word). The array 
        # is of set type, for more complex operations on lists
        movie_name = set(FormatMovieName(query))
        # Will contain the ranked order of the versions list
        version_sub_stages_list = version_sub_stages
        # Will mark that the first item in movie_sub_stages_list 
        # is an exact match.
        first_is_certain = False
        # Store only the properties that apears in the movie_name
        global VideoProperties
        global AudioProperties
        total_props_in_movie_name = \
            set(cls.VideoProperties + cls.AudioProperties)
        total_props_in_movie_name.intersection_update(movie_name)
    
        try:
            def cmp_props(version_sub_stage):
                """ Compare by using intersection_update on the props and the 
                    movie. The return value is the length of props apearing in 
                    both movie_name and movie_sub_stage.VerSum
                """
                version_sub_stage_versum = \
                    set(FormatMovieName(version_sub_stage.version_sum))
                WriteDebug('[%s] cmp_props: %s, %s' % (cls, total_props_in_movie_name, version_sub_stage_versum))
                total_props = total_props_in_movie_name.intersection\
                    (version_sub_stage_versum)
                WriteDebug('[%s] cmp rank: %s' % (cls, len(total_props)))
                return len(total_props)

            version_sub_stages_list = \
                sorted(version_sub_stages_list, key = cmp_props, reverse = True)
            # Because the rank is a ByProperties rank, we're satisfied even 
            # with one tag in the version_sum
            first_is_certain = cmp_props(version_sub_stages_list[0]) > 0
            WriteDebug('[%s] First item is certain by VersionSubStage.version_sum? %s' % (cls, first_is_certain))
        except Exception as eX:
            WriteDebug('[%s] Failure raised while ranking the VersionSubStages.version_sum results: %s' % (cls, eX))

        return (version_sub_stages_list, first_is_certain)
