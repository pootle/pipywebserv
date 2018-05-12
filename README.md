# pipywebserv
A minimalist python web server using only python's built in libraries that uses streaming data to live graph data.

Rather than picking up various large and hairy packages (not that I'm thinking of Apache at all!) to run a little Raspberry pi based web server for personal use, I decided to try using just the basic python libraries to see how far I could get, and to better understand some of python's libraries. In particular I wanted to be able to display in my web page, a live graph of key info about my Raspberry Pi Zero - temerature and cpu utilization for starters.

I didn't want a web site that was necessarily session based, or needed logging into, or even made sense with more than 1 concurrent user - although this will work happily with multiple users with a little care.

I did want it to be usable in a closed network (i.e not connected to the internet). I took very much a [KISS](https://en.wikipedia.org/wiki/KISS_principle) approach. I also wanted to easily understand the *whole* thing.

The overall design is to use the web browser as a proper app front end (in days of my youth this would have been called [client-server computing](https://en.wikipedia.org/wiki/Client%E2%80%93server_model)), with each web page acting as a window would in a full app. The page can both make requests to the web server and the web server can feed event streams (following a request from the web page) back to the web page to update the page in real time - for example, to live graph the cpu utilisation or temperature.

##installation
1. This is setup to run on Raspbian-lite or Raspbian. A few tweak are needed to run on non RaspberryPi or Raspbian setups.
2. install git if you haven't already got it: `sudo apt-get install git`
3. create and / or move to a suitable folder - I keep everything gitish in a folder called *gitbits*
4. clone this repository to your raspberrypi ``
