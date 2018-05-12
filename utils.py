#!/usr/bin/python3
"""
basic functions to check on various aspects of machine state
"""
import os, time, socket


def findMyIp():
    """
    A noddy function to find local machines' IP address for simple cases....
    based on info from https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    
    returns an array of IP addresses (in simple / most cases there will only be one entry)
    """
    return([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or 
            [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]
          )

def _tempfield(tempfilename):
    with open(tempfilename) as cput: #'/sys/class/thermal/thermal_zone0/temp'
        return int(cput.readline().strip())/1000

cpustatfields={
    'user'    : ( 'procstat' , 0),
    'nice'    : ( 'procstat' , 1),
    'system'  : ( 'procstat' , 2),
    'idle'    : ( 'procstat' , 3),
    'iowait'  : ( 'procstat' , 4),
    'irq'     : ( 'procstat' , 5),
    'softirq' : ( 'procstat' , 6),
    'busy'    : ( 'procstat' , 99),
    'cputemp' : ( 'tempfile', '/sys/class/thermal/thermal_zone0/temp'),
}

class systeminfo():
    """
    A class to provide an ongoing stream of values for various system values such as cpu utilization and temperatures.
    
    Once setup use next(instance) to retrieve the new / current values.
    
    fields: The particular info required. If a single string then this value is returned on each call of "next".
            if a list of strings then a dict of values (with the strings as keys) are returned on each call of next.
    
    yields: if fields was a string, then the single current value (typically a float)
             if fields was a list of strings, then a dict with the current values.
             
    fields can be one or more of:
        user        cpu utilisation of normal processes executing in user mode in the interval since last call (float in range 0 - 1)
        nice        cpu utilisation of niced processes executing in user mode in the interval since last call (float in range 0 - 1)
        system      cpu utilisation of processes executing in kernel mode in the interval since last call (float in range 0 - 1)
        idle        cpu utilisation twiddling thumbs in the interval since last call (float in range 0 - 1)
        iowait      cpu utilisation waiting for I/O to complete in the interval since last call (float in range 0 - 1)
        irq         cpu utilisation servicing interrupts in the interval since last call (float in range 0 - 1)
        softirq     cpu utilisation servicing softirqs in the interval since last call (float in range 0 - 1)
        busy        busy cpu time in the interval since last call (float in range 0 - 1) - essentially this is 1-idle
        cputemp     the current cpu temerature in centigrade
    """
    def __init__(self,fields):
        """
        """
        self.proclist=[]    # the list of things we'll call 
        self.cpustatlist=[] # the list of specifically /proc/stat fields we want
        if isinstance(fields, str):
            self.addfield(fields)
            self.resdict=None
        else:
            for f in fields:
                self.addfield(f)
            self.resdict= {f:0 for f in fields}
        if self.cpustatlist:
            self.cpucount=0
            with open('/proc/stat') as cpuinf:
                lix=cpuinf.readline()
                while not lix.startswith('intr'):
                    if lix.startswith('cpu '):
                        li=lix
                    elif lix.startswith('cpu'):
                        self.cpucount+=1
                    lix=cpuinf.readline()
            self.newprocstats=[int(e) for e in li.rstrip().split(' ')[1:] if e != '']
            self.newproctime=time.time()
            self.jiffy = os.sysconf(os.sysconf_names['SC_CLK_TCK'])

    def addfield(self,field):
        assert field in cpustatfields, 'unrecognized fields param <%s>' % field
        procinf=cpustatfields[field]
        procname=procinf[0]
        if procname=='procstat':
            self.cpustatlist.append(field)
            self.proclist.append((self.getprocfield, (procinf[1],),field))
        elif procname=='tempfile':
            self.proclist.append((_tempfield,(procinf[1],),field))
        else:
            x=17/0

    def __next__(self):
        if self.cpustatlist:
            with open('/proc/stat') as cpuinf:
                li=cpuinf.readline()
                while not li.startswith('cpu '):
                    li=cpuinf.readline()
            self.prevprocstats=self.newprocstats
            now=time.time()
            self.elapsed=now-self.newproctime
            self.newproctime=now
            self.newprocstats=[int(e) for e in li.rstrip().split(' ')[1:] if e != '']
        if self.resdict is None:
            return self.proclist[0][0](*self.proclist[0][1])
        else:
            for pl in self.proclist:
                self.resdict[pl[2]] = pl[0](*pl[1])
            return self.resdict

    def getprocfield(self, index):
        useind=3 if index > 20 else index
        increment=self.newprocstats[useind]-self.prevprocstats[useind]
        val=increment/self.elapsed/self.jiffy/self.cpucount
        return val if index <=20 else 1-val
