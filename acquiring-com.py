# -*- coding: utf-8 -*-
# from bad_signal_handler import BadSignalHandler
from models.Signals import Signals

from bad_signal_handler import BadSignalHandler
from libs.udev.ReceptorSerial import ReceptorSerial

__author__ = 'abraham'
import json
import argparse
import base64
import datetime
########################################################################################################################
#  Modulo de comunicaciones por puerto SERIAL                                                                          #
########################################################################################################################
import os
import subprocess
import threading
import serial
import time
#from models.Database import Database
from libs.Debug import Debug
from libs.Document_JSON import Document_JSON
#from models.Alarm import Alarm
#from libs.SocketIOClient import SocketIOClient2NodeJS
#from models.StateRule import StateRule
#import azure_cola
from status_control import status_control
from signals_control import signals_control
from Herbeat import Herbeat
########################################################################################################################


# Construccion de los argumentos obligatorios(parse) y opcionales(group) -----------------------------------------------
parse = argparse.ArgumentParser()
group = parse.add_argument_group()
group.add_argument('-b', '--bits', help='data bits', type=int)
group.add_argument('-p', '--parity', help='parity')
group.add_argument('-s', '--stopbits', help='stop bits', type=float)
group.add_argument('-a', '--ack', help='ack array', action='append', default=None)
group.add_argument('-n', '--nack', help='nack array', action='append', default=None)
group.add_argument('-e', '--endstring', help='end string of receptor')
group.add_argument('-q', '--queuebridge', help='bridge queue receptor')
group.add_argument('-v', '--validationtime', help='verification communication time receptor')
group.add_argument('-l', '--splitstring', help='split string')
group.add_argument('-m', '--accountmang', help='account manage configuration')
parse.add_argument('device', help='device to connect')
parse.add_argument('baudrate', help='baudrate in comunication to device')
parse.add_argument('recid', help='id receptor device')
########################################################################################################################


# Variables y Declaraciones --------------------------------------------------------------------------------------------
args = parse.parse_args()  # instancia de manejo de argumentos
serial_dev = ReceptorSerial()
receptor = 'receptor:' + args.recid  # string identificador de la receptora
ack=args.ack[0]
nack=args.nack[0]
id_receptor=args.recid.replace('receptor:','')
wait_time = 3  # entero de tiempo de espera
last_signal_time = datetime.datetime.now()  # fecha de ultima senal recibida
#db = Database()  # instancia de la base de datos
receptors_document=Document_JSON("Parameters.json")
receptors_document=receptors_document.get_json_array_data("receptor")
bad_signal_handler = BadSignalHandler()
status_control_receptor=status_control("receptor",id_receptor)
signal_control=signals_control(id_receptor)
herbeat=Herbeat()
# Indica el tamaño minimo en bytes que puede tener una señal
__MIN_SIGNAL_SIZE = 2

# Indica la cantidad máxima de lecturas que se pueden hacer sin que se consiga un endstring
MAX_READ_ACUMS_WITHOUT_ENDSTRING = 10

# Cantidad maxima del buffer de lectura
MAX_READ_BUFFER_SIZE = 200


# Funciones ------------------------------------------------------------------------------------------------------------
def preprocess_signal(signal):
    
    #Preprocesa la señal antes de mandarla al manejador de señales
    #:param signal: 
    #:return: 
    print("preprocess "+signal)
    if signal is None or len(signal) == 0:
        return

    # convierto la senal recibida en formato base 64
    regexp = Signals().eval_signal(signal_raw=signal)
    print("AQUI "+str(regexp))
    #groupdict= Signals().eval_signal(signal_raw=signal)
    bad_signal = False
    """ ---Para este metodo se revisa la ultima señal captada en DB(Se debe cambiar)"""
    """if bad_signal_handler.is_cut_signal(signal):
        regexp, groupdict, signal = bad_signal_handler.process_signal(signal)
        # Si aun despues de concatenar con la señal pasada no se consigue una señal
        if regexp is None:
            Debug.printmsg('--- BAD SIGNAL ---')
            bad_signal = True
    """
    #bad_signal_handler.set_prev_signal(signal, regexp) ---ARREGLAR---
    b64data = base64.b64encode(str(signal).encode()).decode()
    send_buffer_signal_to_handler(b64data, regexp, bad_signal)
    return b64data #Esto no va la señal se envia al gestor de señales



