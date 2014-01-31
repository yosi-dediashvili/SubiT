from PySide import QtCore, QtGui

import sys
import os

from Interaction import IInteractor
from Interaction import InteractionTypes
from Interaction import SubiTMainGui
from Interaction import SubiTAboutGui
from Interaction import SubiTSettingsGui
from Interaction import SubiTUpdateGui
from Interaction import SubiTLanguageGui


from Logs import MessageColor
from Logs import MessageString
from Logs import MessageType
from Logs import DIRECTION, INFO, FINISH
from Logs import GUI_SPECIAL as GUI_SPECIAL_LOGS

import Utils
from PySide.QtGui import QApplication

WriteDebug = Utils.WriteDebug
    
class UPDATE_STATUS:
    """ Enum of update status for logs purposes """
    ERROR       = 0
    CHECKING    = 1
    LATEST      = 2
    NEW_VERSION = 3

UPDATE_STATUS_IMAGES = \
    {UPDATE_STATUS.ERROR        : ':/Update/icon-update-error.png',
     UPDATE_STATUS.CHECKING     : ':/Update/icon-update-checking.png',
     UPDATE_STATUS.LATEST       : ':/Update/icon-update-latest.png',
     UPDATE_STATUS.NEW_VERSION  : ':/Update/icon-update-notice.png'}

class DIRECTION_IMAGES:
    INFO_LOG        = ':/MainWindow/icon-main-wait.gif'
    DIRECTION_LOG   = ':/MainWindow/icon-main-info.png'
    FINISHED_LOG    = ':/MainWindow/icon-main-finished.png'

class Signals(QtCore.QObject):
    """ We use the signals to pass the messages between the worker thread and
        the main (GUI) thread. Otherwise, we will get cross-thread warning and
        might crash also.
    """
    _logSignal          = QtCore.Signal(str)
    _movieSignal        = QtCore.Signal(object)
    _versionSignal      = QtCore.Signal(object, object)
    _searchSignal       = QtCore.Signal()
    _directorySignal    = QtCore.Signal(str)
    _updateSignal       = QtCore.Signal(str, str, str)
    _languageSignal     = QtCore.Signal()

class ChoiceTypes:
    """ Enum for possible user selection of SubStages. We need to use such an
        enum because we let the user choose between both a version and a movie
        and with that enum we mark ourself the selection type.
    """
    # In case of failure, we use this value
    UNKNOWN = -1 
    # MovieSubStage got selected
    MOVIE   = 0  
    # VersionSubStage got selected
    VERSION = 1  

