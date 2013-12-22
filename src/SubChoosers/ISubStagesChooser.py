class ISubStagesChooser(object):
    """ Interface for SubStage chooser. A chooser is an object that no matter
        what, will return one SubStage from many. A chooser from one side can
        be the user, and from the other side, be and object that simply select
        the first SubStage in the list.

        The SubChoosers are used as part of the main SubFlow procedure. The 
        Choosers should use the SubRankers in order to choose the SubStage.
    """
    
    @classmethod
    def chooseMovieSubStageFromMoviesSubStages(cls, movie_sub_stages, query):
        """ Choose a single MovieSubStage from the results returned by the 
            QuerySubSearch. The function returns a MovieSubStage. query is the 
            file_name from the SubFlow, or the user query.
            
            The only case where the function return None, is when sub_movies
            returnes no Results or when returning a MovieSubStage won't reflect 
            the True defenition of the Chooser, for example, When we say that 
            the chooser chosses MovieSubStage with a 100% reliability of match.
        """
        raise NotImplementedError\
            ('ISubStageChooser.chooseMovieSubStageFromMoviesSubStages')

    @classmethod
    def chooseVersionSubStageFromVersionSubStages\
        (cls, version_sub_stages, movie_sub_stages, query):
        """ Choose a single VersionSubStage from the results returned by the 
            MovieSubStage. The function returns a VersionSubStage. query is the 
            file_name from the SubFlow, or the user query.
            
            The only case where the function return None, is when sub_versions
            returnes no Versions or when returning a VersionSubStage won't 
            reflect the True defenition of the Chooser, for example, When we 
            say that the chooser chosses VersionSubStage with a 100% reliability 
            of match.
        """
        raise NotImplementedError\
            ('ISubStageChooser.chooseVersionSubStageFromVersionSubStages')