from api import requestsmanager

import time
import doctest
import unittest

SECONDS_BETWEEN_REQEUESTS = 2
NUMBER_OF_THREADS = 2


class TimeDiffCheckerRequestsManager(requestsmanager.RequestsManager):
    _last_request_time = time.time()

    def _perform_request(self, *args, **kwargs):
        time.sleep(SECONDS_BETWEEN_REQEUESTS)
        current_time = time.time()
        time_diff = current_time - type(self)._last_request_time
        self.test_case.assertGreaterEqual(time_diff, SECONDS_BETWEEN_REQEUESTS)
        type(self)._last_request_time = current_time

class NoTimeDiffCheckerRequestsManager(requestsmanager.RequestsManager):
    def _perform_request(self, *args, **kwargs):
        pass

class TestRequestsManagerAsyncOp(unittest.TestCase):
    def setUp(self):
        from multiprocessing.dummy import Pool
        self.threads_pool = Pool(NUMBER_OF_THREADS)

    def test_multithreaded_perform_request(self):
        start_time = time.time()
        requests_manager = TimeDiffCheckerRequestsManager()
        requests_manager.test_case = self
        self.threads_pool.map(
            lambda idx: requests_manager.perform_request("a", "a"),
            range(NUMBER_OF_THREADS))
        end_time = time.time()
        self.assertGreaterEqual(
            end_time - start_time,
            SECONDS_BETWEEN_REQEUESTS * NUMBER_OF_THREADS)

    def test_multithreaded_perform_request_next(self):
        start_time = time.time()
        requests_manager = NoTimeDiffCheckerRequestsManager()
        self.threads_pool.map(
            lambda idx: requests_manager.perform_request_next("a", "a"),
            range(NUMBER_OF_THREADS))
        end_time = time.time()
        self.assertLess(
            end_time - start_time,
            SECONDS_BETWEEN_REQEUESTS * NUMBER_OF_THREADS)

class TestPerformRequestContent(unittest.TestCase):
    def setUp(self):
        self.manager = requestsmanager.get_manager_instance("test_manager")

    def test_no_answer_request(self):
        self.assertFalse(self.manager._perform_request(
            "http://123.123.123.123/no_such_host"))

    def test_not_found_request(self):
        self.assertFalse(self.manager._perform_request(
            "http://www.google.com/should_return_error_404"))

    def test_textual_page(self):
        sha1_value = "57b1c1bfae35dea72cb9c2ddea997b7107da75a2".decode("hex")
        html_content = self.manager._perform_request(
            "http://subit-app.sf.net/tests/html_file.html")
        from hashlib import sha1
        self.assertEquals(sha1_value, sha1(html_content).digest())

    def test_binary_content(self):
        sha1_value = "99f13c24bfe7ea1c526cd8cdb6ffcc9644af5a9f".decode("hex")
        binary_content = self.manager._perform_request(
            "http://subit-app.sf.net/tests/binary_file.bin")
        from hashlib import sha1
        self.assertEquals(sha1_value, sha1(binary_content).digest())

    def test_with_response_headers(self):
        self.assertFalse(True)

    def test_with_missing_response_headers(self):
        self.assertFalse(True)

def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        requestsmanager, 
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(
        TestRequestsManagerAsyncOp))
    tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(
        TestPerformRequestContent))
    test_runner.run(tests)