class GuiInteractor(IInteractor.IInteractor):
    """ GUI implementation of the IInteractor. Serves SubiT in the GUI mode. 
        This implementation is supposed to be SubiT main interactor. """

    # Static variable to indicate the Interaction module that we're loaded
    IS_LOADED = False
    # Instance variable that holds all the signals for us
    messages_signals = None

    def __init__(self):
        """ The consturctor of the GuiInteractor """
        super(GuiInteractor, self).__init__()
        GuiInteractor.InteractionType = InteractionTypes.Gui
        self.waitCondition  = QtCore.QWaitCondition()
        self.mutex          = QtCore.QMutex()

        self.messages_signals = Signals()
        
        # Define all the signals connection
        self.messages_signals._logSignal.connect(self._writeLog)
        self.messages_signals._movieSignal.connect(self._getMovieChoice)
        self.messages_signals._versionSignal.connect(self._getVersionChoice)
        self.messages_signals._searchSignal.connect(self._getSearchInput)
        self.messages_signals._directorySignal.connect\
            (self._getDestinationDirectoryInput)
        self.messages_signals._updateSignal.connect(self._notifyNewVersion)
        self.messages_signals._languageSignal.connect(self._showLanguageSelection)

        # Start new instance of the gui
        self.app = QtGui.QApplication(sys.argv)
        self.mainWindow = QtGui.QMainWindow()

        self.mainWindow.closeEvent = self.onClose

        self.subitMainWindow = SubiTMainGui.Ui_SubiTMainWindow()
        # Build the Gui
        self.subitMainWindow.setupUi(self.mainWindow)

        self.finilizeSubiTMainGuiWidgets(self.mainWindow, self.subitMainWindow)

    def load(self):
        self.mainWindow.show()
        # Notify loading, and call exec 
        self.notifyLoaded()
        self.app.exec_()

    def notifyLoaded(self):
        GuiInteractor.IS_LOADED = True

    def onClose(self, close_event):
        from Settings.Config import SubiTConfig

        if SubiTConfig.Singleton().getBoolean\
            ('Gui', 'remember_last_window_size', True):
            current_window_size = \
                [str(self.mainWindow.width()), str(self.mainWindow.height())]
            SubiTConfig.Singleton().setList\
                ('Gui', 'last_window_size', current_window_size)

        if SubiTConfig.Singleton().getBoolean\
            ('Gui', 'remember_last_window_position', False):
            current_window_position = \
                [str(self.mainWindow.x()), str(self.mainWindow.y())]
            SubiTConfig.Singleton().setList\
                ('Gui', 'last_window_position', current_window_position)

        SubiTConfig.Singleton().setValue\
            ('Gui', 'show_log', self.subitMainWindow.logDockWidget.isVisible())

        close_event.accept()

    @staticmethod
    def IsLoaded():
        return GuiInteractor.IS_LOADED
    
    def writeLog(self, logMsg):
        """Write message to log"""
        self.messages_signals._logSignal.emit(logMsg)
    
    def _set_log_image(self, msg_type):
        """ Will set the log image to the relevant one. The msg_type is the
            value of the _TYPE_ variable of the message's class.
        """
        def _set(img_path):
            if not self.subitMainWindow.directionLogsIconLabel.movie():
                _movie = QtGui.QMovie()
                self.subitMainWindow.directionLogsIconLabel.setMovie(_movie)
            
            self.subitMainWindow.directionLogsIconLabel.movie().stop()
            self.subitMainWindow.directionLogsIconLabel\
                .movie().setFileName(img_path)
            self.subitMainWindow.directionLogsIconLabel.movie().start()

        if msg_type == DIRECTION._TYPE_:
            _set(DIRECTION_IMAGES.DIRECTION_LOG)
        elif msg_type == FINISH._TYPE_:
            _set(DIRECTION_IMAGES.FINISHED_LOG)
        else:
            _set(DIRECTION_IMAGES.INFO_LOG)

    @QtCore.Slot(str)
    def _writeLog(self, logMsg):
        real_message = MessageString(logMsg)
        color = MessageColor(logMsg)
        type = MessageType(logMsg)

        # If it's a direction message, we place it also on the direction label
        # with a info icon. If not, we place the DIRECTION.LOADING_PLEASE_WAIT 
        # value, with a wait icon
        self._set_log_image(type)
        if type in [DIRECTION._TYPE_, FINISH._TYPE_]:
            self.subitMainWindow.directionLogsLabel.setText(real_message)
        elif type == GUI_SPECIAL_LOGS._TYPE_:
            self.subitMainWindow.movieNameLineEdit.setText(real_message)
            return
        else:
            # We are appending dots to the end of the message in order to give
            # a more "working" feeling. We add up to 3 dots to the end
            _dot = '.'
            last_three = self.subitMainWindow.directionLogsLabel.text()[-3:]
            dots_count = last_three.count(_dot)
            if dots_count == 0:
                dots_count = 1
            elif dots_count == 1:
                dots_count = 2
            elif dots_count == 2:
                dots_count = 3
            else:
                dots_count = 1
            
            msg = MessageString(DIRECTION.LOADING_PLEASE_WAIT) +\
                (_dot * dots_count)
            self.subitMainWindow.directionLogsLabel.setText(msg)

        logItem = QtGui.QListWidgetItem(real_message)
        logItem.setBackground(QtGui.QBrush(QtGui.QColor(color)))
        
        #Insert log message, and scroll to latest line
        self.subitMainWindow.logListWidget.addItem(logItem)        
        self.subitMainWindow.logListWidget.setCurrentItem(logItem)            
        self.subitMainWindow.logListWidget.scrollToItem\
            (logItem, QtGui.QAbstractItemView.ScrollHint.EnsureVisible)        
        self.subitMainWindow.logListWidget.clearFocus()
    
    def getSearchInput(self, logMsg = None):
        if logMsg: 
            self.writeLog(logMsg)
            
        self.mutex.unlock()
        self.waitCondition.wakeAll()
        self.mutex.lock()
        self.messages_signals._searchSignal.emit()
        self.waitCondition.wait(self.mutex)
        return self.subitMainWindow.movieNameLineEdit.displayText()
    
    def _onMovieNameGoButtonClicked(self):
        self.subitMainWindow.movieNameBrowseToolButton.setEnabled(False)
        self.subitMainWindow.movieNameGoToolButton.setEnabled(False)
        self.subitMainWindow.movieNameLineEdit.setEnabled(False)
        self.subitMainWindow.movieNameLineEdit.setAcceptDrops(False)
        self.waitCondition.wakeAll()

    def _onMovieNameBrowseButtonClicked(self):
        from Utils import GetMoviesExtensions
        # Take all the extension, without the directory
        extensions = filter\
            (lambda i: i.lower() != 'Directory', GetMoviesExtensions())
        extensions_filter = ' *'.join(extensions)

        new_name = QtGui.QFileDialog.getOpenFileName\
            (None, 'Movie Selection', '', 'Movies (*%s)' % extensions_filter)
        WriteDebug('User file selection is: %s' % new_name)
        self.subitMainWindow.movieNameLineEdit.setText(new_name[0])

    @QtCore.Slot()
    def _getSearchInput(self):
        self.subitMainWindow.moviesListWidget.clear()
        self.subitMainWindow.versionsListWidget.clear()
        self.subitMainWindow.movieNameGoToolButton.setEnabled(False)
        self.subitMainWindow.movieNameBrowseToolButton.setEnabled(True)
        self.subitMainWindow.movieNameLineEdit.setEnabled(True)
        self.subitMainWindow.movieNameLineEdit.setAcceptDrops(True)
        self.subitMainWindow.movieNameLineEdit.setFocus()
        self.subitMainWindow.movieNameLineEdit.selectAll()

    def getDestinationDirectoryInput(self, default_directory, logMsg = None):
        if logMsg: 
            self.writeLog(logMsg)
    
        self.download_directory = default_directory
        self.mutex.unlock()
        self.mutex.lock()
        self.messages_signals._directorySignal.emit(default_directory)
        self.waitCondition.wait(self.mutex)
        return self.download_directory
    
    @QtCore.Slot(object)
    def _getDestinationDirectoryInput(self, default_directory):
        new_value = QtGui.QFileDialog.getExistingDirectory\
            (self.mainWindow, 'Download Destination', default_directory, QtGui.QFileDialog.ShowDirsOnly)
        WriteDebug('User choice directory: %s' % new_value)
        if new_value and os.path.isdir(new_value):
            WriteDebug('The path is valid')
            self.download_directory = new_value
        else:
            WriteDebug('The path is invalid, ignoring the value')
        self.waitCondition.wakeAll()
        
    # ======================================================================== #
    # MovieSubStage And VersionSubStage selections
    # ======================================================================== #
    def _getChoiceType(self):
        """ Because the user is allowed to choose either movie or subversion, 
            we need to know which one was it eventually in order to get the 
            selection.
        """
        if self.choiceType == ChoiceTypes.VERSION:
            WriteDebug('A Version got chosen')
        elif self.choiceType == ChoiceTypes.MOVIE:
            WriteDebug('A Movie got chosen')
            
        return self.choiceType
        
    def _notifyChoice(self, choiceType):
        """ Notify that the user chose a SubStage. We're setting the global 
            choice type to the one that got selected, and releasing the motex.
        """
        self.choiceType = choiceType
        self.subitMainWindow.moviesListWidget.setEnabled(False)
        self.subitMainWindow.versionsListWidget.setEnabled(False)
        self.subitMainWindow.downloadVersionToolButton.setEnabled(False)
        self.waitCondition.wakeAll()

    def _list_widget_item_with_provider_icon\
        (self, provider_png, provider_name, text):
        """ Create a QListWidgetItem with the provider_png as the icon, and the
            provider_name as the tooltip, and text as text
        """
        path_to_png = path_to_png = ':/Providers/' + provider_png
        if not QtCore.QResource(path_to_png).isValid():
            path_to_png = ':/Providers/icon-subprovider-unknown.png'

        icon_of_png = QtGui.QIcon()
        icon_of_png.addPixmap\
            (QtGui.QPixmap(path_to_png), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        list_widget_item = QtGui.QListWidgetItem(icon_of_png, text)
        list_widget_item.setToolTip(provider_name)
        
        return list_widget_item

    def getVersionChoice(self, subVersions, subMovies, logMsg = None):
        """Get the user selection for the given SubVersions."""
        if logMsg: 
            self.writeLog(logMsg)

        self.mutex.unlock()
        self.mutex.lock()
        self.messages_signals._versionSignal.emit(subVersions, subMovies)
        self.waitCondition.wait(self.mutex)
        # If user selected a version
        if self._getChoiceType() == ChoiceTypes.VERSION:
            current_row = self.subitMainWindow.versionsListWidget.currentRow()
            WriteDebug('Version row position is: %s' % current_row)
            return subVersions[current_row]
        # User selected a movie
        else:
            current_row = self.subitMainWindow.moviesListWidget.currentRow()
            WriteDebug('Movie row position is: %s' % current_row)
            return subMovies[current_row]

    @QtCore.Slot(object, object)
    def _getVersionChoice(self, subVersions, subMovies):
        from SubProviders import getSubProviderByName
        from Interaction import ImagesResources
        
        self.subitMainWindow.versionsListWidget.clear()

        for version in subVersions:
            sub_provider = getSubProviderByName(version.provider_name)
            provider_png = sub_provider.PROVIDER_PNG
            version_sum = version.version_sum
            provider_name = version.provider_name

            ver_list_widget_item = self._list_widget_item_with_provider_icon\
                (provider_png, provider_name, version_sum)
            self.subitMainWindow.versionsListWidget.addItem\
                (ver_list_widget_item)

        self.subitMainWindow.versionsListWidget.setEnabled(True)
        self.subitMainWindow.versionsListWidget.scrollToItem\
            (self.subitMainWindow.versionsListWidget.item(0),
             QtGui.QAbstractItemView.ScrollHint.EnsureVisible)

        if subMovies:
            self._getMovieChoice(subMovies)

    def getMovieChoice(self, subMovies, logMsg = None):
        """Get the user selection for the given SubMovies."""
        if logMsg: 
            self.writeLog(logMsg)
        
        self.mutex.unlock()
        self.mutex.lock()
        self.messages_signals._movieSignal.emit(subMovies)
        self.waitCondition.wait(self.mutex)
        # If user selected a movie
        if self._getChoiceType() == ChoiceTypes.MOVIE:
            return subMovies[self.subitMainWindow.moviesListWidget.currentRow()]
        # Can't happen, but just in case (it might happend in getVersionChoice)
        else:
            return subMovies[0]

    @QtCore.Slot(object)
    def _getMovieChoice(self, subMovies):
        from SubProviders import getSubProviderByName
        from Interaction import ImagesResources
        self.subitMainWindow.moviesListWidget.clear()

        for movie in subMovies:
            provider_name = movie.provider_name
            sub_provider = getSubProviderByName(provider_name)
            provider_png = sub_provider.PROVIDER_PNG
            movie_name = movie.movie_name
            versions_sum = movie.versions_sum
            provider_name = movie.provider_name

            formatted_name = movie_name
            # It might be empty
            if versions_sum:
                formatted_name += ' -> ' + versions_sum

            movie_list_widget_item = self._list_widget_item_with_provider_icon\
                (provider_png, provider_name, formatted_name)
            
            self.subitMainWindow.moviesListWidget.addItem\
                (movie_list_widget_item)
            
        self.subitMainWindow.moviesListWidget.setEnabled(True)
    # ======================================================================== #
    # ======================================================================== #

    # ======================================================================== #
    # Movie files dragging
    # ======================================================================== #
    def _onMovieFileDragEnterEvent(self, e):
        """ For UI porpuse, we always accept the dragging (we want to keep the
            coloring).
        """
        def _show_accepted():
            self.subitMainWindow.movieNameLineEdit.setStyleSheet\
                ('QLineEdit{background: LightGreen;}')
        def _show_ignored():
            self.subitMainWindow.movieNameLineEdit.setStyleSheet\
                ('QLineEdit{background: rgba(255, 134, 134, 225);}')

        # Accept only drop of single file with movie extension
        if e.mimeData().hasUrls():
            _dropped_urls = e.mimeData().urls()
            if len(_dropped_urls) == 1:
                WriteDebug("_dropped_urls[0]: %s" % _dropped_urls[0])
                # Remove leading dot from extensions
                _path = _dropped_urls[0].toLocalFile()
                WriteDebug("_path: %s" % _path)
                if Utils.IsWindowPlatform():
                    _path = _path.replace('/', '\\')
                if os.path.splitext(_path)[1].lower() in \
                    Utils.GetMoviesExtensions():
                    e.accept()
                    return _show_accepted()
        _show_ignored()        
        e.accept()

    def _onMovieFileDragLeaveEvent(self, e):
        """ Reset the LineEdit background on exit """
        self.subitMainWindow.movieNameLineEdit.setStyleSheet(None)

    def _onMovieFileDropEvent(self, e):
        """ Because we always accept the drag, we check in the drop that the file
            is OK for us 
        """
        self.subitMainWindow.movieNameLineEdit.setStyleSheet(None)
        file_path = e.mimeData().urls()[0].toLocalFile()
        WriteDebug("_onMovieFileDropEvent(): %s" % file_path)
        if Utils.IsWindowPlatform():
            file_path = file_path.replace('/', '\\')

        if os.path.splitext(file_path)[1].lower() in \
            Utils.GetMoviesExtensions():
            self.subitMainWindow.movieNameLineEdit.setText(file_path)
        else:
            e.ignore()
    # ======================================================================== #
    # ======================================================================== #

    # ======================================================================== #
    # Update procedure 
    # ======================================================================== #
    def notifyNewVersion(self, current_version, new_version, new_version_link):
        self.messages_signals._updateSignal.emit\
            (current_version, new_version, new_version_link)

    @QtCore.Slot(str, str, str)
    def _notifyNewVersion(self, current_version, new_version, new_version_link):
        self.updateDialog = QtGui.QDialog\
            (self.mainWindow, QtCore.Qt.WindowSystemMenuHint)
        self.subitUpdateDialog = SubiTUpdateGui.Ui_UpdateDialog()
        self.subitUpdateDialog.setupUi(self.updateDialog)
        self.updateDialog.open()

        self.subitUpdateDialog.currentVersionLabel.setText(current_version)
        self.subitUpdateDialog.latestVersionLabel.setText(new_version)
        self.subitUpdateDialog.latestVersionLinkLabel.setText\
            ('<a href="%s">%s</a>' % (new_version_link, new_version_link))

    def _set_version_status_in_label\
        (self, status_label, status, text_label, text):        
        """ Set the status and text under the given status label and text_label.
            The status should be taken from the Enum of UPDATE_STATUS in order
            to match with the UPDATE_STATUS_IMAGES dict
        """
        if status not in UPDATE_STATUS_IMAGES.keys():
            status = UPDATE_STATUS.ERROR
        
        status_label.setPixmap(QtGui.QPixmap(UPDATE_STATUS_IMAGES[status]))
        text_label.setText(text)

    def _onCheckForUpdateFired(self, status_label, text_label, should_notify):
        """ Will peform an update check, and log the procedure under the given
            status_label (which holds the icon) and the text_label (which holds
            the text...). If should_notify is True, a Dialog will popup to the
            user, letting him to access the latest version url
        """
        from Settings import Updaters

        def _log(status, text):
            self._set_version_status_in_label\
                (status_label, status, text_label, text)

        _log(UPDATE_STATUS.CHECKING, 'Checking for updates...')
        # Try to get an updater
        updater = Updaters.getUpdater()
        if updater:
            (is_latest, latest_ver, latest_url) = updater.IsLatestVersion(True)
            if not is_latest:
                _log(UPDATE_STATUS.NEW_VERSION, 
                     'New version of SubiT is avaliable (%s)' % latest_ver)
                if should_notify:
                    self.notifyNewVersion\
                        (updater.CurrentVersion(), latest_ver, latest_url)
            else:
                _log(UPDATE_STATUS.LATEST, 
                     'SubiT is up to date (%s)' % updater.CurrentVersion())
        # We assume that the reason we got None for the updater is because we
        # dont have any for the current platform
        else:
            _log(UPDATE_STATUS.ERROR, 
                 'No updater is not avaliable for this platform')

    def _onCheckForUpdateFiredInAbout(self):
        self._onCheckForUpdateFired\
            (self.subitAboutDialog.versionStatusIconLabel, 
             self.subitAboutDialog.versionStatusTextLabel, False)

    def _onCheckForUpdateFiredInSettings(self):
        self._onCheckForUpdateFired\
            (self.subitSettingsDialog.versionStatusIconLabel, 
             self.subitSettingsDialog.versionStatusTextLabel, False)
    # ======================================================================== #
    # ======================================================================== #
    @QtCore.Slot(object)
    def _onLogToggle(self):
        if self.log_action.isChecked():
            self.subitMainWindow.logDockWidget.show()
        else:
            self.subitMainWindow.logDockWidget.hide()

    @QtCore.Slot(object)
    def _onToolsToolButtonClicked(self):
        pos_on_screen = self.subitMainWindow.toolsToolButton.mapToGlobal\
            (QtCore.QPoint(0,self.subitMainWindow.toolsToolButton.height()))
        self.menu.exec_(pos_on_screen)

    def _onDefaultDirectoryBrowseButtonClicked(self):
        current_value   = self.subitSettingsDialog.defaultDirectoryLineEdit.text()
        new_value       = QtGui.QFileDialog.getExistingDirectory\
            (None, 'Default Directory', '', QtGui.QFileDialog.ShowDirsOnly)
        if new_value and os.path.isdir(new_value):
            self.subitSettingsDialog.defaultDirectoryLineEdit.setText(new_value)
        
    def _onOkPushButtonClicked(self):
        """ Will save the config """
        from Settings import DEFAULT_DIRECTORY_DEFAULT_VAL
        from Settings.Config import SubiTConfig
        from Settings.Associators import getAssociator

        #============================================
        # Global Tab
        #============================================
        close_on_finish = self.subitSettingsDialog.closeOnFinishCheckBox\
            .isChecked()
        default_directory = self.subitSettingsDialog.defaultDirectoryLineEdit\
            .text() or DEFAULT_DIRECTORY_DEFAULT_VAL
        always_use_default_directory = self.subitSettingsDialog\
            .alwaysUseDefaultDirCheckBox.isChecked()

        remember_last_window_size = self.subitSettingsDialog\
            .rememberLastWindowSizeCheckBox.isChecked()
        remember_last_window_position = self.subitSettingsDialog\
            .rememberLastWindowPositionCheckBox.isChecked()

        check_updates = self.subitSettingsDialog.checkForUpdatesCheckBox\
            .isChecked()
        auto_update = self.subitSettingsDialog.autoUpdateCheckBox.isChecked()

        #============================================
        # Providers Tab
        #============================================
        # Thats how we can get the the items inside a QListWidget in QT..., we
        # look for items with the wild card, so we get all the items.
        languages_items = self.subitSettingsDialog.advancedLanguageListWidget\
            .findItems('.*', QtCore.Qt.MatchFlag.MatchRegExp)
        # We take only the checked once, and return their text() value
        languages_order = Utils.myfilter\
            (lambda i: i.checkState() == QtCore.Qt.CheckState.Checked, 
             languages_items,
             lambda i: i.text())

        # Again, QT sucks...
        providers_items = self.subitSettingsDialog.advancedProvidersListWidget\
            .findItems('.*', QtCore.Qt.MatchFlag.MatchRegExp)
        # We take only the checked once, and return their text() value
        providers_order = Utils.myfilter\
            (lambda i: i.checkState() == QtCore.Qt.CheckState.Checked, 
             providers_items, 
             lambda i: i.text())

        do_properties_based_ranks = self.subitSettingsDialog\
            .rankUsingPropertiesCheckBox.isChecked()
        do_in_depth_search = \
            self.subitSettingsDialog.inDepthSearchCheckBox.isChecked()

        #============================================
        # Association Tab
        #============================================
        if getAssociator():
            associate_extensions = self.subitSettingsDialog\
                .associateExtensionsCheckBox.isChecked()
            # Again, QT...
            extensions_items = self.subitSettingsDialog.extensionsListWidget\
                .findItems('.*', QtCore.Qt.MatchFlag.MatchRegExp)
            extensions_keys = list(map(lambda i: i.text(), extensions_items))


            from Interaction import InteractionTypes
            from Utils import myfilter
            interaction_desc = self.subitSettingsDialog\
                .interactionTypeSelectionComboBox.currentText()
            # Take the interaction_type of the selected item in the combobox
            interaction_type = myfilter\
                (lambda i: i[1] == interaction_desc, 
                 InteractionTypes.InteractionTypeDescriptions.items(), 
                 lambda i: i[0], 
                 True)

        
        # Now we finally save the settings
        SubiTConfig.Singleton().setValue\
            ('Global', 'close_on_finish', close_on_finish)
        SubiTConfig.Singleton().setValue\
            ('Global', 'default_directory', default_directory)
        SubiTConfig.Singleton().setValue\
            ('Global', 'always_use_default_directory', always_use_default_directory)

        SubiTConfig.Singleton().setValue\
            ('Gui', 'remember_last_window_size', remember_last_window_size)
        SubiTConfig.Singleton().setValue\
            ('Gui', 'remember_last_window_position', remember_last_window_position)

        SubiTConfig.Singleton().setValue\
            ('Updates', 'check_updates', check_updates)
        SubiTConfig.Singleton().setValue\
            ('Updates', 'auto_update', auto_update)

        SubiTConfig.Singleton().setList\
            ('Providers', 'languages_order', languages_order)
        SubiTConfig.Singleton().setList\
            ('Providers', 'providers_order', providers_order)
        SubiTConfig.Singleton().setValue\
            ('Flow', 'do_properties_based_rank', do_properties_based_ranks)
        SubiTConfig.Singleton().setValue\
            ('Flow', 'in_depth_search', do_in_depth_search)

        if getAssociator():
            SubiTConfig.Singleton().setValue\
                ('Association', 'associate_extensions', associate_extensions)
            SubiTConfig.Singleton().setList\
                ('Association', 'extensions_keys', extensions_keys)
            SubiTConfig.Singleton().setValue\
                ('Association', 'interaction_type', interaction_type)

            if associate_extensions:
                getAssociator().SetAssociation()
            else:
                getAssociator().RemoveAssociation()
        
        # Restart subit, with the user input if there was any, otherwise, we
        # restart we the original sys.argv values
        movie_name_query = self.subitMainWindow.movieNameLineEdit.displayText()
        if movie_name_query:
            Utils.restart(movie_name_query)
        else:
            Utils.restart()
        
    def _onExtensionsAddToolButtonClicked(self):
        newExtItem = QtGui.QListWidgetItem('<new extension>')
        newExtItem.setFlags(QtCore.Qt.ItemIsSelectable    | 
                            QtCore.Qt.ItemIsEnabled       | 
                            QtCore.Qt.ItemIsEditable)
        self.subitSettingsDialog.extensionsListWidget.addItem(newExtItem)
        self.subitSettingsDialog.extensionsListWidget.setCurrentItem(newExtItem)
        self.subitSettingsDialog.extensionsListWidget.editItem(newExtItem)

    def _onExtensionsDeleteToolButtonClicked(self):
        self.subitSettingsDialog.extensionsListWidget.takeItem\
            (self.subitSettingsDialog.extensionsListWidget.currentRow())

    def _onDownToolButtonClicked(self, listWidget):
        current_index   = listWidget.currentRow()
        current_item    = listWidget.currentItem()
        if current_index < listWidget.count() - 1:
            # Delete the item from the previous position
            listWidget.takeItem(current_index)
            new_index = current_index + 1
            listWidget.insertItem(new_index, current_item)
            listWidget.setCurrentRow(new_index)

    def _onUpToolButtonClicked(self, listWidget):
        current_index   = listWidget.currentRow()
        current_item    = listWidget.currentItem()
        if current_index > 0:
            # Delete the item from the previous position
            listWidget.takeItem(current_index)
            new_index = current_index - 1
            listWidget.insertItem(new_index, current_item)
            listWidget.setCurrentRow(new_index)
     
    def showSettings(self):
        self.settingsDialog = QtGui.QDialog\
            (self.mainWindow, QtCore.Qt.WindowSystemMenuHint)
        self.subitSettingsDialog = SubiTSettingsGui.Ui_SettingsQDialog()
        self.subitSettingsDialog.setupUi(self.settingsDialog)
        self.finilizeSubiTSettingsGuiWidgets()
        self.settingsDialog.open()

    def showAbout(self):
        self.aboutDialog = QtGui.QDialog\
            (self.mainWindow, QtCore.Qt.WindowSystemMenuHint)
        self.subitAboutDialog = SubiTAboutGui.Ui_AboutBoxDialog()
        self.subitAboutDialog.setupUi(self.aboutDialog)
        self.finilizeSubiTAboutGuiWidgets()
        self.aboutDialog.open()

    @QtCore.Slot(object)
    def _showLanguageSelection(self):
        self.languageDialog =\
        QtGui.QDialog(self.mainWindow, QtCore.Qt.WindowSystemMenuHint)
        self.subitLanguageDialog = SubiTLanguageGui.Ui_Dialog()
        self.subitLanguageDialog.setupUi(self.languageDialog)
        self.finilizeSubiTLanguageSelectionGuiWidgets()
        self.languageDialog.open()

    def showLanguageSelection(self):
        self.messages_signals._languageSignal.emit()

    def _onLanguageSelectionOkClicked(self):
        from Settings.Config import SubiTConfig

        languages_items = self.subitLanguageDialog.languageOrderListWidget\
            .findItems('.*', QtCore.Qt.MatchFlag.MatchRegExp)
        # We take only the checked once, and return their text() value
        languages_order = Utils.myfilter\
            (lambda i: i.checkState() == QtCore.Qt.CheckState.Checked,
             languages_items,
             lambda i: i.text())

        SubiTConfig.Singleton().setList\
            ('Providers', 'languages_order', languages_order)

        Utils.restart()

    # ======================================================================== #                  
    # Windows widget finilizing
    # ======================================================================== #
    def finilizeSubiTLanguageSelectionGuiWidgets(self):
        from SubProviders import getAvaliableLanguages
        from Settings.Config import SubiTConfig

        languages_order = SubiTConfig.Singleton().getList\
            ('Providers', 'languages_order')
        all_languages = getAvaliableLanguages()
        not_selected_languages = filter\
            (lambda l: l not in languages_order, all_languages)

        def _add_languages(languages, check_state):
            for language in languages:
                lang_item = QtGui.QListWidgetItem(language)
                lang_item.setCheckState(check_state)
                self.subitLanguageDialog.languageOrderListWidget.addItem\
                    (lang_item)

        _add_languages(languages_order, QtCore.Qt.CheckState.Checked)
        _add_languages(not_selected_languages, QtCore.Qt.CheckState.Unchecked)

        def _on_item_clicked(item):
            languages_items = \
                self.subitLanguageDialog.languageOrderListWidget.findItems\
                    ('.*', QtCore.Qt.MatchFlag.MatchRegExp)
            languages_checked = Utils.myfilter\
                (lambda i: i.checkState() == QtCore.Qt.CheckState.Checked,
                 languages_items)
            self.subitLanguageDialog.okPushButton.setEnabled\
                (len(languages_checked) > 0)

        self.subitLanguageDialog.languageOrderListWidget.itemClicked.connect\
            (_on_item_clicked)

        # Connect the click event on up and down buttons
        self.subitLanguageDialog.languageDownToolButton.clicked.connect\
            (lambda: (self._onDownToolButtonClicked
                          (self.subitLanguageDialog.languageOrderListWidget)))
        self.subitLanguageDialog.languageUpToolButton.clicked.connect\
            (lambda: (self._onUpToolButtonClicked
                          (self.subitLanguageDialog.languageOrderListWidget)))
        self.subitLanguageDialog.okPushButton.clicked.connect\
            (self._onLanguageSelectionOkClicked)

        from Utils import exit
        self.subitLanguageDialog.cancelPushButton.clicked.connect(exit)


    def finilizeSubiTAboutGuiWidgets(self):
        from Settings.Config import SubiTConfig
        version = SubiTConfig.Singleton().getStr\
            ('Global', 'version', 'Failed getting version')
        self.subitAboutDialog.versionLabel.setText(version)
        self._onCheckForUpdateFiredInAbout()

    def finilizeSubiTSettingsGuiWidgets(self):
        #============================================
        # Global Tab
        #============================================
        from Settings.Config import SubiTConfig
        from Settings.Updaters import getUpdater
        
        version = SubiTConfig.Singleton().getStr\
            ('Global', 'version', 'Failed getting the vesion')
        close_on_finish = SubiTConfig.Singleton().getBoolean\
            ('Global', 'close_on_finish', False)
        default_directory = SubiTConfig.Singleton().getStr\
            ('Global', 'default_directory', Utils.GetProgramDir())
        always_use_default_directory = SubiTConfig.Singleton().getBoolean\
            ('Global', 'always_use_default_directory', False)

        remember_last_window_size = SubiTConfig.Singleton().getBoolean\
            ('Gui', 'remember_last_window_size', True)
        remember_last_window_position = SubiTConfig.Singleton().getBoolean\
            ('Gui', 'remember_last_window_position', False)

        check_updates = SubiTConfig.Singleton().getBoolean\
            ('Updates', 'check_updates', True)
        auto_update = SubiTConfig.Singleton().getBoolean\
            ('Updates', 'auto_update', False)

        self.subitSettingsDialog.closeOnFinishCheckBox\
            .setChecked(close_on_finish)
        self.subitSettingsDialog.defaultDirectoryLineEdit\
            .setText(default_directory)
        self.subitSettingsDialog.alwaysUseDefaultDirCheckBox\
            .setChecked(always_use_default_directory)

        self.subitSettingsDialog.rememberLastWindowSizeCheckBox.setChecked\
            (remember_last_window_size)
        self.subitSettingsDialog.rememberLastWindowPositionCheckBox.setChecked\
            (remember_last_window_position)

        self.subitSettingsDialog.checkForUpdatesCheckBox\
            .setChecked(check_updates)
        self.subitSettingsDialog.autoUpdateCheckBox\
            .setEnabled(check_updates)
        self.subitSettingsDialog.autoUpdateCheckBox\
            .setChecked(auto_update)

        self.subitSettingsDialog.okPushButton.clicked.connect\
            (self._onOkPushButtonClicked)
        self.subitSettingsDialog.defaultDirectoryBrowseButton.clicked.connect\
            (self._onDefaultDirectoryBrowseButtonClicked)
        self.subitSettingsDialog.checkForUpdatesButton.clicked.connect\
            (self._onCheckForUpdateFiredInSettings)

        #============================================
        # Providers Tab
        #============================================
        from SubProviders import getAvaliableLanguages
        from SubProviders import getAvaliableSubProviders
        from SubProviders import getSubProviderByName
        from SubProviders import buildSubProviderName
        from SubProviders import getSubProviderPngByName

        languages_order = SubiTConfig.Singleton().getList\
            ('Providers', 'languages_order')
        all_languages = getAvaliableLanguages()
        not_selected_languages = filter\
            (lambda l: l not in languages_order, all_languages)

        def _add_languages(languages, check_state):
            for language in languages:
                lang_item = QtGui.QListWidgetItem(language)
                lang_item.setCheckState(check_state)
                self.subitSettingsDialog.advancedLanguageListWidget\
                    .addItem(lang_item)

        _add_languages(languages_order, QtCore.Qt.CheckState.Checked)
        _add_languages(not_selected_languages, QtCore.Qt.CheckState.Unchecked)

        # Connect the click event on up and down buttons
        self.subitSettingsDialog.languageDownToolButton.clicked.connect\
            (lambda: (self._onDownToolButtonClicked
                      (self.subitSettingsDialog.advancedLanguageListWidget)))
        self.subitSettingsDialog.languageUpToolButton.clicked.connect\
            (lambda: (self._onUpToolButtonClicked
                      (self.subitSettingsDialog.advancedLanguageListWidget)))
        

        providers_order = SubiTConfig.Singleton().getList\
            ('Providers', 'providers_order')
        all_providers = getAvaliableSubProviders()
        not_selected_providers = filter\
            (lambda p: p not in providers_order, all_providers)

        def _add_providers(providers, check_stage):
            for provider_name in providers:
                provider_png = getSubProviderPngByName(provider_name)
                provider_item = self._list_widget_item_with_provider_icon\
                    (provider_png, provider_name, provider_name)
                provider_item.setCheckState(check_stage)
                self.subitSettingsDialog.advancedProvidersListWidget\
                    .addItem(provider_item)

        _add_providers(providers_order, QtCore.Qt.CheckState.Checked)
        _add_providers(not_selected_providers, QtCore.Qt.CheckState.Unchecked)

        # Connect the click event on up and down buttons
        self.subitSettingsDialog.providerUpTooButton.clicked.connect\
            (lambda: (self._onUpToolButtonClicked
                      (self.subitSettingsDialog.advancedProvidersListWidget)))
        self.subitSettingsDialog.providerDownToolButton.clicked.connect\
            (lambda: (self._onDownToolButtonClicked
                      (self.subitSettingsDialog.advancedProvidersListWidget)))


        def _select_all_providers(select):
            # If the checkbox is checked, we want to disable the widget because
            # we are going to select all the providers.
            self.subitSettingsDialog.advancedProvidersListWidget.setEnabled(not select)
            self.subitSettingsDialog.providerUpTooButton.setEnabled(not select)
            self.subitSettingsDialog.providerDownToolButton.setEnabled(not select)

            if select:
                providers_items = self.subitSettingsDialog.\
                    advancedProvidersListWidget.findItems\
                    ('.*', QtCore.Qt.MatchFlag.MatchRegExp)
                for item in providers_items:
                    # Check
                    item.setCheckState(QtCore.Qt.CheckState.Checked)


        self.subitSettingsDialog.useAllProvidersCheckBox.toggled.connect(_select_all_providers)

        do_properties_based_ranks = SubiTConfig.Singleton().getBoolean\
            ('Flow', 'do_properties_based_rank', True)
        self.subitSettingsDialog.rankUsingPropertiesCheckBox.setChecked\
            (do_properties_based_ranks)
        do_in_depth_search = SubiTConfig.Singleton().getBoolean\
            ('Flow', 'in_depth_search', False)
        self.subitSettingsDialog.inDepthSearchCheckBox.setChecked\
            (do_in_depth_search)

        #============================================
        # Association Tab
        #============================================
        from Settings.Associators import getAssociator
        if getAssociator():
            associate_extensions = SubiTConfig.Singleton().getBoolean\
                ('Association', 'associate_extensions', True)
            extensions_keys = SubiTConfig.Singleton().getList\
                ('Association', 'extensions_keys')

            self.subitSettingsDialog.associateExtensionsCheckBox.setChecked\
                (associate_extensions)
            self.subitSettingsDialog.extensionsListWidget.addItems\
                (extensions_keys)

            self.subitSettingsDialog.extensionsDeleteToolButton.clicked.connect\
                (self._onExtensionsDeleteToolButtonClicked)
            self.subitSettingsDialog.extensionsAddToolButton.clicked.connect\
                (self._onExtensionsAddToolButtonClicked)

            from Interaction import getDefaultInteractorByConfig
            from Interaction import InteractionTypes
            
            interaction_type = getDefaultInteractorByConfig()
            self.subitSettingsDialog.interactionTypeSelectionComboBox.addItem\
                (InteractionTypes.InteractionTypeDescriptions[interaction_type])

            for type in InteractionTypes.InteractionTypeDescriptions.iteritems():
                if type[0] != interaction_type:
                    self.subitSettingsDialog\
                        .interactionTypeSelectionComboBox.addItem(type[1])

        else:
            # We disable the whole tab
            self.subitSettingsDialog.fileExtensionsGroupBpx.setEnabled(False)

        self._onCheckForUpdateFiredInSettings()

    def finilizeSubiTMainGuiWidgets(self, mainWindow, subitMainGui):        
        # Input scope
        self.subitMainWindow.movieNameLineEdit.dragEnterEvent = \
            self._onMovieFileDragEnterEvent
        self.subitMainWindow.movieNameLineEdit.dragLeaveEvent = \
            self._onMovieFileDragLeaveEvent
        self.subitMainWindow.movieNameLineEdit.dropEvent = \
            self._onMovieFileDropEvent
        self.subitMainWindow.movieNameGoToolButton.clicked.connect\
            (self._onMovieNameGoButtonClicked)
        self.subitMainWindow.movieNameBrowseToolButton.clicked.connect\
            (self._onMovieNameBrowseButtonClicked)
        self.subitMainWindow.movieNameLineEdit.textChanged.connect\
            (lambda text: (self.subitMainWindow.movieNameGoToolButton
                           .setEnabled(bool(text))))

        # Enter shortcut for movie name entering
        enter_shortcut = \
            QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter),
                            self.subitMainWindow.movieNameLineEdit)
        return_shortcut = \
            QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return),
                            self.subitMainWindow.movieNameLineEdit)

        enter_shortcut.activated.connect\
            (self.subitMainWindow.movieNameGoToolButton.click)
        return_shortcut.activated.connect\
            (self.subitMainWindow.movieNameGoToolButton.click)


        # Item selection scope
        self.subitMainWindow.moviesListWidget.itemDoubleClicked.connect\
            (lambda e: self._notifyChoice(ChoiceTypes.MOVIE))
        self.subitMainWindow.moviesListWidget.itemClicked.connect\
            (lambda checked: (self.subitMainWindow.downloadVersionToolButton
                              .setEnabled(False)))
        self.subitMainWindow.versionsListWidget.itemDoubleClicked.connect\
            (lambda e: self._notifyChoice(ChoiceTypes.VERSION))
        self.subitMainWindow.versionsListWidget.itemClicked.connect\
            (lambda checked: (self.subitMainWindow.downloadVersionToolButton
                              .setEnabled(True)))
        self.subitMainWindow.downloadVersionToolButton.clicked.connect\
            (lambda: self._notifyChoice(ChoiceTypes.VERSION))

        

        # Tools menu
        self.menu = QtGui.QMenu(self.subitMainWindow.toolsToolButton)

        self.log_action = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap\
            (":/MainWindow/icon-main-log.png")), 'Show Log', self.menu)
        self.log_action.setCheckable(True)
        self.log_action.setIconVisibleInMenu(True)
        self.log_action.triggered.connect(self._onLogToggle)
        self.menu.addAction(self.log_action)

        self.menu.addSeparator()

        self.settings_action = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap\
            (":/MainWindow/icon-main-config.png")), 'Settings', self.menu)
        self.settings_action.setIconVisibleInMenu(True)
        self.settings_action.triggered.connect(self.showSettings)
        self.menu.addAction(self.settings_action)
        
        self.about_action = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap\
            (":/MainWindow/icon-main-about.png")), 'About', self.menu)
        self.about_action.setIconVisibleInMenu(True)
        self.about_action.triggered.connect(self.showAbout)
        self.menu.addAction(self.about_action)

        self.subitMainWindow.toolsToolButton.clicked.connect\
            (self._onToolsToolButtonClicked)

        from Settings.Config import SubiTConfig

        # We first re-show the log, and then, if needed, making it hidden. We do
        # it that way in order to correctly set the check state of the log
        # button.
        self.log_action.trigger()
        if not SubiTConfig.Singleton().getBoolean('Gui', 'show_log', False):
            self.log_action.trigger()

        if SubiTConfig.Singleton().getBoolean\
            ('Gui', 'remember_last_window_size', True):
            current_window_size = SubiTConfig.Singleton().getList\
                ('Gui', 'last_window_size', [580, 250])
            current_window_size =\
                map(lambda i: int(i), current_window_size)
            self.mainWindow.resize(*current_window_size)
        else:
            self.mainWindow.resize(580, 250)

        if SubiTConfig.Singleton().getBoolean\
            ('Gui', 'remember_last_window_position', False):
            current_window_position = SubiTConfig.Singleton().getList\
                ('Gui', 'last_window_position', [0, 0])
            current_window_position = \
                map(lambda i: int(i), current_window_position)
            self.mainWindow.move(*current_window_position)
        else:
            cursor_pos = QtGui.QCursor().pos()
            # We figure out the correct screen by the point of the mouse
            cursor_screen_center = \
                self.app.desktop().screenGeometry(cursor_pos).center()
            # Put the center of the program at the center of the screen
            self.mainWindow.move\
                (cursor_screen_center - self.mainWindow.rect().center())


    # ======================================================================== #
    # ======================================================================== #
