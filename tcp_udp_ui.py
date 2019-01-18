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
from PyQt5.QtWidgets import QFileDialog, QMessageBox
class Tcp_ucpUi(Ui_NetAssist):
    # 主线程属性继承自Ui_NetAssist
    # 信号槽机制：设置一个信号，用于触发接收区写入动作
    signal_write_msg = pyqtSignal(str)
    signal_status_connected = pyqtSignal(str)
    signal_status_removed = pyqtSignal(str)
    signal_add_clientstatus_info = pyqtSignal(str)
    signal_messagebox_info = pyqtSignal(str)

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
        self.signal_add_clientstatus_info.connect(self.add_clientstatus_plain)
        self.signal_messagebox_info.connect(self.messagebox_info)

    def send_fileload(self):
        if self.file_load.isChecked():
            # 载入发送文件
            send_file_name, sf_ok = QFileDialog.getOpenFileName(
                    self, u'保存文件', './', u'所有文件(*.*)')
            if sf_ok:
                self.statusbar.showMessage('文件载入成功', msecs=3000)
                with open(send_file_name,'rb') as send_f:
                    self.f_data = send_f.read()
                print(self.f_data)
            else:
                self.statusbar.showMessage('文件载入失败', msecs=3000)

    def add_clientstatus_plain(self,info):
        self.DataRecvtext.insertPlainText(info)

    def messagebox_info(self,info):
        QMessageBox.critical(self,'错误',info)

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
                self.DataRecvtext.insertPlainText('%s' % msg)
            else:
                self.DataRecvtext.insertPlainText('[%s]' % ctime())
                self.DataRecvtext.insertPlainText('%s' % msg)
        else:
            if self.newline.isChecked():
                self.DataRecvtext.insertPlainText('\n%s' % msg)
            else:
                self.DataRecvtext.insertPlainText('%s' % msg)
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

    def hex_show(self,str):
        """
        将字符串转换为大写字母并每隔2个字符用空格分割处理后得到一个新字符串
        如：faa5fbb5fcc5fdd5010200000028000001900000000a002d00000000017d7840000003e800005fa55fb55fc55fd5
            FA A5 FB B5 FC C5 FD D5 01 02 00 00 00 28 00 00 01 90 00 00 00 0A 00 2D 00 00 00 00 01 7D 78 40 00 00 03 E8 00 00 5F A5 5F B5 5F C5 5F D5
        :param str:
        :return:
        """
        t = str.upper()
        return ' '.join([t[2*i:2*(i+1)] for i in range(len(t)//2)])
        # / 是精确除法， // 是向下取整除法， % 是求模
