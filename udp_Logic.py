#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/11 15:48
# @Author  : SeniorZhu1994
# @Site    : 
# @File    : udp_Logic.py
# @Software: PyCharm
from PyQt5.QtWidgets import QMessageBox
from tcp_udp_ui import Tcp_ucpUi
import socket
import threading
import stopThreading
from time import ctime
import time

class UdpLogic(Tcp_ucpUi):
    def __init__(self):
        super(UdpLogic, self).__init__()
        self.us = None  # us代表udp socket
        self.us_th = None
        self.client_th = None
        self.link = False # 初始化连接状态为False
        self.working = False # 初始化工作状态为False

    def socket_open_udps(self):
        """
        功能函数，UDP服务端开启的方法
        :return: None
        """
        self.open_btn.setEnabled(False)
        self.working = True

        local_ip = self.Localip_lineedit.text()
        local_port = self.Localport_lineedit.text()
        ip_port = (local_ip, int(local_port))
        self.BUFSIZE = 1024

        self.us = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.us.bind(ip_port)  # 绑定地址
        print('UDPServer listening...')

        self.us_th = threading.Thread(target=self.udp_server_concurrency)
        self.us_th.setDaemon(True)
        self.us_th.start()
        self.link = True

    def udp_server_concurrency(self):
        """
        创建新线程以供UDPServer持续监听
        :return:
        """
        show_client_info = True
        while True:
            recv_msg, addr = self.us.recvfrom(self.BUFSIZE)
            msg = recv_msg.decode('utf-8')
            print(addr,type(addr))
            print(msg, type(msg))  # msg为 str 类型
            if show_client_info is True:
            # 将接收到的消息发送到接收框中进行显示
                self.signal_write_msg.emit('[Remote IP %s Port: %s ]\n' % addr + msg)
                show_client_info = False
            else:
                self.signal_write_msg.emit(msg)

    def socket_open_udpc(self):
        """
        功能函数，UDPClient开启的方法
        :return: None
        """
        self.open_btn.setEnabled(False)
        self.working = True

        remote_ip = self.Localip_lineedit.text()
        remote_port = self.Localport_lineedit.text()
        self.remote_ip_port = (remote_ip, int(remote_port))
        self.BUFSIZE = 1024

        self.us = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('UDPClient connecting...')

        self.client_th = threading.Thread(target=self.udp_client_concurrency)
        self.client_th.setDaemon(True)
        self.client_th.start()
        self.link = True

    def udp_client_concurrency(self):
        """
        创建新线程以供UDPClient持续监听Server的消息
        :return:
        """
        while True:
            try:
                recv_msg, self.addr = self.us.recvfrom(self.BUFSIZE)
            except Exception as ret:
                pass
            else:
                msg = recv_msg.decode('utf-8')
                print(self.addr)
                print(msg, type(msg))  # msg为 str 类型
                # 将接收到的消息发送到接收框中进行显示
                self.signal_write_msg.emit(str(self.addr) + '\n' + msg)

    def socket_close_u(self):
        if self.prot_box.currentIndex() == 2:
            try:
                self.us.close()
                self.working = False
                self.open_btn.setEnabled(True)
                print('UDP closed...')
                self.open_btn.setEnabled(True)
            except Exception as ret:
                pass

        if self.prot_box.currentIndex() == 3:
            try:
                self.us.close()
                self.working = False
                self.open_btn.setEnabled(True)
                print('UDP closed...')
                self.open_btn.setEnabled(True)
            except Exception as ret:
                pass

        try:
            stopThreading.stop_thread(self.us_th)
        except Exception as ret:
            pass

        try:
            stopThreading.stop_thread(self.client_th)
        except Exception as ret:
            pass


    def data_send_u(self):
        """
        用于UDP发送消息
        :return:
        """
        if self.working is False :
            QMessageBox.critical(self, '警告', '请先设置UDP网络')
        else:
            if self.link :
                send_msg = (str(self.DataSendtext.toPlainText())).encode('utf-8')
                # print(send_msg)
                if self.prot_box.currentIndex() == 2:
                    # 判断发送是否为空
                    if send_msg != b'':
                        # try:
                        self.us.sendto(send_msg, self.addr)
                        # except Exception as e_crst:
                        #     print("Error:",e_crst)
                    else:
                        QMessageBox.critical(self, '警告', '发送不可为空')
                if self.prot_box.currentIndex() == 3:
                    if send_msg != b'':
                        self.us.sendto(send_msg, self.remote_ip_port)
                    else:
                        QMessageBox.critical(self, '警告', '发送不可为空')

            else:
                QMessageBox.critical(self, '警告', '当前无任何连接')
