from argparse import ArgumentParser, Action

from Utils import exit


# Association 
def handleAssociationAction(associate):
    from Settings.Associators import getAssociator

    associator = getAssociator()
    if not associator:
        print "Association is not avaliable."
        return
    if associate:
        associator.SetAssociation()
    else:
        associator.RemoveAssociation()
    exit()

class AssociationArgumentAction(Action):
    """ Action class that will get execute with the association request. """
    def __call__(self, parser, namespace, values, option_string):
        handleAssociationAction(True)

class DisassociationArgumentAction(Action):
    """ Action class that will get execute with the disassociation request. """
    def __call__(self, parser, namespace, values, option_string):
        handleAssociationAction(False)

class AssociationArgumentParser(ArgumentParser):
    """ Argument parser for handling association requests. """
    def __init__(self):
        from Settings.Associators import ASSOCIATE_COMMAND
        from Settings.Associators import DISASSOCIATE_COMMAND

        super(AssociationArgumentParser, self).__init__(add_help = None)
        self.add_argument\
            (ASSOCIATE_COMMAND, '-' + ASSOCIATE_COMMAND,
             action = AssociationArgumentAction, 
             default = None,
             nargs = 0,
             help = "Associate SubiT with the configured file types.")

        self.add_argument\
            (DISASSOCIATE_COMMAND, '-' + DISASSOCIATE_COMMAND,
             action = DisassociationArgumentAction, 
             default = None,
             nargs = 0,
             help = "Diassociate SubiT from the configured file types.")

# Query
def handleQueryAction(queries, files, directories):
    import SubiT
    
    queries = queries if queries else []
    files = files if files else []
    directories = directories if directories else []

    SubiT.startWorking(queries, files, directories)

class QueryArgumentParser(ArgumentParser):
    """ Argument parser for handling query requests. """
    def __init__(self):
        super(QueryArgumentParser, self).__init__(add_help = None)
        self.add_argument\
            ('-q', '-query', '-queries', '--q', '--query', '--queries',
             metavar = 'Query',
             type = str, 
             nargs = '+',
             help = "One or more queries to execute.")

        self.add_argument\
            ('-f', '-file', '-files', '--f', '--file', '--files', 
             metavar = 'File',
             type = str, 
             nargs = '+',
             help = "One or more files to query with.")

        self.add_argument\
            ('-d', '-dir', '-dirs', '--d', '--dir', '--dirs',
             metavar = 'Directory',
             type = str, 
             nargs = '+',
             help = "One or more directories to query with.")

# Loading mode
def handleLoadingModeAction(mode):
    from Interaction import setInteractor
    choices = LoadingModeArgumentParser.ChoicesVals

    if mode == choices.GUI:
        from Interaction.GuiInteractor import GuiInteractor
        setInteractor(GuiInteractor())
    elif mode == choices.CLI:
        from Interaction.ConsoleInteractor import ConsoleInteractor
        setInteractor(ConsoleInteractor())
    elif mode == choices.CLI_SILENT:
        from Interaction.ConsoleSilentInteractor import ConsoleSilentInteractor
        setInteractor(ConsoleSilentInteractor())
    elif mode == choices.BY_CONFIG:
        from Interaction import setDefaultInteractorByConfig
        setDefaultInteractorByConfig()
        
class LoadingModeArgumentParser(ArgumentParser):
    class ChoicesVals:
        GUI = 'GUI'
        CLI = 'CLI'
        CLI_SILENT = 'CLI-SILENT'
        BY_CONFIG = 'BY-CONFIG'

    Choices = [ChoicesVals.GUI, 
               ChoicesVals.CLI, 
               ChoicesVals.CLI_SILENT, 
               ChoicesVals.BY_CONFIG]

    def __init__(self):
        super(LoadingModeArgumentParser, self).__init__(add_help = None)
        self.add_argument\
            ('-mode', '--mode',
             # Notice that the default value will only set the attribute, but
             # it will no cause an execution of the associated Action. What it
             # means is that we have to execute the action in other way, and we 
             # do that by by calling the handleLoadingModeAction(mode) function
             # after we call the parse_args() function of the parser.
             default = [LoadingModeArgumentParser.ChoicesVals.GUI],
             choices = LoadingModeArgumentParser.Choices,
             nargs = 1,
             type = str,
             help = "The mode in which SubiT will be loaded.")

# Module function
def Parse():
    """ Will create the parser, and initiate SubiT loading procedure according 
        to the arguments. 
    """
    MainArgumentParser = ArgumentParser\
        (prog = "SubiT", 
         description = "Subtitles downloading, the right way.",
         parents = [AssociationArgumentParser(), 
                    QueryArgumentParser(),
                    LoadingModeArgumentParser()])
    
    
    args = MainArgumentParser.parse_args()
    # If for some reason, we are missing the mode attribute, we will use the 
    # GUI.
    handleLoadingModeAction(args.mode[0])
    handleQueryAction(args.q, args.f, args.d)

if __name__ == '__main__':
    Parse()