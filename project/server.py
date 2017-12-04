import re
import sys
import json
import time
import asyncio
import logging
import urllib.request
import async_timeout
from functools import partial

Server_Connect={
    'Alford':['Hamilton', 'Welsh'],
    'Hamilton':['Holiday', 'Alford'],
    'Welsh':['Alford', 'Ball'],
    'Ball':['Welsh', 'Holiday'],
    'Holiday':['Ball', 'Hamilton']
}

Server_Address = {
    'Alford':('localhost', 10001),
    'Hamilton':('localhost', 10002),
    'Holiday':('localhost', 10003),
    'Ball':('localhost', 10004),
    'Welsh':('localhost', 10005)
}

name = sys.argv[1];

clients_dict=dict();
#log file basic config
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
)

#setting log file
Server_Log=logging.getLogger('Server:%s'%(name));
fileHandler=logging.FileHandler('%s.log'%(name));
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler.setFormatter(formatter);
Server_Log.addHandler(fileHandler);


#Url address
Url_Address = ["https://maps.googleapis.com/maps/api/place/search/json?location=",
",",
"&radius=",
"&key=AIzaSyB0xXtrdEjVUoDh4zQUGiA0WWNRtMe1A5w"]

#create event_loop
event_loop = asyncio.get_event_loop();

#Client port setting
class EchoClient(asyncio.Protocol):
    #constructor
    def __init__(self, message):
        super().__init__();
        self.message=message;
        Server_Log.info('Create client');

    #connect_made
    def connection_made(self, transport):
        self.transport=transport;
        self.address=transport.get_extra_info('peername');
        Server_Log.info('As Client: connectiong to _{}_{}'.format(*self.address));

        ####################send message####################
        transport.write(self.message.encode());
        Server_Log.info('As Client: sending _{}_{}'.format(*self.address)+'\n{!r}'.format(self.message));
        ####################send message####################
    
    #Response from Server
    def data_received(self, data):
        Server_Log.info('As Client: received \n{!r}'.format(data))

    #Received EOF close port
    def eof_received(self):
        Server_Log.info('As Client: Client closed connection with _{}_{}'.format(*self.address)+' Because eof was received.');
        self.transport.close();

    #Server-side close then Client side closed
    def connnection_lost(self, exc):
        Server_Log.info('As Client: Client closed connection with _{}_{}'.format(*self.address));
        self.transport.close()
        super().connectiong_lost(exc)




