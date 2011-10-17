"""client

Client first says "Hi" to server's public port. Then server opens a private port and responses the "Hi" with the new ip and port. Now client can up/downlaod using the new connection.
Note1: we regard each operation as a single request. For example, if the same user upload once and download once, the server will open two thresds to server it. In other words, the current version
is request-oriented, NOT user-oriented.
Note2: the recv() function will not receive what is expected and sometimes two megs will reach together. So we need the recvall(), which will receive the packet of the exact size.
The format of packet for recvall() is "len(msg)+" "+msg".
"""

__author__ = 'Mindi Yuan'
__version__ = '1.0'

import socket, sys, time, os

HOST, PORT = "localhost", 9999 #I use them for experiment in my machine
PACKETSIZE = 1024
recv_buf=""

class Client(object):
    """Client can upload OR download"""    
    def __init__(self, name):                
        self.name = name
        
    def connect(self, host, port):        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creat a TCP socket
        self.sock.connect((host, port))
        
    def handShake(self): 
        #say hi to server's public port        
        self.connect(HOST, PORT)
        self.sock.sendall(pack("Hi"))
        new_add = recvall(self.sock) #get the new ip and port from the server
        self.sock.close() #"say hi" complete
        #set up the new PRIVATE connection
        ip_and_port = new_add.split()           
        self.connect(ip_and_port[0], int(ip_and_port[1]))
        
    def upload(self, file_name):        
        self.handShake()
        self.sock.sendall(pack("u")) #upload signal        
        self.sock.sendall(pack(self.name+" "+file_name))
        file=open(file_name, 'rb') #binary mode, because we have more than txt files       
        #file_size = os.path.getsize(file_name)        
        #self.sock.sendall(str(file_size)+" ") #the server's recvall() will think it is a big packet of size file_size
        #self.sock.sendall(file.read()) #if the file size is larger than RAM, this will fail
        while 1: #correct way to send the file
            #time.sleep(3)
            packet = file.read(PACKETSIZE)
            if packet == "":
                break
            self.sock.sendall(packet)       
        self.sock.close()
        
    def download(self, file_name):
        self.handShake()
        self.sock.sendall(pack("d")) #download signal
        self.sock.sendall(pack(self.name+" "+file_name))        
        file=open(file_name, 'wb')
        while True: #receive all
            #time.sleep(3)
            self.data = self.sock.recv(PACKETSIZE)
            if not self.data:                
                break            
            file.write(self.data)            
        self.sock.close()
        
def recvall(socket):
    global recv_buf
    while 1:        
        split_msg = recv_buf.partition(" ")
        if split_msg[1] == '': #even have not got the separator
            recv_buf += socket.recv(PACKETSIZE)
            continue
        msg_len = int(split_msg[0])
        msg = split_msg[2]
        if len(msg) >= msg_len: #if the entire msg is received, update the buf (keep the next (partitial) msg) and return the current msg
            recv_buf = msg[msg_len:]
            return msg[:msg_len]         
        
def pack(msg):#pack len(msg)+" "+msg for sending
    return str(len(msg))+" "+msg

def main():    
    client=Client("user1")        
    client.upload("upload.txt")
    client.download("upload.txt")   

if __name__ == '__main__':
    main()