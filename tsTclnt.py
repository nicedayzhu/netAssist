#!python3
# -*- coding: utf-8 -*-
import socket,os
ip_port=('127.0.0.1',8081)
BUFSIZE=1024
c=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    c.connect(ip_port)
except ConnectionRefusedError as eref: # 服务器未开启造成客户端无法连接
    print("Error: ",eref)
    # 为了防止运行时一闪而过，看不到错误信息
    os.system("pause")
else:
    server_info = c.recv(BUFSIZE).decode('utf8')#接受服务端的欢迎消息
    print(server_info)
    while True:#通讯循环，客户端可以无限发消息
        msg = input('>>:').strip()
        if len(msg)==0:continue
        try:
            c.sendall(msg.encode('utf8'))#发送消息，utf8格式
        except ConnectionResetError as erst: # 服务器主动关闭，导致连接被重置
            print("Error ",erst)
            # 为了防止运行时一闪而过，看不到错误信息
            os.system("pause")
        if msg == 'exit':
            break
        feedback = c.recv(BUFSIZE)#接受服务端消息
        print(feedback.decode('utf8'))
    c.close()#关闭套接字