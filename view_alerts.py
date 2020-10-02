# -*- coding: utf-8 -*-

from tkinter import PhotoImage,Tk,Frame,Canvas,Button,Label,N,W,NO,CENTER,GROOVE
from tkinter.ttk import Treeview,Scrollbar
import threading
from threading import Thread
import time
import os,sys
#from view_add_receptor import add_receptor_com,add_receptor_tcp
from status_control import status_control
from receptor_control import receptor_control
from datastorage import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
#from signals_control import signals_control
#sys.path.append('/home/home/Escritorio/core')

class InterfaceBridges():
    def __init__(self):
        self.__root=Tk()
        self.__principalFrame=Frame()
        self.__principalFrame.pack(fill="both",expand="True")
        self.__principalFrame.config(bg='gray80', height=32, width=32)
        self.__root.resizable(width=0, height=0)
        self.__canvas = Canvas(self.__principalFrame, height=700, width=1000,bg='gray80')
        rc=receptor_control(0)
        self.receptors_id=rc.get_id_receptors()
        self.receptors_data={}
        self.__init_receptors_data()
        self.label_receptor = {}
        
        self.label_receptor = {}
        self.receptor_img={}
        self.label_receptor_status = {}

        
        self.table_last_activies=Treeview(self.__root, height=7)
        self.lb_title_table_last_act = Label(self.__principalFrame, text="Ultimas Señales", font=("Franklin Gothic Medium Cond",11,'bold'), bg="gray57", height = 1, width = 92,anchor=CENTER, relief=GROOVE) #medium sea green
        
        self.scrollbar_table = Scrollbar(self.__principalFrame, orient="vertical", command=self.table_last_activies.yview)


        self.lb_cola = Label(self.__principalFrame, text="Estado\n Cola Azure", font=("Franklin Gothic Medium Cond", 9), bg="white") #medium sea green
        self.lb_status_cola =  Label(self.__principalFrame, text="En cola:  \n  Enviadas: ", font=("Franklin Gothic Medium Cond", 9), bg="gray80", height = 3, width = 20)
        self.img_cola = PhotoImage(file="Interfaz/resorce_image/Small/cola_image/cloud_one_off_x.png")
        self.lb_cola.config(image=self.img_cola)
        self.desactive_datetime_receptors={}
        self.desactive_datetime_cola=""
        self.desactive_cola_flag=False
        self.desactive_receptors_flag={}
        self.lb_error= Label(self.__principalFrame, text="Falla", font=("Franklin Gothic Medium Cond", 10), bg="red") 
        self.table_last_activies.configure(yscrollcommand=self.scrollbar_table.set)
        
        
    def get_diff_datetime(self, data_time):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
            date2 = datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S')
            date_time_obj = datetime.strptime(str(data_time), '%Y-%m-%d %H:%M:%S')

            diff = relativedelta(date2, date_time_obj)
            return diff.minutes
        except Exception as e:
            print("Calculado tiempo interfaz"+str(e))

    def initializeFrame(self,size='1000x700'):
    
        self.__root.title("Bridges XP")
        self.__initialize_receptor_label()
        self.show_receptor_label()
        self.create_last_activities_table()
        self.mostrar_last_activities()
        self.draw_line_connect()
        self.__root.geometry(size)

    def __init_receptors_data(self):
        for id in self.receptors_id:
            rd=get_receptor_data_db(id)
            self.receptors_data[id]=rd

    def __initialize_receptor_label(self):
        print("")

        for id in self.receptors_id:
            if(self.receptors_data[id] is not None):
                status_text=str(self.receptors_data[id]['name'])+"["+str(self.receptors_data[id]['type'])+"] \n Recibidas:. -"
                lb_receptor = Label(self.__principalFrame, text=id, font=("Franklin Gothic Medium Cond", 9), bg="gray80", width = 120,height=80)#tomato2 medium sea green yellow green
                lb_status = Label(self.__principalFrame, text=status_text, font=("Franklin Gothic Medium Cond", 9), bg="gray80", height = 3, width = 16)
                img = PhotoImage(file="Interfaz/resorce_image/Small/receptor_image1/receptor_alarm_error3.png") # make sure to add "/" not "\"
                self.label_receptor[id] = lb_receptor
                self.receptor_img[id]=img
                self.label_receptor_status[id]=lb_status
                self.desactive_receptors_flag[id]=False
            
            else:
                lb_receptor = Label(self.__principalFrame, text=id, font=("Franklin Gothic Medium Cond", 9), bg="gray80", width = 120,height=80)#tomato2 medium sea green yellow green
                img = PhotoImage(file="Interfaz/resorce_image/Small/receptor_image1/receptor_unknow.png") # make sure to add "/" not "\"
                self.receptor_img[id]=img

    def draw_line_connect(self):
        self.N=N
        self.W=W
        self.__canvas.place(x=0,y=0)
        cant_receptor=len(self.receptors_data)
        if(cant_receptor==1):
            #Para 1
            self.line_connect_receptor_img = PhotoImage(file="Interfaz/resorce_image/line_connect/prueba/connect_1.png")
            self.line_connect_receptor_label = self.__canvas.create_image((485,80), image=self.line_connect_receptor_img, anchor=self.N+self.W)
        
        if(cant_receptor==2):
            #Para 2
            self.line_connect_receptor_img = PhotoImage(file="Interfaz/resorce_image/line_connect/receptor2/connect_long_izq.png")
            self.line_connect_receptor_label = self.__canvas.create_image((580,70), image=self.line_connect_receptor_img, anchor=self.N+self.W)

            self.line_connect_receptor_img_1 = PhotoImage(file="Interfaz/resorce_image/line_connect/receptor2/connect_long_der.png")
            self.line_connect_receptor_label_1 = self.__canvas.create_image((180,70), image=self.line_connect_receptor_img_1, anchor=self.N+self.W)
            
        if(cant_receptor==3):
            #Para 3
            self.line_connect_receptor_img = PhotoImage(file="Interfaz/resorce_image/line_connect/receptor3/connect_1.png")
            self.line_connect_receptor_label = self.__canvas.create_image((487,80), image=self.line_connect_receptor_img, anchor=self.N+self.W)

            self.line_connect_receptor_img_1 = PhotoImage(file="Interfaz/resorce_image/line_connect/receptor3/connect_long_izq.png")
            self.line_connect_receptor_label_1 = self.__canvas.create_image((570,80), image=self.line_connect_receptor_img_1, anchor=self.N+self.W)

            self.line_connect_receptor_img_2 = PhotoImage(file="Interfaz/resorce_image/line_connect/receptor3/connect_long_der.png")
            self.line_connect_receptor_label_2 = self.__canvas.create_image((190,80), image=self.line_connect_receptor_img_2, anchor=self.N+self.W)
            
        if(cant_receptor==4):
            #Para 4
            self.line_connect_receptor_img = PhotoImage(file="Interfaz/resorce_image/line_connect/receptor4/connect_middle_der.png")
            self.line_connect_receptor_label = self.__canvas.create_image((280,75), image=self.line_connect_receptor_img, anchor=self.N+self.W)

            self.line_connect_receptor_img_1 = PhotoImage(file="Interfaz/resorce_image/line_connect/receptor4/connect_middle_izq.png")
            self.line_connect_receptor_label_1 = self.__canvas.create_image((520,75), image=self.line_connect_receptor_img_1, anchor=self.N+self.W)

            self.line_connect_receptor_img_2 = PhotoImage(file="Interfaz/resorce_image/line_connect/receptor4/connect_long_izq.png")
            self.line_connect_receptor_label_2 = self.__canvas.create_image((565,70), image=self.line_connect_receptor_img_2, anchor=self.N+self.W)

            self.line_connect_receptor_img_3 = PhotoImage(file="Interfaz/resorce_image/line_connect/receptor4/connect_long_der.png")
            self.line_connect_receptor_label_3 = self.__canvas.create_image((90,70), image=self.line_connect_receptor_img_3, anchor=self.N+self.W)
            

    def create_last_activities_table(self):
        self.table_last_activies["columns"]=("one","two")
        self.table_last_activies.column("#0", width=270, minwidth=270, stretch=NO)
        self.table_last_activies.column("one", width=150, minwidth=150, stretch=NO)
        self.table_last_activies.column("two", width=486, minwidth=200)
        self.table_last_activies.heading("#0",text="Nombre Receptora",anchor=W)
        self.table_last_activies.heading("one", text="Hora",anchor=W)
        self.table_last_activies.heading("two", text="Señal",anchor=W)

    def mostrar_last_activities(self):
        
        last_activities=get_last_activities()
        for i in self.table_last_activies.get_children():
            self.table_last_activies.delete(i)

        if(last_activities is not None):
            for i in range(len(last_activities)):
                
                id_receptor=last_activities[i]['id_receptor']
                signal=last_activities[i]['signal']
                data_datetime=last_activities[i]['data_datetime']
                date_time_obj = datetime.strptime(str(data_datetime), '%Y-%m-%d %H:%M:%S')
                data_datetime=date_time_obj.strftime('%H:%M:%S') 
                
                if(id_receptor in self.receptors_data):
                    self.table_last_activies.insert("", i, text=str(self.receptors_data[id_receptor]['name']), values=(str(data_datetime),str(signal)))
                else:
                    self.table_last_activies.insert("", i, text="repector "+str(id_receptor), values=(str(data_datetime),str(signal)))
                
        
        



    def init_position(self):
        self.posx_receptor={}
        cant_receptor=len(self.receptors_id)
        if(cant_receptor==1):
            self.posx_receptor[0]=432
            self.posy_receptor=10

        elif(cant_receptor==2):
            self.posx_receptor[0]=125
            self.posy_receptor=10

        elif(cant_receptor==3):
            self.posx_receptor[0]=125
            self.posy_receptor=10
        elif(cant_receptor==3):
            self.posx_receptor[0]=300
            self.posy_receptor=10
        elif(cant_receptor==4):    
            self.posx_receptor[0]=30
            self.posy_receptor=10
            
    def show_receptor_label(self):
        if(self.receptors_data is not None):
            self.init_position()
        cont=0
        cant_receptor=len(self.receptors_id)
        for id in self.receptors_id:
            
            self.label_receptor[id].config(image=self.receptor_img[id])
            self.label_receptor[id].place(x=self.posx_receptor[cont], y=self.posy_receptor)
            self.label_receptor_status[id].place(x=self.posx_receptor[cont], y=self.posy_receptor+100)
            cont+=1

            if(cant_receptor==2):
                self.posx_receptor[cont]=self.posx_receptor[cont-1]+630
            elif(cant_receptor==3):
                self.posx_receptor[cont]=self.posx_receptor[cont-1]+310
            elif(cant_receptor==4):
                
                if(cont==1 or cont==3):
                    self.posx_receptor[cont]=self.posx_receptor[cont-1]+190
                elif(cont==2):
                    self.posx_receptor[cont]=self.posx_receptor[cont-1]+425
                

        self.lb_cola.place(x=425,y=300)
        self.lb_status_cola.place(x=420,y=402)
        self.lb_title_table_last_act.place(x=50,y=480)
        self.table_last_activies.place(x=50,y=500)
        self.scrollbar_table.place(x=50+906+2, y=500, height=163)
            
        
 
    def resideFrame(self,size='500x500'):
        self.__root.geometry(size)

    def update_alert_label(self):
        sc_cola=status_control("cola_azure",0)
        sc_receptors={}
        for id in self.receptors_id:
            sc_receptors[id]=status_control("receptor",id)
        try:
            while True:
                #net_is_up()
                status_object_cola=sc_cola.get_status_object()
                #diff=self.get_diff_datetime(status_object_cola['data_datetime'])
                #status_text="Act. "+str(diff)+" min"
                
                status_text="En cola: "+str(sc_cola.get_status_local_signal())+" \n Enviadas:"+str(sc_cola.get_status_statistic_send_cola())
                if(status_object_cola['status']=='active'):
                    self.img_cola = PhotoImage(file="Interfaz/resorce_image/Small/cola_image/cloud_one_on_green.png")
                    self.lb_cola.config(image=self.img_cola)
                    self.lb_status_cola.config(text=status_text)
                    if(self.desactive_cola_flag==True):
                        self.desactive_cola_flag=False
                        self.desactive_datetime_cola=""

                elif(status_object_cola['status']=='desactive'):
                    diff_cola=0
                    if(self.desactive_cola_flag==False):
                        self.desactive_datetime_cola=status_object_cola['data_datetime']
                        self.desactive_cola_flag=True

                    diff_cola=self.get_diff_datetime(self.desactive_datetime_cola)
                    status_text+="\n Tiempo Desact. "+str(diff_cola)+" min"
                    self.img_cola = PhotoImage(file="Interfaz/resorce_image/Small/cola_image/cloud_one_off_x.png")
                    self.lb_cola.config(image=self.img_cola,text=status_text)
                    self.lb_status_cola.config(text=status_text)

                
                diff_receptors={}
                for id in self.receptors_id:
                    status_object_receptor=sc_receptors[id].get_status_object()
                    status_text=str(self.receptors_data[id]['name'])+"["+str(self.receptors_data[id]['type'])+"] \n Recibidas: "+str(sc_receptors[id].get_status_statistic_receptor())
                    if(status_object_receptor['status']=='active'):
                        update_active_img = PhotoImage(file="Interfaz/resorce_image/Small/receptor_image1/receptor_two_only.png") # make sure to add "/" not "\"
                        self.receptor_img[id]=update_active_img
                        self.label_receptor[id].config(image=self.receptor_img[id])
                        self.label_receptor_status[id].config(text=status_text)
                        if(self.desactive_receptors_flag[id]==True):
                            self.desactive_receptors_flag[id]=False
                            self.desactive_datetime_receptors[id]=""

                    elif(status_object_receptor['status']=='desactive'):
                        diff_receptors[id]=0
                        if(self.desactive_receptors_flag[id]==False):
                            self.desactive_receptors_flag[id]=True
                            self.desactive_datetime_receptors[id]=status_object_receptor['data_datetime']
                        
                        diff_receptors[id]=self.get_diff_datetime(self.desactive_datetime_receptors[id])
                        status_text+="\n Tiempo Desact."+str(diff_receptors[id])+" min"
                        update_desactive_img = PhotoImage(file="Interfaz/resorce_image/Small/receptor_image1/receptor_alarm_error3.png") # make sure to add "/" not "\"
                        self.receptor_img[id]=update_desactive_img
                        self.label_receptor[id].config(image=self.receptor_img[id], text=status_text)
                        self.label_receptor_status[id].config(text=status_text)
                
                time.sleep(1)
                self.mostrar_last_activities()

        except Exception as Error:
            print("INICIAR INTERFAZ "+str(Error))
            sys.exit()
   
   
    def runRoot(self):
        try:
            update_label = Thread(target=self.update_alert_label, args=())
            update_label.start()
            self.__root.mainloop()
        except Exception as Error:
            print("ERROR DE AL INICIAR INTERFAZ "+str(Error))



if __name__ == "__main__":
    GUI=InterfaceBridges()
    GUI.initializeFrame()
    GUI.runRoot()
    sys.exit()