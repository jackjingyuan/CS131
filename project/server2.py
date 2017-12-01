# asyncio_echo_server_protocol.py



request_tokens = ["https://maps.googleapis.com/maps/api/place/search/json?location=",
",",
"&radius=",
"&key=AIzaSyBPBQr0gNpjRp97a_rotWd-lJHjut1Pp9o"]

srv_addr_port = {
    'Alford':('localhost', 10000),
    'Hamilton':('localhost', 10001),
    'Holiday':('localhost', 10002),
    'Ball':('localhost', 10003),
    'Welsh':('localhost', 10004)
}


server_buddies = {
    'Alford':['Hamilton', 'Welsh'],
    'Hamilton':['Holiday', 'Alford'],
    'Welsh':['Alford', 'Ball'],
    'Ball':['Welsh', 'Holiday'],
    'Holiday':['Ball', 'Hamilton']
}


server_dict = {}

# check if coordinate string is properly formated
def check_coords(coord_str):
    if not coord_str[0] in ['+', '-']:
        raise ValueError;
    coord_tokens = None
    index = -1
    for i in range(1, len(coord_str)):
        if coord_str[i] == '+' or coord_str[i] == '-':
            coord_tokens = (coord_str[:i], coord_str[i:])
            index = i
            break
        
    if coord_tokens == None:
        raise ValueError;
    float(coord_str[:index])
    float(coord_str[index:])
    

async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def get_page(transport, url):
        async with aiohttp.ClientSession(loop=even_loop) as session:
            html = await fetch(session, url)
            return html

        
event_loop = asyncio.get_event_loop()

class InterserverProtocol(asyncio.Protocol):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def connection_made(self, transport):
        logfile.write('\nCONNECTION MADE WITH ' \
                      + str(transport.get_extra_info('peername')))
        transport.write(self.message.encode())
        logfile.write('\nWRITE TO ' \
                      + str(transport.get_extra_info('peername')) + ':\n{}'.format(self.message))
        transport.close()
        
    def data_received(self, data):
        msg = data.decode()
        
