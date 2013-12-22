from Utils import WriteDebug
from Utils import IsPython3

if IsPython3():
    from queue import Queue
else:
    from Queue import Queue

# The name of all the Choosers avaliable. The order of the Choosers in the list
# is such that the first chooser is the one we whould like to use the first and 
# so on.
class SubStagesChossersEnum:
    """ Enum for the Choosers indexes """
    CertainSubStagesChooser        = 0
    UncertainSubStagesChooser      = 1
    FirstResultSubStagesChooser    = 2
    InteractiveSubStagesChooser    = 3

SubStagesChoosers = \
    ['CertainSubStagesChooser.CertainSubStagesChooser', 
     'UncertainSubStagesChooser.UncertainSubStagesChooser',
     'FirstResultSubStagesChooser.FirstResultSubStagesChooser', 
     'InteractiveSubStagesChooser.InteractiveSubStagesChooser']
WriteDebug('SubStagesChoosers: %s' % SubStagesChoosers)

# Queue that will store all the Choosers names. We store them in queue in order
# to simplify the process of loading them in the right order
SubStagesChoosersQueue = Queue(len(SubStagesChoosers))
for chooser in SubStagesChoosers:
    WriteDebug('Adding chooser name to the queue: %s' % chooser)
    SubStagesChoosersQueue.put_nowait(chooser)

CurrentChooser = None
def getCurrentChooser():
    """ Return the current module set as the SubStagesChooser """
    WriteDebug('Returning Chooser: %s' % CurrentChooser)
    return CurrentChooser

def setNextChooser(interactive_allowed, first_allowed, uncertain_allowed):
    """ Will set the CurrentChooser to be the next one in the queue. The three
        parameters specify wether the corresponding chooser are allowed for use.
    """

    def _set_chooser(chooser_module):
        WriteDebug('Setting chooser: %s' % chooser_module)
        global CurrentChooser
        CurrentChooser = (chooser_module)

    if SubStagesChoosersQueue.empty():
        WriteDebug('The SubStagesChoosersQueue is empty, no more Choosers!')
        _set_chooser(None)
        return

    next_chooser = SubStagesChoosersQueue.get_nowait()
    WriteDebug('Next chooser is: %s' % next_chooser)
    

    if next_chooser == SubStagesChoosers[SubStagesChossersEnum.CertainSubStagesChooser]:
        from SubChoosers.CertainSubStagesChooser import CertainSubStagesChooser
        _set_chooser(CertainSubStagesChooser)
    elif next_chooser == SubStagesChoosers[SubStagesChossersEnum.UncertainSubStagesChooser] and uncertain_allowed:
        from SubChoosers.UncertainSubStagesChooser import UncertainSubStagesChooser
        _set_chooser(UncertainSubStagesChooser)
    elif next_chooser == SubStagesChoosers[SubStagesChossersEnum.FirstResultSubStagesChooser] and first_allowed:
        from SubChoosers.FirstResultSubStagesChooser import FirstResultSubStagesChooser
        _set_chooser(FirstResultSubStagesChooser)
    elif next_chooser == SubStagesChoosers[SubStagesChossersEnum.InteractiveSubStagesChooser] and interactive_allowed:
        from SubChoosers.InteractiveSubStagesChooser import InteractiveSubStagesChooser
        _set_chooser(InteractiveSubStagesChooser)
    else:
        WriteDebug('%s is not allowed!' % next_chooser)
        setNextChooser(interactive_allowed, first_allowed, uncertain_allowed)

