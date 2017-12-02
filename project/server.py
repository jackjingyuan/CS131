import re
import sys
import json
import time
import aiohttp
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
#log 文件设置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
)

#设置log file
Server_Log=logging.getLogger('Server:%s'%(name));
fileHandler=logging.FileHandler('%s.log'%(name));
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler.setFormatter(formatter);
Server_Log.addHandler(fileHandler);


#Url 地址
Url_Address = ["https://maps.googleapis.com/maps/api/place/search/json?location=",
",",
"&radius=",
"&key=AIzaSyB0xXtrdEjVUoDh4zQUGiA0WWNRtMe1A5w"]

#创建时间循环
event_loop = asyncio.get_event_loop();

#客户端端口设置
class EchoClient(asyncio.Protocol):
    #初始函数
    def __init__(self, message):
        super().__init__();
        self.message=message;
        Server_Log.info('create client');

    #再定义connect_made
    def connection_made(self, transport):
        self.transport=transport;
        self.address=transport.get_extra_info('peername');
        Server_Log.info('As Client: connectiong to _{}_{}'.format(*self.address));

        #发送信息
        transport.write(self.message.encode());
        Server_Log.info('As Client: sending _{}_{}'.format(*self.address)+'\n{!r}'.format(self.message));

        #最后发送eof
    
    #作为客户端 受到信息
    def data_received(self, data):
        Server_Log.info('As Client: received \n{!r}'.format(data))

    #收到EOF
    #def eof_received(self):
    #    Server_Log.info('As Client: received EOF')
    #    self.transport.close()
    #    if not self.f.done():
    #        self.f.set_result(True)

    #对接端口关闭
    def connnection_lost(self, exc):
        Server_Log.info('As Client: Client closed connection with _{}_{}'.format(*self.address));
        self.transport.close()
        if not self.f.done():
            self.f.set_result(True)
        super().connectiong_lost(exc)




