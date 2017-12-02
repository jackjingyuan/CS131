import time
import asyncio
import logging

name= 'testclient';
Server_Log=logging.getLogger('Server:%s'%(name));
fileHandler=logging.FileHandler('%s.log'%(name));
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler.setFormatter(formatter);
fileHandler.setLevel(logging.INFO);
Server_Log.addHandler(fileHandler);



class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop

    def connection_made(self, transport):
        transport.write(self.message.encode())
        Server_Log.info('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        Server_Log.info('Data received: {}'.format(data.decode()))

    def connection_lost(self, exc):
        Server_Log.info('The server closed the connection')
        Server_Log.info('Stop the event loop')
        self.loop.stop()

loop = asyncio.get_event_loop()
when = time.time()
message = 'IAMAT kiwi.cs.ucla.edu +34.068930-118.445127 %s'%(str(when));
coro = loop.create_connection(lambda: EchoClientProtocol(message, loop),
                               '127.0.0.1', 10001)
loop.run_until_complete(coro)
loop.run_forever()
message = 'WHATSAT kiwi.cs.ucla.edu 10 5'
coro = loop.create_connection(lambda: EchoClientProtocol(message, loop),
                              '127.0.0.1', 10001)
loop.run_until_complete(coro)
loop.run_forever()
message = 'IAMAT kiwi.cs.ucla.edu +50.068930-118.445127 {when+1}'
coro = loop.create_connection(lambda: EchoClientProtocol(message, loop),
                              '127.0.0.1', 10001)
loop.run_until_complete(coro)
loop.run_forever()
message = 'WHATSAT kiwi.cs.ucla.edu 10 5'
coro = loop.create_connection(lambda: EchoClientProtocol(message, loop),
                              '127.0.0.1', 10001)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()