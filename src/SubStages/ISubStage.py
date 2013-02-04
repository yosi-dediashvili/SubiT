def getSubProviderByName(provider_name):
    """ Call the getSubProviderByName function of the SubProviders module """
    from SubProviders import getSubProviderByName
    return getSubProviderByName(provider_name)

def getSubProvider():
    """ Call the getSubProvider function of the SubProviders module """
    from SubProviders import getSubProvider
    return getSubProvider()

class ISubStage(object):
    """ An interface for the different stages of the procedure of retriving a
        subtitle file. 
        
        The Stages in SubiT are (more info on each stage is avaliable at the 
        stage implementation):
            1. Query: Sending a movie query to some SubProvider
            2. Movie: A single item from the results returned from the Query
            3. Version: The last stage, the one that will give us the subtitle

        The stages simplify the the connection to the rest of the modules in 
        SubiT. For example, instead of addressing the SubProviders directly,
        by using the SubStage, we can send a query to the current SubProvider
        by simply instantiating QuerySubStage, and calling his Results method.
    """
    def __init__(self, provider_name):
        # provider_name stores the PROVIDER_NAME value of the Provider that got 
        # the results. We need to know that because the SubFlow might get 
        # results for many providers, so the provider that returns from 
        # GetProvider method is not necessarily us, and he won't be able to 
        # process the values of the SubStage correctly.
        self.provider_name = provider_name


    # Overwrite comparison operators so we can check if two Results are equals 
    # using only the relevant params, and not addresses and so on
    def __eq__(self, other_result):
        raise NotImplementedError('ISubStage.__eq__')
    def __ne__(self, other_result):
        raise NotImplementedError('ISubStage.__ne__')

    def info(self):
        """ Return string of the relevant params on the SubStage. """
        raise NotImplementedError('ISubStage.Info')

