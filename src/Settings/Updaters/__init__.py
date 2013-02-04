import Utils

def getUpdater():
    if Utils.GetSystemPlatform() == 'Windows':
        from Settings.Updaters.WinUpdater import WinUpdater
        if WinUpdater.GetRelevantPlatform() == Utils.GetSystemPlatform():
            return WinUpdater
    elif Utils.GetSystemPlatform() == 'Linux':
        from Settings.Updaters.LinuxUpdater import LinuxUpdater
        if LinuxUpdater.GetRelevantPlatform() == Utils.GetSystemPlatform():
            return LinuxUpdater
    else:
        return None