#Server setting
class EchoServer(asyncio.Protocol):
    #constructor
    def __init__(self, name):
        super().__init__();
        self.name=name;
        Server_Log.info('Create Server');
    
    #Client connection with Server
    def connection_made(self, transport):
        self.transport=transport;
        self.address=transport.get_extra_info('peername');
        Server_Log.info('connection accpted from_{}_{}'.format(*self.address));

    #Server received message from client
    def data_received(self, data):
        msg=data.decode();
        Server_Log.info('received data from_{}_{}'.format(*self.address)+'\n%s'%(msg));
        self.procString(msg);
    
    #Close connection
    def connection_lost(self, error):
        if error:
            Server_Log.error('Error occur when connection lost error:{}'.format(error));
        else:
            Server_Log.info('connection closed from_{}_{}'.format(*self.address));
        super().connection_lost(error);
    
    #接受EOF文件
    #def eof_received(self):
    #    Server_Log.info('received EOF')
    #    if self.transport.can_write_eof():
    #        self.transport.write_eof()

    #Check legality of coord_str
    def check_coords(self, coord_str):
        ##############0##############
        if not coord_str[0] in ['+', '-']:
            Server_Log.error("Error format in coordination "+coord_str);
            raise ValueError;
        ##############0##############
        ########secode sign position#########
        index=-1;
        for i in range(1, len(coord_str)):
            if coord_str[i] == '+' or coord_str[i] == '-':
                index = i;
                break;
        if index==-1:
            Server_Log.error("Error format in coordination "+coord_str);
            raise ValueError;
        ########secode sign position#########
        #####transfer to float#######
        float(coord_str[:index]);
        float(coord_str[index:]);
        #####transfer to float#######

    #coord_str  to two parts
    def coord_to_tuple(self, coord_str, msg):
        index=-2;
        if coord_str.find('+', 1)==-1:
            index=coord_str.find('-', 1);
        else:
            index=coord_str.find('+', 1);
        return (coord_str[:index], coord_str[index:]);
    
    #get html file
    async def get_html(self, url):
        Server_Log.info('Get json file from google');
        reader, writer = await asyncio.open_connection("maps.google.com", 443,loop=event_loop,ssl=True);
        url = "/maps/" + url.split("/maps/")[1]
        http = "GET "+ url + " HTTP/1.1\r\n" +"User-Agent: curl/7.16.3 libcurl/7.16.3 " +"OpenSSL/0.9.7l zlib/1.2.3\r\n" + "Host: maps.googleapis.com\r\n" + "Content-Type: text/plain; charset=utf-8\r\n\r\n";
        writer.write(http.encode());

        html_file = '';
        Head_buffer = '    ';
        while Head_buffer != '\r\n\r\n':
            await writer.drain();
            Head_buffer = Head_buffer[1:];
            data = (await reader.read(1)).decode('latin1');
            Head_buffer += data;

        while True:                                    
            chunk_len = 0;
            Shit_buffer = '';
            while len(Shit_buffer) < 2 or Shit_buffer[-2:] != '\r\n':
                await writer.drain();
                Shit_buffer += (await reader.read(1)).decode('latin1');
                
            chunk_len = int(Shit_buffer[:-2], 16)
            if chunk_len == 0:
                break;
            
            cnt = 0;
            while cnt < chunk_len:
                await writer.drain();
                data = (await reader.read(1)).decode('latin1');
                cnt += len(data);
                html_file += data;
            await writer.drain();
            data = (await reader.read(1)).decode('latin1');
            await writer.drain();                   
            data = (await reader.read(1)).decode('latin1');
                
        writer.close()
        return html_file
    
    def handler_client(self , server_name, task):
        Server_Log.info('handling client result');
        try:
            ret = task.result();
        except:
            Server_Log.error('Connecting issue with '+server_name+' at the port_{}_{}'.format(*Server_Address[server_name]));
    
    #html file check
    def handler_html(self, items, task):        
        try:
            ###########get json###########
            data = task.result();
            data_dict = json.loads(data);
            ###########get json###########
            ###########deal with json###########
            data_dict['results'] = data_dict['results'] [:items];
            res = json.dumps(data_dict, indent=4) + "\n";
            ###########deal with json###########
            ###########send json###########
            self.transport.write(res.encode());
            Server_Log.info('send to _{}_{}'.format (*self.address)+' with json message\n{}'.format  (res));
            ###########send json###########
        except:
            Server_Log.error("Connect issue with Google. Google server == potato");
        finally:
            self.transport.close();

    #error handler
    def errorhandler(self, msg):
        Server_Log.error('Error at _{}_{}'.format(*self.address)+' Because error format:\n{}'.format(msg));
        self.transport.write(('? '+msg).encode());
        self.transport.close();
        return;
    
    
    #process message
    def procString(self, msg):
        Server_Log.info('Processing String');
        temp=list(filter(None,msg.split(' ')));
        if temp[0]=='IAMAT':
            self.proc_IAMAT(msg);#line: 216
        elif temp[0]=='AT':
            self.proc_AT(msg);#line 250
        elif temp[0]=='WHATSAT':
            self.proc_WHATSAT(msg);#line 297
        else:
            self.errorhandler(msg)
    
    #process IAMAT
    def proc_IAMAT(self, msg):
        Server_Log.info('Processing IAMAT command');
        ##############check  legality##############
        split_msg=list(filter(None,msg.split(' ')));
        if len(split_msg) !=4:
            self.errorhandler(msg);
            return;
        
        try:
            self.check_coords(split_msg[2]);
            float(split_msg[3]);
        except ValueError:
            self.errorhandler(msg);
            return;
        ##############check  legality##############
        ##############built AT command##############
        rece_time=float(split_msg[3])
        cur_time=time.time();
        sign='';
        if (cur_time>rece_time):
            sign='+';
        else:
            sign='-';

        reponse="AT "+self.name+" "+sign+str(cur_time-rece_time)+" "+" ".join(split_msg[1:]);
        ##############built AT command##############
        ############send/call AT command############
        self.transport.write(reponse.encode());
        self.proc_AT(reponse);
        ############send/call AT command############
        self.transport.close();
    
    #proccess AT command
    #AT[0] Alford[1] +0.263873386[2] kiwi.cs.ucla.edu[3] +34.068930-118.445127[4] 1479413884.392014450[5]
    def proc_AT(self, msg):
        Server_Log.info('process AT command');
        ##############check  legality##############
        split_msg=list(filter(None,msg.split(' ')));
        if len(split_msg)!=6:
            self.errorhandler(msg);
            return;
        
        try:
            float(split_msg[2]);
            float(split_msg[5]);
            self.check_coords(split_msg[4]);
        except ValueError:
            self.errorhandler(msg);
            return;
        ##############check  legality##############
        #############extract varibles#############
        client=split_msg[3];
        coords=split_msg[4];
        time=float(split_msg[5]);
        #############extract varibles#############
        #判断是否在client的data_base若不存在查看创建时间->
        if (client in clients_dict and (time>clients_dict[client][1])) or (not client in clients_dict):
            #->放入本服务器的client的data_base->
            clients_dict[client]=(coords, time, msg);
            Server_Log.info("SAVED");
            Server_Log.info("%s"%{str(clients_dict)});
            #->通过Client和其它服务器交换数据
            target=Server_Connect[self.name];
            for server_name in target:
                try:
                    Server_Log.info("Ready to create a  client to tranfer message");
                    factory_coroutine = event_loop.create_connection(
                    partial(EchoClient,message=msg),
                    *Server_Address[server_name]
                    )
                    task=asyncio.ensure_future(factory_coroutine);
                    task.add_done_callback(partial(self.handler_client, server_name));
                except:
                    Server_Log.error('Connecting issue with '+server_name+' at the port_{}_{}'.format(*Server_Address[server_name]));
            #通过Client和其它服务器交换数据<-
            #放入本服务器的client的data_base<-
        #判断是否在client的data_base若不存在查看创建时间<-
        self.transport.close();

    #process WHATSAT command
    #WHATSAT[0] kiwi.cs.ucla.edu[1] 10[2] 5[3]
    def proc_WHATSAT(self, msg):
        Server_Log.info('process WHATSAT command');
        ##############check  legality##############
        split_msg=list(filter(None,msg.split(' ')));
        if len(split_msg)!=4:
            self.errorhandler(msg);
            return;
        
        try:
            if float(split_msg[2])>50:
                raise ValueError;
            if float(split_msg[3])>20:
                raise ValueError;
        except ValueError:
            self.errorhandler(msg);
            return;
        ##############check  legality##############
        ####check client with data_base####
        Server_Log.info("%s"%{str(clients_dict)});
        client=split_msg[1];
        if not client in clients_dict:
            self.errorhandler(msg);
            return;
        ####check client with data_base####
        ##########create url link##########
        radius=int(split_msg[2])*1000;
        items_num=int(split_msg[3]);
        coords=self.coord_to_tuple(clients_dict[client][0], msg);
        At_msg=clients_dict[client][2];
        url_link=Url_Address[0]+coords[0]+Url_Address[1]+coords[1]+Url_Address[2]+str(radius)+Url_Address[3];
        ##########create url link##########
        #############send at command#############
        Server_Log.info('send to '+str(self.address)+'with AT message\n{}'.format(At_msg));
        self.transport.write(At_msg.encode());
        #############send at command#############
        ##########obtain and deal with html file###########
        task=event_loop.create_task(self.get_html(url_link));
        task.add_done_callback(partial(self.handler_html, items_num));
        ##########obtain and deal with html file###########
        return;


#program entance
factory=event_loop.create_server(partial(EchoServer, name), *Server_Address[name]);
server=event_loop.run_until_complete(factory);
Server_Log.info('starting up on {} port {}'.format(*Server_Address[name]));

try:
    event_loop.run_forever();
finally:
    Server_Log.info('closing server');
    server.close();
    event_loop.run_until_complete(server.wait_closed());
    Server_Log.info('closing event loop');
    event_loop.close();