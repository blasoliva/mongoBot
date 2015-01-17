#!/usr/bin/python
"""rBot (r33bot) sends information to IRC channel"""

import irclib
irclib.DEBUG = True
import feedparser
import sys
import threading
import time
from config import *

def main():
    try:
        c = rBot()
    except irclib.ServerConnectionError, e:
        exit()

class rBot:
    def __init__(self):
        
        self.irc = irclib.IRC()
        self.server = self.irc.server()
        self.server.connect( IRC_SERVER, IRC_PORT, NICK )

        for c in CHANNEL_LIST:
            self.server.join( c )
            self.sendmessage( c, WELCOME_MSG )

        self.irc.add_global_handler("ping", self._ping_ponger, -42)
        self.irc.add_global_handler( 'privmsg', self.handlePrivMessage )
        self.irc.add_global_handler( 'pubmsg', self.handlePubMessage )
            
        self.feed_list = FEED_LIST
        # self.feed_refresh()
        self.irc.process_forever()

    def sendmessage(self, channel, message):
        self.server.privmsg( channel, message )
        
    def _ping_ponger(self, connection, event):
        connection.pong(event.target())

    def handlePrivMessage (self, connection, event):
        print event.source().split ( '!' ) [ 0 ] + ': ' + event.arguments() [ 0 ]
        if event.arguments() [ 0 ].lower().find ( 'hola r33bot' ) == 0:
            self.sendmessage( event.source().split ( '!' ) [ 0 ], 'h014' )

    def handlePubMessage (self, connection, event):
        print event.target() + '> ' + event.source().split ( '!' ) [ 0 ] + ': ' + event.arguments() [ 0 ]
        if event.arguments() [ 0 ].lower().find ( 'hola r33bot' ) == 0:
            self.sendmessage( '#reevo-dev', 'h014' 

    def feed_refresh(self):

        old_feeds = []
        new_feeds = []
        msgqueue = []
        
        with open( LOG_PATH, 'r' ) as f:
            old_feeds = [ line.strip() for line in f ]
            
        for feed in self.feed_list:
            name, source = feed.split( "|" )
            d = feedparser.parse( source )
            
            for entry in d.entries:
                link = [ entry.link.encode('utf-8') ]
                if link[0] not in old_feeds:
                    msgqueue.append( name
                        + " | " + d.feed.title.encode('utf-8')
                        + " > " + entry.title.encode('utf-8')
                        + " : " + entry.link.encode('utf-8') )
                    new_feeds.append(link[0])
                    
        nf = open( LOG_PATH, "a" )
        for item in new_feeds:
            nf.write( "%s\n" % item )
        nf.close()

        while len( msgqueue ) > 0:
            msgq = msgqueue.pop()
            for c in CHANNEL_LIST:
                self.sendmessage( c, msgq )
            
        time.sleep(5)
        threading.Timer( 30.0, self.feed_refresh() ).start()
        
if __name__ == "__main__":
    main()
