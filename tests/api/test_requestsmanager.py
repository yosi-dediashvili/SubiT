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
        requests_manager = \
            TimeDiffCheckerRequestsManager.get_instance("async_test")
        requests_manager.test_case = self
        self.threads_pool.map(
            lambda idx: requests_manager.perform_request("a", "a"),
            range(NUMBER_OF_THREADS))
        end_time = time.time()
        self.assertGreaterEqual(
            end_time - start_time,
            SECONDS_BETWEEN_REQEUESTS * NUMBER_OF_THREADS)

    def test_multithreaded_perform_request_uniqe(self):
        pass

    def test_multithreaded_perform_request_next(self):
        start_time = time.time()
        requests_manager = \
            NoTimeDiffCheckerRequestsManager.get_instance("async_test_next")
        self.threads_pool.map(
            lambda idx: requests_manager.perform_request_next("a", "a"),
            range(NUMBER_OF_THREADS))
        end_time = time.time()
        self.assertLess(
            end_time - start_time,
            SECONDS_BETWEEN_REQEUESTS * NUMBER_OF_THREADS)

def run_tests():
    doctest.testmod(
        requestsmanager,
        verbose=False,
        optionflags=doctest.NORMALIZE_WHITESPACE)
    unittest.TextTestRunner(verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestRequestsManagerAsyncOp))
