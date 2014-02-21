
import Utils

from Queue import Queue

import threading
import time

from SubProviders.Torec.TorecProvider.TorecProvider \
    import HttpRequestTypes, TOREC_PAGES

class Hamster:
    """ 
    Purpose is simple - Decrease the waiting time in the procedure. Instead of 
    waiting ~8 secs  in the middle of the flow, we collect hash codes in a 
    different thread, outside the flow, and when it's time to send the hash 
    code back, we check to see if enough time was passed, and if so, we send 
    the request immediately, and if not, we wait the secs left, either way, it
    is a WinWin situation.
    """

    MAX_TIME_TO_WAIT = 12 # Maximum time to wait after code request.

    # Torec improved their ticket mechanism. We now need to deliver the right
    # sub_id (which is the movie code in the VersionSubStage) for each download
    # request, otherwise, we get a default subtitle file (which says that we
    # should be shame for trying to use a program for downloading from the site
    # or something like that).
    def __init__(self, sub_id):

        self.sub_id = sub_id
        self.should_stop = False
        self.hash_codes = Queue(10) # Queue with max size of 10 items.
        # Start at his own thread.
        hamsterRunner = threading.Thread(target=self.runner)
        hamsterRunner.daemon = True
        hamsterRunner.start()

    def __del__(self):
        """ 
        On destruction, we call the stop method in order to stop the worker 
        thread.
        """
        self.stop()

    def runner(self):
        """ 
        The worker in this class. each 5 secs send request for hash code, and 
        stores it in the queue, the queue is built from tuple -> (time of 
        request, hash code). After 10 items, the queue is blocked.
        """
        sleep_time = 5 # 5 secs between each request.
        post_content_template = 'sub_id=%s&s=%s'
        
        while not self.should_stop:
            time_got = int(time.time())

            # sub_id is the movie code, s is the width resolution of the screen
            # (or at least supposed to be).
            guest_code = Utils.PerformRequest(
                TOREC_PAGES.DOMAIN,
                TOREC_PAGES.TICKET,
                post_content_template  % (self.sub_id, 1600),
                HttpRequestTypes.POST,
                '')
            
            self.hash_codes.put((time_got, guest_code), block=True)
            time.sleep(sleep_time)

    def stop(self):
        """ Signal the working thread to stop. """
        self.should_stop = True

    def getCode(self):
        """ 
        This function pops one code from the queue, and wait the time left (if 
        there is such).
        """
        (time_got, guest_code) = self.hash_codes.get(block=True)
        time_past = int(time.time()) - time_got
        
        # Maximum time to wait (8 secs) - (Current time - time of request).
        time_to_wait = Hamster.MAX_TIME_TO_WAIT - time_past
        if time_to_wait > 0:
            # If we still got some time to wait.
            time.sleep(time_to_wait)
            time_past = Hamster.MAX_TIME_TO_WAIT
            
        return (time_past, guest_code)
        