"""
Test classes for Addic7edProvider. 
	
The classes derives all the test from BaseSubProviderTest.
"""
import unittest

import BaseSubProviderTest

class Test_heb_Addic7edProviderTest(
	unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
	def setUp(self):
		from SubProviders.Addic7ed.heb_Addic7edProvider import Addic7edProvider
		BaseSubProviderTest.BaseSubProviderTest.__init__(
			self, 
			Addic7edProvider.Addic7edProvider(),
			"A Little Bit of Heaven",
			"Lost S06E16")

class Test_eng_Addic7edProviderTest(
	unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
	def setUp(self):
		from SubProviders.Addic7ed.eng_Addic7edProvider import Addic7edProvider
		BaseSubProviderTest.BaseSubProviderTest.__init__(
			self, 
			Addic7edProvider.Addic7edProvider(),
			"The Dark Knight",
			"The Big Bang Theory S04E12")

class Test_nor_Addic7edProviderTest(
	unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
	def setUp(self):
		from SubProviders.Addic7ed.nor_Addic7edProvider import Addic7edProvider
		BaseSubProviderTest.BaseSubProviderTest.__init__(
			self, 
			Addic7edProvider.Addic7edProvider(),
			"24: Redemption",
			"24 S08E17")

class Test_rus_Addic7edProviderTest(
	unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
	def setUp(self):
		from SubProviders.Addic7ed.rus_Addic7edProvider import Addic7edProvider
		BaseSubProviderTest.BaseSubProviderTest.__init__(
			self, 
			Addic7edProvider.Addic7edProvider(),
			"A Scanner Darkly",
			"Gossip Girl S02E05")

class Test_spa_Addic7edProviderTest(
	unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
	def setUp(self):
		from SubProviders.Addic7ed.spa_Addic7edProvider import Addic7edProvider
		BaseSubProviderTest.BaseSubProviderTest.__init__(
			self, 
			Addic7edProvider.Addic7edProvider(),
			"The Dark Knight",
			"How I Met Your Mother S08E02")

class Test_tur_Addic7edProviderTest(
	unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
	def setUp(self):
		from SubProviders.Addic7ed.tur_Addic7edProvider import Addic7edProvider
		BaseSubProviderTest.BaseSubProviderTest.__init__(
			self, 
			Addic7edProvider.Addic7edProvider(),
			"The Dark Knight",
			"Heroes S03E09")

class Test_slo_Addic7edProviderTest(
	unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
	def setUp(self):
		from SubProviders.Addic7ed.slo_Addic7edProvider import Addic7edProvider
		BaseSubProviderTest.BaseSubProviderTest.__init__(
			self, 
			Addic7edProvider.Addic7edProvider(),
			"Barbie as Rapunzel",
			"Lost S04E05")

class Test_cze_Addic7edProviderTest(
	unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
	def setUp(self):
		from SubProviders.Addic7ed.cze_Addic7edProvider import Addic7edProvider
		BaseSubProviderTest.BaseSubProviderTest.__init__(
			self, 
			Addic7edProvider.Addic7edProvider(),
			"Barbie of Swan Lake",
			"The Big Bang Theory S03E04")
		