from Queue import Queue

from SubInputs import getSingleInputsFromAllTypes
from Utils import WriteDebug

class SingleInputsQueue(Queue):
    """ A Queue for storing SingleInputs for SubFlow work. The class is a 
        simple wrapper for the Queue.Queue class of python.
    """
    def __init__(self, queries = [], files = [], directories = []):
        WriteDebug('Initalzing SingleInputsQueue: %s' % self)
        Queue.__init__(self)

        for single_input in getSingleInputsFromAllTypes\
            (queries, files, directories):
            self.putSingleInput(single_input)

        WriteDebug('Finished intialzing the SingleInputsQueue: %s' % self)

    def putSingleInputs(self, single_inputs, block = False):
        """ Put the given single_inputs in the queue. If block is True, the 
            calling thread will get blocked until the queue is not full.
        """
        WriteDebug('Putting %s SingleItems in the queue.' % len(single_inputs))
        for single_input in single_inputs:
            self.putSingleInput(single_input, block)


    def putSingleInput(self, single_input, block = False):
        """ Put SingleInput item in the queue. If block is True, the calling
            thread will get blocked until the queue is not full.
        """
        WriteDebug('Putting SingleItem in the queue.')
        self.put(single_input, block)

    def getSingleInputs(self, max_items):
        """ Get a list of single inputs from the queue. The max possible size
            of the list is max_items. If the queue get empty in the middle, we
            return the items retrieved so far.
        """
        single_inputs = []
        WriteDebug('Getting %s from the SingleInputsQueue.' % max_items)
        while max_items > 0:
            single_input = self.getSingleInput()
            # If we got None, it means that the queue is empty, therefore, we
            # break the loop, and return the list.
            if not single_input:
                break
            single_inputs.append(single_input)
            max_items -= 1

        WriteDebug('Returning %s items from the SingleInputsQueue.' % len(single_inputs))
        return single_inputs

    def getSingleInput(self, block = False):
        """ Retrieve a single SingleInput from the queue. Return None if the 
            queue is empty and block is set to Fasle, otherwise, wait until an
            item is added to the queue.
        """
        single_input = None
        if not block and self.empty():
            WriteDebug('The queue is empty, returning None.')
            return single_input

        try:
            WriteDebug('Getting single item from the queue.')
            single_input = self.get(block)  
        except:
            WriteDebug('Failed getting single item from the queue, returning None.')

        return single_input