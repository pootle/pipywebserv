#!/usr/bin/python3

import http.server
from socketserver import ThreadingMixIn
from queue import Queue as simplequeue
import errno
from urllib.parse import urlparse, parse_qs

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
                staticfilename=server.mypyconf['servefrom']/pathdef.get('pagefile', 'nopage')
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
                params = parse_qs(pr.query) if pr.query else {}
                if 's' in params and len(params['s'])==1:
                    streamparams=pathdef.get('streams',{}).get(params['s'][0],{})
                    if 'modfunc' in streamparams:
                        f=sys.modules[__name__].__dict__.get(streamparams['modfunc'], None)
                    elif 'servfunc' in streamparams:
                        f=getattr(self.server, streamparams['servfunc'], None)
                        if not f is None and not callable(f):
                            f=None
                    else:
                        print('where is the stream function? in', streamparams)
                        send_error(500,'pywebhandler.do_GET unable to identify streaming function')
                    if callable(f):
                        if 'generator'==streamparams.get('streamtype', None):
                            genr=f()
                            tickinterval=streamparams['period']
                            self.send_response(200)
                            self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
                            self.end_headers()
                            running=True
                            while running:
                                datats=json.dumps(next(genr))
                                try:
                                    self.wfile.write(('data: %s\n\n' % datats).encode('utf-8'))
                                except Exception as e:
                                    running=False
                                    if e.errno!=errno.EPIPE:
                                        raise
                                time.sleep(tickinterval)
                        else:
                            send_error(500, 'pywebhandler.do_GET eventstream unknown streamtype', streamparams.get('streamtype', None))
                    else:
                        self.send_error(500,'pywebhandler.do_GET eventstream no function', f)
                else:
                    print('pywebhandler.do_GET eventstream request did not include single stream id ("s")', (str(params['s'] if 's' in params else '<none>')))
                    self.send_error(400,'s not present or not single valued')
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statusqueues={}

    def queueupdate(self, qname, update):
        if qname in self.statusqueues:
            sq=self.statusqueues[qname]
        else:
            sq=simplequeue()
            self.statusqueues[qname] = sq
        sq.put(update)
        while sq.qsize() > 5:
            print('Q %s overflow' % qname)
            sq.get()

if __name__ == '__main__':
    from pathlib import Path
    serverconf=config.serverdefaults.copy()
    p=Path(serverconf['servefrom'])
    if p.is_dir():
        serverconf['servefrom']=p.absolute()
    else:
        sys.exit('the servefrom directory in server config file is not a directory or does not exist: %s' % str(p.absolute()))
    ips=utils.findMyIp()
    if len(ips)==0:
        print('starting webserver on internal IP only (no external IP addresses found), port %d' % (serverconf['port']))
    elif len(ips)==1:
        print('Starting webserver on %s:%d' % (ips[0], serverconf['port']))
    else:
        print('Starting webserver on multiple ip addresses (%s), port:%d' % (str(ips), server['port']))
    server = ThreadedHTTPServer(('',serverconf['port']),pywebhandler)
    server.mypyconf=serverconf
    try:
        server.serve_forever()
        print('webserver shut down')
    except KeyboardInterrupt:
        server.socket.close()
