class Languages(object):
	"""
	This class holds all the supported languages by SubiT. Each languages has 
	its full name, and its short, ISO 639-2 version.

	This is the only place where the language is referenced directly, and not 
	via its "Language" instance. In any other place, there will be a reference
	to this place.

	The class implements the __iter__ function so it can be iterated in order
	to get all the languages that it holds.
	"""
	class Language(object):
		def __init__(self, full_name, iso_name):
			self.full_name = full_name
			self.iso_name = iso_name

		def __str__(self):
			return repr(self)

		def __repr__(self):
			return "<Language full_name='%s', iso_name='%s'>" % \
				(self.full_name, self.iso_name)

	class __metaclass__(type):
		""" 
		Define a metaclass in here in order to implement the __iter__ function.
		Otherwise, we won't be able to use __iter__ on the class object itself,
		and not instance of it.
		"""
		def __iter__(self):
			for name, value in Languages.__dict__.items():
				if isinstance(value, Languages.Language):
					yield value
	
	HEBREW = Language("Hebrew", "heb")
	ENGLISH = Language("English", "eng")

