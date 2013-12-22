from SubChoosers.ISubStagesChooser import ISubStagesChooser
from SubRankers.ByFullNameSubStagesRanker import ByFullNameSubStagesRanker
from Utils import WriteDebug

class FirstInCertainSubStagesChooser(ISubStagesChooser):
    """ Implementation of ISubStagesChooser. This chooser return results after
        ranking them in the ByFullNameSubStagesRanker,
        
        In practice, the chooser uses the ByFullNameSubStagesRanker ranker, and
        return the first SubStages after the rank, regardless of the value in 
        first_is_certain.
    """
    @classmethod
    def chooseMovieSubStageFromMoviesSubStages(cls, movie_sub_stages, query):
        """ Choose the first MovieSubStage after ranking the Results using the 
            most accurate ranker avaliable (ByFullNameSubStagesRanker).

            The function will return MovieSubStage even if first_is_certain is 
            False for the first MovieSubStage that the ranker returned. Will
            return None if movie_sub_stages is empty.
        """
        movie_sub_stage = None
        if movie_sub_stages:
            WriteDebug('Got results in movie_sub_stages, sending them to the ranker')
            (movie_sub_stages, first_is_ceratin) = ByFullNameSubStagesRanker\
                .rankMovieSubStages(movie_sub_stages, query)
            WriteDebug('Ranker returned %s for first_is_certain, but we dont care' % first_is_ceratin)
            movie_sub_stage = movie_sub_stages[0]
            WriteDebug('MovieSubStage: %s' % movie_sub_stage.info())
        else:
            WriteDebug('There is not results in movie_sub_stages, returning None')

        return movie_sub_stage

    @classmethod
    def chooseVersionSubStageFromVersionSubStages\
        (cls, version_sub_stages, movie_sub_stages, query):
        """ Choose the first VersionSubStage after ranking the Results using 
            the most accurate ranker avaliable (ByFullNameSubStagesRanker).

            The function will return VersionSubStage even if first_is_certain 
            is False for the first VersionSubStage that the ranker returned.
            Will return None if version_sub_stages is empty.
        """
        version_sub_stage = None
        if version_sub_stages:
            WriteDebug('Got Versions in version_sub_stages, sending them to the ranker')
            (version_sub_stages, first_is_ceratin) = ByFullNameSubStagesRanker\
                .rankVersionSubStages(version_sub_stages, query)
            WriteDebug('Ranker returned %s for first_is_certain, but we dont care' % first_is_ceratin)
            version_sub_stage = version_sub_stages[0]
            WriteDebug('VersionSubStage: %s' % version_sub_stage.info())
        else:
            WriteDebug('There is not results in version_sub_stages, returning None')

        return version_sub_stage
