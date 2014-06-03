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
		"""
		pass
	def get_input(self):
		pass
	def get_title_versions(self, input):
		pass
	def get_subtitle_buffer(self, input, version):
		pass
	def deploy_subtitle(self, input, version, path):
		pass
	def download_subtitle(self, input_path, download_directory):
		pass