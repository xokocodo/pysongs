from Tkinter import *
import Tkinter
import tkMessageBox

import random

import database

from utils import *

db = database.SongList(CSV_FILE)
db.load()


top = Tk()

frame_ = Frame(top)
frame_.pack( side = BOTTOM )

frame0 = Frame(top)
frame0.pack( side = BOTTOM )

frame1 = Frame(top)
frame1.pack( side = BOTTOM )

frame2 = Frame(top)
frame2.pack( side = BOTTOM )

frame3 = Frame(top)
frame3.pack( side = BOTTOM )

frame4 = Frame(top)
frame4.pack( side = BOTTOM )

label = Label(frame4, text="Song Title:")
label.pack( side = LEFT)

title_ = Entry(frame4, bd =5)
title_.pack(side = LEFT)

label = Label(frame3, text="Song Artist:")
label.pack( side = LEFT)

artist_ = Entry(frame3, bd =5)
artist_.pack(side = LEFT)

label = Label(frame2, text="Youtube URL:")
label.pack( side = LEFT)

url_ = Entry(frame2, bd =5)
url_.pack(side = LEFT)


label = Label(frame1, text="Download Type:")
label.pack( side = LEFT)


result = StringVar()
result_label = Message( frame_, textvariable=result, relief=FLAT, width=300)
result_label.pack( side = BOTTOM)


result.set("Ready")


def savebutton():

   title = title_.get()

   artist = artist_.get()

   url = url_.get()
   url = url[-11:]

   source = "GUI"
   
   if url != "":
      status = "Ready for Download"
   elif title != "" and artist != "":
      status = "Added"
   else:
      status = "Unknown"

   if status != "Unknown":
   
        song = database.SongRow(title=title,
                            artist=artist,
                            source=source,
                            status=status,
                            url=url)


        log("GUI Entry: %s"%song.info())


        log("Adding to the DB")
        result.set("Adding to the DB")
        db.add(song)


   else:
      result.set("Needs Artist and Title, or URL")
   
B = Tkinter.Button(frame0, text ="Save to Database", command = savebutton)
B.pack(side = BOTTOM)



top.mainloop()

