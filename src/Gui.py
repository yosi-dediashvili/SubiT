from Tkinter import *
import time
import threading
import tkFont
import tkMessageBox
import tkFileDialog
import os

import TorecResult
import Utils
import SubiT
from AboutBox import AboutBox



ICON_LOCATION = os.path.join(os.path.split(os.path.abspath(__file__))[0]
                                                  .replace('\\library.zip', '')
                                                  , 'icon.ico')
class BOXES_SIZES:
    WIDTH = 50
    LOG_HEIGHT = 7
    CHOICE_HEIGHT = 8
    FRAME_PAD = 2

class gui:
    def __init__(self):
        self.root = Tk()
        self.root.title('SubiT - %s' % SubiT.VERSION)
        
        if os.name == 'nt':
            self.root.iconbitmap(default=ICON_LOCATION)
        self.root.geometry("700x350")
        self.root.resizable(width=FALSE, height=FALSE)
        
        self.cfont = tkFont.Font(family='Arial', size=8)        
        #=======================================================================
        # Right frame - subtitle files choice
        #=======================================================================
        self.framer = Frame(self.root, borderwidth=2, relief=GROOVE)
        self.framer.pack(side=RIGHT, fill=BOTH, expand=1, padx=BOXES_SIZES.FRAME_PAD, pady=BOXES_SIZES.FRAME_PAD)
        #label
        self.labelr = Label(self.framer, text='Versions:', anchor=W)
        self.labelr.pack(fill=X)
        #inside frame for listbox&scrollbar
        self.framercb = Frame(self.framer)
        self.framercb.pack(fill=BOTH)
        #scrollbar&listbox
        self.choicescrollrcb = Scrollbar(self.framercb)
        self.choicescrollrcb.pack(side=RIGHT, fill=Y)
        self.choicelistboxrcb = Listbox(self.framercb, state=DISABLED, width=40, height=340, 
                                        yscrollcommand = self.choicescrollrcb.set)
        self.choicelistboxrcb.config(font = self.cfont, selectbackground='Dark Gray', activestyle='none')
        self.choicelistboxrcb.pack(fill=BOTH, anchor=NE)
        self.choicescrollrcb.config(command = self.choicelistboxrcb.yview)
        #=======================================================================
        
        
        #=======================================================================
        # Left frame - log + movie choice + textbox
        #=======================================================================
        #upper left frame
        self.framelu = Frame(self.root, borderwidth=2, relief=GROOVE )
        self.framelu.pack(side=TOP, fill=X, expand=1, padx=BOXES_SIZES.FRAME_PAD, pady=BOXES_SIZES.FRAME_PAD)
        #log label
        self.loglabel = Label(self.framelu, text='Log:', anchor=W)
        self.loglabel.pack(fill=X)
        #scrollbar&text frame
        self.framelu0 = Frame(self.framelu)
        self.framelu0.pack(fill=BOTH)
        #scrollbar
        self.logscroll = Scrollbar(self.framelu0)
        self.logscroll.pack(side=RIGHT, fill=Y)
        #log text
        self.logtext = Text(self.framelu0, height=BOXES_SIZES.LOG_HEIGHT, 
                            state=DISABLED, yscrollcommand = self.logscroll.set)
        self.logtext.config(font = self.cfont)
        self.logtext.pack(fill=BOTH, anchor=W)
        self.logscroll.config(command = self.logtext.yview)
        
        #bottom left frame
        self.framelb = Frame(self.root, borderwidth=2, relief=GROOVE )
        self.framelb.pack( fill=X, side=BOTTOM, expand=1, padx=BOXES_SIZES.FRAME_PAD, pady=BOXES_SIZES.FRAME_PAD)
        #options label
        self.optionslabel = Label(self.framelb, text='Movies:', anchor=W)
        self.optionslabel.pack(fill=X)
        #Buttons================
        #about
        self.cancelbutton = Button(self.framelb, text='About', command=self.showabout)
        self.cancelbutton.pack(fill=X,side=BOTTOM)
        #ok
        self.gobutton = Button(self.framelb, text='Go!', state=DISABLED, command=lambda: self.disablebutton())
        self.gobutton.pack(fill=BOTH, side=BOTTOM)
        #textbox
        self.frametbandbtn = Frame(self.framelb)
        self.frametbandbtn.pack(fill=X, side=BOTTOM)
        self.texttextbox = Entry(self.frametbandbtn, state=DISABLED, width=65)
        self.texttextbox.config(font = self.cfont)
        self.texttextbox.pack(fill=X, side=LEFT)
        self.browsebutton = Button(self.frametbandbtn, text='...', width=3, command=self.dobrowse)
        self.browsebutton.config(state=DISABLED)
        self.browsebutton.pack(side=RIGHT)
        #inputlabel
        self.inputlabel = Label(self.framelb, text='Input:', anchor=W)
        self.inputlabel.pack(fill=X, side=BOTTOM)        
        #choice frame
        self.framelb0 = Frame(self.framelb)
        self.framelb0.pack(fill=BOTH)

        #scrollbar
        self.choicescroll = Scrollbar(self.framelb0)
        self.choicescroll.pack(side=RIGHT, fill=Y)
        #listbox
        self.choicelistbox = Listbox(self.framelb0, state=DISABLED, width=BOXES_SIZES.WIDTH, 
                                     height=BOXES_SIZES.CHOICE_HEIGHT, yscrollcommand = self.choicescroll.set)
        self.choicelistbox.config(font = self.cfont, selectbackground='Dark Gray', activestyle='none')
        self.choicelistbox.pack(fill=BOTH, anchor=NE)
        
        self.choicescroll.config(command = self.choicelistbox.yview)

    def dobrowse(self):
        chosendir = tkFileDialog.askdirectory(initialdir=self.texttextbox.get() if os.path.isdir(self.texttextbox.get()) else '')
        self.texttextbox.delete(0, END)
        self.texttextbox.insert(0, chosendir)
        
    def load(self, functorun, ms):
        self.doneinit = True
        self.root.after(ms, functorun)
        self.root.mainloop()

    def writelog(self, message):
        self.logtext.config( state=NORMAL )
        #coding is different from torec and from computer, we try to change it.
        #if we fail, we'll use the original(the listboxes will always insert items
        #from torec, so there's no need to try another coding)
        try:
            self.logtext.insert( END, unicode(str(message + '\n'), 'cp1255'))
        except:
            self.logtext.insert( END, message + '\n')

        self.logtext.see(END)
        self.logtext.config( state=DISABLED )
    
    #===========================================================
    # Sub selection Handling
    #===========================================================
    def setversionchoices(self, choices, message):       
        self.subselected = False
        self.versionchoices = choices
        
        Utils.writelog( message )
        self.choicelistboxrcb.config( state=NORMAL )
        self.choicelistbox.config( state=NORMAL )
        self.choicelistboxrcb.delete(0, END)
        for choice in choices:
            self.choicelistboxrcb.insert( END, choice.VerSum)
                
    def getsubselection(self):
        self.choicelistbox.config( state=NORMAL )
        self.choicelistboxrcb.config( state=NORMAL )

        self.choicelistboxrcb.focus()
        self.choicelistboxrcb.bind('<Double-Button-1>', lambda x: self.notifyselection('SUB'))
        self.choicelistboxrcb.bind('<Return>', lambda x: self.notifyselection('SUB'))
        self.choicelistbox.bind('<Double-Button-1>', lambda x: self.notifyselection('MOVIE'))
         
    #===========================================================================
    # Movie selection handling
    #===========================================================================
    def setmoviechoices(self, choices, message):
        self.movieselected = False
        self.moviechoices = choices
        
        Utils.writelog( message )
        self.choicelistboxrcb.config( state=NORMAL )
        self.choicelistbox.config( state=NORMAL )
        self.choicelistbox.delete(0, END)
        for choice in choices:
            self.choicelistbox.insert( END, choice.MovieName + ' -> ' + choice.VerSum)
        
    def getmovieselection(self):
        self.choicelistboxrcb.config( state=NORMAL )
        self.choicelistbox.config( state=NORMAL )
        self.choicelistbox.focus()
        self.choicelistbox.bind('<Double-Button-1>', lambda x: self.notifyselection('MOVIE'))
        self.choicelistbox.bind('<Return>', lambda x: self.notifyselection('MOVIE'))
        self.choicelistboxrcb.bind('<Double-Button-1>', lambda x: self.notifyselection('SUB'))

    #===========================================================================
    # Selection logic
    #===========================================================================
    def notifyselection(self, source):
        if source == 'SUB':
            self.subselected = bool(self.choicelistboxrcb.curselection())
        elif source == 'MOVIE':
            self.movieselected = bool(self.choicelistbox.curselection())
    
    def getselection(self, type):
        selection = ('','')
        if type == 'SUB':
            self.subselected = False
            self.getsubselection()
            #Wait for selection
            while not self.subselected: time.sleep(0.05)
            selection = ('SUB', self.versionchoices[int(self.choicelistboxrcb.curselection()[0])])
            self.choicelistbox.delete(0, END)
            self.choicelistboxrcb.delete(0, END)
                
        elif type == 'MOVIE':
            self.movieselected = False
            self.getmovieselection()
            #Wait for selection
            while not self.movieselected: time.sleep(0.05)
            selection = ('MOVIE', self.moviechoices[int(self.choicelistbox.curselection()[0])])
                
        elif type == 'ANY':
            self.subselected = False
            self.movieselected = False
            self.getsubselection()
            self.getmovieselection()
            #Wait for selection
            while (not self.subselected) and (not self.movieselected): time.sleep(0.05)
            if self.subselected:
                selection = ('SUB', self.versionchoices[int(self.choicelistboxrcb.curselection()[0])])
                self.choicelistbox.delete(0, END)
                self.choicelistboxrcb.delete(0, END)
            elif self.movieselected:
                selection = ('MOVIE', self.moviechoices[int(self.choicelistbox.curselection()[0])])
        
        if self.choicelistboxrcb.cget('state') == NORMAL:
            self.choicelistboxrcb.config( state=DISABLED )
        if self.choicelistbox.cget('state') == NORMAL:    
            self.choicelistbox.config( state=DISABLED )        
        return selection
            
    #===========================================================================        
    
    def getuserinput(self, message, canempty, withdialog=False):
        Utils.writelog( message )
        self.texttextbox.config(state=NORMAL)
        self.texttextbox.focus()
        
        if withdialog:
            self.browsebutton.config(state=NORMAL)
        else:
            self.browsebutton.config(state=DISABLED)
            
        
        if not canempty:
            while self.texttextbox.get() == '':
                time.sleep(0.05)
        
        self.enablebutton()

        while not self.gobutton['state'] == DISABLED:
            time.sleep(0.05)
        
        movie_name = self.texttextbox.get()
        self.texttextbox.delete(0, len(self.texttextbox.get()) + 1)
        self.texttextbox.config(state=DISABLED)
        self.browsebutton.config(state=DISABLED)
        return movie_name
        
        
    def enablebutton(self, event = None):
        self.gobutton.config( state=NORMAL )
        self.root.bind('<Return>', self.disablebutton)
        
    def disablebutton(self, event = None):
        self.gobutton.config( state=DISABLED )
        self.root.bind('<Return>', None)
        
    def showabout(self):
        AboutBox().show()