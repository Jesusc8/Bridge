# -*- coding: utf-8 -*-
from iface_watcher import IfaceWatcher

__author__ = 'abraham'

########################################################################################################################
#  Modulo de comunicaciones por puerto TCP                                                                             #
########################################################################################################################
import os
import time
import base64
import socket
import asyncore
import argparse
import datetime
import threading
import subprocess
from libs import Debug
#from libs import Models
#from models import StateRule, Database
from libs import SocketIOClient
from signals_control import signals_control
from status_control import status_control
from Herbeat import Herbeat
########################################################################################################################


# Construccion de los argumentos obligatorios(parse) y opcionales(group) -----------------------------------------------
parse = argparse.ArgumentParser()
group = parse.add_argument_group()
group.add_argument('-a', '--ack', help='ack array', action='append', default=[])
group.add_argument('-n', '--nack', help='ack array', action='append', default=[])
group.add_argument('-q', '--queuebridge', help='bridge queue receptor')
group.add_argument('-v', '--validationtime', help='verification communication time receptor')
group.add_argument('-m', '--accountmang', help='account manage configuration')
parse.add_argument('host', help='ip communication device')
parse.add_argument('port', help='port comunication device')
parse.add_argument('recid', help='id receptor device')

args = parse.parse_args()
id_receptor=args.recid
ack=args.ack[0]
nack=args.nack[0]
status_control_receptor=status_control("receptor",id_receptor)
signal_control=signals_control(id_receptor)
herbeat=Herbeat()
########################################################################################################################


# Variables y Declaraciones --------------------------------------------------------------------------------------------
#db = Database.Database()  # instancia de la base de datos
debug = Debug.Debug  # instancia de la clase Debug, se utiliza para parecerse mas a python3, utilizando una instancia
fail_count=0

# ----------------------------------------------------------------------------------------------------------------------


# Clase Cliente TCP ----------------------------------------------------------------------------------------------------
class ClientSocket(asyncore.dispatcher):
    NACK = nack
    ACK = ack
    def __init__(self, host, port):
        """
        Contruct --->  function prototype
        Constructor de la clase Cliente TCP
        """
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.read_buffer = bytes()
        self.write_buffer = bytes()
        self.connect((host, port))
        
        
    def send_byte(self, data):
        my_bytes = bytearray()
        my_bytes.append(6)
        self.send(my_bytes)

    def send_nack(self):
        self.send_byte(self.NACK)

    def send_ack(self):
        self.send_byte(self.ACK)

    def handle_connect(self):
        """
        EventConnect --->  function prototype
        Evento que ocurre al aceptar la conexion del dispositivo mediante TCP
        """
        
        
        print("----------------------CONEXION TCP---------------------------")
        status_control_receptor.status_report(
            True,
            "Receptor activado "+str(id_receptor)
        )

        
        print("SEND ACK -> {}".format(args.ack))
        self.send_ack()
        print("Conect!")
        return True


    def handle_read(self):
        print("-----------------LEYENDO TCP--------------------")
        """
        EventRead --->  function prototype
        Evento que ocurre al recibir informacion al buffer del dispositivo TCP
        """
        # instancio la ultima senal recibida y le asigno la hora actual
        global fail_count
        global last_signal_time
        fail_count=0
        last_signal_time = datetime.datetime.now()

        # leo informacion del buffer, [ BLOQUEANTE ]
        data = bytes(self.recv(8192))
        self.read_buffer.__add__(data)
        data = str(data)[2:-1]
        #herbeat.herbeat_status_receptor_alive(id_receptor)
        # imprimir mensaje de lo recibido
        debug.printmsg(str(receptor) + ' --> ' + str(data), 'DBG_RECEPTOR', True)
        print("-----------------leyendo TCP--------------------")
        try:
            # convierto la senal recibida en formato base 64
            #b64data = str(base64.b64encode(str(data).encode()))
            #data_str=data.decode("utf-8") 
            b64data = base64.b64encode(str(data).encode()).decode()
            b64data=str(b64data)
            print("--------SE RECIBIO LA SEÑAL---------------------")
            

            if args.ack:
                print("SEND ACK -> {}".format(args.ack))
                self.send_ack()

            #if args.printed_mode:
            #    VirtualPrinter.print(args.recid, data)
            #    return

            if len(data) < 2:
                return
            print("--------SE ENVIO EL ACK---------------------")
            horaRecepcion=time.strftime("%H:%M:%S")
            fechaRecepcion=time.strftime("%d/%m/%y")
            status_object= status_control_receptor.get_status_object()
            if(status_object['status']=='active'):
                print("----------------------CONEXION---------------------------")
                status_control_receptor.status_report(
                    True,
                    "Se recibio una signal del receptor "+str(id_receptor)
                )
            
            document_signal={
                'id_receptor':id_receptor,
                'hora_recepcion':horaRecepcion,
                'fecha_recepcion':fechaRecepcion,
                'signal':b64data
            }
            signal_control.save_signal_local(document_signal)
            print("--------------------SE ENVIO SEÑAL TCP--------------------------")
            # invoco al manejador de senales para que procese la senal, pasandole como parametros el receptor y la senal
            """subprocess.Popen('python3 ' + os.getcwd() + '/signal-handler.py ' + args.recid + ' ' + b64data + ' &',
                             shell=True)"""

            # si se paso como parametro envio de senales por cola de mensajes, enviar a la respectiva cola asignada
            """if args.queuebridge:
                subprocess.Popen(
                    'python2 ' + os.getcwd() + '/azure-service.py signal ' + args.queuebridge + ' -m ' + b64data + ' &',
                    shell=True)"""
        except Exception as e:
            print("ERROR RECIBIENDO"+str(e))
            debug.printmsg('--- NO PROCESS BASE64 DATA IN SIGNAL_HANDLER ---')

    def handle_close(self):
        """
        EventClose --->  function prototype
        Evento que ocurre al cerrar la conexion con el dispositivo mediante TCP
        """
        herbeat.herbeat_status_receptor(id_receptor)
        self.close()

    def readable(self):
        """
        EventReadable --->  function prototype
        Setea la posibilidad de lectura en True
        """
        herbeat.herbeat_status_receptor_alive(id_receptor)
        return True

    def handle_write(self):
        """
        EventWrite --->  function prototype
        Evento que ocurre al escribir por el buffer con el dispositivo mediante TCP
        """
        sent = self.send(self.write_buffer)
        self.write_buffer = self.write_buffer[sent:]


