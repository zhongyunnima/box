"""Server

Server handles client's upload and download. Server listens on a public port. Upon a new request's arrival, server opnes a new thread to server it.
Note1: we regard each operation as a single request. For example, if the same user upload once and download once, the server will open two thresds to server it. In other words, the current version
is request-oriented, NOT user-oriented.
Note2: the recv() function will not receive what is expected and sometimes two megs will reach together. So we need the recvall(), which will receive the packet of the exact size.
The format of packet for recvall() is "len(msg)+" "+msg".

tested: two users mixed up/download binary files
to be test: pretty large file(>RAM); two Hi reach together. I will test when I have time
"""

__author__ = 'Mindi Yuan'
__version__ = '1.0'

import socket, threading, sys, SocketServer, os, time

HOST, PORT = "localhost", 9999
PACKETSIZE = 1024
listen_buf = ""

class SubHandler(SocketServer.BaseRequestHandler):
    """handle upload OR download"""
    def recvall(self):    
        while 1:                        
            split_msg = self.recv_buf.partition(" ")
            if split_msg[1] == '': #even have not got the separator
                self.recv_buf += self.request.recv(PACKETSIZE)
                continue
            msg_len = int(split_msg[0])
            msg = split_msg[2]
            if len(msg) >= msg_len: #if the entire msg is received, update the buf (keep the next (partitial) msg) and return the current msg
                self.recv_buf = msg[msg_len:] 
                return msg[:msg_len]
            
    
    def receive_file(self):        
        """client wants to upload"""        
        file=open(os.getcwd()+"\\"+self.user_name+"\\"+self.file_name, 'wb') #binary mode, because we have more than txt files
        file.write(self.recv_buf) #the first part of file could follow the previous msg, so need to be pulled out especially        
        while True: #receive all            
            self.data = self.request.recv(PACKETSIZE)
            if not self.data:                
                break            
            file.write(self.data)
        print self.user_name, "uploaded", self.file_name
        
    def send_file(self):
        """client wants to download"""
        file=open(os.getcwd()+"\\"+self.user_name+"\\"+self.file_name, 'rb')         
        while 1:           
            packet = file.read(PACKETSIZE)            
            if packet == "":
                break
            self.request.sendall(packet)
        print self.user_name, "downloaded", self.file_name
        self.request.close()   
        
    def handle(self):
        self.recv_buf = "" #init teh recv_buf
        up_or_download = self.recvall()        
        self.data = self.recvall()        
        user_and_file_names = self.data.split()
        self.user_name, self.file_name = user_and_file_names[0], user_and_file_names[1]
        
        if not os.path.isdir(self.user_name): #if it is a new client(request), ceata a new folder to store her files
            os.mkdir(self.user_name)     
        
        if up_or_download == 'u':
            print self.user_name, "wants to upload", self.file_name
            self.receive_file()            
        else:
            print self.user_name, "wants to download", self.file_name
            self.send_file()
        self.request.close()     
        
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class MainHandler(SocketServer.BaseRequestHandler):
    """open a threaded subsever to serve each request"""
    def handle(self): #override the handle        
        #Hi = recvall(self.request) #not necessarily receive the Hi
        #if Hi == "Hi":#if it is a new client(request), open a thread to serve that client
            
            #"""a normal subserver, which is wrong"""
            #subserver =  SocketServer.TCPServer((HOST, 0), SubHandler) #open a subserver, port 0 means any unused port    
            #ip, port = subserver.server_address
            #self.request.send(ip+" "+str(port)) #tell client the new ip and port
            ##print threading.enumerate()
            #subserver.handle_request() #not serve_forever because only need to process a single upload/download request
            
        """"or a threaded subserver"""
        subserver =  ThreadedTCPServer((HOST, 0), SubHandler) #port 0 means any unused port            
        ip, port = subserver.server_address #the new ip and port
        subserver_thread = threading.Thread(target=subserver.handle_request)#not serve_forever because only need to process a single upload/download request            
        subserver_thread.setDaemon(True) 
        subserver_thread.start() #start the new threaded private subServer for the new client       
        self.request.send(pack(ip+" "+str(port))) #tell client the new ip and port
            
def pack(msg):#pack len(msg)+" "+msg for sending
    return str(len(msg))+" "+msg
            
#def recvall(socket):
#    global listen_buf
#    while 1:        
#        split_msg = listen_buf.partition(" ")
#        if split_msg[1] == '': #have not got the separator
#            listen_buf += socket.recv(PACKETSIZE)    
#            continue
#        msg_len = int(split_msg[0])
#        msg = split_msg[2]
#        if len(msg) >= msg_len:
#            listen_buf = msg[msg_len:]
#            return msg[:msg_len]

def main():    
    server =  SocketServer.TCPServer((HOST, PORT), MainHandler)  
    server.serve_forever() #listen on the public port
        
if __name__ == '__main__':
    main()