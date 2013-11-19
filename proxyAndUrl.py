#proxyAndUrl.py
# Ben Jones
# ECE 649 Fall 2012
# proxyAndUrl.py: sets up a proxy server and parses out the tracking cookies,
#  inserts a new ones, then send the requests to the proxy server. After the 
#  requests have been returned, tracking cookies are inserted again, then 
#  the page is returned to the user

#get the

from twisted.python import log
from twisted.web import proxy, http
from random import randint
import re

class Data():
    def __init__(self):
        self.trackerAdded = False

data = Data()
def set_data(new_data):
    global data
    data = new_data
    return new_data

def get_data():
    return data
    
class MyProxyClient(proxy.ProxyClient):
    def __init__(self,*args,**kwargs):
        self.buffer = ""
        proxy.ProxyClient.__init__(self,*args,**kwargs)

    def handleResponsePart(self, buffer):
        # Here you will get the data retrieved from the web server
        # In this example, we will buffer the page while we shuffle it.
        self.buffer = buffer + self.buffer
#        log.msg(get_data().trackerAdded)
#        log.msg(self.buffer)
#        if(get_data().trackerAdded == False):
#            self.buffer = self.buffer + "Set-Cookie: tracker=" + str(get_data().trackID) + "\n"
#            get_data().trackerAdded = True
#            log.msg("Added tracker: %s" % get_data().trackID)
    def handleResponseEnd(self):
        if not self._finished:
            # We might have increased or decreased the page size. Since we have not written
            # to the client yet, we can still modify the headers.

            lines = self.buffer.split("\n")
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
                self.buffer = "\n".join(newBuff)

            log.msg("Response End: %s" % self.buffer)
            self.father.responseHeaders.setRawHeaders("content-length", [len(self.buffer)])
            self.father.write(self.buffer)
        proxy.ProxyClient.handleResponseEnd(self)

class MyProxyClientFactory(proxy.ProxyClientFactory):
    protocol = MyProxyClient

class ProxyRequest(proxy.ProxyRequest):
    protocols = {'http':MyProxyClientFactory}
    ports = {'http':80 }
    def process(self):
        tracker = self.getCookie('tracker')
        log.msg('Request')
        data = get_data()
        #add the tracker onto the list of equivalent cookies
        if(tracker != str(data.trackID)):
            trackList = data.trackers[data.trackID]
            if(not(tracker in trackList)):
                data.trackers[data.trackID].append(tracker)
        proxy.ProxyRequest.process(self)

class MyProxy(http.HTTPChannel):
    requestFactory = ProxyRequest

class ProxyFactory(http.HTTPFactory):
    protocol = MyProxy

portstr = "tcp:8080:interface=localhost" # serve on localhost:8080

if __name__ == '__main__':
    data = get_data()
    data.trackID = randint(1, 400000000)
    data.trackerAdded = False
    data.trackers = {}
    data.trackers[data.trackID] = []

    import sys
    from twisted.internet import endpoints, reactor

    def shutdown(reason, reactor, stopping=[]):
        """Stop the reactor."""
        if stopping: return
        stopping.append(True)
        if reason:
            log.msg(reason.value)
        reactor.callWhenRunning(reactor.stop)

    log.startLogging(sys.stdout)
    endpoint = endpoints.serverFromString(reactor, portstr)
    d = endpoint.listen(ProxyFactory())
    d.data = data
    d.addErrback(shutdown, reactor)
    reactor.run()

else: # $ twistd -ny proxy_modify_request.py
    data = get_data()
    data.trackID = randint(1, 400000000)
    data.trackerAdded = False
    data.trackers = {}
    data.trackers[data.trackID] = []
    from twisted.application import service, strports

    application = service.Application("proxy_modify_request")
    strports.service(portstr, ProxyFactory()).setServiceParent(application)
