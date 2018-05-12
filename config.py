#!/usr/bin/python3

serverdefaults={
    'port':8000,            # this is the port the webserver will respond to
    'servefrom': 'static',  # this is the relative or absolute path to the folder containing static files 
    'getpaths' : {          # paths to be handled by pywebhandler.do_GET for GETs
        ''            : {'pagetype': 'static',      'pagefile': 'homepage.html'},
        'index'       : {'pagetype': 'static',      'pagefile': 'homepage.html'},
        'base1.css'   : {'pagetype': 'static',      'pagefile': 'base1.css'},
        'smoothie.js' : {'pagetype': 'static',      'pagefile': 'smoothie.js'},
        'dostream'    : {'pagetype': 'eventstream', 
                'streams':{'pistatus':{'streamtype': 'generator', 'modfunc': 'pistatus', 'period': 1.9},
                }
                        },
        'favicon.ico' : {'pagetype': 'static',      'pagefile': 'rasppi.ico', 'log':1},
    }
}
