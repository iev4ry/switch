
from pysondb import db
import datetime
import secrets
import json

class switch:
    def __init__(self):
        self.switch_map = db.getDb('switch_map.json')

    def make_json(self, json_able_data):
        return json.dumps(json_able_data, indent=4)

    def check_switch_exist(self, switch_name):
        if len(self.switch_map.getByQuery({'switch':switch_name})) == 0:
            return True

    def create_switch(self, switch_name, port_count=16):
        if self.check_switch_exist(switch_name):
            self.port_map = db.getDb('{}_port_map.json'.format(switch_name))
            self.switch_map.add({
                'switch':switch_name,
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
                    'created':str(datetime.datetime.now())}})
            
            self.made_switch = self.get_switch(switch_name)
            for port_number in range(0, port_count):
                self.port_name = 'port{}'.format(port_number)
                self.made_switch['ports']['port_count'] = port_count
                self.port_id = '{}{}'.format(switch_name, self.port_name)
                self.made_switch['pids'].append(self.port_id)
                self.port_map.add({
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
                
            self.switch_map.updateById(self.get_switch_id(switch_name), self.made_switch)

    def update_switch(self, switch_name, switch_update):
        self.switch_map.updateById(self.get_switch_id(switch_name), switch_update)

    def update_port(self, switch_name, port, port_update):
        self.up = self.load_port(switch_name)
        self.up.updateById(self.get_port_id(switch_name, port), port_update)

    def get_switch_id(self, switch_name):
        return self.switch_map.getByQuery({'switch':switch_name})[0]['id']

    def get_port_id(self, switch_name, port_name):
        self.gpi = self.load_port(switch_name)
        return self.gpi.getByQuery({'port':port_name})[0]['id']
        
    def get_switch(self, switch_name):
        return self.switch_map.getByQuery({'switch':switch_name})[0]

    def get_switch_by_name(self, switch_name):
        if not len(self.get_switch(switch_name)['switch']) == 0:
            return True
        
    def get_switch_ports(self, switch_name):
        if self.get_switch_by_name(switch_name):
            return self.get_switch(switch_name)['ports']['owned']
        
    def show_switch(self, switch_name):
        return self.make_json(self.switch_map.getByQuery({'switch':switch_name}))

    def load_port(self, switch_name):
        return db.getDb('{}_port_map.json'.format(switch_name))

    def query_port(self, switch_name, port):
       self.qp = self.load_port(switch_name)
       return self.qp.getByQuery({'port':port})[0]

    def query_switch(self, switch_name):
        try:
            self.get_switch(switch_name)

        except IndexError:
            pass
        else:
            return self.get_switch(switch_name)
    
    def is_port_owned(self, switch_name, port):
        self.get_port = self.query_port(switch_name, port)
        if self.get_port['stats']['owner'] == None:
           return True
        else:return False
        
    def register_port(self, switch_name, port_name, owner, key):
        if not self.query_switch(switch_name) == None:
           if self.is_port_owned(switch_name, port_name):
               self.rps = self.query_switch(switch_name)
               if not owner in self.rps['clients']:
                   self.rps['clients'].append(owner)
                   self.rps['clientmap'][owner] = {}
                   self.rps['clientmap'][owner]['port'] = port_name
                   self.rps['portmap'][port_name] = {}
                   self.rps['portmap'][port_name] = owner
                   self.update_switch(switch_name, self.rps)
                   self.regport = self.query_port(switch_name, port_name)
                   self.regport['stats']['owner'] = owner
                   self.regport['info']['key'] = key
                   self.regport['info']['last-change'] = 'Port Registered'
                   self.regport['info']['registered-at'] = str(datetime.datetime.now())
                   self.update_port(switch_name, port_name, self.regport)
               
    def enable_port(self, switch_name, owner, key):
        if not self.query_switch(switch_name) == None:
            self.eps = self.query_switch(switch_name)
            self.ep_owner_port_name = self.eps['clientmap'][owner]['port']
            self.ep_owner_port = self.query_port(switch_name, self.ep_owner_port_name)
            if key == self.ep_owner_port['info']['key']:
                if self.ep_owner_port['stats']['state'] == False:
                    self.ep_owner_port['stats']['state'] = True
                    self.ep_owner_port['info']['last-change'] = 'Port enabled by {}'.format(owner)
                    self.ep_owner_port['stats']['enabled-on'] = str(datetime.datetime.now())
                    self.update_port(switch_name, self.ep_owner_port_name, self.ep_owner_port)
                                             
    def disable_port(self, switch_name, owner, key):
        if not self.query_switch(switch_name) == None:
            self.dps = self.query_switch(switch_name)
            self.dps_owner_portname = self.dps['clientmap'][owner]['port']
            self.dp_owner_port = self.query_port(switch_name, self.dps_owner_portname)
            if key == self.dp_owner_port['info']['key']:
                if self.dp_owner_port['stats']['state'] == True:
                    del self.dp_owner_port['stats']['enabled-on'] 
                    self.dp_owner_port['stats']['state'] = False
                    self.dp_owner_port['info']['last-change'] = 'Port disabled by {}'.format(owner)
                    self.dp_owner_port['stats']['disabled-on'] = str(datetime.datetime.now())
                    self.update_port(switch_name, self.dps_owner_portname, self.dp_owner_port)
                    
    def allow_port_access(self, switch_name, destination, owner, key):
        if not self.query_switch(switch_name) == None:
            self.apa = self.query_switch(switch_name)
            self.get_owner_portname_apa = self.apa['clientmap'][owner]['port']
            self.get_owner_port_apa = self.query_port(switch_name, self.get_owner_portname_apa)
            if key == self.get_owner_port_apa['info']['key']:
                if self.get_owner_port_apa['stats']['state'] == True:
                    if not destination in self.get_owner_port_apa['info']['access']:
                        self.get_owner_port_apa['info']['access'].append(destination)
                        self.get_owner_port_apa['info']['last-change'] = 'allowed {} access to self'.format(destination)
                        self.update_port(switch_name, self.get_owner_portname_apa, self.get_owner_port_apa)

    def add_port_group(self, switch_name, group, owner, key):
        if not self.query_switch(switch_name) == None:
            self.apgs = self.query_switch(switch_name)
            self.get_owner_portname_apg = self.apgs['clientmap'][owner]['port']
            self.get_owner_port_apg = self.query_port(switch_name, self.get_owner_portname_apg)
            if key == self.get_owner_port_apg['info']['key']:
                if self.get_owner_port_apg['stats']['state'] == True:
                    if self.get_owner_port_apg['stats']['group'] == None:
                        if not group == self.get_owner_port_apg['stats']['group']:
                            if not group in self.apgs['groupmap'].keys():
                                self.apgs['groupmap'][group] = []
                                self.apgs['groupmap'][group].append(owner)
                                self.get_owner_port_apg['stats']['group'] = group
                                self.update_switch(switch_name, self.apgs)
                                self.update_port(switch_name, self.get_owner_portname_apg, self.get_owner_port_apg)
                            else:
                                if self.get_owner_port_apg['stats']['group'] == None:
                                    if not owner in self.apgs['groupmap'][group]:
                                        self.apgs['groupmap'][group].append(owner)
                                        self.update_switch(switch_name, self.apgs)
                                        self.update_port(switch_name, self.get_owner_portname_apg, self.get_owner_port_apg)
                                        
                    self.old_group = self.get_owner_port_apg['stats']['group']
                    if not self.old_group == group:
                        if not group in self.apgs['groupmap'].keys():
                            self.old_group_count = len(self.apgs['groupmap'][self.old_group]) -1 
                            if self.old_group_count == 0:
                                del self.apgs['groupmap'][self.old_group]
                                self.apgs['groupmap'][group] = []
                                self.apgs['groupmap'][group].append(owner)
                                self.get_owner_port_apg['stats']['group'] = group
                                self.update_switch(switch_name, self.apgs)
                                self.update_port(switch_name, self.get_owner_portname_apg, self.get_owner_port_apg)
                            else:
                                self.apgs['groupmap'][self.old_group].remove(owner)
                                self.apgs['groupmap'][group] = []
                                self.apgs['groupmap'][group].append(owner)
                                self.get_owner_port_apg['stats']['group'] = group
                                self.update_switch(switch_name, self.apgs)
                                self.update_port(switch_name, self.get_owner_portname_apg, self.get_owner_port_apg)
                        else:
                            try:
                                self.old_group_count = len(self.apgs['groupmap'][self.old_group])-1
                            except KeyError:
                                self.get_owner_port_apg['stats']['group'] = group
                                self.update_port(switch_name, self.get_owner_portname_apg, self.get_owner_port_apg)
                            else:
                                if self.old_group_count == 0:
                                    del self.apgs['groupmap'][self.old_group]
                                    self.apgs['groupmap'][group].append(owner)
                                    self.get_owner_port_apg['stats']['group'] = group
                                    self.update_switch(switch_name, self.apgs)
                                    self.update_port(switch_name, self.get_owner_portname_apg, self.get_owner_port_apg)
                                else:
                                    self.apgs['groupmap'][self.old_group].remove(owner)
                                    self.apgs['groupmap'][group].append(owner)
                                    self.get_owner_port_apg['stats']['group'] = group
                                    self.update_switch(switch_name, self.apgs)
                                    self.update_port(switch_name, self.get_owner_portname_apg, self.get_owner_port_apg)        
                    else:
                        print('gmatch')

    def remove_group_manual(self, switch_name, group):
        if not self.query_switch(switch_name) == None:
            self.rgms = self.query_switch(switch_name)
            if group in self.rgms['groupmap'].keys():
                del self.rgms['groupmap'][group]
                self.update_switch(switch_name, self.rgms)
                                       
    def remove_port_group(self, switch_name, owner, key):
        if not self.query_switch(switch_name) == None:
           self.rpgs = self.query_switch(switch_name)
           self.get_owner_portname = self.sds['clientmap'][owner]['port']
           self.get_owner_port = self.query_port(switch_name, self.get_owner_portname)
           if key == self.get_owner_port['info']['key']:
               self.network = self.get_owner_port['stats']['group']
               self.get_owner_port['stats']['group'] = None
               self.get_owner_port['info']['last-change'] = '{} removed self from {} network'.format(owner, self.network)
               self.update_port(switch_name, self.get_owner_portname, self.get_owner_port)
           
    def revoke_port_access(self, switch_name, source, destination, owner, key):
        if not self.query_switch(switch_name) == None:
            if not self.is_port_owned(switch_name, source):
                self.rpa = self.query_port(switch_name, source)
                if self.rpa['stats']['state'] == True:
                    if owner == self.rpa['stats']['owner']:
                        if key == self.rpa['info']['key']:
                            if destination in self.rpa['info']['access']:
                                self.rpa['info']['access'].remove(destination)
                                self.rpa['info']['last-change'] = 'removed {} access to self'.format(destination)
                                self.update_port(switch_name, source, self.rpa)

    def ack(self, switch_name, message_id, owner, key):
        if not self.query_switch(switch_name) == None:
            self.acks = self.query_switch(switch_name)
            self.gopn = self.acks['clientmap'][owner]['port']
            self.gopn_obj = self.query_port(switch_name, self.gopn)
            if message_id in self.acks['ackmap'].keys():
                self.ack_entry = self.acks['ackmap'][message_id]
                if owner == self.ack_entry['ack-responder']:
                   if self.acks['ackmap'][message_id]['ack'] == False:
                      self.acks['ackmap'][message_id]['ack'] = True
                      self.acks['ackmap'][message_id]['ack-when'] = str(datetime.datetime.now())
                      self.update_switch(switch_name, self.acks)
                      
    def ack_confirm(self, switch_name, message_id, owner, key):
        if not self.query_switch(switch_name) == None:
            self.accs = self.query_switch(switch_name)
            self.acp = self.accs['clientmap'][owner]['port']
            self.acp_obj = self.query_port(switch_name, self.acp)
            if message_id in self.accs['ackmap'].keys():
                self.ack_entry = self.accs['ackmap'][message_id]
                if owner == self.ack_entry['ack-owner']:
                    del self.accs['ackmap'][message_id]
                    self.update_switch(switch_name, self.accs)

    def delete_acks(self, switch_name):
        if not self.query_switch(switch_name) == None:
            self.del_acks = self.query_switch(switch_name)
            self.del_acks['ackmap'] = {}
            self.update_switch(switch_name, self.del_acks)

    def send_data(self, switch_name, destination, owner, key, message, ack=False):
         if not self.query_switch(switch_name) == None:
            self.sds = self.query_switch(switch_name)
            if owner in self.sds['clients']:
                self.owner_port = self.sds['clientmap'][owner]['port']
                self.owner_port_obj = self.query_port(switch_name, self.owner_port)
                if key == self.owner_port_obj['info']['key']:
                    if destination in self.sds['clients']:
                       self.dest_port = self.sds['clientmap'][destination]['port']
                       self.dest_obj = self.query_port(switch_name, self.dest_port)
                       if self.owner_port_obj['stats']['group'] == None and self.dest_obj['stats']['group'] == None:
                           if self.owner_port in self.dest_obj['info']['access']:
                               self.dest_obj['data'].append(self.format_data(self.owner_port, message, ack))
                               self.dest_obj['stats']['rx'] = self.dest_obj['stats']['rx'] + 1
                               self.owner_port_obj['stats']['tx'] = self.owner_port_obj['stats']['tx'] + 1
                               self.dest_obj['stats']['rx'] = self.dest_obj['stats']['rx'] + 1
                               self.sds['stats']['tx'] = self.sds['stats']['tx'] + 1
                               self.sds['stats']['rx'] = self.sds['stats']['rx'] + 1
                               self.owner_port_obj['info']['last-change'] = 'Sent message to {}'.format(self.dest_obj['stats']['owner'])
                               self.dest_obj['info']['last-change'] = 'Got message from {}'.format(self.owner_port_obj['stats']['owner'])
                               self.update_switch(switch_name, self.sds)
                               self.update_port(switch_name, self.dest_port, self.dest_obj)
                               self.update_port(switch_name, self.owner_port, self.owner_port_obj)
                       else:
                           if not self.owner_port_obj['stats']['group'] == None:
                               if not self.dest_obj['stats']['group'] == None:
                                   if self.owner_port_obj['stats']['group'] == self.dest_obj['stats']['group']:
                                       self.dest_obj['data'].append(self.format_data(self.owner_port, message, ack))
                                       self.dest_obj['stats']['rx']  = self.dest_obj['stats']['rx'] + 1
                                       self.owner_port_obj['stats']['tx'] = self.owner_port_obj['stats']['tx'] + 1
                                       self.sds['stats']['tx'] = self.sds['stats']['tx'] + 1
                                       self.sds['stats']['rx'] = self.sds['stats']['rx'] + 1
                                       self.dest_obj['info']['last-change'] = 'Got message from {}'.format(self.owner_port_obj['stats']['owner'])
                                       self.owner_port_obj['info']['last-change'] = 'Sent message to {}'.format(self.dest_obj['stats']['owner'])
                                       self.update_switch(switch_name, self.sds)
                                       self.update_port(switch_name, self.owner_port, self.owner_port_obj)
                                       self.update_port(switch_name, self.dest_port, self.dest_obj)
                           
    def format_data(self, source, message, ack):
        self.data = {}
        self.id = secrets.token_hex(4)
        self.data[self.id] = {
            'source':self.owner_port_obj['stats']['owner'],
            'port':source,
            'data':message,
            'when':str(datetime.datetime.now())}
        if ack == True:
            if not self.id in self.sds['ackmap'].keys():
                self.sds['ackmap'][self.id] = {
                'ack':False,
                'ack-made':str(datetime.datetime.now()),
                'ack-when':None,
                'ack-owner':self.owner_port_obj['stats']['owner'],
                'ack-responder':self.dest_obj['stats']['owner']}
                self.update_switch('myswitch', self.sds)
                return self.data
        else:
            return self.data
                       
            
s = switch()
s.create_switch('myswitch', 4)
#s.check_switch_exist('myswitch')
#s.query_port('myswitch', 'port0')
#s.is_port_owned('myswitch', 'port0')
s.register_port('myswitch', 'port0', 'client1', 'mykey')
s.register_port('myswitch', 'port1', 'mylan', 'mykey')
s.register_port('myswitch', 'port2', 'mylanc', 'mykey')

s.enable_port('myswitch', 'client1', 'mykey')
s.enable_port('myswitch',  'xxx', 'mykey')
s.enable_port('myswitch',  'fff', 'mykey')

s.add_port_group('myswitch','mygroup', 'xxx', 'mykey')
s.add_port_group('myswitch','mygroup', 'xxx', 'mykey')

s.allow_port_access('myswitch',  'port1', 'client1', 'mykey')
s.allow_port_access('myswitch',  'port0', 'xxx', 'mykey')
s.allow_port_access('myswitch',  'port1', 'xxx', 'mykey')

#s.send_data('myswitch', 'client1', 'xxx', 'mykey', 'somedata')
#s.send_data('myswitch', 'client1', 'xxx', 'mykey', 'somedata233!!!!!!!!!')
s.send_data('myswitch', 'mylan', 'client1', 'mykey', 'somedata233!!!dsdadsadas!!!!!!', ack=False)

#s.ack('myswitch', '43817c85', 'xxx', 'mykey')
s.ack_confirm('myswitch', '43817c85', 'client1', 'mykey')
#s.delete_acks('myswitch')

#s.remove_port_group('myswitch', 'client1', 'mykey')
#s.add_port_group('myswitch', 'mygroup', 'client1', 'mykey')

#s.remove_group_manual('myswitch', 'o332')
#print(s.get_port_id('myswitch', 'port0'))
#print(s.get_switch_ports('myswitch'))
#print(s.get_switch_id('myswitchd='))
#print(s.show_switch('myswitch'))

