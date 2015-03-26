import logging
logger = logging.getLogger("subit.api.providers.torec.hamster")
from api.providers.torec.provider import TOREC_PAGES

from threading import Thread
from collections import deque, namedtuple
import time


__all__ = ['TorecHashCodesHamster']


TIME_BETWEEN_POSTS = 3 # Time between each post to the server.
MAX_TICKET_SECS    = 12 # Time it takes for us to invalidate a ticket.
QUEUE_SIZE         = 5

TorecTicket = namedtuple('TorecTicket', 'time_got, guest_code')

class TorecHashCodesHamster(object):
    """
    The hamster is a class that given a movie code from Torec, starts to collect
    hash codes (i.e., download tickets).

    An hamster is being assigned to every ProviderVersion.
    """

    def __init__(self, movie_code, requests_manager):
        self.sub_id = movie_code
        # sub_id is the movie code, s is the width resolution of the screen
        # (or at least supposed to be).
        self._post_content = {"sub_id" : self.sub_id, "s" : 1600}
        logger.debug("Constructed post_content: {}".format(self._post_content))
        self._requests_manager = requests_manager

        self._should_stop = False
        self._hashes_queue = deque(maxlen=QUEUE_SIZE)
        # Start at his own thread.
        hamsterRunner = Thread(target=self._runner)
        hamsterRunner.daemon = True
        hamsterRunner.start()

    def __del__(self):
        """ 
        On destruction, we call the stop method in order to stop the worker 
        thread.
        """
        self.stop()

    def _runner(self):
        """ 
        The worker in this class. each 5 secs send request for hash code, and 
        stores it in the queue, the queue is built from tuple -> (time of 
        request, hash code). After 10 items, the queue is blocked.
        """
        logger.debug("_runner started.")
        while not self._should_stop:
            time_got = int(time.time())
            logger.debug(
                "_runner getting ticket with: {}".format(self._post_content))
            guest_code = self._requests_manager.perform_request(
                TOREC_PAGES.TICKET,
                data = self._post_content
                )
            ticket = TorecTicket(time_got, guest_code)
            logger.debug("_runner got ticket: {}".format(ticket))
            self._hashes_queue.append(ticket)
            time.sleep(TIME_BETWEEN_POSTS)
        logger.debug("_runner ending.")

    def stop(self):
        """ Signal the working thread to stop. """
        self._should_stop = True

    def get_hash_code(self):
        """ 
        This function pops one code from the queue, and wait the time left (if 
        there is such).
        """
        ticket = self.hashes_queue.pop()
        time_past = int(time.time()) - ticket.time_got
        logger.debug("Popped a ticket: {}".format(ticket))
        time_to_wait = MAX_TICKET_SECS - time_past
        if time_to_wait:
            logger.debug(
                "Ticket requires sleeping for {} secs".format(time_to_wait))
            time.sleep(time_to_wait)
            time_past = MAX_TICKET_SECS
            
        return (MAX_TICKET_SECS, ticket.guest_code)
        