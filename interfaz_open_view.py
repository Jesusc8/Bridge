#!usr/bin/env
# -*- coding: utf-8 -*-

from tkinter import Tk,Frame,Button,Label,N,W,NO,CENTER,GROOVE,Entry,CENTER,NW,SE
import threading
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo
from threading import Thread
import time,multiprocessing
import os,sys,,platform
from datastorage import save_cola_azure_db
from crypt_password import encode_password
import subprocess





class interfaz_azure():
    def __init__(self):
        self.__root=Tk()
        
        self.__principalFrame=Frame()
        self.__principalFrame.pack(fill="both",expand="True")
        self.__principalFrame.config(bg='gray80', height=32, width=32)


        self.btn_interfaz_principal = Button(self.__principalFrame,font=("Franklin Gothic Medium Cond",9),text="Interfaz Principal",bg="gray84", height = 3, width = 40, command=self.open_interfaz_principal) # you can add you image to it using photoimage
        self.btn_interfaz_azure = Button(self.__principalFrame,font=("Franklin Gothic Medium Cond",9),text="Interfaz Datos Azure",bg="gray84", height = 3, width = 40, command=self.open_interfaz_azure)
        self._lbl_title=Label(self.__principalFrame,font=("Franklin Gothic Medium Cond",12),text="CENTRO DE ACCESO A LAS INTERFACES DEL BRIDGES",bg="gray80", width = 45,height=1,anchor=CENTER)

 

    def initializeFrame(self,size='500x500'):
    
        self.__root.title("CENTRO DE ACCESO A VISTAS")
        self.__root.geometry(size)
        self.make_place()
        

    def open_interfaz_azure(self):
        try:
            self.__root.destroy()
            if(platform.platform().startswith("Windows")):
                subprocess.call("py view_data_azure.py", shell=True)
            else:
                euid = os.geteuid() 
                if euid != 0:
                    root = Tk() # Create an instance of tkinter
                    root.withdraw()
                    Password = askstring('root', '   SUDO PASSWORD', show='*')
                    sudo_command = 'python3 view_data_azure.py' 
                    root.destroy()
                    os.system('echo %s|sudo -S %s' % (Password, sudo_command))
                else:
                    subprocess.call("python3 view_data_azure.py", shell=True)
        except Exception as e:
            print("Error interfaz azure "+str(e))
        

    def open_interfaz_principal(self):
        try:
            self.__root.destroy()
            if(platform.platform().startswith("Windows")):
                subprocess.call("py view_alerts.py", shell=True)
            else:
                subprocess.call("python3 view_alerts.py", shell=True)
        except Exception as e:
            print("Error interfaz principal de alertas "+str(e))
        

    def make_place(self):
        self._lbl_title.place(x=25,y=50)
        self.btn_interfaz_principal.place(x=80,y=125)
        self.btn_interfaz_azure.place(x=80,y=225)



    def resideFrame(self,size='500x500'):
        self.__root.geometry(size)
   
    def runRoot(self):
        self.__root.mainloop()

if  __name__ == "__main__":    
    GUI=interfaz_azure()
    GUI.initializeFrame()
    GUI.runRoot()