def send_buffer_signal_to_handler(b64data, regexp, bad_signal):
    
    #SendBufferSignalToHandler --->  function prototype
    #Funcion para enviar una señal al gestor de senales
    
    try:
        if not bad_signal:
            serial_dev.write_device_ack(ack)
            print("----------ack "+str(ack))
        # invoco al manejador de senales para que procese la senal, pasandole como parametros el receptor y la senal
        #script = 'python3 ' + os.getcwd() + '/signal-handler.py ' + args.recid + ' ' + b64data
        #if regexp:
        #    script += ' -r ' + str(regexp['id'])
        #if bad_signal:
        #    script += ' -b' + str(bad_signal)

        #subprocess.Popen(script + ' &', shell=True)

        # si se paso como parametro envio de senales por cola de mensajes, enviar a la respectiva cola asignada
        #if args.queuebridge:
        #    subprocess.Popen(
        #        'python2 ' + os.getcwd() + '/azure-service.py signal ' + args.queuebridge + ' -m ' + b64data + ' &',
        #       shell=True)
    except:
        Debug.printmsg('--- NO PROCESS BASE64 DATA IN SIGNAL_HANDLER ---')


def is_the_read_limit_exceeded(signal_data, read_cont):
     
    #Indica que el limite del buffer de lectura ha sido excedido.
    #Se usa para evitar que se lea indefinidamente del buffer esperando al caracter
    #de finalización del string.
    
    return len(signal_data) < MAX_READ_BUFFER_SIZE and read_cont < MAX_READ_ACUMS_WITHOUT_ENDSTRING

def is_device_conect():
    exits=serial_dev.exist_device("/dev/ttyUSB0")
    print(exits)
    return exits

def asig_endstring(signal):
    rutaJSON="Parameters.json"
    with open(rutaJSON) as file:
        data = json.load(file)
    signal+=data['connectionParams']['stringEnd']
    return signal

def read_device_thread():
    """
    ReadDeviceThread --->  function prototype
    Funcion del hilo que hace lecturas asincronas del dipositivo serial
    """
    # inicializo la variable de los datos de la senal en vacio
    signal_data = ''
    read_cont = 0

    try:
        while True:
            # espero 200 ms entre cada lectura
            time.sleep(.2)
            
            # si existe informacion por leer en el buffer
            if(is_device_conect()):
                status_object=status_control_receptor.get_status_object()
                if(status_object['status']=='desactive'):
                    print("----------------------CONEXION---------------------------")
                    status_control_receptor.status_report(
                        True,
                        "Receptor activado "+str(id_receptor)
                    )
                
                herbeat.herbeat_status_receptor_alive(id_receptor)

                if serial_dev.inWaiting():

                    if(status_object['status']=='active'):
                        status_control_receptor.status_report(
                            True,
                            "Se recibio un signal"
                        )
                    # instancio la ultima senal recibida y le asigno la hora actual
                    global last_signal_time
                    last_signal_time = datetime.datetime.now()

                    # leo informacion del buffer y formateo la cadena para eliminar el b''
                    data = serial_dev.read_device_binary()
                
                    #if(data!=0)
                    data = str(data)[2:-1]
                    horaRecepcion=time.strftime("%H:%M:%S")
                    fechaRecepcion=time.strftime("%d/%m/%y")
                    # verificaarchivos binarios en python mensaje de lo recibido, este es sobre lo recibido propiamente sin procesar por el algoritmo de nomarlizacion
                    Debug.printmsg('acquiring-com:' + str(args.recid) + ' --> ' + str(data), 'DBG_AQC', True)

                    # concatenarlo a la variable de datos de la senal
                    
                    signal_data += data #Code

                    # si se recibio como parametro que debe haber un final de cadena especifico

                    #if args.endstring and str(signal_data).find(args.endstring) == -1 and \
                    #        not is_the_read_limit_exceeded(signal_data, read_cont):
                    #    continue

                    # imprimir mensaje de lo recibido, este es sobre el algoritmo de normalizacion de cadena, muestra el mensaje real a procesar
                    Debug.printmsg('\n\n' + str(receptor) + ' --> ' + str(signal_data), 'DBG_RECEPTOR', True)
                    print("AD RAW SIGNAL= ", signal_data)
                    

                    # si tiene un corte de señal, porque puede suceder que venga mas de una señal procesable junta
                    # procesar cada senal y enviarla al manejador de senales
                    #print("Señal ", signal_data)

                    for signal in signal_data.split('\r'):
                        print(str(signal_data.split('\r')))
                        if(len(signal)>0):
                            if len(signal) > __MIN_SIGNAL_SIZE or is_the_read_limit_exceeded(signal_data, read_cont):

                                signalBase64=preprocess_signal(str(signal))
                                signalBase64=str(signalBase64)
                                print("horaRecepcion : "+str(horaRecepcion)+ " Signal: "+signalBase64+"  \n")
                                document_signal={
                                    'id_receptor':id_receptor,
                                    'hora_recepcion':horaRecepcion,
                                    'fecha_recepcion':fechaRecepcion,
                                    'signal':signalBase64
                                }
                                
                                signal_control.save_signal_local(document_signal)
                           

                                read_cont = 0
                                time.sleep(0.5)
                            else:
                                read_cont += 1

                    # volver a inicializar la variable de datos de la senal, para iniciar nuevamente el ciclo
                    
                    signal_data = ''
            else:
                print("----------------------NO CONEXION---------------------------")
                if(status_object['status']=='active'):
                    status_control_receptor.status_report(
                        False,
                        "Receptor desconectado "+str(id_receptor)
                    )
                herbeat.herbeat_status_receptor(id_receptor)
                
                
                
    except KeyboardInterrupt:
        print("finish")
        


