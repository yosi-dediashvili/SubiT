import unittest

import BaseSubProviderTest
from SubProviders.Torec.TorecProvider import TorecProvider

from TestUtils import WriteTestLog

class Test_TorecProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    """
    Test class for TorecProvider. 
    
    The class derives all the test from BaseSubProviderTest, but replaces the 
    implementation of test_downloadSubtitle.

    Our implementation verifies that we didn't get the "Fake" subtitle file
    from Torec, that a zip file contatinig a subtitle that is full of lines
    telling us not to download the subtitles using a program. 
    """
    def setUp(self):
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            TorecProvider.TorecProvider())

    def test_downloadSubtitle(self):
        """
        Perform the regular check, but also, verify the the file size is greater
        than 4KB. Torec's fake zip file is about 2KB in size, so it's engouh to
        check for this size in order for us to be sure that this is not a fake.
        """
        file_size = super(Test_TorecProviderTest, self).test_downloadSubtitle()
        self.assertGreater(
            file_size, 
            4096, 
            "Received fake download file from Torec.")

    def test_downloadSubtitlesMultiple(self):
        """
        This test will execute the base test_downloadSubtitle() several times, 
        in order to gather statistics about are success rate agaisnt Torec's 
        defense.
        """
        success_count = 0
        failure_count = 0
        for i in range(100):
            WriteTestLog("Checkig Torec's defense for the %s time." % i) 
            file_size = super(Test_TorecProviderTest, self)\
                .test_downloadSubtitle()
            succeeded = file_size > 4096
            if succeeded:
                success_count += 1
            else:
                failure_count += 1

            WriteTestLog(
                "\nTorec Stats:\n\tsuccess_count: %s\n\tfailure_count: %s" % 
                (success_count, failure_count))