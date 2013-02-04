from SubChoosers.ISubStagesChooser import ISubStagesChooser

from Utils import WriteDebug
from Interaction import getInteractor as Interactor

from SubStages.MovieSubStage import MovieSubStage
from SubStages.VersionSubStage import VersionSubStage

from Logs import INFO as INFO_LOGS
from Logs import WARN as WARN_LOGS
from Logs import DIRECTION as DIRC_LOGS
from Logs import BuildLog

class InteractiveSubStagesChooser(ISubStagesChooser):
    """ Implementation of ISubStagesChooser. This chooser will ask the user for 
        the right choice. We use this chooser as a last resort if we can ask 
        the user to choose the SubStage.
    """
    @classmethod
    def chooseMovieSubStageFromMoviesSubStages(cls, movie_sub_stages, query):
        """ Ask the user to choose the right MovieSubStage. 
            
            The function returns MovieSubStage in most cases, except when 
            there's no results in the movie_sub_stages.
        """
        movie_sub_stage = None
        if movie_sub_stages:
            WriteDebug('We have Results in movie_sub_stages, asking the user choice')
            movie_sub_stage = Interactor().getMovieChoice\
                (movie_sub_stages, DIRC_LOGS.CHOOSE_MOVIE_FROM_MOVIES)
            WriteDebug('User MovieSubStage selection: %s' % movie_sub_stage.info())
        else:
            WriteDebug('There is no Results in movie_sub_stages, returning None')

        return movie_sub_stage

    @classmethod
    def chooseVersionSubStageFromVersionSubStages\
        (cls, version_sub_stages, movie_sub_stages, query):
        """ Ask the user to choose the right VersionSubStage. We let the user 
            browse the MovieSubStages also, and if he chose one, we call our 
            self again, until he chooses a VersionSubStage.
            
            The only case where the function will return None, is when both the
            version_sub_stages and movie_sub_stages has Results.
        """
        version_sub_stage = None
        if version_sub_stages or movie_sub_stages:
            WriteDebug('We have Results in version_sub_stages or in movie_sub_stages, asking the user choice')
            while not version_sub_stage:
                sub_stage = Interactor().getVersionChoice\
                    (version_sub_stages, movie_sub_stages,
                     DIRC_LOGS.CHOOSE_VERSION_FROM_VERSIONS)

                if type(sub_stage) is MovieSubStage:
                    WriteDebug('User selected MovieSubStage: %s' % sub_stage.info())
                    WriteDebug('Calling ourself again with selected MovieSubStage')
                    version_sub_stages = sub_stage.getVersionSubStages()
                    version_sub_stage = \
                        cls.chooseVersionSubStageFromVersionSubStages\
                        (version_sub_stages, movie_sub_stages, query)
                # Assuming that the only other option is VersionSubStage
                else:
                    WriteDebug('User selected SubVerion: %s' % sub_stage.info())
                    version_sub_stage = sub_stage
        else:
            WriteDebug('There is no Results in version_sub_stages, returning None')

        return version_sub_stage
