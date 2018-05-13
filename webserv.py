#!/usr/bin/python3

import http.server
from socketserver import ThreadingMixIn
from queue import Queue as simplequeue
import errno
from urllib.parse import urlparse, parse_qs
import argparse
import json, time, sys

import utils, config

class pywebhandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """
        There are just a few basic paths that this uses (the part after the host:port and before the '?'):
            <empty>: uses the 'defaultgetpage' entry in the server parameters
            'runm' : 
        """
        pr = urlparse(self.path)
        pf = pr.path.split('/')
        pname=pf[-1]
        if pname in self.server.mypyconf['getpaths']:
            pathdef=self.server.mypyconf['getpaths'][pname]
            if 'static'==pathdef.get('pagetype', None):
                staticfilename=server.mypyconf['servefrom'][pathdef.get('folder','static')]/pathdef.get('pagefile', 'nopage')
                if staticfilename.is_file():
                    sfx=staticfilename.suffix
                    if sfx in sfxlookup:
                        self.send_response(200)
                        self.send_header(*sfxlookup[sfx])
                        self.end_headers()
                        with staticfilename.open('rb') as sfile:
                            self.wfile.write(sfile.read())
                        if 'log' in pathdef:
                            print('pywebhandler.do_GET file {} sent in response to {} using headers {}.'.format(
                                    str(staticfilename), pname, str(sfxlookup[sfx])) )
                        print(pathdef)
                    else:
                        print("pywebhandler.do_GET doesn't know how to handle file suffix", sfx)
                        self.send_error(500,'page suffix unknown' % pname)
                else:
                    print('pywebhandler.do_GET pagefile {} does not refer to a file'.format(str(staticfilename)))
                    self.send_error(500,'page %s not found in server pages' % pinfo)
            elif 'eventstream'==pathdef.get('pagetype', None):
                if 'obid' in pathdef:
                    obid=pathdef['obid']
                    if not obid in self.server.mypyobjects:
                        #try and setup the object
                        if obid in self.server.mypyconf['obdefs']:
                            if 'ondemand' in self.server.mypyconf['obdefs'][obid]:
                                obdef=self.server.mypyconf['obdefs'][obid]['ondemand']
                                params = parse_qs(pr.query) if pr.query else {}
                                params = {k:v if len(v)>1 else v[0] for k, v in  params.items()}
                                params.update(obdef)
                                print(params)
                                self.server.mypyobjects[obid]=utils.makeClassInstance(**params)
                            else:
                                print("no ondemand info for object", obid)
                                self.send_error(500,'object setup error - object info for %s not found' % pname)
                        else:
                            print("failed to find object definition for % in config['obdefs']" % obid)
                            self.send_error(500,'object setup error - object for %s not found' % pname)
                    if 'generator' == pathdef['streamtype']:
                        tickinterval=pathdef['period']
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
                        self.end_headers()
                        running=True
                        while running:
                            datats=json.dumps(next(self.server.mypyobjects[obid]))
                            try:
                                self.wfile.write(('data: %s\n\n' % datats).encode('utf-8'))
                            except Exception as e:
                                running=False
                                if e.errno!=errno.EPIPE:
                                    raise
                            time.sleep(tickinterval)
                    else:
                        send_error(500, 'pywebhandler.do_GET eventstream unknown streamtype', pathdef.get('streamtype', None))
                else:
                    print('missing object id in path %s with pathdef %s' % (pname, str(pathdef)))
                    self.send_error(500,'stream setup error - stream %s not found' % pname)
            else:
                print('pywebhandler.do_GET unsupported pagetype in path definition', pathdef)
                self.send_error(500,'something went a bit wrong!')
        else:
            print('pywebhandler.do_GET bounced', pf)
            self.send_error(404,'unknown page {} requested'.format(pname))

        return

