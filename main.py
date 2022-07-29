import os
import sys
import numpy as np
import cv2
import matplotlib

from PySide6.QtGui import Qt

from matplotlib import pyplot as plt
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import *
matplotlib.use('qt5agg')


class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "GUI\\dialog.ui"), self)
        self.lbl = QLabel()
        self.lbl.mousePressEvent = self.goScale
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.lbl)
        scroll_area.setWidgetResizable(True)
        grid = QGridLayout()
        grid.addWidget(scroll_area, 0, 0)
        self.setLayout(grid)

    def goScale(self, event):
        if event.button() == Qt.RightButton:
            self.pixmap = self.pixmap.scaled(self.w//2, self.h//2)
            self.w //= 2
            self.h //= 2
        if event.button() == Qt.LeftButton:
            self.pixmap = self.pixmap.scaled(self.w * 2, self.h * 2)
            self.w *= 2
            self.h *= 2
        self.lbl.clear()
        self.lbl.setPixmap(self.pixmap)

    def set_image(self, image):
        self.image = image
        self.pixmap = convert(image)
        self.lbl.setPixmap(self.pixmap)
        self.w = self.pixmap.width()
        self.h = self.pixmap.height()


class MainWindow(QtWidgets.QMainWindow):
    G_height = 3
    G_width = 3
    sigma1 = 1
    sigma2 = 1
    image_ = []
    kernel1 = np.array([[0, 1, 0],
                        [1, -4, 1],
                        [0, 1, 0]])

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "GUI\\6.ui"), self)
        self.set_icon()
        self.menu_ = {}
        self.getItems()
        self.connect()
        self.filename = 'media/photos/i.jpg'
        self.set_image()

    def getItems(self):
        self.menu_ = {'download': self.down_2,
            'save': {
                'RGB': self.RGB,
                'Luv': self.Luv,
                'Grey': self.Grey,
                'ContrastGrey': self.ContrastGrey,
                'MedianFilter': self.MedianFilter,
                'GauseFilter':  self.GauseFilter,
                'IndividualFilter':  self.IndividualFilter
            },
            'graphics': {
                'Grey': self.greyHistrogram,
                'GreyContrastHist': self.greyContrastHist,
                'R_Hist': self.R_Hist,
                'G_Hist': self.G_Hist,
                'B_Hist': self.B_Hist,
                'L_Hist': self.L_Hist,
                'u_Hist': self.u_Hist,
                'v_Hist': self.v_Hist
            }
        }

    def connect(self):
        self.menu_['download'].triggered.connect(self.open_file)
        for item in self.menu_['save'].values():
            item.triggered.connect(self.save_image)
        for item in self.menu_['graphics'].values():
            item.triggered.connect(self.histogram)
        self.pushButton.clicked.connect(self.OnBtnClick)
        labels = [self.RGB_2, self.Luv_2, self.Grey_2, self.ContrastGrey_2,self.MedianFilter_2, self.GauseFilter_2,self.IndividualFilter_2]
        for item in labels:
            item.mousePressEvent = self.scale
        self.scaleM.triggered.connect(self.msg_box)

    def msg_box(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Для масштабирования нажмите на первую картинку")
        msg.setWindowTitle("Масшатбирование")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def scale(self, event):
        dialog = Dialog(self)
        dialog.set_image(self.image_)
        dialog.exec_()

    def save_image(self, action):
        sender = self.sender()
        name = str(sender.objectName() + '_2')
        label = self.findChild(QtWidgets.QLabel, name)
        label.pixmap().save('media/savedImages/' + name.strip('_2') + '.png')

    def OnBtnClick(self):
        self.G_height = int(self.plainTextEdit_4.toPlainText())
        self.G_width = int(self.plainTextEdit_3.toPlainText())
        self.sigma1 = int(self.plainTextEdit_5.toPlainText())
        self.sigma2 = int(self.plainTextEdit_6.toPlainText())
        self.GauseFilter_2.clear()
        self.GauseFilter_2.setPixmap(convert(cv2.GaussianBlur(self.image_, (self.G_height, self.G_width), self.sigma1, self.sigma2)))

    def open_file(self):
        self.filename = str(QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.path.join(os.path.dirname(__file__), 'media\\photos'))[0])

        self.set_image()

    def set_icon(self):
        appIcon = QIcon('media/icons/icons8-пустой-фильтр-50.png')
        self.setWindowIcon(appIcon)

    def set_image(self):
        self.image_ = cv2.imread(self.filename)
        self.RGB_2.setPixmap(convert(self.image_))
        self.Luv = cv2.cvtColor(self.image_, cv2.COLOR_RGB2Luv)
        self.Luv_2.setPixmap(convert(self.Luv))
        self.grey = cv2.cvtColor(self.image_, cv2.COLOR_RGB2GRAY)
        self.Grey_2.setPixmap(convert(self.grey))
        self.contrastGrey = self.linear_contrast(self.grey)
        self.ContrastGrey_2.setPixmap(convert(self.contrastGrey))
        self.MedianFilter_2.setPixmap(convert(cv2.medianBlur(self.image_, 11)))
        self.GauseFilter_2.setPixmap(convert(cv2.GaussianBlur(self.image_, (self.G_height, self.G_width), self.sigma1, self.sigma2)))
        self.IndividualFilter_2.setPixmap(convert(cv2.filter2D(self.image_, -2, self.kernel1)))

    def linear_contrast(self, gray_img):
        a, b = 1.5, 10
        new_img2 = np.ones((gray_img.shape[0], gray_img.shape[1]), dtype=np.uint8)
        for i in range(new_img2.shape[0]):
            for j in range(new_img2.shape[1]):
                if gray_img[i][j] * a + b > 255:
                    new_img2[i][j] = 255
                else:
                    new_img2[i][j] = gray_img[i][j] * a + b
        return new_img2

    def histogram(self):
        color = ''
        mng = plt.get_current_fig_manager()
        mng.set_window_title('Графики')
        if self.sender().objectName() == 'greyHistrogram':
            hist = cv2.calcHist([self.grey], [0], None, [256], [0, 256])
            color = 'grey'
            plt.title('Гистограмма для серого цвета')

        if self.sender().objectName() == 'greyContrastHist':
            hist = cv2.calcHist([self.contrastGrey], [0], None, [256], [0, 256])
            color = 'grey'
            plt.title('Гистограмма для контрастного серого цвета')

        if self.sender().objectName() == 'R_Hist':
            hist = cv2.calcHist([self.image_], [2], None, [256], [0, 256])
            color = 'r'
            plt.title('Гистограмма для красного цвета')

        if self.sender().objectName() == 'B_Hist':
            hist = cv2.calcHist([self.image_], [0], None, [256], [0, 256])
            color = 'b'
            plt.title('Гистограмма для красного цвета')

        if self.sender().objectName() == 'G_Hist':
            hist = cv2.calcHist([self.image_], [1], None, [256], [0, 256])
            color = 'g'
            plt.title('Гистограмма для красного цвета')

        if self.sender().objectName() == 'L_Hist':
            hist = cv2.calcHist([self.Luv], [0], None, [256], [0,256])
            color = 'hotpink'
            plt.title('Гистограмма для канала L')
        if self.sender().objectName() == 'u_Hist':
            hist = cv2.calcHist([self.Luv], [1], None, [256], [0, 256])
            color = 'darkviolet'
            plt.title('Гистограмма для канала u')

        if self.sender().objectName() == 'v_Hist':
            hist = cv2.calcHist([self.Luv], [2], None, [256], [0, 256])
            color = 'mediumblue'
            plt.title('Гистограмма для канала v')

        plt.plot(hist, color=color)
        plt.show()


def convert(image):
    im_resize = cv2.resize(image, (500, 500))
    is_success, im_buf_arr = cv2.imencode(".jpg", im_resize)
    qp = QPixmap()
    qp.loadFromData(im_buf_arr)
    return qp


def main():
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.showMaximized()
    app.exec_()


if __name__ == '__main__':
    main()
