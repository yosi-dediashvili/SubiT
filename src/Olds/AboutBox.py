from Tkinter import *
import SubHandlers
import SubiT
import tkFont
import os

from PIL import Image, ImageTk
from ttk import Notebook, Combobox, Button

IMAGE_LOCATION = ICON_LOCATION = os.path.join(os.path.split(os.path.abspath(__file__))[0]
                                                  .replace('\\library.zip', '')
                                                  , 'icon.png')


class AboutBox:
    IMAGE = None
    IMAGETK = None
            
    def __init__(self):        
        self.root = Tk()
        self.root.title('Settings - SubiT')
        self.cfont = ('Lucida Grande', 8)
        self.root.geometry("360x200")
        self.root.resizable(width=FALSE, height=FALSE)
        
        self.mainbook = Notebook(self.root)
        #=======================================================================
        # Settings page in Tabs
        #=======================================================================
        self.settngsTab = Frame(self.root)
        self.settngsTab.pack()
        self.langlabel = Label(self.settngsTab, text='Select the desired handler:', anchor=W)
        self.langlabel.pack(fill=X, padx=3, pady=3)
        self.langcombobox = Combobox(self.settngsTab)
        handlers_names = map(lambda x: x.HANDLER_NAME, SubHandlers.getHandlers())
        self.langcombobox.config(values=handlers_names)
        self.langcombobox.set(SubHandlers.getSelectedHandler().HANDLER_NAME)
        self.langcombobox.pack(fill=X, padx=3, pady=3)
        self.langcombobox.bind('<<ComboboxSelected>>', self.enableSaveButton)
        
        self.savesettbtn = Button(self.settngsTab, text='Save', command=self.saveSettings, state='disabled')
        self.savesettbtn.pack()
        self.mainbook.add(self.settngsTab, text='Settings')
        
        #=======================================================================
        # About Page in Tabs
        #=======================================================================
        self.aboutTab = Frame(self.root)
        AboutBox.IMAGE = Image.open(IMAGE_LOCATION)
        AboutBox.IMAGETK = ImageTk.PhotoImage(AboutBox.IMAGE, master=self.aboutTab, size='5x5')
        self.logolabel = Label(self.aboutTab, image=AboutBox.IMAGETK, width=50, height=50, pady=50)
        self.logolabel.photo = AboutBox.IMAGETK
        self.logolabel.pack()
        
        self.bodylabel = Label(self.aboutTab, font = self.cfont, text=
'''SubiT is an automated system for subtitle downloading.
                              
SubiT was created in order to ease the process of downloading 
hebrew subtitles - with just one click you can download subtitles 
for a whole collection of your favorite movies and TV shows.

Version: {0}
'''.format(SubiT.VERSION) )
        self.bodylabel.pack()

        text='http://www.subit-app.sf.net'
        self.visitlabel = Label(self.aboutTab, text=text, foreground="#0000ff", font=('Consolas', 8), height=1)
        self.visitlabel.bind("<1>", lambda event, text=text: self.on_click_link(event, text))
        visitlabelfont = tkFont.Font(self.visitlabel, self.visitlabel.cget('font'))
        visitlabelfont.configure(underline = True)
        self.visitlabel.configure(font = visitlabelfont)
        self.visitlabel.pack()
        self.aboutTab.pack()
        self.mainbook.add(self.aboutTab, text='About')
                
        self.mainbook.pack()


    def saveSettings(self, ):
        if self.langcombobox.select_present():
            print self.langcombobox.selection_get()
            SubHandlers.setSelectedHandler(self.langcombobox.selection_get())
            self.disableSaveButton()
            
    def enableSaveButton(self, opt=None):
        self.savesettbtn.config(state='normal')
        
    def disableSaveButton(self, opt=None):
        self.savesettbtn.config(state='disabled')
    def show(self):
        self.root.mainloop()
        
    def on_click_link(self, event, text):
        os.startfile(text)