import datetime
import time 


''' Here we track the rate of a users actions throughout the entire api.''' 


class rate:
    def __init__(self):
        self.rate_db = {}

    def submit(self, owner, reason):
        if not owner in self.rate_db.keys():
            self.rate_db[owner] = {
                'stamp':datetime.datetime.now().timestamp(),
                'current-rate':0,
                'history':[],
                'count':1, }

            self.history_entry = {
                'reason':reason,
                'when':str(datetime.datetime.now())}
            self.rate_db[owner]['history'].append(self.history_entry)
            return True
            
        else:
            self.current_timestamp = datetime.datetime.now().timestamp()
            self.rate_db[owner]['count'] = self.rate_db[owner]['count']=+1
            self.rate = self.current_timestamp - self.rate_db[owner]['stamp']
            self.rate_db[owner]['stamp'] = self.current_timestamp
            self.rate_db[owner]['current-rate'] = round(self.rate, 1)
            if self.rate >= 2:
                return True 
            else:
                return False
                
