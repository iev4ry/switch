from pathlib import Path
from pysondb import db
import datetime
import secrets
import json
import os


class switch:
    def __init__(self):
        self.switch_list_name = 'switch_list.json'
        self.base_cwd = os.getcwd()
        if not Path(self.switch_list_name).is_file():
            self.switch_list = db.getDb(self.switch_list_name)

    def make_json(self, json_able_data):
        return json.dumps(json_able_data, indent=4)

    def make_path(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def make_db_path(self, switch_name, flag):
        self.test = os.path.join(self.base_cwd, switch_name)
        if flag == 'port':
            self.port_file_name = '{}_ports.json'.format(switch_name)
            return os.path.join(self.test, self.port_file_name)
        else:
            if flag == 'switch':
                self.switch_file_name = '{}.json'.format(switch_name)
                return os.path.join(self.test, self.switch_file_name) 
                    
    def get_port(self, switch_name, port):
        try:
            self.req_port_file = db.getDb(self.make_db_path(switch_name, 'port'))
            self.gp_file = self.req_port_file.getByQuery({'port':port})[0]
        except IndexError:
           pass
        except FileNotFoundError:
            pass
        else:return self.gp_file

    def get_switch(self, switch_name):
        try:
            self.get_switch_file = db.getDb(self.make_db_path(switch_name, 'switch'))
            self.gs_file = self.get_switch_file.getByQuery({'switch':switch_name})[0]
        except IndexError:
            pass
        except FileNotFoundError:
            pass
        else:return self.gs_file 
        
    def get_port_id(self, switch_name, port):
        self.get_path = os.path.join(self.base_cwd, switch_name)
        if os.path.isdir(self.get_path):
            self.port_file = db.getDb(self.make_db_path(switch_name, 'port'))
            return self.port_file.getByQuery({'port':port})[0]['id']
        
    def get_switch_id(self, switch_name):
        self.switch_id_path = os.path.join(self.base_cwd, switch_name)
        if os.path.isdir(self.switch_id_path):
            self.switch_file = db.getDb(self.make_db_path(switch_name, 'switch'))
            return self.switch_file.getByQuery({'switch':switch_name})[0]['id']
    
    def load_port(self, switch_name):
        try:
            self.load_ports_file = db.getDb(self.make_db_path(switch_name, 'port'))
        except FileNotFoundError:
            pass
        else:
            return self.load_ports_file

    def update_port(self, switch_name, port, update):
        self.update_port_load = self.load_port(switch_name)
        self.update_port_load.updateById(self.get_port_id(switch_name, port), update)

    def enable_port(self, switch_name, port):
        self.ep = self.get_port(switch_name, port)
        if not self.ep == None:
            if self.ep['stats']['state'] == False:
                self.ep['stats']['state'] = True
                self.update_port(switch_name, port, self.ep)
                   
    def make_switch(self, switch_name, port_count=16):
        self.raw_switch_name = switch_name
        self.switch_name = '{}.json'.format(switch_name)
        self.make_path(self.raw_switch_name)
        os.chdir(self.raw_switch_name)
        if not Path(self.switch_name).is_file():
            self.switch = db.getDb(self.switch_name)
            self.switch_config = {
                'switch':self.raw_switch_name,
                'ports':{},
                'clients':[],
                'clientmap':{},
                'groupmap':{},
                'portmap':{},
                'ackmap':{},
                'pids':[],
                'stats':{
                    'rx':0,
                    'tx':0,
                    'created':str(datetime.datetime.now())}}
            
            self.ports = db.getDb('{}_ports.json'.format(self.raw_switch_name))
            for port_number in range(0, port_count):
                self.port_name = 'port{}'.format(port_number)
                self.switch_config['ports']['port_count'] = port_count
                self.port_id = '{}{}'.format(self.raw_switch_name, self.port_name)
                self.switch_config['pids'].append(self.port_id)
                self.ports.add({
                    'port':self.port_name,
                    'stats':{
                        'state':False,
                        'owner':None,
                        'group':None,
                        'tx':0,
                        'rx':0,},
                    'info':{
                        'pid':self.port_id,
                        'access':[],
                        'last-change':'SYSTEM'},
                    'data':[]})
            self.switch.add(self.switch_config)
            
        
                       
    
s = switch()
s.make_switch('123df')
print(s.get_port_id('123d', 'port5'))
print(s.get_switch_id('123d'))
print(s.load_port('123df'))
s.update_port('123df', 'port3',{'info':{'owner':'me'}})
s.enable_port('123df', 'port5')
#print(s.get_port('123d', 'port0'))
#print(s.get_switch('123d'))
#print(s.make_db_path('123d', 'switch'))