server_dict = dict()
class EchoServer(asyncio.Protocol):
    def __init__(self, name):
        super().__init__()
        self.name = name

        
    def connection_made(self, transport):
        logfile.write('\nCONNECTION MADE WITH ' \
                      + str(transport.get_extra_info('peername')))
        self.transport = transport
        self.address = transport.get_extra_info('peername')

    def connection_lost(self, exc):
        logfile.write('\nCONNECTION DROPPED WITH ' \
                      + str(self.transport.get_extra_info('peername')))
                      
    def data_received(self, data):        
        msg = data.decode()
        logfile.write('\nREAD FROM ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format(msg))
        msg_code = msg.split(" ")[0]
        if msg_code == "IAMAT":
            self.process_IAMAT(msg)
        elif msg_code == "AT":
            self.process_AT(msg)
        elif msg_code == "WHATSAT":
            self.process_WHATSAT(msg)
        else:
            # incorrect query cmd
            self.transport.write(('? ' + msg).encode())
            logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format('? ' + msg))            
            self.transport.close()
            return
    
    async def get_html(self, url):
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(10):
                async with session.get(url) as response:
                    html = await response.text()
                    return html
            
    def process_AT(self, msg):
        tokens = msg.split(" ")
        # incorrect number of arguments
        if len(tokens) != 6:
            self.transport.write(('? ' + msg).encode())
            logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format('? ' + msg))
            self.transport.close()
            return
        try:
            float(tokens[5])
            float(tokens[2])
            check_coords(tokens[4])
        except ValueError:
            # incorrect argument type
            self.transport.write(('? ' + msg).encode())
            logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format('? ' + msg))
            self.transport.close()
            return            
            
        client = tokens[3]
        coords = tokens[4]
        # only add new and send through if I don't have a newer version
        if not server_dict.get(client, False) or \
           float(tokens[5]) > float(server_dict[client][1].split(" ")[5]):
            server_dict[client] = (coords, msg)
            for srv_id in server_buddies[self.name]:
                try:
                    coro = event_loop.create_connection(partial(InterserverProtocol, msg) , *srv_addr_port[srv_id])
                    self.at_msg = msg
                    fut = asyncio.async(coro)
                    fut.add_done_callback(self.process_connection)
                except Exception: 
                    print("Issue connecting")
                    
    def coord_str_to_tuple(self, coord_str):
        for i in range(1, len(coord_str)):
            if coord_str[i] == '+' or coord_str[i] == '-':
                coord_tokens = (coord_str[:i], coord_str[i:])
                break
        return (coord_tokens[0], coord_tokens[1])

    def handle_google(self, task):        
        data = task.result()
        data_dict = json.loads(data)
        data_dict['results'] = data_dict['results'][:self.place_num]
        res = json.dumps(data_dict, indent=4) + "\n"
        resenc = res.encode()
        self.transport.write(resenc)
        logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format(res))
        self.transport.close()
        
    def process_WHATSAT(self, msg):
        tokens = msg.split(" ")
        # incorrect number of arguments
        if len(tokens) != 4:
            self.transport.write(('? ' + msg).encode())
            logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format('? ' + msg))
            self.transport.close()
            return
        try:
            if float(tokens[3]) > 20:
                raise ValueError
            if float(tokens[2]) > 50:
                raise ValueError
        except ValueError:
            # incorrect argument type
            self.transport.write(('? ' + msg).encode())
            logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format('? ' + msg))
            self.transport.close()
            return            
        
        tokens = msg.split(" ")
        client = tokens[1]
        # non existant client request
        if not server_dict.get(client, False):
            self.transport.write(('? ' + msg).encode())
            logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format('? ' + msg))
            self.transport.close()
            return
        
        radius = int(tokens[2]) * 1000  # radius in meters
        self.place_num = int(tokens[3])
        coord_str = server_dict[client][0]
        AT_response = server_dict[client][1]
        self.transport.write(AT_response.encode())
        logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format(AT_response))
        coord_tuple = self.coord_str_to_tuple(coord_str)
        request = request_tokens[0] + coord_tuple[0] \
                  + request_tokens[1] + coord_tuple[1] \
                  + request_tokens[2] + str(radius) + request_tokens[3]
        task = asyncio.async(self.get_html(request))
        task.add_done_callback(self.handle_google)
        
    def process_IAMAT(self, msg):
        # incorrect number of arguments
        tokens = msg.split(" ")        
        if len(tokens) != 4:
            self.transport.write(('? ' + msg).encode())
            logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format('? ' + msg))
            self.transport.close()
            return
        try:
            float(tokens[3])
            check_coords(tokens[2])
        except ValueError:
            # incorrect argument type
            self.transport.write(('? ' + msg).encode())
            logfile.write('\nWRITE TO ' + str(self.transport.get_extra_info('peername')) + ':\n{}'.format('? ' + msg))
            self.transport.close()
            return            
        
        curr_time = time.time()
        sign = '+'
        if (curr_time > float(tokens[3])):
            sign = '+'
        else:
            sign = '-'
        
        response = "AT " + self.name + " " \
                   + sign + str(curr_time - float(tokens[3])) + " " + " ".join(msg.split(" ")[1:])
        self.process_AT(response)   # add to own storage        
        self.transport.close()

        
    def process_connection(self, task):
        try:
            ret = task.result()
            ret[0].write(self.at_msg.encode())
            logfile.write('\nWRITE TO ' + str(ret[0].get_extra_info('peername')) + ':\n{}'.format(self.at_msg))
            ret[0].close()
        except:
            print("Error connecting!!!")

    def connection_lost(self, exc):
        logfile.write('\nCONNECTION DROPPED WITH ' \
                      + str(self.transport.get_extra_info('peername')))
                      
name = sys.argv[1]
logfile = open(name + "_log.txt", 'w')
srv = event_loop.create_server(partial(EchoServer, name), *srv_addr_port[name])
server = event_loop.run_until_complete(srv)


                
# Enter the event loop permanently to handle all connections.
try:
    event_loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.close()
    event_loop.run_until_complete(server.wait_closed())
    logfile.write('\n')
    logfile.close()
    event_loop.close()