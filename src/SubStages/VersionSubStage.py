from SubStages.ISubStage import ISubStage
from SubStages.ISubStage import getSubProviderByName

from Utils import WriteDebug, getlist, GetFile

from Logs import INFO as INFO_LOGS
from Logs import WARN as WARN_LOGS
from Logs import DIRECTION as DIRC_LOGS
from Logs import BuildLog

from Interaction import getInteractor
writeLog = getInteractor().writeLog

class VersionSubStage(ISubStage):
    """ This stage represent the final stage. What stands behind this stage is 
        simply a movie file, so by comparing the movie file to this version, 
        we can know wether or not they fit. In this stage we got the opportunity
        to finally download a subtitle, and therefor, after that stage, there's
        nowhere else to proceed and the flow ends for the specific movie/query.
    """
    def __init__(self, provider_name, version_sum, version_code, 
                 movie_code, extra = {}):
        """ Simple constructor. version_sum is the way that the site represent
            the file version, i.e. "the.matrix.720p.dts.ctrlhd", version_code
            is the code that represent the version in the site, movie_code is 
            the code that represent the movie (possibly equal to the movie_code
            of the MovieSubStage that returned this version).
        """
        self.provider_name  = provider_name
        self.version_sum    = version_sum
        self.version_code   = version_code
        self.movie_code     = movie_code
        # Extra param for anything that might come later in the life of SubiT
        self.extra          = extra

    def downloadSubtitle(self, directory_path, file_name):
        """ Download the subtitle. The file is saved under the file_name name
            in the directory_path. The function return True if the download
            succeeded, otherwise, False.
        """
        writeLog(INFO_LOGS.SENDING_SUBTITLE_FILE_REQUEST_FOR_SUBTITLE % 
                 self.info())
        WriteDebug('Sending subtitle file request for: %s' % self.info())
        (domain, url, referer) = \
            getSubProviderByName(self.provider_name).getSubtitleUrl(self)
        WriteDebug('Got subtitle url. domain: [%s], url: [%s], referer: [%s]' % (domain, url, referer))
        return GetFile(domain, url, directory_path, file_name, referer)

    def info(self):
        return ('provider_name: [%s], version_sum: [%s], version_code: [%s], '
                'movie_code: [%s]' % (self.provider_name, self.version_sum,
                                      self.version_code, self.movie_code))

    def __eq__(self, other):
        is_equal = True
        WriteDebug('Checking VersionSubStage equality')

        WriteDebug('Checking provider_name values: %s == %s' % (self.provider_name, other.provider_name))
        is_equal = is_equal and self.provider_name == other.provider_name
        WriteDebug('Checking version_sum values: %s == %s' % (self.version_sum, other.version_sum))
        is_equal = is_equal and self.version_sum == other.version_sum
        WriteDebug('Checking version_code values: %s == %s' % (self.version_code, other.version_code))
        is_equal = is_equal and self.version_code == other.version_code
        WriteDebug('Checking movie_code values: %s == %s' % (self.movie_code, other.movie_code))
        is_equal = is_equal and self.movie_code == other.movie_code

        WriteDebug('is_equal? [%s]' % is_equal)
        return is_equal

    def __ne__(self, other):
        WriteDebug('Checking VersionSubStage negative equality')
        return not self.__eq__(other)