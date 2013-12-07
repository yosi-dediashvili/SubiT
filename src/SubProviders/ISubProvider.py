class ISubProvider(object):
    """ Interface for handling sub requests, implementation will be made on each 
        site. Keep in mind, the implementation can have as many more functions 
        or classes, in order to help with the procedure of getting the data.
    """
    # The PROVIDER_NAME is used to identify the specific provider all over the 
    # code. The name format should be [language] - [site]. for example if the 
    # provider is supplying hebrew subtitles from www.opensubtitles.org, the 
    # provider name will be: "Hebrew - www.opensubtitles.org"
    PROVIDER_NAME = 'ISubProvider.PROVIDER_NAME'
    # The png image related to that provider, the name should be the file name 
    # of the png file related to that provider, the format we use for the name
    # is "icon-subprovider-" + <subprovider_domain>, for example: if we set png 
    # to www.torec.net, the file name will be "icon-subprovider-torec.png"
    PROVIDER_PNG = 'ISubProvider.PROVIDER_PNG'
    
    def __init__(self):
        """ Init of the provider. Keep in mind, that on load time, the init is 
            called automatically, so that's the place to run all the stuff that 
            are outside of the SubFlow/SubStage.
        """
        pass
    
    @classmethod
    def findMovieSubStageList(cls, query_sub_stage):
        """ def:    Function to retrieve movies matching the given query_sub_stage.
            input:  query_sub_stage - instance of QuerySubStage.
            return: List<MovieSubStage>.
        """
        raise NotImplementedError('ISubProvider.findMovieSubStageList')

    @classmethod
    def findVersionSubStageList(cls, movie_sub_stage):
        """ def:    Function to retrieve subtitles version under the given 
                    movie_sub_stage.
            input:  movie_sub_stage - instance of MovieSubStage returned by 
                    findMovieSubStageList.
            return: List<VersionSubStage>.
        """
        raise NotImplementedError('ISubProvider.findVersionSubStageList')

    @classmethod
    def getSubtitleUrl(cls, version_sub_stage):
        """ def:    Function to retrieve the direct url of the subtitle file. 
                    Any special procedures to retrieve the subtitle's url should 
                    be made in here.
            input:  version_sub_stage - instace of VersionSubStage returned by 
                    findVersionSubStageList.
            return: tuple<str(domain), str(url), str(referrer), str(cookies)>
        """
        raise NotImplementedError('ISubProvider.getSubtitleUrl')

    @classmethod
    def SubProviderMethodWrapper(cls, func):
        """ A wrapper for the SubProvider methods. Prints info about the 
            function, and calls it safetly using try/except wrap (will return 
            None on exception, and write about it). In order to use it, just 
            decorate the provider method with @ISubProvider.SubProviderMethodWrapper
        """
        from Utils import WriteDebug
        WriteDebug('SubProviderMethodWrapper set for: %s' % func.__name__)
        def wrapper(*args, **kwargs):
            WriteDebug('Calling %s with: [%s, %s]' % (func.__name__, args, kwargs))
            # We start with None value, so using this decorator will automatically
            # return None on failure
            return_value = None
            try:
                return_value = func(*args, **kwargs)
                WriteDebug('%s Called successfully, return value is: %s' % (func.__name__, return_value))
            except Exception as eX:
                WriteDebug('%s failed: %s' % (func.__name__, eX))
            return return_value
        return wrapper    