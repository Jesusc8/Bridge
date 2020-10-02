# -*- coding: utf-8 -*-

from libs.Debug import Debug
from libs.Serial import Serial
#from models.Receptor import Receptor
#from models.RedisClient import RedisClient

__author__ = 'abraham'

########################################################################################################################
#  Modulo de levantamiento de procesos                                                                                 #
########################################################################################################################
import os,platform
import time
import psutil
import subprocess
import multiprocessing
import json
from threading import Thread
#from models.Database import Database
from libs.Configuration import Configuration
from libs.Network import Network
########################################################################################################################


# Variables ------------------------------------------------------------------------------------------------------------
watchdog_process_acquiring = []  # array de procesos adquisidores de verificacion por el watchdog
watchdog_process_specific = []  # array de procesos especificos de verificacion por el watchdog
#db = Database()  # instancia de la base de datos
#netbox = db.get('netbox')  # informacion de la netbox
from libs.Document_JSON import Document_JSON
from status_control import status_control
from Interfaz.view_alerts import InterfaceBridges
from signals_control import signals_control
from receptor_control import receptor_control
from Herbeat import Herbeat
from azure_cola import init_cola_azure
from datastorage import *
from read_config_file import create_json_receptor
# ----------------------------------------------------------------------------------------------------------------------


# Funciones ------------------------------------------------------------------------------------------------------------
def is_live_process(pid):
    """
    IsLiveProcess --->  function prototype
    Funcion para verificar si un proceso sigue vivo o no
    """
    try:
        # retorna si un proceso segun un PID se encuentra vivo
        return False if psutil.Process(int(pid)).status() == psutil.STATUS_ZOMBIE else True
    except:
        return False


def exec_specific_process(process, cwd=None):
    """
    ExecProcessSpecific --->  function prototype
    Funcion para ejecutar procesos particulares
    """
    # si se paso como parametro directorio de trabajo
    if cwd:
        # ejecutar proceso con directorio suministrado
        p = subprocess.Popen('python3 ' + process + '.py', cwd=cwd, shell=True)
    else:
        # ejecutar proceso en directorio actual de trabajo
        p = subprocess.Popen('python3 ' + os.getcwd() + '/' + process + '.py', shell=True)

    # agregar proceso al verificador del watchdog
    watchdog_process_specific.append(dict({'pid': str(p.pid), 'exec': process, 'cwd': cwd}))


def exec_acquiring_process(idreceptor, cnx_type, receptor_doc, ack, nack, endstring, validation_time):
    """
    ExecProcessAcquiring  --->  function prototype
    Funcion para ejecutar un proceso adquisidor segun su tipo de conexion
    """
    args = ''
    pyversion = '3'
    control_status=status_control("receptor",idreceptor)
    # Todavía UDP no está soportado
    if cnx_type == 'udp':
        return

    # si tipo de conexion es SERIAL
    if cnx_type == 'com':
        from libs.udev.ReceptorSerial import ReceptorSerial
        #receptor_device = ReceptorSerial.get_device_for_receptor(receptor_doc)

        #if receptor_device is None:
        #    print("ERROR: The device for receptor {} not exist".format(idreceptor))
        #    return None

        #v, e = Receptor.validate_receptor_format(receptor_doc)
        #if not v:
        #    print("ERROR: Bad receptor format: {}".format(e))
        #    return None

        pyversion = '3'
        #args = receptor_device.sys_name + ' ' + receptor_doc['connectionParams']['bauds'] + ' ' + idreceptor
        args = receptor_doc['deviceValues']['port'] + ' ' + receptor_doc['connectionParams']['bauds'] + ' ' + 'receptor:'+idreceptor

        
        if receptor_doc['connectionParams']['bits']:
            args += ' -b ' + receptor_doc['connectionParams']['bits']
        if receptor_doc['connectionParams']['parity']:
            args += ' -p ' + receptor_doc['connectionParams']['parity']
        if receptor_doc['connectionParams']['stopbit']:
            args += ' -s ' + receptor_doc['connectionParams']['stopbit']
        if endstring:
            args += ' -e ' + endstring
        try:
            if receptor_doc['connectionParams']['split']:
                args += ' -l ' + receptor_doc['connectionParams']['split']
        except:
            pass
        

    # si tipo de conexion es TCP o UDP
    elif cnx_type == 'tcp' or cnx_type == 'udp':
        args = receptor_doc['connectionParams']['host'] + ' ' + receptor_doc['connectionParams'][
           'port'] + ' ' + idreceptor

    # si receptora tiene configurado desvio de senales
    #try:
    #    if receptor_doc['connectionParams']['queueNetbox']:
    #        args += ' -q ' + receptor_doc['connectionParams']['queueNetbox']
    #except:
    #    pass

    # si existe parametro de envio de ACKnowledge
    if len(ack):
        if isinstance(ack, list):
            for i in range(0, len(ack)):
                args += ' -a ' + ack[i]
        else:
            args += ' -a ' + ack

    if len(nack):
        if isinstance(nack, list):
            for i in range(0, len(nack)):
                args += ' -n ' + nack[i]
        else:
            args += ' -n ' + nack

    # si existe tiempo de verificacion de recepcion de senales
    if validation_time:
        args += ' -v ' + str(validation_time)

    args += ' -m ' + str('GLOBAL_ACCOUNT_MANA')
    print("first "+args)
    # ejecutar proceso de adquisicion de senales con sus respectivos parametros
    if(platform.platform().startswith("Windows")):
        script = 'py'+ ' ' + os.getcwd() + '/acquiring-' + cnx_type + '.py ' + args
    else:
        script = 'python' + pyversion + ' ' + os.getcwd() + '/acquiring-' + cnx_type + '.py ' + args
     
    print("script "+script)
    
    p=subprocess.Popen(script,shell=True)
    
    print("-------------------------------------PID PROCESS---------------------- "+str(p.pid))   ##LOG DE CONEXIONES
    control_status.status_report(
                        False,
                        "Ejecutando adquisidor para receptora "+str(idreceptor)
                    )
    #agregarlo al verificador de procesos del watchdog
    watchdog_process_acquiring.append(dict(
        {'pid': str(p.pid), 'receptor': idreceptor, 'type': cnx_type, 'value': receptor_doc, 'ack': ack, 'nack': nack,
         'endstring': endstring, 'validationTime': validation_time}))
    
    