def config_split_string():
    
    #Configura cual es el string que permitirá dividir una señal de otra.
    #Explicación:
    #Hay protocolos que envian más de una señal en una trama. Ej: 
    #:return: 
    
    if args.endstring is None:
        Debug.printmsg('--ERROR: param endstring is null', 'ERROR null endstring')
        exit()
    flag = False
    try:
        args.endstring = args.endstring.encode().decode('unicode-escape')
    except UnicodeDecodeError:
        flag = True
    if args.splitstring is None and not flag:
        args.splitstring = args.endstring


def main():
    config_split_string()
    
    # instancia de tiempo de espera
    global wait_time
    global serial_dev

    # si se paso como parametro que se debe vigiliar que cada cierto tiempo llegue una senal al buffer
    if args.validationtime:
        # asigno el tiempo de espera suministrado
        wait_time = int(args.validationtime)

    # configurar dispositivo, para lectura
    serial_dev.configure_device(args.device, args.baudrate, args.bits, args.parity, args.stopbits, args.ack, args.nack)
    #receptor_doc = receptors_document.find({ '_id': args.recid})
    #print(str(receptor_doc))
    #assert receptor_doc is not None, 'The receptor % is none' % args.recid
    #bad_signal_handler.configure(receptor_doc, serial_dev, args.endstring)
    # si el dispositivo no logro abrir el puerto, salir
    if not serial_dev.open_device():
        print('Could not open device=', args.device)
        exit()

    # inicia hilo de lectura del buffer
    threading.Thread(target=read_device_thread).start()
    
    try:
        # Ciclo encargado de revisar el estatus del proceso de adquisición
        while True:
            # espero el tiempo de espera asignado, por defecto 3 seg
            time.sleep(wait_time)

            # si el dispositivo no esta conectado, salir
            if not serial_dev.is_device_exist():
                print("------------------SALI DE COMPILACION--------------")
                exit()
                

            # si fue pasado por parametro tiempo de verificacion, y la ultima senal recibida excedio el tiempo permitido
            if args.validationtime and (
                            last_signal_time + datetime.timedelta(
                            minutes=int(args.validationtime)) < datetime.datetime.now()):

                # imprimir mensaje de que se va a generar una ausencia de comunicacion de receptora
                Debug.printmsg('--GENERATED ABSENCE COMMUNICATION RECEPTOR: ' + str(args.recid) + '--')

                # generar la alarma correspondiente
                #staterule = StateRule(db).get('XCMP', 'ARC')
                #doc_alarm = Alarm(db).save_document_absence_communication_receptor(staterule, args.recid)
                
                #try:
                #    SocketIOClient2NodeJS('new alarm').report_monitor(dict(doc_alarm), staterule['doc']['reportAlarms'])
                #except:
                #    Debug.printmsg('--SIO FAIL--')
                
    except KeyboardInterrupt:
        print("finish")
    
        
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
