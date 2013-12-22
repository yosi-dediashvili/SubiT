import Utils

# Params for program
ASSOCIATE_COMMAND   = '-associate'
DISASSOCIATE_COMMAND = '-disassociate'

def getAssociator():
    if Utils.IsWindowPlatform():
        from Settings.Associators.WinAssociator.WinAssociator import WinAssociator
        if WinAssociator.GetRelevantPlatform() == Utils.GetSystemPlatform():
            return WinAssociator
    else:
        return None