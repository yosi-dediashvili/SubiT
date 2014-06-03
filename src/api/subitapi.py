from .langauges import Langauges

class SubiTAPI(object):
	""" 
	The implementation of the API. The interaction with SubiT is made entirely 
	via an instance of this class.

	The class does not use some sort of configuration internally, thus, all of 
	the parameters are exposed as arguments to the class's methods.
	"""

	def __init__(self, langauges, providers = []):
		"""
		The API is initialized with one or more Language instances retrieved 
		from the Languages class, and a list of zero or more providers names
		retrieved ProviderNames class.

		Note that the order of the lists specify their priority regarding 
		selection (The first element has the highest priority, and the last one
		the lowest priority).

		If the providers list is empty, we'll use the default order. Look in the
		ProviderNames class for more details.
		"""
		pass

	def get_input(self, query):
		"""
		Retrieve an Input object for some query. The query is a string that can
		either point to some file available on the filesystem, or a string that
		only contain the file name, or even only the title of the movie/series.
		"""
		pass

	def get_title_versions(self, input):
		"""
		Retrieves a list of TitleVersions instances for the given Input instance
		The list will be retrieved for all the providers and languages that was
		passed to the API when instantiated.

		Note that the versions inside each TitleVersions are sorted such that 
		the first version in the versions list is ranked highest.
		"""
		pass

	def get_subtitle_buffer(self, input, version):
		"""
		Given a Version instance and an Input instance associated with that 
		version, the function returns a tuple of (file name, file buffer) of 
		the subtitle that is associated with the version instance (from the 
		provider that holds that version). The buffer is the Bytes that was 
		retrieved from the site (Usually the zip/rar/srt buffer), and the name
		is the value that the site gave to that download.
		"""
		pass

	def deploy_subtitle(
		self, input, version, download_directory, naming_scheme, 
		subtitle_extensions, override_existing_subtitles = True):
		"""
		Deploys the subtitle file associated with the input and version, and 
		places the files in the download_directory naming the files using the
		naming_scheme instance. The files that will be deployed will always be
		the .srt/.sub files (even if the buffer that was downloaded from the 
		site was an archive file - the files will get extracted from it).

		subtitle_extensions is a list of file extensions (without a leading dot)
		that we'll use in order to decide whether or not to extract them from
		archive files.

		override_existing_subtitles specifies whether or not we'll deploy a 
		subtitle file if a file with the same name is already present in the 
		download_directory. Note that if an archive contains more than a single
		subtitle file, we'll discard the whole deployment process if even a 
		single file within it can't be deployed because of an already present 
		subtitle file.

		If the subtitle files deployed successfully, the function returns True,
		otherwise, the function returns False.
		"""
		pass

	def download_subtitle(
		self, query, minimal_rank, download_directory, naming_scheme, 
		subtitle_extensions, override_existing_subtitles = True):
		"""
		Performs the whole process of selecting and downloading the right 
		subtitle automatically. 

		The minimal_rank specifies the rank that is required in order for us to
		apply to automatic selection. If there is not version (in any specified)
		language that has a rank that is equals of greater from that value, the
		selection will not be performed.

		The query should specify the same thing as in the get_input() method.
		The arguments: download_directory, naming_scheme, subtitle_extensions 
		and override_existing_subtitles has the same meaning as in the 
		deploy_subtitle method.

		If the subtitle files deployed successfully, the function returns True,
		otherwise, the function returns False.
		"""
		pass