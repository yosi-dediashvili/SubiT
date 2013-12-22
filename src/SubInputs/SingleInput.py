import os

from SubInputs.SubInputsUtils import GetSubtitleDownloadDirectory
from SubInputs.SubInputsUtils import GetSubtitleSavingExtension

class SingleInput(object):
    """ The class serves the flow as a unified point of contact between the 
        flow and the input. The flow gets as an input a instance of this class.
    """
    def __init__(self, 
                 query, 
                 query_is_file, 
                 download_directory = None,
                 file_name          = None,
                 directory          = None, 
                 full_path          = None):
        # The query might be a simple query or a file name. The flow might 
        # change this value later for better matching and so on.
        self.query = query
        # Flag to indicate that the query is a file name
        self.query_is_file = query_is_file
        # The location of the download directory.
        self.download_directory = download_directory
        # A file name (optional). The value should not include the extension.
        self.file_name = file_name
        # The directory (optional) in which the file is in.
        self.directory = directory
        # The full path (optional) to the file.
        self.full_path = full_path
        # Finished working on the SingleInput instance? This value might be 
        # True even for Inputs that we didn't ended up with a subtitle.
        self.finisehd = False
        # The final VersionSubStage from which the subtitle is to be downloaded
        # or was downloaded. This parameter will be None also when we failed in
        # matching and downloading a subtitle for the SingleInput instance.
        self.final_version_sub_stage = None
        # Boolean to indicate wether we used the first language in the 
        # languages order set in the config.
        self.used_primary_language = False



    def getDownloadPath(self, interactive = False):
        """ The function return the path in which the subtitle should be saved. 
            The optional interactive parameter determines whether we can ask the
            user for the download location or not. The path returned is the 
            full path (including the file name and the extension) of the 
            subtitle.
        """
        directory = GetSubtitleDownloadDirectory\
            (self.download_directory, interactive)
        sub_file_name = GetSubtitleSavingExtension\
            (self.file_name if self.file_name else self.query)

        return os.path.join(directory, sub_file_name)

    def printableInfo(self):
        return ('%s: query: %s, query_is_file: %s, download_directory: %s, ' 
                'file_name: %s, directory: %s, full_path: %s, ' 
                'final_version_sub_stage: %s, used_primary_language: %s' % 
                (self, self.query, self.query_is_file, self.download_directory,
                 self.file_name, self.directory, self.full_path,
                 self.final_version_sub_stage, self.used_primary_language))
