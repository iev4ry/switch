import datetime
import time
import json

'''
    Here we track the rate of a users actions throughout the entire API.
    Each message a user sends is used for tracking frequency and to note the call
    that was made. 
''' 


class rate:
    def __init__(self):
        self.rate_db = {}


    def make_history_entry(self, reason, owner):
        self.entry = {
            'reason':reason,
            'when':str(datetime.datetime.now())}
        self.rate_db[owner]['history'].append(self.entry)
        return self.entry
        
    def submit(self, owner, reason):
        if not owner in self.rate_db.keys():
            self.rate_db[owner] = {
                'stamp':datetime.datetime.now().timestamp(),
                'current-rate':0,
                'violation-count':0,
                'history':[],
                'count':1,
                'ban-status':False,
                'violations':[],}
            self.make_history_entry(reason, owner)
            return True
        else:
            if self.rate_db[owner]['ban-status'] == False:
                self.current_timestamp = datetime.datetime.now().timestamp()
                self.rate_db[owner]['count'] = self.rate_db[owner]['count'] + 1
                self.rate = self.current_timestamp - self.rate_db[owner]['stamp']
                self.rate_db[owner]['stamp'] = self.current_timestamp
                self.rate_db[owner]['current-rate'] = round(self.rate, 1)
                if self.rate >= 2:
                    self.make_history_entry(reason, owner)
                    return True 
                else:
                    self.rate = datetime.datetime.now().timestamp() - self.rate_db[owner]['stamp'] 
                    self.rate_db[owner]['count'] = self.rate_db[owner]['count'] + 1
                    self.rate_db[owner]['violation-count']= self.rate_db[owner]['violation-count']+1
                    self.rate_db[owner]['violations'].append(self.rate_db[owner]['stamp'])
                    self.rate_db[owner]['violations'] = [ts for ts in self.rate_db[owner]['violations'] if self.rate_db[owner]['stamp'] - ts <=30]
                    self.make_history_entry(reason, owner)
                    if len(self.rate_db[owner]['violations']) >= 3:
                        self.rate_db[owner]['ban-status'] = True
                        print('violated threshold')
                        return False
                    else:
                        return True
            else:
                if self.rate_db[owner]['ban-status'] == True:
                    print('user is banned')
                    return False
               
        
        
myrate = rate()
myrate.submit('myuser', 'doing.something.here')
time.sleep(4)
myrate.submit('myuser', 'doing.something.here')
time.sleep(3)
myrate.submit('myuser', 'doing.something.here')
myrate.submit('myuser', 'doing.something.here')

'''
myrate.submit('myuser', 'doing.something.here')
myrate.submit('myuser', 'doing.something.here')
myrate.submit('myuser3', 'doing.something.here')
myrate.submit('myuser4', 'doing.something.here')
myrate.submit('myuser', 'doing.something.here')
myrate.submit('myuser', 'doing.something.here')
myrate.submit('myuser', 'doing.something.here')
'''
print(json.dumps(myrate.rate_db, indent=4))



