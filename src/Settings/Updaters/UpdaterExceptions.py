class UpdaterException(Exception):
    pass

class DownloadUpdaterException(UpdaterException):
    pass
class ServerTimeoutUpdaterException(DownloadUpdaterException):
    pass
class DownloadUrlMissingUpdaterException(DownloadUpdaterException):
    pass

class ApplyUpdaterException(UpdaterException):
    pass
class BadZipFileUpdaterException(ApplyUpdaterException):
    pass
class FileReplaceUpdaterException(ApplyUpdaterException):
    pass