def verify_database_state():
    """
    VerifyDatabaseState  --->  function prototype
    Funcion para verificar el estado de la base de datos al iniciar el watchdog
    """
    while True:
        # si base de datos no se encuentra corriendo
        #if not db.is_running():
            # reiniciar servicio
         #   Database.restart_service()
        #else:
            # el servicio ya ha iniciado
        #    break
        continue


def validate_network_config():
    """
    Valida que la configuración
    Verifica que las interfaz de red activa tenga un fichero de configuración adecuado.
    Info:
    https://www.centos.org/docs/5/html/Deployment_Guide-en-US/s1-networkscripts-interfaces.html
    """
    flag = True
    if not Network.is_default_iface_up():
        Debug.printmsg('WARNING: Network is DOWN')

    if not Network.is_network_script_path_writable():
        Debug.printmsg('WARNING: Network path is not writable')
    else:
        if Network.create_file_of_active_iface_if_not_exist():
            Debug.printmsg('WARNING: Network config script not exist. Restarting network service')
            Network.restart_network_service()


def exec_acquiring_receptor_process():
    create_json_receptor() #Lectura del archivo de configuracion
    receptores=Document_JSON("Parameters.json")
    #receptor=receptor[0]
    #print("-----RECIBIDO----- "+receptor['connectionType'])
    """
    ExecAcquiringReceptorProcess  --->  function prototype
    Funcion para iniciar los procesos adquisidores de las receptoras
    """
    #receptors_doc = db.view('receptors.all', include_docs=True)
    try:
        receptors_doc = receptores.get_json_array_data("receptor")
        print("IN_PROCESS.........................")
        # recorriendo documentos de la configuracion de las receptoras
        save_daily_statistics_cola()
        exist_receptors=False
        if(len(receptors_doc)>4):
            receptors_doc=receptors_doc[:4]
            delete_receptors()
        elif(len(receptors_doc)>0):
            exist_receptors=True
            delete_receptors()

        for receptor in receptors_doc:
            
            #si receptora se encuentra activa (si el campo active no está entoces está inactiva)
            if 'active' in receptor and receptor['active']:

                control_status=status_control("receptor",receptor['_id'])
                control_status.status_report(False,"Se creo el adquisidor para el receptor "+str(receptor['_id']))
                #print("Activando adquisidores para la receptora", receptor['_id'].split(":")[1])
                print("holaa "+str(control_status.get_status_object()))
                ack = []
                nack = []
                endstring = None
                
                try:
                    if('verificationTime' in receptor and 'value' in receptor['verificationTime'] and receptor['verificationTime']['value']!=""):
                        validationtime=receptor['verificationTime']['value']
                except:
                     validationtime='300'

                #if 'model' in receptor.doc:

                #   if 'ack' in receptor.doc['model']:

                #        ack = receptor.doc['model']['ack']

                #   if 'nack' in receptor.doc['model']:

                #        nack = receptor.doc['model']['nack']

            if 'connectionParams' in receptor and 'stringEnd' in receptor['connectionParams']:
                # intentar asignar final de cadena, para normalizacion de tramas en puerto serial
                endstring = receptor['connectionParams']['stringEnd']
                if endstring!="":
                    endstring="0D"
                
            
            if endstring is None:
                endstring="0D"
                
                    # intentar asignar tiempo de verificacion de lectura de buffer
                    # Requerimiento futuro:
                    # Las receptoras envían un keepalive cada cierto tiempo indicando
                    # que continuan funcionando. Si el netbox no recibe estos mensajes
                    # en un tiempo, puede ser que la receptora esté bloqueada.
                    # verification_time es el tiempo que se va a esperar hasta declarar
                    # la receptora como bloqueada
                #if 'verificationTime' in receptor and 'require' in receptor['verificationTime']:    
                    #verification_time = receptor['verificationTime']['value']

                    # agregar proceso adquisidor al verificador del watchdog
            #SE ALMACENAN LAS RECEPTORAS NUEVAS Y LAS REGISTRADAS SE ACTIVAN EN LA BD LOCAL

            save_receptor_db(receptor['_id'],receptor['name'],receptor['connectionType'])
            save_daily_statistics_receptor(receptor['_id'])
            print(receptor['_id'], receptor['connectionType'].lower(),
                                receptor, receptor['connectionParams']['ack'], receptor['connectionParams']['nack'], endstring, str(validationtime))        
            exec_acquiring_process(receptor['_id'], receptor['connectionType'].lower(),
                                receptor, receptor['connectionParams']['ack'], receptor['connectionParams']['nack'], endstring, validationtime)
            
        
            #exec_acquiring_process(str(receptor['_id']), receptor['connectionType'].lower(),
            #                        receptor.doc, ack, nack, endstring, 45)  # verification_time)
        
            #exec_acquiring_process('72af42e0e74f11e6ac12f5e599fa25e6', receptor['connectionType'].lower(),
            #                        receptor, receptor['connectionParams']['ack'], receptor['connectionParams']['nack'], endstring, 999999)  # verification_time) 
            #   except Exception as e:
        if(exist_receptors==False):
            print("NO EXISTEN RECEPTORAS ENABLED")

    except Exception as e:
        print("Error archivo JSON de receptoras "+str(e))
        exit()

