from Tkinter import *
import SubiT
import tkFont
import os

from PIL import Image, ImageTk

IMAGE_LOCATION = ICON_LOCATION = os.path.join(os.path.split(os.path.abspath(__file__))[0]
                                                  .replace('\\library.zip', '')
                                                  , 'icon.png')

class AboutBox:
    IMAGE = None
    IMAGETK = None
    
    def __init__(self):
        self.root = Tk()
        AboutBox.IMAGE = Image.open(IMAGE_LOCATION)
        AboutBox.IMAGETK = ImageTk.PhotoImage(AboutBox.IMAGE, master=self.root, size='5x5')
        self.root.title('About - SubiT')
        self.cfont = ('Lucida Grande', 8)
        self.root.geometry("360x200")
        self.root.resizable(width=FALSE, height=FALSE)
        
        self.logolabel = Label(self.root, image=AboutBox.IMAGETK, width=50, height=50, pady=50)
        self.logolabel.photo = AboutBox.IMAGETK
        self.logolabel.pack()
        
        self.bodylabel = Label(self.root, font = self.cfont, text=
'''SubiT is an automated system for subtitle downloading.
                              
SubiT was created in order to ease the process of downloading 
hebrew subtitles - with just one click you can download subtitles 
for a whole collection of your favorite movies and TV shows.

Version: {0}
'''.format(SubiT.VERSION) )
        self.bodylabel.pack()

        text='http://www.subit-app.sf.net'
        self.visitlabel = Label(self.root, text=text, foreground="#0000ff", font=('Consolas', 8), height=1)
        self.visitlabel.bind("<1>", lambda event, text=text: self.on_click_link(event, text))
        visitlabelfont = tkFont.Font(self.visitlabel, self.visitlabel.cget('font'))
        visitlabelfont.configure(underline = True)
        self.visitlabel.configure(font = visitlabelfont)
        self.visitlabel.pack()
        

    def show(self):
        self.root.mainloop()
        
    def on_click_link(self, event, text):
        os.startfile(text)