from SubChoosers.ISubStagesChooser import ISubStagesChooser
from SubRankers.ByPropertiesSubStagesRanker import ByPropertiesSubStagesRanker
from Utils import WriteDebug

class FirstInUncertainSubStagesChooser(ISubStagesChooser):
    """ Implementation of ISubStagesChooser. This chooser returns the first 
        SubStage returned from the ranking functions.
        
        In practice, the chooser uses the ByPropertiesSubStagesRanker ranker, 
        and ignores the first_is_certain value, and therefor takes the first
        SubStage no matter what. The only case where the chooser will return
        None is if the SubStages is empty.
    """
    @classmethod
    def chooseMovieSubStageFromMoviesSubStages(cls, movie_sub_stages, query):
        """ Choose the first MovieSubStage after ranking the movie_sub_stages 
            using the less accurate ranker: ByPropertiesSubStagesRanker.

            The function will return MovieSubStage regardless of the value in
            first_is_certain. The only case for returning None is if the value
            in movie_sub_stages is empty.
        """
        movie_sub_stage = None
        if movie_sub_stages:
            WriteDebug('Got results in movie_sub_stages, sending them to the ranker')
            (movie_sub_stages, first_is_ceratin) = ByPropertiesSubStagesRanker\
                .rankMovieSubStages(movie_sub_stages, query)
            WriteDebug('first_is_certain is %s, but we dont care' % first_is_ceratin)            
            movie_sub_stage = movie_sub_stages[0]
            WriteDebug('MovieSubStage: %s' % movie_sub_stage.info())
        else:
            WriteDebug('There is not results in movie_sub_stages, returning None')

        return movie_sub_stage

    @classmethod
    def chooseVersionSubStageFromVersionSubStages\
        (cls, version_sub_stages, movie_sub_stages, query):
        """ Choose the first VersionSubStage after ranking the values in the 
            version_sub_stages using the ByPropertiesSubStagesRanker.

            The function will return VersionSubStage regardless of the value in 
            first_is_certain. The only case for returning None is if the value
            in version_sub_stages is empty.
        """
        version_sub_stage = None
        if version_sub_stages:
            WriteDebug('Got Versions in version_sub_stages, sending them to the ranker')
            (version_sub_stages, first_is_ceratin) = ByPropertiesSubStagesRanker\
                .rankVersionSubStages(version_sub_stages, query)
            WriteDebug('first_is_certain is %s, but we dont care' % first_is_ceratin)                
            version_sub_stage = version_sub_stages[0]
            WriteDebug('VersionSubStage: %s' % version_sub_stage.info())
        else:
            WriteDebug('There is not results in version_sub_stages, returning None')

        return version_sub_stage
