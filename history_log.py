import os, platform, logging
import datetime
from datetime import datetime

class log:
    def __init__(self,path_name='history_log'):
        self.fichero_name_log=path_name+'.log'

        if(platform.platform().startswith("Windows")):
            self.fichero_log=os.path.join(self.fichero_name_log)
        
        else:
            self.fichero_log=os.path.join(self.fichero_name_log)
        
    def config_log(self):
        try:
            create=os.path.getctime(self.fichero_name_log)
            create=datetime.fromtimestamp(create).strftime('%Y-%m-%d') 
            now = datetime.now().strftime('%Y-%m-%d')
            if(now > create):
                print("entre")
                os.close(self)
                os.remove('history_log.log')
        except FileNotFoundError:
                print("--CREATE LOG---")
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - [%(levelname)s] - : %(message)s',
                            filename=self.fichero_log,
                            filemode='a+')

    def write_debug_message(self,name,message):
        try:
            name=name.upper()
            type_msg=""
            if(name=="RECEPTOR"):
                type_msg="INPUT"
            elif(name=="COLA_AZURE"):
                type_msg="OUTPUT"

            logging.debug(type_msg+" - : "+name+" - : "+message)
        except Exception as e:
            print("--CREATE LOG--- "+str(e))
    
    def write_info_message(self,name,message):
        try:
            name=name.upper()
            type_msg=""
            if(name=="RECEPTOR"):
                type_msg="INPUT"
            elif(name=="COLA_AZURE"):
                type_msg="OUTPUT"
            
            logging.info(type_msg+" - : "+name+" - : "+message)

        except Exception as e:
            print("--CREATE LOG--- "+str(e))
    
    def write_warning_message(self,name,message):

        try:
            name=name.upper()
            type_msg=""
            if(name=="RECEPTOR"):
                type_msg="INPUT"
            elif(name=="COLA_AZURE"):
                type_msg="OUTPUT"
            
            logging.warning(type_msg+" - : "+name+" - : "+message)

        except Exception as e:
            print("--CREATE LOG--- "+str(e))
    
    def write_error_message(self,name,message):
        try:
            name=name.upper()
            type_msg=""
            if(name=="RECEPTOR"):
                type_msg="INPUT"
            elif(name=="COLA_AZURE"):
                type_msg="OUTPUT"
            

            logging.error(type_msg+" - : "+name+" - : "+message)
        except Exception as e:
            print("--CREATE LOG--- "+str(e))

    
    def close_log(self):
        logging.shutdown()

