#!python3
# -*- coding: utf-8 -*-
import socket
from time import ctime
filename = 'info.txt'
ip_port = ('127.0.0.1',8081)
BUFSIZE = 1024
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #创建套接字
s.bind(ip_port)#绑定地址
s.listen(5)#监听链接
print('server listening...')
while True: #无限等待连接
    conn,addr = s.accept() #接受客户端连接
    conn.sendall('欢迎使用socket服务器TCP模式\n服务器功能：为客户端发送的文字加上时间戳'
    .encode('utf8'))#发送欢迎信息
    print(conn)
    print(addr)
    print('接到来自%s的连接'%addr[0])
    while True: #通信循环，无限接受客户端信息
        try:
            msg = conn.recv(BUFSIZE) #接受消息的内容

        # 当用户直接点击关闭按钮关闭客户端时，显示主机强制关闭的异常，否则服务器端会奔溃
        except ConnectionResetError as e_crst:
            print("Error: ",e_crst)
            break
        else:
            if msg.decode('utf-8') == 'exit':
                print("客户端主动断开连接!")
                break
            else:
                print(msg.decode('utf-8'),type(msg))
                with open(filename,'a',encoding='utf-8') as f_obj:
                    f_obj.write(msg.decode('utf-8') + '\n')
                # conn.send(msg.upper())#服务端发送消息,将接收的字符串改为全大写

                # 这里的括号很多，要注意整体性，发送的内容必须是.encode()
                # 本行代码的功能：为接收的字符串加上时间戳，同时大写
                conn.sendall(('[%s] %s'%(ctime(),msg.upper().decode('utf-8'))).encode())
    conn.close()#关闭链接
    s.close()#关闭套接字