def init_core_services():
    """
    InitCoreServices  --->  function prototype
    Funcion para iniciar los procesos de servicios del sistema en el core
    """

    # si se tiene configurado iniciar servicios
    if Configuration.get_data()['INIT_SERVICES']:
        #exec_specific_process('replication-cloud')
        #exec_specific_process('eval-absence-open-close')
        #exec_specific_process('eval-absence-open-close-exception')
        #exec_specific_process('eval-absence-signal-report')
        #exec_specific_process('eval-absence-communication')
        #exec_specific_process('discover-red')
        exec_specific_process('inyect-local-signals')
        #exec_specific_process('monitor')
        # exec_process_specific('clean-alarms-signals')

    try:
        # si se tiene configurado inyectar señales de la base de datos de softguard
        if 'inyectSoftGuard' in netbox and 'status' in netbox['inyectSoftGuard'] and \
                netbox['inyectSoftGuard']['status']:
            exec_specific_process('utils/inyect-softguard-signal')
    except:
        pass

def init_alert_interface():
    print("----------------------hola-----------------------------------")
    try:
        interfaz=InterfaceBridges()
        interfaz.initializeFrame()
        if(platform.platform().startswith("Windows")):
            script="py view_alerts.py"
        else:
            script="python3 view_alerts.py"
            
        p=subprocess.Popen(script,shell=True)
    except Exception as e:
        print("NO INICIO INTERFAZ "+str(e))

    
