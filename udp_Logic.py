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
import binascii
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
        try:
            self.us.bind(ip_port)  # 绑定地址
        except Exception as ret:
            print('Error:',ret)
            QMessageBox.critical(self,'错误','端口已被占用')
            # 关闭udp socket
            self.socket_close_u()
        else:
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
            recv_msg, self.raddr = self.us.recvfrom(self.BUFSIZE)
            # 将连接到本服务器的客户端信息显示在客户端列表下拉框中
            statusbar_client_info = '%s:%d' % (self.raddr[0], self.raddr[1])
            connect_info = '[Remote IP %s Port: %s ]' % (self.raddr[0], self.raddr[1])
            print(self.raddr, type(self.raddr))

            if show_client_info is True:
                self.clients_list.addItem(statusbar_client_info)
                # 状态栏显示客户端连接成功信息
                self.signal_status_connected.emit(statusbar_client_info)
                self.signal_add_clientstatus_info.emit(connect_info)
                show_client_info = False

            # 判断是否以16进制显示并处理
            self.if_hex_show_tcpc_udp(recv_msg)
            # 将接收到的数据字节数显示在状态栏的计数区域
            self.rx_count += len(recv_msg)
            self.statusbar_dict['rx'].setText('接收计数：%s' % self.rx_count)

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
        show_client_info = True
        while True:
            try:
                recv_msg, self.addr = self.us.recvfrom(self.BUFSIZE)
            except Exception as ret:
                pass
            else:
                msg = recv_msg.decode('utf-8')
                print(self.addr)
                print(msg, type(msg))  # msg为 str 类型
                if show_client_info is True:
                    # 将接收到的消息发送到接收框中进行显示
                    self.signal_write_msg.emit('[Remote IP %s Port: %s ]\n' % self.addr + msg)
                    show_client_info = False
                else:
                    self.signal_write_msg.emit(msg)
                # 将接收到的数据字节数显示在状态栏的计数区域
                self.rx_count += len(recv_msg)
                self.statusbar_dict['rx'].setText('接收计数：%s' % self.rx_count)

    def socket_close_u(self):
        self.clients_list.clear()
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
                # udpserver模式
                if self.prot_box.currentIndex() == 2:
                    # 判断发送是否为空
                    if send_msg != b'':
                        # try:
                        self.us.sendto(send_msg, self.raddr)
                        # except Exception as e_crst:
                        #     print("Error:",e_crst)
                    else:
                        QMessageBox.critical(self, '警告', '发送不可为空')
                # udpclient模式
                if self.prot_box.currentIndex() == 3:
                    if send_msg != b'':
                        self.us.sendto(send_msg, self.remote_ip_port)
                    else:
                        QMessageBox.critical(self, '警告', '发送不可为空')
                self.tx_count += len(send_msg)
                self.statusbar_dict['tx'].setText('发送计数：%s' % self.tx_count)

            else:
                QMessageBox.critical(self, '警告', '当前无任何连接')

    def file_send_u(self):
        """
        用于UDP发送消息
        :return:
        """
        if self.working is False :
            QMessageBox.critical(self, '警告', '请先设置UDP网络')
        else:
            if self.link :
                if self.file_load.isChecked():
                    send_msg = self.f_data
                else:
                    send_msg = b''
                # print(send_msg)
                # 若当前状态为udp server模式
                if self.prot_box.currentIndex() == 2:
                    # 判断发送是否为空
                    if send_msg != b'':
                        # try:
                        self.us.sendto(send_msg, self.raddr)
                        # except Exception as e_crst:
                        #     print("Error:",e_crst)
                    else:
                        QMessageBox.critical(self, '警告', '发送不可为空')
                # 若当前状态为udp client状态
                if self.prot_box.currentIndex() == 3:
                    if send_msg != b'':
                        self.us.sendto(send_msg, self.remote_ip_port)
                    else:
                        QMessageBox.critical(self, '警告', '发送不可为空')

            else:
                QMessageBox.critical(self, '警告', '当前无任何连接')