def pistatus():
    """
    Uses pistatus to set up a generator that yields up the cpu temp and overall cpu busy time.
    """
    m=utils.systeminfo(('busy','cputemp'))
    return m

sfxlookup={
    '.css' :('Content-Type', 'text/css; charset=utf-8'),
    '.html':('Content-Type', 'text/html; charset=utf-8'),
    '.js'  :('Content-Type', 'text/javascript; charset=utf-8'),
    '.ico' :('Content-Type', 'image/x-icon'),
}

class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """
    Handle requests in a separate thread.
    
    This allows multiple pages to be in progress, and in particular it allows the webserver to send out an event stream for extended periods
    without blocking other requests.
    
    Also it allows queues of status messages to be setup which are served up as event streams on request. No session control etc. here though
    """
    def __init__(self, *args,  mypyconf, **kwargs):
        super().__init__(*args, **kwargs)
        self.mypyconf=mypyconf
        self.mypyobjects={}
        if 'obdefs' in self.mypyconf:
            descs=[]
            for oname, odef in self.mypyconf['obdefs'].items():
                if 'setup' in odef:
                    setupparams=odef['setup']
                    if 'webserver' in setupparams:
                        setupparams=setupparams.copy()
                        setupparams['webserver']=self
                    self.mypyobjects[oname]=utils.makeClassInstance(**setupparams)
                    descs.append('%s:(%s)' %(oname, type(self.mypyobjects[oname]).__name__))
                else:
                    assert 'ondemand' in odef
                    descs.append('%s will be setup on demand' % oname)
            print('added objects', ', '.join(descs))
        else:
            print('no associated objects created')


#        self.statusqueues={}

#    def queueupdate(self, qname, update):
#        if qname in self.statusqueues:
#            sq=self.statusqueues[qname]
#        else:
#            sq=simplequeue()
#            self.statusqueues[qname] = sq
#        sq.put(update)
#        while sq.qsize() > 5:
#            print('Q %s overflow' % qname)
#            sq.get()

if __name__ == '__main__':
    from pathlib import Path
    serverconf=config.serverdefaults.copy()                 # fetch the default server config
    clparse = argparse.ArgumentParser(description='runs a simple webserver.')
    clparse.add_argument('-c', '--config', help='path to optional configuration file.')
    args=clparse.parse_args()
    if not args.config is None:
        configpath=Path(args.config)
        if not configpath.with_suffix('.py').is_file():
            sys.exit('cannot find configuration file ' + str(configpath.with_suffix('.py')))
        incwd=str(configpath.parent) == '.'
        if not incwd:
            sys.path.insert(1,str(configpath.parent))
        try:
            configmod=importlib.import_module(configpath.stem)
        except:
            print('=================================:')
            print('failed to load server config file', str(configpath))
            print('=================================:')
            raise
        serverconf.update(configmod)
    servefolds={}
    for k, foldername in serverconf['servefrom'].items():
        p=Path(foldername)
        if p.is_dir():
            servefolds[k]=p.absolute()
        else:
            sys.exit('the servefrom directory in server config file is not a directory or does not exist: %s' % str(p.absolute()))
    if not 'static' in servefolds:
        print('================================= WARNING:')
        print("default (static) not defined in servefrom entries")
        print('=================================:')
    serverconf['servefrom']=servefolds
    ips=utils.findMyIp()
    if len(ips)==0:
        print('starting webserver on internal IP only (no external IP addresses found), port %d' % (serverconf['port']))
    elif len(ips)==1:
        print('Starting webserver on %s:%d' % (ips[0], serverconf['port']))
    else:
        print('Starting webserver on multiple ip addresses (%s), port:%d' % (str(ips), server['port']))
    server = ThreadedHTTPServer(('',serverconf['port']),pywebhandler, mypyconf=serverconf)
#    server.mypyconf=serverconf
    try:
        server.serve_forever()
        print('webserver shut down')
    except KeyboardInterrupt:
        server.socket.close()