def send_local_signal():
    try:
        rc=receptor_control(0)
        id_receptors=rc.get_id_receptors()
        scs={}
        for id in id_receptors:
            scs[id]=signals_control(id)
        sc_cola=status_control("cola_azure",0)
        while True:
            for id in id_receptors:
                status=scs[id].send_signal_local_to_cola()
                if(status==False):
                    break
    except Exception as e:
        print(str(e))

def init_send_local_signal():
    send_signal = Thread(target=send_local_signal, args=())
    send_signal.start()
    return send_signal

    
def init_herbeat_cola():
    init_cola_azure()
    herbeat=Herbeat()
    herbeat.herbeat_status_cola()
    herbeat_cola = Thread(target=herbeat.active_herbeat_status_cola, args=())
    herbeat_cola.start()
    print("-----------HILO HERBEAT LISTO----------------------")
    return herbeat_cola
   




def watchdog_start():
    """
    WatchdogStart  --->  function prototype
    Funcion para empezar a vigilar los procesos del sistema, es decir levantar si alguno esta muerto
    """
    #Llamado a funcion para envio de señales a la cola, en el while True realizo la prueba de que eta vido
    hilo_envio_azure=init_send_local_signal()
    print("-----------HILO ENVIAR LISTO----------------------")
    hilo_herbeat_cola=init_herbeat_cola()
    print("-----------HILO HERBEAT LISTO----------------------")
    while True:
        time.sleep(1)
        print("SE EJECUTARA EL ADQUISIDOR.....\n")
        # recorro procesos adquisidores que se encuentran en verificacion
        if not hilo_envio_azure.isAlive():
            init_send_local_signal()

        if not hilo_herbeat_cola.isAlive():
            init_herbeat_cola()
        print("----------INICIO AL WATCHDOG---------")
        for p in list(watchdog_process_acquiring):
            # si no esta vivo
            if not is_live_process(p['pid']):
                print("PROCESO MUERTO REVIVIENDO-------------------------------"+p['receptor'])
                # ejecutar proceso nuevo
                exec_acquiring_receptor_process()
                
                exec_acquiring_process(p['receptor'], p['type'], p['value'], p['ack'], p['nack'], p['endstring'],
                                    p['validationTime'])
                # remover proceso anteriorwatchdog_start
                watchdog_process_acquiring.remove(p)
                

        # recorro procesos especificos que se encuentran en verificacion
        for p in list(watchdog_process_specific):
            # si no esta vivo
            if not is_live_process(p['pid']):
                # ejecutar proceso nuevo
                exec_specific_process(p['exec'], p['cwd'])
                # remover proceso anterior
                watchdog_process_specific.remove(p)
    
        

"""
def validate_redis_config():
    if RedisClient.is_active():
        assert RedisClient.validate_config(), "ERROR: Redis config is not valid"
        rc = RedisClient()
        if not rc.is_core_service_up():
            rc.up_core_service()
        assert rc.is_back_service_up(), "ERROR: Redis service not running un back server"
"""
"""
def validate_replication():
    if not db.replicate_doc_exist('nevula-replication'):
        source = Configuration.get_data()['DB_HOST']
        target = 'http://cdb-dev.nevula.com/x' + Serial.get_serial_md5_appliance()
        db.replicate(source, target)
"""


def main():
    
    #validate_replication()
    #print("MAIN->validate_replication() = Ready")

    #validate_network_config()
    #print("MAIN->validate_network_config() = Ready")

    #verify_database_state()
    #print("MAIN->verify_database_state() = Ready")
    
    #validate_redis_config()is_alive
    exec_acquiring_receptor_process()
    print("MAIN->exec_acquiring_receptor_process() = Ready")

    #init_core_services()
    #print("MAIN->init_core_services() = Ready")

    #Desactivo la receptoras almacenadas en bd local
    
    #init_send_local_signal()
    #print("Inicio Proceso Envio Signal->init_cola_azure() = Ready")

    init_alert_interface()
    print("Interfaz Alert->init_alert_interface() = Ready")

    watchdog_start()
    print("MAIN->watchdog_start() = Ready")

    
    


# ----------------------------------------------------------------------------------------------------------------------

main()
""" rutaJSON = "Parameters.json"

with open(rutaJSON) as file:
    data = json.load(file)

receptor = data
endstring = receptor['connectionParams']['stringEnd']
exec_acquiring_process('72af42e0e74f11e6ac12f5e599fa25e6', receptor['connectionType'].lower(),
                            receptor, receptor['connectionParams']['ack'], receptor['connectionParams']['nack'], endstring, 999999)  # verification_time)
 """