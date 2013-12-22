from Utils import WriteDebug
from SubChoosers.ISubStagesChooser import ISubStagesChooser


class FirstResultSubStagesChooser(ISubStagesChooser):
    """ Implementation of ISubStagesChooser. This chooser will always return
        the first SubStage in the list he got. We use that chooser as a last
        resort if we can't ask the user to choose the SubStage.
    """
    @classmethod
    def chooseMovieSubStageFromMoviesSubStages(cls, movie_sub_stages, query):
        """ In our implementation, simply returns the first MovieSubStage in 
            the movie_sub_stages.

            The function returns MovieSubStage in most cases, except when 
            there's no results in movie_sub_stages.
        """
        movie_sub_stage = None
        if movie_sub_stages:
            WriteDebug('Got results in movie_sub_stages, returning first MovieSubStage')
            movie_sub_stage = movie_sub_stages[0]
            WriteDebug('MovieSubStage: %s' % movie_sub_stage.info())
        else:
            WriteDebug('There is not results in the movie_sub_stages, returning None')
        
        return movie_sub_stage

    @classmethod
    def chooseVersionSubStageFromVersionSubStages\
        (cls, version_sub_stages, movie_sub_stages, query):
        """ In our implementation, simply returns the first VersionSubStage in 
            the version_sub_stages.

            The function returns VersionSubStage in most cases, except when 
            there's no versions in version_sub_stages.
        """
        version_sub_stage = None
        if version_sub_stages:
            WriteDebug('Got results in version_sub_stages, returning first VersionSubStage')
            version_sub_stage = version_sub_stages[0]
            WriteDebug('VersionSubStage: %s' % version_sub_stage.info())
        else:
            WriteDebug('There is not results in the version_sub_stages, returning None')
        
        return version_sub_stage            
