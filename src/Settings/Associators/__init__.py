import Utils

def getAssociator():
    if Utils.IsWindowPlatform():
        from Settings.Associators.WinAssociator import WinAssociator
        if WinAssociator.GetRelevantPlatform() == Utils.GetSystemPlatform():
            return WinAssociator
    else:
        return None