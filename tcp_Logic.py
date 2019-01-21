#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/9 12:54
# @Author  : SeniorZhu1994
# @Site    : 
# @File    : tcpLogic.py
# @Software: PyCharm
from PyQt5.QtWidgets import QMessageBox
from tcp_udp_ui import Tcp_ucpUi
import socket
import threading
import stopThreading
import binascii
import time
class TcpLogic(Tcp_ucpUi):
    def __init__(self):
        super(TcpLogic, self).__init__()
        self.s = None   # s代表socket，本文件中为tcp socket
        self.s_th = None    # s_th代表 thread
        self.client_th = None
        self.accept_th = None
        self.client_socket_list = list()
        self.link = False # 初始化连接状态为False
        self.working = False # 初始化工作状态为False

    def socket_open_tcps(self):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        """
            打开监听后直接按X关闭软件，会导致socket没有关闭，有隐患
            问题已解决：对MainWindow的函数closeEvent进行重构,或者将每个子线程设置为守护线程即可
        """
        self.open_btn.setEnabled(False)
        self.working = True

        local_ip = self.Localip_lineedit.text()
        local_port = self.Localport_lineedit.text()
        ip_port = (local_ip, int(local_port))
        self.BUFSIZE = 1024
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP套接字
        try:
            self.s.bind(ip_port)  # 绑定地址
            self.s.listen(5)  # 监听链接
        except Exception as ret:
            print('Error:',ret)
            QMessageBox.critical(self,'错误','端口已被占用')
            # 关闭udp socket
            self.socket_close()
        else:
            print('server listening...')
            self.accept_th = threading.Thread(target=self.accept_concurrency)
            # 设置线程为守护线程，防止退出主线程时，子线程仍在运行
            self.accept_th.setDaemon(True)
            self.accept_th.start()

    def accept_concurrency(self):
        """
        创建监听线程，使GUI主线程继续运行，以免造成未响应
        :return:
        """
        while True:  # 无限等待连接
            try:
                conn, addr = self.s.accept()  # 接受客户端连接
            except Exception as ret:
                time.sleep(0.001)
            else:
                self.link = True  # 连接建立标志位True，为下面的data_send_t做准备
                self.client_socket_list.append((conn,addr)) # 将连接到本服务器的客户端添加到列表中
                print(self.client_socket_list)
                # 将连接到本服务器的客户端信息显示在客户端列表下拉框中
                statusbar_client_info = '%s:%d' % (addr[0],addr[1])
                self.clients_list.addItem(statusbar_client_info)
                # 状态栏显示客户端连接成功信息
                self.signal_status_connected.emit(statusbar_client_info)
                # 为每个连接创建一个进程
                self.s_th = threading.Thread(target=self.tcp_server_concurrency,args=(conn,addr))
                # 设置线程为守护线程，防止退出主线程时，子线程仍在运行
                self.s_th.setDaemon(True)
                self.s_th.start()


    def tcp_server_concurrency(self,conn,addr):
        """
        功能函数，为每个tcp连接创建一个线程；
        使用子线程用于创建连接，使每个tcp client可以单独地与server通信
        :return:None
        """
        # 这里的show_client_info标志位的作用：仅在收到客户端发送的第一次消息前面加上客户端的ip，port信息
        show_client_info = True
        # 将连接到本服务器的客户端信息显示在客户端列表下拉框中
        statusbar_client_info = '%s:%d' % (addr[0], addr[1])
        while True:
            try:
                recv_msg = conn.recv(self.BUFSIZE)  # 接受消息的内容

            # 当用户直接点击关闭按钮关闭客户端时，显示主机强制关闭的异常，否则服务器端会奔溃
            except ConnectionResetError as con_rest:
                """
                    这里要写成 ConnectionResetError ，
                    如果写成 Expection ，会导致软件进入监听状态，并且有客户端连入后，
                    点击 “断开” 按钮一次，出现 'Remote Client disconnected' 提示信息
                    单机 “断开” 按钮第二次，才会真正断开服务器的socket
                    （总结成一句话，写成Expection会导致点两次 “断开” 才能关闭服务器）
                """
                print('Error:',con_rest)
                conn.close()
                print(self.client_socket_list)
                # 将当前客户端的连接从socket列表中删除
                self.client_socket_list.remove((conn, addr))
                print(self.client_socket_list)
                # 判断socket列表是否已经清空，如果清空，那么self.link置为空
                if self.client_socket_list:
                    pass
                else:
                    self.link = False

                # 将已断开连接的客户端信息从客户端列表下拉box中删除
                self.comboBox_removeItem_byName(self.clients_list,statusbar_client_info)
                # 状态栏显示客户端断开信息
                self.signal_status_removed.emit(statusbar_client_info)
                """
                   下面的break会导致跳出当前接收消息的循环，从而进入监听循环，等待下一个conn。
                   这样的好处是，当客户端断开连接后，服务器并不会断开socket，而是仅仅断开conn。
                   当客户端再一次连接到服务器时，服务器仍可以为其开辟新的conn，并且服务器发送消息的功能运行正确。
                   """
                break
            else:
                print(recv_msg)
                if recv_msg:
                    # 16进制显示功能检测
                    if self.hex_recv.isChecked():
                        msg = binascii.b2a_hex(recv_msg).decode('utf-8')
                        # 例子：str(binascii.b2a_hex(b'\x01\x0212'))[2:-1] == > 01023132
                        print(msg, type(msg),len(msg)) # msg为 str 类型
                        msg = self.hex_show(msg) # 将解码后的16进制数据按照两个字符+'空字符'发送到接收框中显示
                        if show_client_info is True:
                            # 将接收到的消息发送到接收框中进行显示，附带客户端信息
                            connect_info = '[Remote IP %s Port: %s ]' % addr
                            self.signal_add_clientstatus_info.emit(connect_info)
                            self.signal_write_msg.emit(msg)
                            # 仅在收到客户端发送的第一次消息前面加上客户端的ip，port信息
                            show_client_info = False
                        else:
                            self.signal_write_msg.emit(msg)
                    else:
                        try:
                            # 尝试对接收到的数据解码，如果解码成功，即使解码后的数据是ascii可显示字符也直接发送，
                            msg = recv_msg.decode('utf-8')
                            print(msg)
                            if show_client_info is True:
                                # 将接收到的消息发送到接收框中进行显示，附带客户端信息
                                connect_info = '[Remote IP %s Port: %s ]' % addr
                                self.signal_add_clientstatus_info.emit(connect_info)
                                self.signal_write_msg.emit(msg)
                                # 仅在收到客户端发送的第一次消息前面加上客户端的ip，port信息
                                show_client_info = False
                            else:
                                self.signal_write_msg.emit(msg)
                        except Exception as ret:
                            # 如果出现解码错误，提示用户选中16进制显示
                            self.signal_messagebox_info.emit('解码错误，请尝试16进制显示')

                    # 将接收到的数据字节数显示在状态栏的计数区域
                    self.rx_count += len(recv_msg)
                    self.statusbar_dict['rx'].setText('接收计数：%s' % self.rx_count)

                else:
                    # 当前客户端连接主动关闭，但服务器socket并不关闭
                    conn.close()
                    # 将当前客户端的连接从列表中删除
                    self.client_socket_list.remove((conn,addr))
                    # 将已断开连接的客户端信息从客户端列表下拉box中删除
                    self.comboBox_removeItem_byName(self.clients_list, statusbar_client_info)
                    # 状态栏显示客户端断开信息
                    self.signal_status_removed.emit(statusbar_client_info)

                    break

    def socket_open_tcpc(self):
        """
        软件作为tcp client模式连接到其他tcp server
        :return:
        """
        self.open_btn.setEnabled(False)
        remote_ip = self.Localip_lineedit.text()
        remote_port = self.Localport_lineedit.text()
        ip_port = (remote_ip, int(remote_port))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect(ip_port)
        except Exception as ret:
            print("Error:",ret)
            QMessageBox.critical(self,'错误',str(ret))
            self.socket_close()
        else:
            self.working = True
            self.link = True # 设置连接状态标志位 True
            self.client_th = threading.Thread(target=self.tcp_client_concurrency)
            # 设置线程为守护线程，防止退出主线程时，子线程仍在运行
            self.client_th.setDaemon(True)
            self.client_th.start()
            connect_info = '已连接到服务器IP: %s 端口: %s' % ip_port
            self.signal_add_clientstatus_info.emit(connect_info)

    def tcp_client_concurrency(self):
        """
        TCP客户端创建子线程，防止主线程GUI为响应造成崩溃
        :return:
        """
        while True:
            recv_msg = self.s.recv(1024)
            if recv_msg:
                # 判断是否以16进制显示并处理
                self.if_hex_show_tcpc_udp(recv_msg)
                # 将接收到的数据字节数显示在状态栏的计数区域
                self.rx_count += len(recv_msg)
                self.statusbar_dict['rx'].setText('接收计数：%s' % self.rx_count)
            else:
                self.s.close()
                msg = '连接已断开\n'
                self.signal_write_msg.emit(msg)
                self.working = False
                self.socket_close()
                break

    def socket_close(self):
        """
        关闭TCP网络的方法
        :return:
        """
        self.clients_list.clear()
        # 当软件工作在TCPServer模式下
        if self.prot_box.currentIndex() == 0:
            try:
                for client, address in self.client_socket_list:
                    # 关闭所有的conn
                    client.close()
                    # 从conn连接列表中移除每个conn，以防下次进入监听状态时conn列表不为空，影响data_send_t按钮的判断，
                    self.client_socket_list.remove((client, address))
                self.s.close()  # 关闭套接字
                self.working = False
                self.open_btn.setEnabled(True)
                print('server closed...')
            except Exception as ret:
                pass
        # 当软件工作在TCPClient模式下
        if self.prot_box.currentIndex() == 1:
            try:
                self.s.close()
                self.working = False
                self.open_btn.setEnabled(True)
                print('TCP connection closed...')
            except Exception as ret:
                pass

        try:
            # 关闭线程
            stopThreading.stop_thread(self.s_th)
            self.link = False
        except Exception:
            pass
        try:
            # 关闭线程
            stopThreading.stop_thread(self.client_th)
            self.link = False
        except Exception:
            pass

    def data_send_t(self):
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """

        if self.working is False :
            QMessageBox.critical(self, '警告', '请先设置TCP网络')
        else:
            if self.link:
                # send_msg = (str(self.DataSendtext.toPlainText())).encode('utf-8')
                get_msg = self.DataSendtext.toPlainText() # 从发送区获取数据
                # 判断是否是16进制发送
                send_msg = self.if_hex_send(get_msg)
                print(send_msg)
                # 判断发送是否为空
                if get_msg:
                    try:
                        # 发送为All connections，表示服务器向所有连入的客户端发送消息
                        if self.clients_list.currentIndex() == 0:
                            for client, address in self.client_socket_list:
                                client.sendall(send_msg)
                        else:
                            # 服务器向选中的特定客户端发送消息
                            for client, address in self.client_socket_list:
                                address_info = '%s:%d' % (address[0], address[1])
                                if self.clients_list.currentText() == address_info:
                                    client.sendall(send_msg)
                        self.tx_count += len(send_msg)
                        self.statusbar_dict['tx'].setText('发送计数：%s' % self.tx_count)
                    except Exception as e_crst:
                        # QMessageBox.critical(self, '错误', '当前没有任何连接')
                        pass
                else:
                    QMessageBox.critical(self, '警告', '发送不可为空')

            else:
                QMessageBox.critical(self, '警告', '当前无任何连接')


    def data_send_t_c(self):
        """
        功能函数，用于TCP客户端和TCP服务器发送消息
        :return: None
        """
        if self.working is False:
            QMessageBox.critical(self, '警告', '请先设置TCP网络')
        else:
            if self.link:
                get_msg = self.DataSendtext.toPlainText() # 从发送区获取数据
                # 判断是否是16进制发送
                send_msg = self.if_hex_send(get_msg)
                print(send_msg)
                if get_msg:
                    try:
                        self.s.send(send_msg)
                        self.tx_count += len(send_msg)
                        self.statusbar_dict['tx'].setText('发送计数：%s' % self.tx_count)
                    except Exception as ret:
                        pass
                else:
                    QMessageBox.critical(self, '警告', '发送不可为空')
            else:
                QMessageBox.critical(self, '警告', '当前无任何连接')

    def file_send_t(self):
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """

        if self.working is False:
            QMessageBox.critical(self, '警告', '请先设置TCP网络')
        else:
            if self.link :
                if self.file_load.isChecked():
                    send_msg = self.f_data
                else:
                    send_msg = b''
                print(send_msg,len(send_msg))
                # 判断发送是否为空
                if send_msg != b'':
                    try:
                        # 发送为All connections，表示服务器向所有连入的客户端发送消息
                        if self.clients_list.currentIndex() == 0:
                            for client, address in self.client_socket_list:
                                client.sendall(send_msg)
                        else:
                            # 服务器向选中的特定客户端发送消息
                            for client, address in self.client_socket_list:
                                address_info = '%s:%d' % (address[0], address[1])
                                if self.clients_list.currentText() == address_info:
                                    client.sendall(send_msg)
                        self.tx_count += len(send_msg)
                        self.statusbar_dict['tx'].setText('发送计数：%s' % self.tx_count)
                    except Exception as e_crst:
                        # QMessageBox.critical(self, '错误', '当前没有任何连接')
                        pass
                else:
                    QMessageBox.critical(self, '警告', '发送不可为空')

            else:
                QMessageBox.critical(self, '警告', '当前无任何连接')

    def file_send_t_c(self):
        """
        功能函数，用于TCP客户端和TCP服务器发送消息
        :return: None
        """
        if self.working is False:
            QMessageBox.critical(self, '警告', '请先设置TCP网络')
        else:
            if self.link:
                if self.file_load.isChecked():
                    send_msg = self.f_data
                else:
                    send_msg = b''
                print(send_msg,len(send_msg))
                if send_msg != b'':
                    self.s.send(send_msg)
                else:
                    QMessageBox.critical(self, '警告', '发送不可为空')
                self.tx_count += len(send_msg)
                self.statusbar_dict['tx'].setText('发送计数：%s' % self.tx_count)
            else:
                QMessageBox.critical(self, '警告', '当前无任何连接')