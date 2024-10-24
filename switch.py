from pathlib import Path
from pysondb import db
import datetime
import secrets
import json
import os


''' --SWITCH--[DRAFT]
 *** This code may not be the most optimized at this stage ***
 [Author] *33

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


    def load_switch(self, switch_name):
        try:
            self.load_switch_file = db.getDb(self.make_db_path(switch_name, 'switch'))
        except FileNotFoundError:
            pass
        else: return self.load_switch_file


    def update_port(self, switch_name, port, update):
        self.update_port_load = self.load_port(switch_name)
        self.update_port_load.updateById(self.get_port_id(switch_name, port), update)

    def update_switch(self, switch_name, update):
        self.update_switch_load = self.load_switch(switch_name)
        self.update_switch_load.updateById(self.get_switch_id(switch_name), update)

    def enable_port(self, switch_name, port, data):
        try:
            if data['stats']['state'] == False:
                data['stats']['state'] = True
        except TypeError:
            print('cannot enable port')
        else:
            return data

    def disable_port(self, switch_name, port, data):
        try:
            if data['stats']['state'] == True:
                data['stats']['state'] = False
        except TypeError:
            print('cannot disable port')
        else:
            return data

    def set_port_owner(self, switch_name, port, owner, key, data):
        try:
            data['stats']['owner'] = owner
            data['info']['key'] = key
        except TypeError:
            print('port invalid')
        else:
            return data


    def set_port_group(self, switch_name, port, group, data):
        try:
            if data['stats']['group'] == None:
                data['stats']['group'] = group
        except TypeError:
            print('cannot set group')
        else:
            return data
                
    def set_port_last_change(self, switch_name, port, change, data):
        try:
            data['info']['last-change'] = change
        except TypeError:
            print('cannot change port status')
        else:
            return data

    def add_port_access(self, switch_name, port, to_allow_access, data):
        try:
            if not to_allow_access in data['info']['access']:
                data['info']['access'].append(to_allow_access)
        except TypeError:
            pass
        else:
            return data
        

    def remove_port_access(self, switch_name, port, to_remove_access, data):
        try:
            if to_remove_access in data['info']['access']:
                data['info']['access'].remove(to_remove_access)

        except TypeError:
            pass
        else:
            return data
                
                


    def register_port(self, switch_name, owner, key, port):
        self.rps = self.get_switch(switch_name)
        if not owner in self.rps['clients']:
            x = self.set_port_owner(switch_name, port, owner, key, self.get_port(switch_name, port))
            self.enable_port(switch_name, port, x)
            self.disable_port(switch_name, port, x)
            self.set_port_group(switch_name, port, 'mygroup100', x)
            self.set_port_last_change(switch_name, port, 'awesome stuff!', x)
            self.add_port_access(switch_name, port, 'mesun', x)
            self.remove_port_access(switch_name, port, 'mesun', x)
            print(x)
            
            
            '''
            self.rps['clients'].append(owner)
            self.rps['clientmap'][owner] = {}
            self.rps['clientmap'][owner]['port'] = port
            self.rps['portmap'][port] = {}
            self.rps['portmap'][port] = owner
            self.update_switch(switch_name, self.rps)'''
            

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
                        'key':None,
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
#s.update_port('123df', 'port3',{'info':{'owner':'me'}})
s.register_port('123df', 'tom', 'mykey', 'port5')
#s.set_port_owner('123df', 'port5', '1000')
#s.remove_port_access('123dxf', 'port5', 'mycool')
#s.set_port_last_change('123df', 'port5', 'mychange')
#print(s.get_port('123d', 'port0'))
#print(s.get_switch('123d'))
#print(s.make_db_path('123d', 'switch'))
