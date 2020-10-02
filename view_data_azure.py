#!usr/bin/env
# -*- coding: utf-8 -*-

from tkinter import Tk,Frame,Button,Label,N,W,NO,CENTER,GROOVE,Entry,CENTER,NW,SE
import threading
from threading import Thread
import time,multiprocessing
import os,sys
from datastorage import save_cola_azure_db
from crypt_password import encode_password

class interfaz_azure():
    def __init__(self):
        self.__root=Tk()
        self.__root.resizable(width=0, height=0)
        self.__principalFrame=Frame()
        self.__principalFrame.pack(fill="both",expand="True")
        self.__principalFrame.config(bg='gray80', height=32, width=32)

        self._lbl_namespace=Label(self.__principalFrame,font=("Franklin Gothic Medium Cond",11),text="NAMESPACE",bg="gray80", width = 40,height=1,anchor=NW)
        self._entry_namespace=Entry(self.__principalFrame, width = 40)

        self._lbl_sharedname=Label(self.__principalFrame,font=("Franklin Gothic Medium Cond",11),text="SHAREDNAME",bg="gray80", width = 40,height=1,anchor=NW)
        self._entry_sharedname=Entry(self.__principalFrame, width = 40)

        self._lbl_sharedkey=Label(self.__principalFrame,font=("Franklin Gothic Medium Cond",11),text="SHAREDKEY",bg="gray80", width = 40,height=1,anchor=NW)
        self._entry_sharedkey=Entry(self.__principalFrame, width = 40,show="*")
        self.view=False

        self._lbl_qname=Label(self.__principalFrame,font=("Franklin Gothic Medium Cond",11),text="QNAME",bg="gray80", width = 40,height=1,anchor=NW)
        self._entry_qname=Entry(self.__principalFrame, width = 40)

        self.btn_view_key = Button(self.__principalFrame,font=("Franklin Gothic Medium Cond",7),text="Ver",bg="whitesmoke", height = 1, width = 2, command=self.view_key) # you can add you image to it using photoimage
        self.btn_update_data = Button(self.__principalFrame,font=("Franklin Gothic Medium Cond",9),text="Actualizar",bg="whitesmoke", height = 2, width = 7, command=self.save_data) # you can add you image to it using photoimage

        self._lbl_error=Label(self.__principalFrame,font=("Franklin Gothic Medium Cond",12),text="SE REQUIEREN TODOS LOS DATOS",bg="gray80", width = 40,height=1,anchor=CENTER)

 

    def initializeFrame(self,size='500x500'):
    
        self.__root.title("DATOS AZURE")
        self.__root.geometry(size)
        self.place_entry()
        #self.label_legend_data.config(text=text)

    def view_key(self):
        if(self.view==False):
            self._entry_sharedkey.config(show="")
            self.view=True
        elif(self.view==True):
            self._entry_sharedkey.config(show="*")
            self.view=False


    def save_data(self):


        NAMESPACE = self._entry_namespace.get()
        SHAREDNAME = self._entry_sharedname.get()
        SHAREDKEY = encode_password(self._entry_sharedkey.get())
        #SHAREDKEY = 'K66rwj4ufLqxRSbF2PaKTZCGkfqgFdrEVmN4HrIQzMk'
        QNAME = self._entry_qname.get()

        if(NAMESPACE=="" or SHAREDNAME=="" or SHAREDKEY=="" or QNAME==""):
            self._lbl_error.config(text="SE REQUIEREN TODOS LOS DATOS")
            self._lbl_error.place(x=40,y=380)
        elif(NAMESPACE.isspace() or SHAREDNAME.isspace() or SHAREDKEY.isspace() or QNAME.isspace()):
            self._lbl_error.config(text="SE REQUIEREN TODOS LOS DATOS")
            self._lbl_error.place(x=40,y=380)
        else:
            save= save_cola_azure_db(NAMESPACE,SHAREDNAME,SHAREDKEY,QNAME)
            if(save==True):
                self._lbl_error.config(text="DATOS GUARDADOS")
                self._lbl_error.place(x=40,y=380)
            elif(save==False):
                self._lbl_error.config(text="DATOS NO GUARDADOS")
                self._lbl_error.place(x=40,y=380)

        

        

    def place_entry(self):
        self._lbl_namespace.place(x=50,y=70)
        self._entry_namespace.place(x=50,y=100)

        self._lbl_sharedname.place(x=50,y=150)
        self._entry_sharedname.place(x=50,y=180)

        self._lbl_sharedkey.place(x=50,y=220)
        self._entry_sharedkey.place(x=50,y=250)
        self.btn_view_key.place(x=380,y=250)

        self._lbl_qname.place(x=50,y=290)
        self._entry_qname.place(x=50,y=320)

        self.btn_update_data.place(x=390,y=425)


    def resideFrame(self,size='500x500'):
        self.__root.geometry(size)
   
    def runRoot(self):
        self.__root.mainloop()

if  __name__ == "__main__":

    GUI=interfaz_azure()
    GUI.initializeFrame()
    GUI.runRoot()
    sys.exit()