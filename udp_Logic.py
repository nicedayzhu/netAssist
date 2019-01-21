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
        self.link = False # 初始化连接状态为False
        self.working = False # 初始化工作状态为False

    def socket_open_udp(self):
        """
        功能函数，UDPClient开启的方法
        :return: None
        """
        self.open_btn.setEnabled(False)
        self.working = True

        lo_ip = self.Localip_lineedit.text()
        lo_port = self.Localport_lineedit.text()
        lo_ip_port = (lo_ip, int(lo_port))

        self.BUFSIZE = 1024

        self.us = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            self.us.bind(lo_ip_port)  # 绑定地址
        except Exception as ret:
            print('Error:',ret)
            QMessageBox.critical(self,'错误','端口已被占用')
            # 关闭udp socket
            self.socket_close_u()
        else:
            print('UDP establishing...')
            self.us_th = threading.Thread(target=self.udp_client_concurrency)
            self.us_th.setDaemon(True)
            self.us_th.start()
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
                statusbar_client_info = '%s:%d' % (self.addr[0], self.addr[1])
                connect_info = '[Remote IP %s Port: %s ]' % (self.addr[0], self.addr[1])
                print(self.addr, type(self.addr))
                if show_client_info is True:
                    # 状态栏显示客户端连接成功信息
                    self.signal_status_connected.emit(statusbar_client_info)
                    self.signal_add_clientstatus_info.emit(connect_info)
                    show_client_info = False

                # 判断是否以16进制显示并处理
                self.if_hex_show_tcpc_udp(recv_msg)
                # 将接收到的数据字节数显示在状态栏的计数区域
                self.rx_count += len(recv_msg)
                self.statusbar_dict['rx'].setText('接收计数：%s' % self.rx_count)

    def socket_close_u(self):
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


    def data_send_u(self):
        """
        用于UDP发送消息
        :return:
        """
        remote_ip = self.remoteip_text.text()
        remote_port = self.remoteport_text.text()
        try:
            self.remote_ip_port = (remote_ip,int(remote_port))
        except Exception as e:
            QMessageBox.critical(self,'错误','请填写正确的远程主机IP和端口号')
        else:
            if self.working is False :
                QMessageBox.critical(self, '警告', '请先设置UDP网络')
            else:
                if self.link :
                    get_msg = self.DataSendtext.toPlainText() # 从发送区获取数据
                    # 判断是否是16进制发送
                    send_msg = self.if_hex_send(get_msg)
                    print(send_msg)
                    if get_msg:
                        try:
                            self.us.sendto(send_msg, self.remote_ip_port)
                            self.tx_count += len(send_msg)
                            self.statusbar_dict['tx'].setText('发送计数：%s' % self.tx_count)
                        except Exception as ret:
                            pass
                    else:
                        QMessageBox.critical(self, '警告', '发送不可为空')
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
                if send_msg != b'':
                    self.us.sendto(send_msg, self.remote_ip_port)
                else:
                    QMessageBox.critical(self, '警告', '发送不可为空')

            else:
                QMessageBox.critical(self, '警告', '当前无任何连接')