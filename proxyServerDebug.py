#proxyServerDebug.py
# Ben Jones
# ECE 649 Fall 2012
from twisted.internet import protocol
from twisted.internet import reactor
from random import randint
import re

internetProxyPort=8000
torPort=8080


class Data():
    def __init__(self):
        self.trackID = randint(1, 400000000)
        self.trackers = {}
        self.trackerAdded = False
data = Data()
def set_data(new_data):
    global data
    data = new_data
    return new_data

def get_data():
    return data

class ConsoleWriter():
    def write(self, data, type):
        if(data):
            lines = data.split("\n")
            prefix = "<" if type == 'request' else ">"
            for line in lines:
                sys.stdout.write("%s %s\n" % (prefix, line))
        else:
            sys.stdout.write("No response from internet request")

#protocol to insert cookie-> client protocol
class InsertTrackingCookie(protocol.Protocol):
    """Client Protocol: This class will serve 3 purposes. 1) write the data that
    has been returned from the webserver to the console 2) Insert a tracking
    cookie, and 3) send the newly modified data to Tor"""

    def __init__(self, serverTansport):
        self.serverTransport = serverTransport
    
    def sendMessage(slf, data):
        "Send the message to the client. Aka, send 
        self.data = data


    def dataReceived(self, data):
        self.data = data
        sys.stdout.write(data)
        client = protocol.ClientCreator(reactor, GetTrackingCookie, self.transport)

#protocol to retrieve cookie-> server protocol
class GetTrackingCookie(protocol.Protocol):
    def __init__(self, serverTransport):
        self.serverTransport = serverTransport
    
    def getCookie(self, data):
        sys.stdout.write("Getting cookie")
            lines = data.split("\n")
            if(len(lines) > 1):
                newBuff = lines[0:2]
                if(re.search("Set\-Cookie", lines[2]) == None):
                    trackerStr = "Set-Cookie: tracker=" + str(get_data().trackID)
                    newBuff.append(trackerStr)
                    newBuff.append(lines[2])
                    newBuff[4:] = lines[3:]
                else:
                    newline = lines[2] + "; tracker=" + str(get_data().trackID)
                    newBuff.append(newline)
                    newbuff[3:] = lines[3:]
                newData = "\n".join(newBuff)
                return newdata
            else return data

    def sendMessage(self, data):
        #send message-> hand data to the real proxy server
        self.getCookie(data)
        self.transport.write(data)
    
    def dataReceived(self, data):
        #response received-> hand back to the Tor client
        sys.stdout.write(data)
        self.data = data
        get_data().TorConnection.write(data)
        self.transport.loseConnection()
        
    def connectionLost(self, reason):
        self.serverTransport.write(self.data)
        self.serverTransport.loseConnection()

        d = client.connectTCP(self.factory.targetHost, self.factory.targetPort
