#!/usr/bin/python3

serverdefaults={
    'port':8000,            # this is the port the webserver will respond to
    'servefrom': {          # this is the list of folders we can use to find files.
            'static'  : 'static',                                # the default folder for entries with no 'foldname' key
            'appstat' : '/home/pi/gitbits/pipywebserv/static',   # further entries where 'foldname' is one of these keys
        },
    'obdefs'   : {
        'pistat'         : {'ondemand':{'className': 'utils.systeminfo'}}
        },    
    'getpaths' : {          # paths to be handled by pywebhandler.do_GET for GETs
        ''               : {'pagetype': 'static',      'pagefile': 'homepage.html'},
        'index'          : {'pagetype': 'static',      'pagefile': 'homepage.html'},
        'base1.css'      : {'pagetype': 'static',      'pagefile': 'base1.css'},
        'smoothie.js'    : {'pagetype': 'static',      'pagefile': 'smoothie.js'},
        'pipyscripts.js' : {'pagetype': 'static',      'pagefile': 'pipyscripts.js'},
        'speshull'       : {'pagetype': 'static',      'pagefile': 'specialtext.html', 'folder': 'appstat'},
        'pistatus'       : {'pagetype': 'eventstream', 'streamtype': 'generator', 'obid': 'pistat', 'period': 1.9},
        'favicon.ico'    : {'pagetype': 'static',      'pagefile': 'rasppi.ico', 'log':1},
        }
}