#服务器设置
class EchoServer(asyncio.Protocol):
    #构造函数
    def __init__(self, name):
        super().__init__()
        self.name=name;
        clients_dict=dict();
    
    #接收到客户端连接请求
    def connection_made(self, transport):
        self.transport=transport;
        self.address=transport.get_extra_info('peername');
        Server_Log.info('connection accpted from_{}_{}'.format(*self.address));

    #收到信息    
    def data_received(self, data):
        msg=data.decode();
        Server_Log.info('received data from_{}_{}'.format(*self.address)+'\n%s'%(msg));
        self.procString(msg);
    
    #关闭连接
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

    #检查坐标
    def check_coords(self, coord_str):
        ############检查0位############
        if not coord_str[0] in ['+', '-']:
            raise ValueError;
        ############检查0位############
        ########检查第二个符号位#########
        index=-1;
        for i in range(1, len(coord_str)):
            if coord_str[i] == '+' or coord_str[i] == '-':
                index = i;
                break;
        if index==-1:
            raise ValueError;
        ########检查第二个符号位#########
        #####检查是否能转化位浮点型#######
        float(coord_str[:index]);
        float(coord_str[index:]);
        #####检查是否能转化位浮点型#######

    #coord_str 切割为两个部分
    def coord_to_tuple(self, coord_str, msg):
        index=-2;
        if coord_str.find('+', 1)==-1:
            index=coord_str.find('-', 1);
        else:
            index=coord_str.find('+', 1);
        return (coord_str[:index], coord_str[index:]);
    
    #获取html文件
    async def get_html(self, url):
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(10):
                async with session.get(url) as response:
                    html = await response.text();
                    return html;
    
    #处理client端口
    def handler_client(self , server_name, task):
        Server_Log.info('handling client result');
        try:
            ret = task.result();
        except:
            Server_Log.error('Connecting issue with '+server_name+' at the port_{}_{}'.format(*Server_Address[server_name]));
    
    #处理html文件
    def handler_html(self, items, task):        
        ###########获取文件###########
        data = task.result();
        data_dict = json.loads(data);
        ###########获取文件###########
        ###########处理文件###########
        data_dict['results'] = data_dict['results'][:items];
        res = json.dumps(data_dict, indent=4) + "\n";
        ###########处理文件###########
        ###########发送文件###########
        self.transport.write(res.encode());
        Server_Log.info('send to _{}_{}'.format(*self.address)+' with json message\n{}'.format(res));
        self.transport.close();
        ###########发送文件###########

    #处理错误
    def errorhandler(self, msg):
        Server_Log.error('Error at _{}_{}'.format(*self.address)+' Because error format:\n{}'.format(msg));
        self.transport.write(('? '+msg).encode());
        self.transport.close();
        return;
    
    
    #处理message
    def procString(self, msg):
        Server_Log.info('Process String');
        temp=list(filter(None,msg.split(' ')));
        if temp[0]=='IAMAT':
            self.proc_IAMAT(msg);#line: 193
        elif temp[0]=='AT':
            self.proc_AT(msg);#line225
        elif temp[0]=='WHATSAT':
            self.proc_WHATSAT(msg);#line 272
        else:
            self.errorhandler(msg)
    
    #处理指令IAMAT
    def proc_IAMAT(self, msg):
        Server_Log.info('Process IAMAT command');
        ##############查看合法性##############
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
        ##############查看合法性##############
        ##############重造AT指令##############
        rece_time=float(split_msg[3])
        cur_time=time.time();
        sign='';
        if (cur_time>rece_time):
            sign='+';
        else:
            sign='-';

        reponse="AT "+self.name+" "+sign+str(cur_time-rece_time)+" "+" ".join(split_msg[1:]);
        ##############重造AT指令##############
        ############发送/处理AT指令############
        self.transport.write(reponse.encode());
        self.proc_AT(reponse);
        ############发送/处理AT指令############
        self.transport.close();
    
    #处理AT指令
    #AT[0] Alford[1] +0.263873386[2] kiwi.cs.ucla.edu[3] +34.068930-118.445127[4] 1479413884.392014450[5]
    def proc_AT(self, msg):
        Server_Log.info('process AT command');
        ##############查看合法性##############
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
        ##############查看合法性##############
        #############抽取字符变量#############
        client=split_msg[3];
        coords=split_msg[4];
        time=float(split_msg[5]);
        #############抽取字符变量#############
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
                    Server_Log.info("init client to tranfer message");
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

    #处理WHATSAT指令
    #WHATSAT[0] kiwi.cs.ucla.edu[1] 10[2] 5[3]
    def proc_WHATSAT(self, msg):
        Server_Log.info('process WHATSAT command');
        ##############查看合法性##############
        split_msg=list(filter(None,msg.split(' ')));
        if len(split_msg)!=4:
            self.errorhandler(msg+' len');
            return;
        
        try:
            if float(split_msg[2])>50:
                raise ValueError;
            if float(split_msg[3])>20:
                raise ValueError;
        except ValueError:
            self.errorhandler(msg+' Value');
            return;
        ##############查看合法性##############
        ####查看client是否在client的data_base中####
        Server_Log.info("%s"%{str(clients_dict)});
        client=split_msg[1];
        if not client in clients_dict:
            self.errorhandler(msg+ ' no client');
            return;
        ####查看client是否在client的data_base中####
        radius=int(split_msg[2])*1000;
        items_num=int(split_msg[3]);
        coords=self.coord_to_tuple(clients_dict[client][0], msg);
        At_msg=clients_dict[client][2];
        url_link=Url_Address[0]+coords[0]+Url_Address[1]+coords[1]+Url_Address[2]+str(radius)+Url_Address[3];
        ##########抽取变量创建url链接##########
        ##########取得/处理html文件###########
        Server_Log.info('send to '+str(self.address)+'with AT message\n{}'.format(At_msg));
        self.transport.write(At_msg.encode());
        task=event_loop.create_task(self.get_html(url_link));
        task.add_done_callback(partial(self.handler_html, 2));
        ##########取得/处理html文件###########
        return;


#程序入口
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

    