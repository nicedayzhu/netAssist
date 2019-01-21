#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/4 20:25
# @Author  : SeniorZhu1994
# @Site    : 
# @File    : main.py.py
# @Software: PyCharm

# -*- coding: utf-8 -*-

import sys, tcp_Logic, udp_Logic, tcp_udp_ui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QLabel, QPushButton, QFileDialog, QMessageBox
from netAssitui import Ui_NetAssist
import qdarkstyle

import os
class PyQt5_Netassist(QMainWindow,tcp_Logic.TcpLogic,udp_Logic.UdpLogic,tcp_udp_ui.Tcp_ucpUi,Ui_NetAssist):
    def __init__(self):
        # Python3中的继承只用一个super()就可以了，继承后初始化父类的属性
        super(PyQt5_Netassist, self).__init__()
        self.setupUi(self)
        self.working = False
        self.newline.setChecked(1)
        self.remoteip_lbl.hide()
        self.remoteip_text.hide()
        self.remoteport_text.hide()
        self.remoteport_lbl.hide()
        self.init()
        self.custom_connect()
        self.init_statusbar()

    def init(self):
        # 打印选择的协议类型编号
        self.prot_box.currentTextChanged.connect(self.proto_imf)
        # 对open_btn按下进行判断：TCPserver or TCPClient
        self.open_btn.clicked.connect(self.click_select_open)
        # 关闭socket
        self.close_btn.clicked.connect(self.click_select_close)
        # 按钮发送数据
        self.send_Btn.clicked.connect(self.data_send_select)
        # 清空接收区显示
        self.clr_btn.clicked.connect(self.recv_dataclear)
        # 清空发送区显示
        self.clr_btn2.clicked.connect(self.send_dataclear)
        # 当标记状态改变时触发信号，recv2file的isChecked状态作为状态改变的参考
        self.recv2file.toggled.connect(self.rfilechoose)
        # 按下保存数据按钮，进行保存操作
        self.save_btn.clicked.connect(self.datasave2file)
        # 载入需要发送的文件
        self.file_load.toggled.connect(self.send_fileload)
        # 文件发送按钮
        self.file_send_btn.clicked.connect(self.file_send_select)

    def init_statusbar(self):

        # 设置statusbar所有控件自动延伸
        self.statusbar.setSizePolicy(QSizePolicy.Expanding,
                                     QSizePolicy.Expanding)
        # 设置status隐藏控制点（靠齐最右边）
        self.statusbar.setSizeGripEnabled(False)

        self.statusbar_dict['status'] = QLabel()
        self.statusbar_dict['status'].setText('状态：Ready')
        self.statusbar_dict['tx'] = QLabel()
        # self.statusbar_dict['space']=QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.statusbar_dict['tx'].setText('发送计数：0')
        self.statusbar_dict['rx'] = QLabel()
        self.statusbar_dict['rx'].setText('接收计数：0')
        self.statusbar_dict['clear'] = QPushButton()
        self.statusbar_dict['clear'].setText('清除')
        self.statusbar_dict['clear'].setToolTip('清除发送和接收计数')

        self.statusbar_dict['clear'].pressed.connect(
            self.statusbar_clear_pressed)

        for i, w in enumerate(self.statusbar_dict.values()):
            if i != len(self.statusbar_dict) - 1:
                self.statusbar.addWidget(w, 20)
            else:
                # 最后一个控件不拉伸
                self.statusbar.addWidget(w)

    def statusbar_clear_pressed(self):
        self.statusbar_dict['tx'].setText('发送计数：0')
        self.statusbar_dict['rx'].setText('接收计数：0')
        self.rx_count = 0
        self.tx_count = 0

    def click_select_open(self):
        if self.prot_box.currentIndex() == 0:
            # 创建TCPServer
            self.socket_open_tcps()
            self.clients_list.addItem('All Connections')
        if self.prot_box.currentIndex() == 1:
            # 创建TCPClient
            self.socket_open_tcpc()
        if self.prot_box.currentIndex() == 2:
            # 创建UDPClient socket
            self.socket_open_udp()
        if self.working is True:
            self.statusbar_dict['status'].setText('状态：打开')
        self.prot_box.setEnabled(0)

    def click_select_close(self):
        if self.prot_box.currentIndex() == 0:
            # 关闭TCPServer
            self.socket_close()
        if self.prot_box.currentIndex() == 1:
            # 断开TCPClient
            self.socket_close()
        if self.prot_box.currentIndex() == 2:
            # 关闭UDP socket
            self.socket_close_u()
        self.prot_box.setEnabled(1)
        self.statusbar_dict['status'].setText('状态：关闭')

    def data_send_select(self):
        if self.prot_box.currentIndex() == 0:
            self.data_send_t()
        if self.prot_box.currentIndex() == 1:
            self.data_send_t_c()
        if self.prot_box.currentIndex() == 2:
            self.data_send_u()

    def file_send_select(self):
        if self.prot_box.currentIndex() == 0:
            self.file_send_t()
        if self.prot_box.currentIndex() == 1:
            self.file_send_t_c()
        if self.prot_box.currentIndex() == 2:
            self.file_send_u()

    def proto_imf(self):
        # 协议类型选择
        imf_s = self.prot_box.currentIndex()
        if imf_s == 0:
            self.clients_list.clear()
            self.localip_lb.setText('2.本地ip地址')
            self.localport_lb.setText('3.本地端口号')
            self.open_btn.setText('开始监听')
            self.clients_lbl.setText('客户端:')
        if imf_s == 1:
            self.localip_lb.setText('2.远程ip地址')
            self.localport_lb.setText('3.远程端口号')
            self.open_btn.setText('开始连接')
            self.clients_lbl.setText('远程主机:')
            self.clients_list.clear()
        if imf_s == 2:
            self.localip_lb.setText('2.本地ip地址')
            self.localport_lb.setText('3.本地端口号')
            self.open_btn.setText('开始监听')
            self.clients_lbl.setText('客户端:')
            self.remoteip_lbl.show()
            self.remoteip_text.show()
            self.remoteport_text.show()
            self.remoteport_lbl.show()
            self.clients_list.hide()
            self.clients_lbl.hide()

    def recv_dataclear(self):
        """
        pushbutton_clear控件点击触发的槽
        :return: None
        """
        # 清空接收区屏幕
        self.DataRecvtext.clear()

    def send_dataclear(self):
        # 清空发送区框内容
        self.DataSendtext.clear()

    def rfilechoose(self):
        if self.recv2file.isChecked():
            '''接收转向文件'''
            file_name, ok = QFileDialog.getSaveFileName(
                    self, u'保存文件', './', u'所有文件(*.*)')
            print(file_name)
            if ok:
                self.save_file_name = file_name
            else:
                self.save_file_name = None

    def datasave2file(self):
        if not self.DataRecvtext.toPlainText():
            QMessageBox.critical(self, '警告', '当前没有需要的数据')
        else:
            file_name, state = QFileDialog.getSaveFileName(self, '保存文件', './',
                                                           'Text文件(*.txt)')
            if state:
                with open(file_name, 'a', encoding='utf-8') as f_obj:
                    f_obj.write(self.DataRecvtext.toPlainText())
                QMessageBox.information(self, '成功', '%s文件保存成功! ' % file_name)

    def closeEvent(self, event):
        """
        对MainWindow的函数closeEvent进行重构
        退出软件时结束所有进程
        :param event:
        :return:
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '本程序',
                                               "是否要退出程序？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            os._exit(0)
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = PyQt5_Netassist()
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    myWin.show()
    sys.exit(app.exec_())