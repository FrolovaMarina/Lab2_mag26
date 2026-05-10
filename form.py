from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from encryption import *
import pygame as pg
from appearance import *
from extra import *
import re


class UiEntry(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UiEntry, self).__init__(parent)
        self.setupUi(self)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(426, 459)
        Dialog.setStyleSheet("background-color: rgb(158, 78, 255)")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setGeometry(QtCore.QRect(39, 30, 351, 401))
        self.frame.setStyleSheet("background-color: rgb(223, 196, 255);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(40, 10, 281, 51))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setItalic(False)
        self.label.setFont(font)
        self.label.setStyleSheet("color: rgb(0, 36, 103);")
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self.frame)
        self.lineEdit.setGeometry(QtCore.QRect(50, 90, 251, 31))
        font.setPointSize(10)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_2.setGeometry(QtCore.QRect(50, 150, 251, 31))
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setObjectName("lineEdit_2")
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(100, 330, 151, 23))
        font.setPointSize(12)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.add_functions()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Регистрация / Авторизация:  "))
        self.lineEdit.setPlaceholderText(_translate("Dialog", "Имя "))
        self.lineEdit_2.setPlaceholderText(_translate("Dialog", "Пароль "))
        self.pushButton.setText(_translate("Dialog", "Войти: "))

    def add_functions(self):
        self.pushButton.clicked.connect(self.method_1)

    def method_1(self):
        if self.lineEdit.text() == "" or self.lineEdit_2.text() == "":
            error = QMessageBox()
            error.setWindowTitle("Ошибка")
            error.setText("Введите имя и пароль")
            error.setStandardButtons(QMessageBox.Ok)

            error.exec()
        elif not re.fullmatch(r'[а|А-я|Я]{,12}', self.lineEdit.text()) and\
                not re.fullmatch(r'[a|A-z|Z]{,12}', self.lineEdit.text()):
            error = QMessageBox()
            error.setWindowTitle("Ошибка")
            error.setText("В имени могут использоваться только буквы, максимальная длина - 12 символов")
            error.setStandardButtons(QMessageBox.Ok)

            error.exec()
        elif not re.fullmatch(r'\w{,10}', self.lineEdit_2.text()):
            error = QMessageBox()
            error.setWindowTitle("Ошибка")
            error.setText("В пароле могут содержаться только буквы, цифры или нижнее подчёркивание, "
                          "максимальная длина - 10 символов")
            error.setStandardButtons(QMessageBox.Ok)

            error.exec()
        else:
            encoded_txt = xtea_encode(self.lineEdit.text() + self.lineEdit_2.text())
            new_file = open("file.txt", "wb")
            new_file.write(encoded_txt)
            decoded_txt = xtea_decode(self.lineEdit.text() + self.lineEdit_2.text())
            new_file = open("file.txt", "a")
            new_file.write(decoded_txt) 
            self.open_game()

    def open_game(self):
        clock = pg.time.Clock()
        screen = pg.display.set_mode(WINDOW_SIZE)

        playboard = Playboard(screen)

        run = True
        while run:
            clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    playboard.button_down(event.button, event.pos)
                if event.type == pg.MOUSEBUTTONUP:
                    playboard.button_up(event.button, event.pos)

        pg.quit()
