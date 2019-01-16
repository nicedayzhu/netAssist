#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/10 16:00
# @Author  : SeniorZhu1994
# @Site    : 
# @File    : tcp_udp_ui.py
# @Software: PyCharm
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from netAssitui import Ui_NetAssist
from time import ctime

class Tcp_ucpUi(Ui_NetAssist):
    # 主线程属性继承自Ui_NetAssist
    # 信号槽机制：设置一个信号，用于触发接收区写入动作
    signal_write_msg = pyqtSignal(str)
    signal_status_connected = pyqtSignal(str)
    signal_status_removed = pyqtSignal(str)

    # statusbar上添加的控件
    # 使用字典方式进行管理
    statusbar_dict = {}
    rx_count = 0
    tx_count = 0
    # statusbar End
    def __init__(self):
        super(Tcp_ucpUi, self).__init__()

    def custom_connect(self):
        """
        控件信号-槽的设置
        :param : QDialog类创建的对象
        :return: None
        """
        self.signal_write_msg.connect(self.write_msg)
        self.signal_status_connected.connect(self.statusbar_connect)
        self.signal_status_removed.connect(self.statusbar_remove)

    def hex_str_convert(self,msg):
        """
        字符串和16进制相互转换
        1.字符串转16进制显示（finished）
        To do:
            16进制发送
        :param msg:
        :return:
        """
        if self.hex_recv.isChecked():
            hex_msg = self.str_to_hex(msg)
        else:
            hex_msg = msg
        return hex_msg

    def write_msg(self, msg):
        # signal_write_msg信号会触发这个函数
        """
        功能函数，向接收区写入数据的方法
        信号-槽触发
        tip：PyQt程序的子线程中，直接向主线程的界面传输字符是不符合安全原则的
        :return: None
        """
        # 为接收到的数据加上时间戳并且显示在接收框中
        if self.timestamp.isChecked():
            if self.newline.isChecked():
                self.DataRecvtext.insertPlainText('\n[%s]' % ctime())
                # 将传入的msg进行字符串转16进制功能判断，显示处理
                processed_msg = self.hex_str_convert(msg)
                self.DataRecvtext.insertPlainText('%s' % processed_msg)
            else:
                self.DataRecvtext.insertPlainText('[%s]' % ctime())
                # 将传入的msg进行字符串转16进制功能判断，显示处理
                processed_msg = self.hex_str_convert(msg)
                self.DataRecvtext.insertPlainText('%s' % processed_msg)
        else:
            if self.newline.isChecked():
                # 将传入的msg进行字符串转16进制功能判断，显示处理
                processed_msg = self.hex_str_convert(msg)
                self.DataRecvtext.insertPlainText('\n%s' % processed_msg)
            else:
                # 将传入的msg进行字符串转16进制功能判断，并显示处理
                processed_msg = self.hex_str_convert(msg)
                self.DataRecvtext.insertPlainText('%s' % processed_msg)
        # 滚动条移动到结尾
        self.DataRecvtext.moveCursor(QtGui.QTextCursor.End)

    def comboBox_removeItem_byName(self, combo, name):
        '''QComboBox中删除特定名字的项目'''
        for i in range(0, combo.count()):
            if name == combo.itemText(i):
                # 找到对应的项目
                combo.removeItem(i)

    def statusbar_connect(self,statusbar_client_info):
        self.statusbar.showMessage('客户端：%s 成功连接！' % statusbar_client_info, msecs=2000)

    def statusbar_remove(self,statusbar_client_info):
        self.statusbar.showMessage('客户端：%s 断开连接！' % statusbar_client_info, msecs=2000)

    def str_to_hex(self,s):
        """
        字符串转16进制显示
        :param s:
        :return:
        """
        return ' '.join([hex(ord(c)).replace('0x', '') for c in s])

    def hex_to_str(self,s):
        """
        16进制转字符串显示
        :param s:
        :return:
        """
        return ''.join([chr(i) for i in [int(b, 16) for b in s.split(' ')]])

    def str_to_bin(self,s):
        """
        字符串转二进制显示
        :param s:
        :return:
        """
        return ' '.join([bin(ord(c)).replace('0b', '') for c in s])

    def bin_to_str(self,s):
        """
        二进制转字符串显示
        :param s:
        :return:
        """
        return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])
