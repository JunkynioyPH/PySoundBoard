from tkinter import *
from tkinter import ttk
root = Tk()
root.title("SoundBoard by Junkynioy#2408")
mframe = ttk.Frame(root, relief=SUNKEN, borderwidth=20)
mframe.grid(column=0, row=0, sticky=(N, W, E, S))
btn = ttk.Button
lb = ttk.Label

def Close():
    root.destroy()
    
lb(mframe, text="Note that this program assumes you have \nVoiceMeeter & VB-Audio Virtual Cable\nalready setup.\nUnless you know what you are doing\nif you don't have them setup.").grid(column=2, row=1,sticky=(N,E,W))
btn(mframe,text="Continue",command=Close).grid(column=2,row=2,sticky=(N,S,E,W))

root.mainloop()
