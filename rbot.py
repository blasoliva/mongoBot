#!/usr/bin/python
""" rBot: Reevo IRC client 2nd generation"""

import irclib
irclib.DEBUG = True
import feedparser
import sys
import threading
import time
import os
from config import *

def main():
    try:
        c = rBot()
    except irclib.ServerConnectionError, e:
        exit()
    
class rBot:
    def __init__(self):
        """ IRC objects constructor """
        # Create IRC object and connect to the network
        self.irc = irclib.IRC()
        self.server = self.irc.server()
        self.server.connect( IRC_SERVER, IRC_PORT, NICK )

        # Join channels and send welcome message
        for channel in CHANNEL_LIST:
            self.server.join( channel )
            self.sendmessage( channel, WELCOME_MSG )

        # Register handlers
        self.irc.add_global_handler( 'ping', self.ponger, -42 )
        self.irc.add_global_handler( 'privmsg', self.handleprivmessage )
        self.irc.add_global_handler( 'pubmsg', self.handlepubmessage )

        # Go into an infinite loop
        self.irc.process_forever()

    def sendmessage(self, channel, message):
        """ Send messages function"""
        self.server.privmsg(channel, message)
        
    def ponger(self, connection, event):
        """ Send pong command """
        connection.pong(event.target())

    def handleprivmessage (self, connection, event):
        """Handle private messages function

        argument -- message
        source -- origin of the message (nickname)
        """
        argument = event.arguments() [0].lower()
        source = event.source().split( '!' ) [0]
        
        if argument.find ( 'hola r33bot' ) == 0:
            self.sendmessage( source, 'hola ' + source )
             
    def handlepubmessage (self, connection, event):
        """ Handle public messages function
        
        argument -- message
        source -- origin of the message (nickname)
        target -- target of the command (channel)
        """
        argument = event.arguments() [0].lower()
        source = event.source().split( '!' ) [0]
        target = event.target()
        
        if argument.find ( 'hola r33bot' ) == 0:
            self.sendmessage( target, 'hola ' + source )
        elif argument.find ( 'feed_refresh' ) == 0:
            self.feed_refresh()

    def ping(self, host):
        """ Send ping
        host -- IP address or domain
        """
        response = os.system( "ping -c 1 " + host )
        return response

    def feed_refresh(self):

        msgqueue = []
        
        for feed_url in FEED_LIST:
            name, source = feed_url.split( '|' )
            f = feedparser.parse( source )
            f2 = feedparser.parse( source, etag=f.etag )

            if int(f2.status) != 304:
                for feed in f2.entries:
                    msgqueue.append( name
                        + " | " + f2.feed.title.encode('utf-8')
                        + " > " + feed.title.encode('utf-8')
                        + " : " + feed.link.encode('utf-8') )
            else:
                msgqueue.append( f2.debug_message )
                
            while len( msgqueue ) > 0:
                msgq = msgqueue.pop()
                for channel in CHANNEL_LIST:
                    self.sendmessage( channel, msgq )
                
        time.sleep(3)
        # threading.Timer( 60, self.feed_refresh ).start()

if __name__ == "__main__":
    main()
