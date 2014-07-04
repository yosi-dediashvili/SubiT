class ProvidersNames(object):
    """
    The class holds the names of all the subtitles providers that SubiT uses. 
    This is the only place in which the provider name is typed directly. In any
    other place, a reference to this class will be present.

    Echo provider has its full name, which is usually its lower-cased fully 
    qualified DNS name, i.e., "www.torec.net", and its short name, which usually
    is just the middle name of the domain name, in the previous example, it will
    be "torec".
    """
    class ProviderName(object):
        def __init__(self, full_name, short_name):
            self.full_name = full_name
            self.short_name = short_name

        def __eq__(self, other):
            return (
                self.full_name == other.full_name and 
                self.short_name == other.short_name)

        def __str__(self):
            return repr(self)

        def __repr__(self):
            return (
                "<ProviderName full_name='%(full_name)s', "
                "short_name='%(short_name)s'>"
                % self.__dict__)

    class __metaclass__(type):
        def __iter__(self):
            for name, value in ProvidersNames.__dict__.items():
                if isinstance(value, ProvidersNames.ProviderName):
                    yield value

    OPEN_SUBTITLES = ProviderName("www.opensubtitles.org", "opensubtitles")