import datetime

class Temperature:
    def __init__(self, zone, actual, target=None):
        self.zone = zone
        self.actual = actual
        self.target = target
    
    def __repr__(self):
       cur_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
       return (cur_date + " : " + str(self.zone) + " " + str(self.actual) + " set (" + str(self.target) + ")")
