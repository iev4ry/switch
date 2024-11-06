from pathlib import Path
from pysondb import db
import datetime
import secrets
import json
import os


''' --SWITCH--[DRAFT]
 *** This code may not be the most optimized at this stage ***
 [Author] *33
 
'''

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

    def add_switch_client(self, client, data):
        try:
            if not client in data['clients']:
                data['clients'].append(client)
                
        except TypeError:
            pass
        else:
            return data

    def change_key(self, data, new_key):
        try:
            data['info']['key'] = new_key

        except TypeError:
            print('cannot change key')
        else:
            return data
            

    def enable_port(self, data):
        try:
            if data['stats']['state'] == False:
                data['stats']['state'] = True
        except TypeError:
            print('cannot enable port')
        else:
            return data

    def disable_port(self, data):
        try:
            if data['stats']['state'] == True:
                data['stats']['state'] = False
        except TypeError:
            print('cannot disable port')
        else:
            return data

    def set_port_owner(self, owner, key, data, client_list):
        try:
            if owner not in client_list:
                data['stats']['owner'] = owner
                data['info']['key'] = key
                data['info']['registered'] = str(datetime.datetime.now())
        except TypeError:
            print('port invalid')
            return None
        else:
            return data

    def set_port_description(self, data, description):
        try:
            data['info']['description'] = description

        except TypeError:
            print('Cannot set des')

        else:
            return data

    def set_port_group(self, switch_name, group, data, owner, sdata):
        try:
            self.old_group = data['stats']['group']
            self.new_group = group
            if data['stats']['group'] == None:
                data['stats']['group'] = group
                self.add_switch_group(switch_name, group, self.get_switch(switch_name), owner)
                
            else:
                if data['stats']['group'] == group:
                    pass #when group is the same just ignore the request to set a portgroup 
                else:
                    self.old_group = data['stats']['group']
                    self.new_group = group
                    if owner in sdata['groupmap'][self.old_group]['members']:
                       if len(sdata['groupmap'][self.old_group]['members']) - 1 == 0:
                           del sdata['groupmap'][self.old_group]
                           self.add_switch_group(switch_name, self.new_group, sdata, owner)
                           data['stats']['group'] = self.new_group
                           print('ok')
                       else:
                           print('looo')
                           sdata['groupmap'][self.old_group]['members'].remove(owner)
                           self.add_switch_group(switch_name, self.new_group, sdata, owner)
                           data['stats']['group'] = self.new_group
        except KeyError as e:
            print(sdata)
            #self.add_switch_group(switch_name, self.new_group, sdata, owner)
                    

    def del_user_from_switch_group(self, switch_name, group, data, user):
        if user in data['groupmap'][group]['members']:
            data['groupmap'][group]['members'].remove(user)
            self.update_switch(switch_name, data)

    def add_switch_group(self, switch_name, group, data, owner):
        if not group in data['groupmap'].keys():
           data['groupmap'][group] = {
               'members':[owner]}
           self.update_switch(switch_name, data)
        else:
            if not owner in data['groupmap'][group]['members']:
                data['groupmap'][group]['members'].append(owner)
                self.update_switch(switch_name, data)
                return data

    def del_switch_group(self, switch_name, group, data):
        if group in data['groupmap'].keys():
            del data['groupmap'][group]
            self.update_switch(switch_name, data)   
                
    def set_port_last_change(self, change, data):
        try:
            data['info']['last-change'] = change
        except TypeError:
            print('cannot change port status')
        else:
            return data

    def add_port_access(self, to_allow_access, data):
        try:
            if not to_allow_access in data['info']['access']:
                data['info']['access'].append(to_allow_access)
        except TypeError:
            pass
        else:
            return data
        
    def remove_port_access(self, to_remove_access, data):
        try:
            if to_remove_access in data['info']['access']:
                data['info']['access'].remove(to_remove_access)

        except TypeError:
            pass
        else:
            return data
                      
    def register_port(self, switch_name, owner, key, port):
        self.rps = self.get_switch(switch_name)
        self.port_data = self.get_port(switch_name, port)
        if self.port_data['stats']['owner'] == None:
            if not self.set_port_owner(owner, key, self.port_data, self.rps['clients']) == None:
                self.set_port_last_change('{} registered to self'.format(owner), self.port_data)
                self.rps['clientmap'][owner] = {}
                self.rps['clientmap'][owner] = {
                    'port':port}
                self.add_switch_client(owner, self.rps)
                self.update_switch(switch_name, self.rps)
                self.update_port(switch_name, port, self.port_data)

    def send_data(self, switch_name, owner, key, destination, data, ack=False):
        self.sd_switch = self.get_switch(switch_name)
        if not self.sd_switch == None:
            self.sd_owner_port = self.get_port(switch_name, self.sd_switch['clientmap'][owner]['port'])
            if self.auth_check(self.sd_owner_port, owner, key):
                if not self.sd_owner_port['stats']['state'] == False:
                    self.destination_owner_port = self.get_port(switch_name, self.sd_switch['clientmap'][destination]['port'])
                    if not self.destination_owner_port['stats']['state'] == False:
                        self.owner_group = self.sd_owner_port['stats']['group']
                        self.destination_group = self.destination_owner_port['stats']['group']
                        if self.owner_group == self.destination_group:
                            if self.owner_group == None and self.destination_group == None:
                                if self.sd_owner_port['stats']['owner'] in self.destination_owner_port['info']['access']:
                                    if ack:
                                        self.dest_port_data = self.format_send_data(owner, destination, data)
                                        self.ack(switch_name, self.sd_switch, self.dest_port_data['id'], owner, destination)
                                        self.destination_owner_port['data'].append(self.dest_port_data)
                                        self.update_port(switch_name, self.destination_owner_port['port'], self.destination_owner_port)
                                        self.update_switch(switch_name, self.sd_switch)
                                    else:
                                        self.dest_port_data = self.format_send_data(owner, destination, data)
                                        self.destination_owner_port['data'].append(self.dest_port_data)
                                        self.update_port(switch_name, self.destination_owner_port['port'], self.destination_owner_port)
                        else:
                            print('mistmatch', self.owner_group, self.destination_group) # when mismatch logg
                    else:
                        print('dest port is not enabled') 

    def format_send_data(self, owner, destination, data):
        return {
            'id':secrets.token_urlsafe(4),
            'source':owner,
            'data':data,
            'created':str(datetime.datetime.now())}
        
    def auth_check(self, data, owner, key):
        try:
            if data['info']['key'] == key:
                return True
        except TypeError:
            return False

    def client_to_port_lookup(self, switch_name, owner):
        try:
            self.ctp = self.get_switch(switch_name)
            if owner in self.ctp['clientmap'].keys():
                return self.ctp
        except TypeError:
           return None

    def ack(self, switch_name, switch_data, message_id, owner, destination):
        if not message_id in switch_data['ackmap'].keys():
            switch_data['ackmap'][message_id] = {
                'ack':False,
                'ack-owner':owner,
                'ack-responder':destination,
                'ack-when-owner':str(datetime.datetime.now())}
            return switch_data

    def ack_confirm(self, switch_data, message_id, owner, key):
        if message_id in switch_data['ackmap'].keys():
            print('great')

    def del_all_acks(self, switch_data):
        switch_data['ackmap'] = {}
        return switch_data
        
    def action_change_key(self, switch_name, owner, old_key, new_key):
        self.achnk = self.client_to_port_lookup(switch_name, owner)
        if not self.achnk == None:
            self.achnk_data = self.get_port(switch_name, self.achnk['clientmap'][owner]['port'])
            if self.auth_check(self.achnk_data, owner, old_key):
                if not old_key == new_key:
                    self.change_key(self.achnk_data, new_key)
                    self.set_port_last_change('{} updated key'.format(owner), self.achnk_data)
                    self.update_port(switch_name, self.achnk['clientmap'][owner]['port'], self.achnk_data)

    def action_set_port_description(self, switch_name, description, owner, key):
       self.asd = self.client_to_port_lookup(switch_name, owner)
       if not self.asd == None:
           self.asd_data = self.get_port(switch_name, self.asd['clientmap'][owner]['port'])
           if self.auth_check(self.asd_data, owner, key):
               self.set_port_description(self.asd_data, description)
               self.set_port_last_change('{} updated description'.format(owner), self.asd_data)
               self.update_port(switch_name, self.asd['clientmap'][owner]['port'], self.asd_data)
               
    def action_set_port_group(self, switch_name, group, user, key):
            self.plookup = self.client_to_port_lookup(switch_name, user)
            if not self.plookup == None:
                self.pdata = self.get_port(switch_name, self.plookup['clientmap'][user]['port'])
                if self.auth_check(self.pdata, user, key):
                    self.set_port_group(switch_name, group, self.pdata, user, self.plookup)
                    self.set_port_last_change('{} joined group --> [{}]'.format(user, group), self.pdata)
                    self.update_port(switch_name, self.plookup['clientmap'][user]['port'], self.pdata)
                    
    def action_remove_from_group(self, switch_name, group, user, key):
        self.arf = self.client_to_port_lookup(switch_name, user)
        if not self.arf == None:
            self.arf_data = self.get_port(switch_name, self.arf['clientmap'][user]['port'])
            if self.auth_check(self.arf_data, user, key):
                if not self.arf_data['stats']['group'] == None:
                    self.del_user_from_switch_group(switch_name, group, self.arf, user)
                    self.arf_data['stats']['group'] = None
                    self.set_port_last_change('{} left group --> [{}]'.format(user, group), self.arf_data)
                    self.update_port(switch_name, self.arf['clientmap'][user]['port'], self.arf_data)

    def action_add_port_access(self, switch_name, user, owner, key):
        self.aap = self.client_to_port_lookup(switch_name, owner)
        if not self.aap == None:
            self.aap_data = self.get_port(switch_name, self.aap['clientmap'][owner]['port'])
            if self.auth_check(self.aap_data, user, key):
                if self.aap_data['stats']['group'] == None:
                    if not user in self.aap_data['info']['access']:
                        self.add_port_access(user, self.aap_data)
                        self.set_port_last_change('{} allowed {} access'.format(owner, user), self.aap_data)
                        self.update_port(switch_name, self.aap['clientmap'][owner]['port'], self.aap_data)

    def action_remove_port_access(self, switch_name, user, owner, key):
         self.arp = self.client_to_port_lookup(switch_name, owner)
         if not self.arp == None:
             self.arp_data = self.get_port(switch_name, self.arp['clientmap'][owner]['port'])
             if self.auth_check(self.arp_data, user, key):
                 if self.arp_data['stats']['group'] == None:
                     self.remove_port_access(user, self.arp_data)
                     self.set_port_last_change('{} removed {} from access '.format(owner, user), self.arp_data)
                     self.update_port(switch_name, self.arp['clientmap'][owner]['port'], self.arp_data)

    def action_enable_port(self, switch_name, owner, key):
        self.aep = self.client_to_port_lookup(switch_name, owner)
        if not self.aep == None:
            self.aep_data = self.get_port(switch_name, self.aep['clientmap'][owner]['port'])
            if self.auth_check(self.aep_data, owner, key):
                if self.aep_data['stats']['state'] == False:
                    self.enable_port(self.aep_data)
                    self.set_port_last_change('{} enabled port'.format(owner), self.aep_data)
                    self.update_port(switch_name, self.aep['clientmap'][owner]['port'], self.aep_data)

    def action_disable_port(self, switch_name, owner, key):
        self.adp = self.client_to_port_lookup(switch_name, owner)
        if not self.adp == None:
            self.adp_data = self.get_port(switch_name, self.adp['clientmap'][owner]['port'])
            if self.auth_check(self.adp_data, owner, key):
                if self.adp_data['stats']['state'] == True:
                    self.disable_port(self.adp_data)
                    self.set_port_last_change('{} disabled port'.format(owner), self.adp_data)
                    self.update_port(switch_name, self.adp['clientmap'][owner]['port'], self.adp_data)

    def action_del_acks(self, switch_name):
        self.update_switch(switch_name, self.del_all_acks(self.get_switch(switch_name)))

    def action_ack_confirm(self, switch_name, message_id, owner, key):
        self.aac = self.client_to_port_lookup(switch_name, owner)
        if not self.aac == None:
            self.aac_port_data = self.get_port(switch_name, self.aac['clientmap'][owner]['port'])
            if self.auth_check(self.aac_port_data, owner, key):
                if message_id in self.aac['ackmap'].keys():
                    if self.aac['ackmap'][message_id]['ack-responder'] == owner:
                        if self.aac['ackmap'][message_id]['ack'] == False:
                            self.aac['ackmap'][message_id]['ack'] = True
                            self.aac['ackmap'][message_id]['ack-when-client'] = str(datetime.datetime.now())
                            self.update_switch(switch_name, self.aac)

    def action_del_data(self, switch_name, owner, key):
        self.add = self.client_to_port_lookup(switch_name, owner)
        if not self.add == None:
            self.add_port_data = self.get_port(switch_name, self.add['clientmap'][owner]['port'])
            if self.auth_check(self.add_port_data, owner, key):
                self.add_port_data['data'] = {}
                if not len(self.add_port_data) == 0:
                    self.add_port_data['data'] = {}
                    self.update_port(switch_name, self.add_port_data['port'], self.add_port_data)
                                             
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
                        'last-change':'SYSTEM',
                        'description':None,},
                    'data':[]})
            self.switch.add(self.switch_config)
            
                  
    
