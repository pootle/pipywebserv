# pipywebserv
A minimalist python web server using only python's built in libraries that uses streaming data to live graph data.

Rather than picking up various large and hairy packages (not that I'm thinking of Apache at all!) to run a little Raspberry pi based web server for personal use, I decided to try using just the basic python libraries to see how far I could get, and to better understand some of python's libraries. In particular I wanted to be able to display in my web page, a live graph of key info about my Raspberry Pi Zero - temerature and cpu utilization for starters.

I didn't want a web site that was necessarily session based, or needed logging into, or even made sense with more than 1 concurrent user - although this will work happily with multiple users with a little care.

I did want it to be usable in a closed network (i.e not connected to the internet). I took very much a [KISS](https://en.wikipedia.org/wiki/KISS_principle) approach. I also wanted to easily understand the *whole* thing.

The overall design is to use the web browser as a proper app front end (in days of my youth this would have been called [client-server computing](https://en.wikipedia.org/wiki/Client%E2%80%93server_model)), with each web page acting as a window would in a full app. The page can both make requests to the web server and the web server can feed event streams (following a request from the web page) back to the web page to update the page in real time - for example, to live graph the cpu utilisation or temperature.

This is derived from my older repo minimal-live-graph (now deleted), which was just a basic demo of the live graphing capability.

## installation
1. This is setup to run on Raspbian-lite or Raspbian. A few tweaks are needed to run on non RaspberryPi or non Raspbian setups.
2. install git if you haven't already got it: `sudo apt-get install git`
3. create and / or move to a suitable folder - I keep everything gitish in a folder called *gitbits*
4. clone this repository to your raspberrypi `git clone https://github.com/pootle/pipywebserv.git`
## running from shell
1. move to the cloned folder `cd pipywebserv`
2. run the web server `python3 webserv.py` you should see a message like `Starting webserver on 192.168.1.187:8000`
3. if you get a failure ending with `OSError: [Errno 98] Address already in use` then edit config.py and change `'port':8000`, to use another (unused..) port.
4. on another PC on the same network (or even on the raspberry pi if you have a full desktop installation) open a web browser and put in the address from the `starting webserver` message.

You should now get a screen like this:
![alt text](https://github.com/pootle/pipywebserv/blob/master/rpi%20live%20graph.png "web page image")
## stopping it
Just use <ctrl>-c twice and python will exit.

# The files
+ webserv.py: This is the application. Run this file using `python3 webserv.py`, or make it executable and just do `./webserv.py`.
+ utils.py: a couple of utility functions and classes used by webserv.py. Systeminfo can do a lot more than is used here.
+ config.py: This defines the webserver's port and has details of all the requests it will respond to and how they are handled.
+ static (folder):
  + homepage.html: The single displayed page in this demo. It has a basic page layout and some js that kicks off the event stream to display the live graphs.
  + base1.css: a style sheet using a darkish theme for the homepage. It has some stuff not used here (yet)
  + smoothie.js: Having found several huge js graphing libraries, none of which seemed to be much good at live graphs anyway, and many of which demanded live internet connections to run, I found this little gem which is perfect for this type of use. Get an up to date version at [the smoothie charts website](http://smoothiecharts.org/). I included a version here just for convenience.
  + rasppi.ico: an icon file for the website. Stops the rude messages at the server side, but still does not display the actual icon *sigh*.
