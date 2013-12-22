
import Utils

if Utils.IsPython3():
    from queue import Queue
else:
    from Queue import Queue

import threading
import time

from SubProviders.Torec.TorecProvider.TorecProvider \
    import HttpRequestTypes, TOREC_PAGES

#===============================================================================
# Purpose is simple - Decrease the waiting time in the procedure. Instead of waiting
#    ~8 secs  in the middle of the flow, we collect hashcodes in a different thread,
#    outside the flow, and when it's time to send the hashcode back, we check to see
#    if enough time was passed, and if so, we send the request immidiately, and if
#    not, we wait the secs left, either way, it a WinWin situation.
#===============================================================================
class Hamster:
    HashCodes = Queue(10) #Queue with max size of 10 items
    MAX_TIME_TO_WAIT = 8 #Maximum time to wait after code request
        
    def __init__(self):
        #Start at his own thread
        hamsterRunner = threading.Thread(target=self.runner)
        hamsterRunner.daemon = True
        hamsterRunner.start()
    
    #===========================================================================
    # The worker in this class. each 5 secs send request for hashcode, and stores
    #    it in the queue, the queue is built from tuple -> (time of request, hashcode).
    #    After 10 items, the queue is blocked.
    #===========================================================================
    def runner(self):
        sleep_time = 5 #5 secs between each request
        
        while True:
            ctime = int(time.time()) #time of request
            guest_code = Utils.PerformRequest(TOREC_PAGES.DOMAIN, 
                                              TOREC_PAGES.TICKET, 
                                              #Torec "improved the mechanizm of the hash code, so it wants us 
                                              #to deliver the screen res and the sub_id, so we give him something
                                              'sub_id=1337&s=1600', 
                                              HttpRequestTypes.POST, 
                                              '')
            
            Hamster.HashCodes.put((ctime, guest_code), block=True)
            time.sleep(sleep_time)
    
    #===========================================================================
    # This function pops one code from the queue, and wait the time left (if there
    #    is such).
    #===========================================================================
    @staticmethod
    def getCode():
        (timegot, guest_code) = Hamster.HashCodes.get(block=True)
        timepast = int(time.time()) - timegot
        
        #Maximum time to wait (8 secs) - (Current time - time of request)
        time_to_wait = Hamster.MAX_TIME_TO_WAIT - timepast
        if time_to_wait > 0:
            #If we still got some time to wait
            time.sleep(time_to_wait)
            timepast = Hamster.MAX_TIME_TO_WAIT
            
        return (timepast, guest_code)
        