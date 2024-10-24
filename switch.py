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

    def get_switch(self, switch_name):
        if os.path.isdir(switch_name):
            os.chdir(switch_name)
            self.switch_file = db.getDb('{}.json'.format(switch_name))
            return self.switch_file.getByQuery({'switch':switch_name})[0]

    def get_ports_id(self, switch_name):
        if os.path.isdir(switch_name):
            os.chdir(switch_name)
            self.port_file = db.getDb('{}_ports.json'.format(switch_name))
            self.id = self.port_file.getByQuery({})[0]['id']
            os.chdir(self.base_cwd)
            return self.id

    def get_ports(self, switch_name):
        if os.path.isdir(switch_name):
            os.chdir(switch_name)
            self.port_query = db.getDb('{}_ports.json'.format(switch_name))
            return self.port_query.getByQuery({})[0]

    def update_port(self, switch_name, port):
        os.chdir(switch_name)
        self.load_ports = self.get_ports(switch_name)
        self.loaded_id = self.get_ports_id(switch_name)
        self.load_ports[port]['owner'] ='hello'
        p = db.getDb('{}_ports.json'.format(switch_name))
        print(self.get_ports_id(switch_name))
        os.chdir(self.base_cwd)
        p.updateById(self.get_ports_id(switch_name), self.load_ports)
        print(os.getcwd())
              
    def make_switch(self, switch_name, port_count=16):
        raw_switch_name = switch_name
        switch_name = '{}.json'.format(switch_name)
        self.make_path(raw_switch_name)
        self.pre_cwd = os.getcwd()
        os.chdir(raw_switch_name)
        if not Path(switch_name).is_file():
            self.switch = db.getDb(switch_name)
            self.switch_config = {
                'switch':raw_switch_name,
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
            self.switch.add(self.switch_config)
            self.ports = db.getDb('{}_ports.json'.format(raw_switch_name))
            self.temp = {}
            for port_number in range(0, port_count):
                self.port_name ='port{}'.format(port_number)
                self.port_id = '{}{}'.format(raw_switch_name, self.port_name)
                self.switch_config['pids'].append(self.port_id)
                self.temp[self.port_name] = {}
                self.temp[self.port_name]['stats'] = {}
                self.temp[self.port_name]['stats']['state'] = False
                self.temp[self.port_name]['stats']['owner'] = None
                self.temp[self.port_name]['stats']['group'] = None
                self.temp[self.port_name]['stats']['tx'] = 0
                self.temp[self.port_name]['stats']['rx'] = 0
                self.temp[self.port_name]['info'] = {}
                self.temp[self.port_name]['info']['pid'] = self.port_id
                self.temp[self.port_name]['info']['access'] = []
                self.temp[self.port_name]['info']['last-change']='SYSTEM'
                self.temp[self.port_name]['data'] = []
            self.ports.add(self.temp)
            os.chdir(self.pre_cwd)
        os.chdir(self.pre_cwd)

        
s = switch()
s.make_switch('myswitch')
s.get_ports_id('oknb')
s.update_port('myswitch', 'port2')

#print(s.get_switch('myswitch'))
#s.make_path('myswitch')


