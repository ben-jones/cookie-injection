#interceptProxy.py
#Ben Jones
#ECE 649 Fall 2012
#interceptProxy.py: this file contains code that will insert and retreive
# tracking cookies sent to the proxy.

from twisted.internet import protocol, reactor
from random import randint

class TrackInfo():
    def __init__(self):
        self.trackers = {}
        self.genTrackID()
        self.trackers[self.trackID] = []

    def genTrackID(self):
        self.trackID = randint(1, 400000000)
        
    def addEqual(self, newTracker):
        """Check if the new tracker is already in the equivalency list. If it is,
        do nothing, otherwise add the tracker to the equivalency list"""
        if(newTracker in self.trackers[self.trackID]):
            return
        else:
            self.trackers[self.trackID].append(newTracker)

class ConsoleWriter():
    def write(self, data, type):
        if(data):
            lines = data.split("\n")
            prefix = "<" if type == "request" else ">"
            for line in lines:
                sys.stdout.write("%s %s\n" % (prefix, line))
        else:
            sys.stdout.write("No response from server\n")

#protocol to insert and retrieve cookies from the requests and responses
class ClientProtocol(protocol.Protocol):
    """Client protocol which will insert and retreive tracking cookies from the
    requests and responses"""
    def __init__(self, serverTransport, proxyTransport):
        self.serverTransport = serverTransport
        self.proxyTransport = proxyTransport

    def sendMessage(self, data):
        self.getCookie(data)
        self.transport.write(data)

    def dataReceived(self, data):
        self.data = data
        ConsoleWriter().write(self.data)
        self.insertCookie(data)
        self.
        self.transport.loseConnection()

    def connectionLost(self, reason):
        self.serverTransport.write(self.data)
        self.serverTransport.lostConnection()

class ServerProtocol(protocol.Protocol):
    def dataReceived(self, data):
        self.data = data
        ConsoleWriter().write(self.data, "request")
        client = protocol.ClientCreator(reactor, ClientProtocol, self.transport)
        client.trackerInfo = self.trackerInfo
        d = client.connectTCP(self.factory.targetHost, self.factory.targetPort)
        d.addCallback(self.forwardToClient, client)

    def forwardToClient(self, client, data):
        client.sendMessage(self.data):

class ServerFactory(protocol.ServerFactory):
    protocol = ServerProtocol

    def __init__(self, targetHost, targetPort, tracker):
        self.targetHost = targetHost
        self.targetPort = targetPort
        self.trackerInfo = tracker

sourcePort=8000 #the port which Tor will forward its traffic to
targetHost="localhost" #the address the other proxy operates on 
targetPort=8080 #the port the other proxy operates on
if __name__ == "__main__":
    tracker = TrackerInfo()
    reactor.listenTCP(sourcePort, ServerFactory(targetHost, targetPort, tracker))
    reactor.run()
