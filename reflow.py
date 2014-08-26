
import serial
import time
import ConfigParser

POSTS = ['temp', 'time', 'pwr']
PRES = ['pht', 'soak', 'dwell', 'reflow']

class ReflowController(object):
    
    def __init__(self, port='/dev/ttyUSB0', baud=9600, parity='N', stopbit=1,
                 bytesize=8, conf=None, pres=None, posts=None, to=.1):
        self._port = port
        self._baud = baud
        self._parity = parity
        self._stopbit = 1
        self._s = serial.Serial(port=port, baudrate=baud, bytesize=bytesize, 
                                parity=parity, stopbits=stopbit, timeout=to)
        if conf is None:
            self._conf = ConfigParser.SafeConfigParser()
        else:
            self._conf = conf
        if pres is None:
            self._pres = ['pht', 'soak', 'dwell', 'reflow']
        if posts is None:
            self._posts = ['temp', 'time', 'pwr']
        
    @classmethod
    def from_config(cls, path):
        conf = ConfigParser.SafeConfigParser()
        conf.read(path)
        port = conf.get('connection', 'port')
        return cls(port, conf=conf)
        
    def read_config(self, path):
        self._conf.read(path)
        
    def write_config(self, path):
        self._conf.write(path)
    
    def set_preheat_properties(self, temp=None, time=None, pwr=None):
        if temp is not None:
            self._conf.set('profile', 'phttemp', value=temp)
        if time is not None:
            self._conf.set('profile', 'phttime', value=time)
        if pwr is not None:
            self._conf.set('profile', 'phtpwr', value=pwr)

    def set_soak_properties(self, temp=None, time=None, pwr=None):
        if temp is not None:
            self._conf.set('profile', 'soaktemp', value=temp)
        if time is not None:
            self._conf.set('profile', 'soaktime', value=time)
        if pwr is not None:
            self._conf.set('profile', 'soakpwr', value=pwr)

    def set_reflow_properties(self, temp=None, time=None, pwr=None):
        if temp is not None:
            self._conf.set('profile', 'reflowtemp', value=temp)
        if time is not None:
            self._conf.set('profile', 'reflowtime', value=time)
        if pwr is not None:
            self._conf.set('profile', 'reflowpwr', value=pwr)

    def set_dwell_properties(self, temp=None, time=None, pwr=None):
        if temp is not None:
            self._conf.set('profile', 'dwelltemp', value=temp)
        if time is not None:
            self._conf.set('profile', 'dwelltime', value=time)
        if pwr is not None:
            self._conf.set('profile', 'dwellpwr', value=pwr)

    def set_liquidus(self, temp=None):
        if temp is not None:
            self._conf.set('profile', 'liquidus', value=temp)
            
    def set_offset(self, degs=None):
        if degs is not None:
            self._conf.set('offset', 'degps', value=degs)

    def send_profile_to_controller(self, section='profile'):
        for pre in self._pres:
            for post in self._posts:
                cmd = pre + post
                val = self._conf.get(section, cmd)
                self._send_cmd(cmd, val, check=True)

    def start(self):
        self._send_cmd('doStart')
        self._start_time = time.time()

    def stop(self):
        self._send_cmd('doStop')

    def close(self):
        self._s.close()
        
    def open(self):
        self._s.open()

    def del_conn(self):
        del self._s
        
    def get_temp_and_time(self):
        tempstring = self._send_cmd('tempshow').strip()
        print tempstring
        temp = int(tempstring[-5:-1])
        secs = int(round(time.time() - self._start_time))
        return secs, temp

    def get_temp_and_time_encoded(self):
        tempstring = self._send_cmd('tempshow')
        secs, whoknows, temp = tempstring.split(',')
        secs = int(secs)
        temp = int(temp[:-1])
        return secs, temp

    def get_profile(self):
        xs = [0]
        ys = [int(self._conf.get('profile', 'starttemp'))]
        labels = []
        for i, pre in enumerate(self._pres):
            labels.append(pre)
            dt = int(self._conf.get('profile', pre+'time'))
            temp = int(self._conf.get('profile', pre+'temp'))
            xs.append(xs[i] + dt)
            ys.append(temp)
        return xs, ys, labels 

    def _send_cmd(self, cmd, val=None, check=False):
        if val is None:
            cmdstring = cmd + '\n'
        else:
            cmdstring = cmd + ' ' + str(val) + '\n'
        self._s.write(cmdstring)
        out = self._s.readall()
        if check:
            checkstring = cmd + '\n'
            self._s.write(checkstring)
            print self._s.readall()
            print cmd, val
        return out
