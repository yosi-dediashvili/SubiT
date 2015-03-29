import logging
logger = logging.getLogger("subit.api.providers.torec.hamster")
from threading import Thread
from collections import deque
import time

from api.providers.torec.provider import TOREC_PAGES

__all__ = ['TorecHashCodesHamster']


# Time it takes for us to invalidate a ticket. The value is taken from the JS
# in torec handling the waiting time.
MAX_TICKET_SECS = 10
TICKETS_QUEUE_SIZE = 5
RUNNER_MAIN_LOOP_SLEEP_SECS = 1


class TorecTicket(object):
    def __init__(self, sub_id, time_got, guest_code):
        self.sub_id     = sub_id
        self.time_got   = time_got
        self.guest_code = guest_code
        logger.debug("Constructed a ticket: {}".format(self))

    @property
    def time_past(self):
        return int(time.time()) - self.time_got
    
    @property
    def time_to_wait(self):
        return MAX_TICKET_SECS - self.time_past

    @property
    def is_still_valid(self):
        return self.time_to_wait >= 0

    def wait_required_time(self):
        ttw = self.time_to_wait
        if ttw:
            logger.debug("Ticket requires sleeping for {} secs".format(ttw))
            time.sleep(ttw)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ("<TorecTicket sub_id={0.sub_id} "
            "time_got={0.time_got} guest_code={0.guest_code}>".format(self))


class TorecHashCodesHamster(object):
    """
    The hamster is responsible for obtaining download tickets from Torec's 
    servers for all the sub_ids that was passed to it.

    The hamster iterates over all its sub_ids, and makes sure that they have
    valid ticket. Each sub_id has a queue of size TICKETS_QUEUE_SIZE that gets
    filled as time passes.

    The hamster keeps requesting tickets for a given sub_id until the user marks
    that sub_id for deletion.
    """
    def __init__(self, requests_manager):
        self._requests_manager = requests_manager

        self._should_stop = False
        self._tickets = {}
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

    def _ensure_has_ticket(self, sub_id):
        post_content, tickets = self._tickets[sub_id]

        guest_code = None
        while not guest_code:
            logger.debug(
                "Getting ticket with: {}".format(post_content))
            guest_code = self._requests_manager.perform_request_next(
                TOREC_PAGES.TICKET,
                data = post_content
                )
            if guest_code == 'error':
                logger.error(
                    "Failed getting ticket for sub_id: {}".format(sub_id))

        time_got = int(time.time())
        ticket = TorecTicket(sub_id, time_got, guest_code)
        logger.debug("Got ticket: {}".format(ticket))
        tickets.append(ticket)

    def _runner(self):
        """ 
        The worker in this class. each 5 secs send request for hash code, and 
        stores it in the queue, the queue is built from tuple -> (time of 
        request, hash code). After 10 items, the queue is blocked.
        """
        logger.debug("_runner started.")

        while not self._should_stop:
            # Because the dict might change during iteration, we can't use the 
            # iterX methods.
            for sub_id in self._tickets.keys():
                self._ensure_has_ticket(sub_id)

            time.sleep(RUNNER_MAIN_LOOP_SLEEP_SECS)
        
        logger.debug("_runner ending.")

    def stop(self):
        """ Signals the working thread to stop. """
        self._should_stop = True

    def add_sub_id(self, sub_id):
        """ 
        Adds sub_id to the dict. Does not check whether or not that sub_id is
        in the dict already. This means that if a ticket was already obtained, 
        it will be removed for that sub_id.
        """
        # s according to Torec's JS is the screen width.
        post_content = {"sub_id" : sub_id, "s" : 1600}
        logger.debug("Constructed post_content: {}".format(post_content))
        self._tickets[sub_id] = (post_content, deque(maxlen=TICKETS_QUEUE_SIZE))

    def remove_sub_id(self, sub_id):
        del self._tickets[sub_id]

    def _get_valid_ticket(self, sub_id):
        post_content, tickets = self._tickets[sub_id]
        while not tickets:
            time.sleep(0.5)
            post_content, tickets = self._tickets[sub_id]

        ticket = tickets.popleft()
        while not ticket.is_still_valid and tickets:
            ticket = tickets.popleft()

        # Recursion if there are no valid tickets
        if not ticket.is_still_valid:
            return _get_valid_ticket(sub_id)

        return ticket
        
    def get_ticket(self, sub_id):
        """ 
        Retrieve the ticket associated with the provided sub_id. If the sub_id 
        is not in the dict, this methods adds it. 

        The method waits until the appropriate time is passed for that ticket.
        """
        if sub_id not in self._tickets:
            self.add_sub_id(sub_id)

        ticket = self._get_valid_ticket(sub_id)
        logger.debug("Got a ticket: {}".format(ticket))
        ticket.wait_required_time()

        return ticket
        
