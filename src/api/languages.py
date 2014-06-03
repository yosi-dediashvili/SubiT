class Languages(object):
	"""
	This class holds all the supported languages by SubiT. Each languages has 
	its full name, and its short, ISO 639-2 version.

	This is the only place where the language is referenced directly, and not 
	via its "Language" instance. In any other place, there will be a reference
	to this place.
	"""
	class Langauge(object):
		def __init__(self, full_name, iso_name):
			self.full_name = full_name
			self.iso_name = iso_name
	pass