s = switch()
s.make_switch('123df')
print(s.get_port_id('123d', 'port5'))
print(s.get_switch_id('123d'))
print(s.load_port('123df'))
#s.update_port('123df', 'port3',{'info':{'owner':'me'}})
s.register_port('123df', 'tom', 'mykey', 'port5')
s.register_port('123df', 'tom11', 'mykey', 'port11')
s.register_port('123df', 'tom3', 'mykey4000', 'port6')
s.register_port('123df', 'tom12', 'mykey4000', 'port12')
#s.action_set_port_group('123df','mygroup3009', 'tom', 'mykey')
#s.action_set_port_group('123df', 'mygroup3009', 'tom3', 'mykey4000')
#s.action_change_key('123df', 'tom', 'mynewkey', 'mynewkey900')
#s.action_enable_port('123df', 'tom', 'mykey')
#s.action_enable_port('123df', 'tom3', 'mykey4000')
s.action_set_port_description('123df', 'this port is from api.fastbank', 'tom', 'mykey')
#s.action_remove_from_group('123df', 'mygroup20', 'tom', 'mykey')
#s.action_add_port_access('123df', 'tom', 'tom3', 'mykey4000')
#s.action_remove_port_access('123df', 'tom3', 'tom', 'mykey')
#s.send_data('123df', 'tom', 'mykey', 'tom3', 'mydata', ack=True)
#s.action_del_acks('123df')

s.action_ack_confirm('123df', 'vnDg9w', 'tom3', 'mykey4000')

s.action_del_data('123df', 'tom3', 'mykey4000')


#print(s.get_port('123d', 'port0'))
#print(s.get_switch('123d'))
#print(s.make_db_path('123d', 'switch'))