# ----------------------------------------------------------------------------------------------------------------------


# Variables y Declaraciones --------------------------------------------------------------------------------------------
#args = parse.parse_args()  # instancia de manejo de argumentos
args.validationtime = int(args.validationtime)
try:
    client = ClientSocket(args.host, int(args.port))  # instancia de la clase del socket TCP
except:
    client.close()
    debug.printmsg('--CLIENT NOT CONECTED: RESTARTING ACQUISITOR: --', color='RED')
    exit()
receptor = 'receptor:' + args.recid  # string identificador de la receptora
last_signal_time = datetime.datetime.now()  # fecha de ultima senal recibida
i = None

# ----------------------------------------------------------------------------------------------------------------------
def reopen_port():
    global client
    client.close()
    time.sleep(2)
    client = ClientSocket(args.host, int(args.port))

# Funciones ------------------------------------------------------------------------------------------------------------
def thread_validation_communication():
    print("------------CORRIENDO VALIDACION DE COMUNICACION----------------------")
    """
    ThreadValidationCommunication --->  function prototype
    Funcion para validar la comunicacion de la receptora en la netbox
    """
    # instancia de ultia senal recibida
    global last_signal_time
    global client
    global fail_count

    wait_time = int(args.validationtime) if args.validationtime else 20000000

    while True:
        print("-------------VALIDATION TIME RUN---------------------------")
        # espero el tiempo de espera asignado
        time.sleep(wait_time)

        # si el cliente no se encuentra conectado, salir
        if not client.connected:
            debug.printmsg('--CLIENT NOT CONECTED: RESTARTING ACQUISITOR: --')
            client.close()
            i.exit()
            exit()

        # si ultima senal recibida excedio el tiempo permitido
        if (last_signal_time + datetime.timedelta(seconds=int(args.validationtime))) < datetime.datetime.now():
            fail_count += 1

            if fail_count < 3:
                debug.printmsg('--TIMEOUT: SEND ACK #{}: --'.format(fail_count))
                client.send_ack()
                continue

            if fail_count < 5:
                reopen_port()
                debug.printmsg('--TIMEOUT: REOPEN SOCKET PORT: --')
                send_absence_comunication_alarm()
                fail_count = 2
                continue

            if args.validationtime:
                send_absence_comunication_alarm()
                debug.printmsg('--TIMEOUT: RESTARTING ACQUISITOR: --')
                client.close()
                i.exit()
                exit()

    


def send_absence_comunication_alarm():
    # imprimir mensaje de que se va a generar una ausencia de comunicacion de receptora
    debug.printmsg('--GENERATED ABSENCE COMMUNICATION RECETOR: ' + str(args.recid) + '--')
    status_object= status_control_receptor.get_status_object()
    if(status_object['status']=='active'):
        print("----------------------CONEXION---------------------------")
        status_control_receptor.status_report(
            False,
            "Conexion TCP cerrada para el receptor"
        )
    herbeat.herbeat_status_receptor(id_receptor)
    # generar la alarma correspondiente
    #staterule = StateRule.StateRule(db).get('XCMP', 'ARC')
    #doc_alarm = Models.Alarm(db).save_document_absence_communication_receptor(staterule, args.recid)
    #SocketIOClient.SocketIOClient2NodeJS('new alarm').report_monitor(dict(doc_alarm), staterule['doc']['reportAlarms'])


def main():
    print("-----------------MAIN TCP--------------------"+str(id_receptor))
    global i
    i = IfaceWatcher(1, send_absence_comunication_alarm)
    i.test_network_status()
    # si fue pasado por parametro tiempo de verificacion, iniciar hilo de tiempo de verificacion de recepcion de senal
    if args.validationtime:
        threading.Thread(target=thread_validation_communication).start()

    # inicar proceso recursivo para la clase TCP
    asyncore.loop()



# ----------------------------------------------------------------------------------------------------------------------

main()
