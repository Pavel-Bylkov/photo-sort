# -*- coding: utf-8 -*-

import os
import datetime
# import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel,
    QPushButton, QLineEdit, QGroupBox,
    QCheckBox, QRadioButton, QListWidget,
    QHBoxLayout, QVBoxLayout, QFileDialog,
    QMessageBox)
from PyQt5.QtGui import QPixmap, QPalette, QColor

from PIL import Image
from hashlib import md5
from uuid import uuid4

from config import *


def is_duplicate_md5(file1, file2):
    with open(file1, "rb") as test1:
        m = md5()
        m.update(test1.read())
        original_md5 = m.hexdigest()
    with open(file2, "rb") as test2:
        m = md5()
        m.update(test2.read())
        duplicate_md5 = m.hexdigest()
    return original_md5 == duplicate_md5


class ProgressBarr(QWidget):

    def __init__(self, prog_title, parent=None, flags=Qt.WindowFlags()):
        """Окно для визуализации прогресса"""
        super().__init__(parent=parent, flags=flags)
        self.prog_title = prog_title

        # создаём и настраиваем графические элементы:
        self.init_ui()

        # устанавливает связи между элементами
        self.connects()

        # устанавливает, как будет выглядеть окно (надпись, размер)
        self.set_appear()

        # старт:
        self.show()

    def init_ui(self):
        """Создаем виджеты"""
        pass
        self.lay_widgets()

    def lay_widgets(self):
        """ Привязка виджетов к линиям и окну"""
        main_col = QVBoxLayout()  # Основная вертикальная линия
        self.setLayout(main_col)

    def connects(self):
        pass

    def set_appear(self):
        """устанавливает, как будет выглядеть окно (надпись, размер)"""
        self.setWindowTitle(self.prog_title)
        self.resize(700, 300)


class MainWindow(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        """Главное окно программы"""
        super().__init__(parent=parent, flags=flags)

        self.workdir = ""
        self.filename = ""
        self.save_dir = ""
        self.numfiles = 0
        self.widgets = {}

        # создаём и настраиваем графические элементы:
        self.init_ui()

        # устанавливает связи между элементами
        self.connects()

        # устанавливает, как будет выглядеть окно (надпись, размер)
        self.set_appear()

    def init_ui(self):
        """Создаем виджеты для приложения"""
        self.lb_ru = QLabel("RUS")
        self.lb_en = QLabel("ENG")
        self.lang_switch = QCheckBox()
        self.lang_switch.setStyleSheet('''
            QCheckBox::indicator:unchecked {
                image: url(sw_left.png);
            }
            QCheckBox::indicator:checked {
                image: url(sw_right.png);
            }''')
        self.lb_image = QLabel(lang1["lb_image"][cur_lang])
        self.widgets["lb_image"] = self.lb_image
        self.lb_from = QLabel(lang1["lb_from"][cur_lang])
        self.widgets["lb_from"] = self.lb_from
        self.btn_from = QPushButton(lang1["btn_from"][cur_lang])
        self.widgets["btn_from"] = self.btn_from
        self.path_from = QLineEdit("")
        self.path_from.setPlaceholderText(lang2["path_holder"][cur_lang])
        self.lb_to = QLabel(lang1["lb_to"][cur_lang])
        self.widgets["lb_to"] = self.lb_to
        self.btn_to = QPushButton(lang1["btn_to"][cur_lang])
        self.widgets["btn_to"] = self.btn_to
        self.path_to = QLineEdit("")
        self.path_to.setPlaceholderText(lang2["path_holder"][cur_lang])
        self.lb_dirs = QLabel(lang1["lb_dirs"][cur_lang])
        self.widgets["lb_dirs"] = self.lb_dirs
        self.lw_dirs = QListWidget()
        self.lb_files = QLabel(lang1["lb_files"][cur_lang])
        self.widgets["lb_files"] = self.lb_files
        self.lw_files = QListWidget()
        self.lb_ext = QLabel(lang1["lb_ext"][cur_lang])
        self.widgets["lb_ext"] = self.lb_ext
        self.lw_ext = QListWidget()
        self.lb_info = QLabel(lang2["lb_info"][cur_lang].format(0))
        self.file_info = QGroupBox(lang2["file_info"][cur_lang])
        self.lb_filesize = QLabel(lang1["lb_filesize"][cur_lang])
        self.widgets["lb_filesize"] = self.lb_filesize
        self.lb_ratio = QLabel(lang1["lb_ratio"][cur_lang])
        self.widgets["lb_ratio"] = self.lb_ratio
        self.lb_data = QLabel(lang1["lb_data"][cur_lang])
        self.widgets["lb_data"] = self.lb_data
        self.btn_left = QPushButton(lang1["btn_left"][cur_lang])
        self.widgets["btn_left"] = self.btn_left
        self.btn_right = QPushButton(lang1["btn_right"][cur_lang])
        self.widgets["btn_right"] = self.btn_right
        self.btn_flip = QPushButton(lang1["btn_flip"][cur_lang])
        self.widgets["btn_flip"] = self.btn_flip
        self.btn_save = QPushButton(lang1["btn_save"][cur_lang])
        self.widgets["btn_save"] = self.btn_save
        self.check_copy = QCheckBox(lang1["check_copy"][cur_lang])
        self.widgets["check_copy"] = self.check_copy
        self.RadioGroupBox = QGroupBox(lang2["RadioGroupBox"][cur_lang])
        self.rbtn_1 = QRadioButton(lang1["rbtn_1"][cur_lang])
        self.widgets["rbtn_1"] = self.rbtn_1
        self.rbtn_2 = QRadioButton(lang1["rbtn_2"][cur_lang])
        self.widgets["rbtn_2"] = self.rbtn_2
        self.rbtn_3 = QRadioButton(lang1["rbtn_3"][cur_lang])
        self.widgets["rbtn_3"] = self.rbtn_3
        self.btn_run = QPushButton(lang1["btn_run"][cur_lang])
        self.widgets["btn_run"] = self.btn_run
        self.lay_widgets()

    def lay_widgets(self):
        """ Привязка виджетов к линиям и главному окну"""
        main_col = QVBoxLayout()  # Основная вертикальная линия
        row0 = QHBoxLayout()
        row0.addStretch(92)
        row0.addWidget(self.lb_ru, 2, alignment=Qt.AlignCenter)
        row0.addWidget(self.lang_switch, 4, alignment=Qt.AlignCenter)
        row0.addWidget(self.lb_en, 2, alignment=Qt.AlignLeft)

        row1 = QHBoxLayout()
        row1.addWidget(self.lb_from, 15, alignment=Qt.AlignCenter)
        row1.addWidget(self.path_from, 70)
        row1.addWidget(self.btn_from, 15)

        row2 = QHBoxLayout()
        col4 = QVBoxLayout()
        col4.addWidget(self.lb_dirs)
        col4.addWidget(self.lw_dirs, 50)
        col4.addWidget(self.lb_ext)
        col4.addWidget(self.lw_ext, 50)
        row2.addLayout(col4, 20)
        col5 = QVBoxLayout()
        col5.addWidget(self.lb_files)
        col5.addWidget(self.lw_files, 80)
        col5.addWidget(self.lb_info)
        row2.addLayout(col5, 20)
        col1 = QVBoxLayout()
        row5 = QHBoxLayout()
        col3 = QVBoxLayout()
        col3.addWidget(self.lb_image, 90)  # alignment=Qt.AlignCenter
        row5.addLayout(col3, 100)
        row6 = QHBoxLayout()
        row6.addWidget(self.btn_left)
        row6.addWidget(self.btn_right)
        row6.addWidget(self.btn_flip)
        row6.addWidget(self.btn_save)
        col1.addLayout(row6)
        col1.addLayout(row5)
        col_box_info = QVBoxLayout()
        col_box_info.addWidget(self.lb_filesize, alignment=Qt.AlignLeft)
        col_box_info.addWidget(self.lb_ratio, alignment=Qt.AlignLeft)
        col_box_info.addWidget(self.lb_data, alignment=Qt.AlignLeft)
        self.file_info.setLayout(col_box_info)
        col1.addWidget(self.file_info)
        row2.addLayout(col1, 70)

        row3 = QHBoxLayout()
        row3.addWidget(self.lb_to, 15, alignment=Qt.AlignCenter)
        row3.addWidget(self.path_to, 70)
        row3.addWidget(self.btn_to, 15)

        row7 = QHBoxLayout()
        row4 = QHBoxLayout()
        row4.addWidget(self.rbtn_1)
        row4.addWidget(self.rbtn_2)
        row4.addWidget(self.rbtn_3)
        self.RadioGroupBox.setLayout(row4)
        row7.addWidget(self.RadioGroupBox, 80)
        col6 = QVBoxLayout()
        col6.addWidget(self.btn_run, alignment=Qt.AlignBottom)
        row7.addLayout(col6, 20)

        main_col.addLayout(row0)
        main_col.addLayout(row1)
        main_col.addLayout(row2)
        main_col.addWidget(self.check_copy)
        main_col.addLayout(row3)
        main_col.addLayout(row7)

        self.setLayout(main_col)

    def run_click(self):
        if self.action == "copy":
            self.progress = ProgressBarr(lang2["copy"][cur_lang])
        else:
            self.progress = ProgressBarr(lang2["move"][cur_lang])
        self.progress.exec()
        # self.hide()

    def connects(self):
        self.btn_run.clicked.connect(self.run_click)
        self.path_from.editingFinished.connect(self.open_folder_from2)
        self.btn_from.clicked.connect(self.open_folder_from)
        self.lw_files.itemClicked.connect(self.show_chosen_image)
        self.lw_dirs.doubleClicked.connect(self.change_folder_from)
        self.lang_switch.clicked.connect(self.lang_click)

    def set_appear(self):
        """устанавливает, как будет выглядеть окно (надпись, размер)"""
        self.setWindowTitle(win_title)
        self.resize(win_width, win_height)

    def lang_click(self):
        global cur_lang
        cur_lang = 'ru' if cur_lang == 'en' else 'en'
        for key in lang1:
            self.widgets[key].setText(lang1[key][cur_lang])
        self.path_from.setPlaceholderText(lang2["path_holder"][cur_lang])
        self.path_to.setPlaceholderText(lang2["path_holder"][cur_lang])
        self.lb_info.setText(lang2["lb_info"][cur_lang].format(self.numfiles))
        self.RadioGroupBox.setTitle(lang2["RadioGroupBox"][cur_lang])
        self.file_info.setTitle(lang2["file_info"][cur_lang])

    def choose_workdir(self):
        self.workdir = QFileDialog.getExistingDirectory()
        if self.workdir is None or self.workdir == "":
            return False
        return True

    def filter(self):
        self.lw_files.clear()
        self.filenames = {}
        self.extensions = []  # заменить на выделенные
        for root, dirs, files in os.walk(self.workdir):
            for file in files:
                ext = os.path.splitext(file.lower())[1]
                if ext in self.extensions:
                    self.filenames[file] = root
        self.lw_files.addItems(sorted(self.filenames.keys()))
        self.numfiles = len(self.filenames)
        self.lb_info.setText(lang1["lb_info"][cur_lang].format(self.numfiles))

    def add_file_in_filenames(self, root, file):
        ext = os.path.splitext(file.lower())[1]
        if ext and ext not in ignor_ext:
            if file not in self.filenames:
                self.filenames[file] = root
            elif not is_duplicate_md5(
                    os.path.join(self.filenames[file], file),
                    os.path.join(root, file)):
                unic_key = str(uuid4().hex)[:6]
                new_name = os.path.splitext(file)[0] + unic_key + ext
                os.rename(os.path.join(root, file),
                          os.path.join(root, new_name))
                self.filenames[new_name] = root
            if ext not in self.extensions:
                self.extensions.append(ext)

    def set_folder_from(self):
        self.path_from.setText(self.workdir)
        self.extensions = []
        self.filenames = {}
        self.dirs = []
        for root, dirs, files in os.walk(self.workdir):
            for file in files:
                self.add_file_in_filenames(root, file)
            if root == self.workdir:
                self.dirs = dirs
        self.lw_dirs.clear()
        self.lw_dirs.addItem("..")
        self.lw_dirs.addItems(sorted(self.dirs))
        self.lw_files.clear()
        self.lw_files.addItems(sorted(self.filenames.keys()))
        self.lw_ext.clear()
        self.lw_ext.addItems(sorted(self.extensions))
        self.numfiles = len(self.filenames)
        self.lb_info.setText(lang2["lb_info"][cur_lang].format(self.numfiles))

    def open_folder_from(self):
        if self.choose_workdir():
            self.set_folder_from()
        else:
            QMessageBox.warning(
                self, lang2["msg"][cur_lang], lang2["msg_path"][cur_lang])

    def open_folder_from2(self):
        if self.path_from.text():
            if os.path.exists(self.path_from.text()):
                self.workdir = self.path_from.text()
                self.set_folder_from()
            else:
                QMessageBox.warning(
                    self, lang2["msg"][cur_lang], lang2["msg_path"][cur_lang])

    def change_folder_from(self):
        if self.lw_dirs.selectedItems():
            key = self.lw_dirs.selectedItems()[0].text()
            if key == "..":
                self.workdir = self.workdir[:self.workdir.rfind(os.sep)]
            else:
                self.workdir = self.workdir + os.sep + key
            self.set_folder_from()

    def load_image(self):
        if self.filename in self.filenames:
            self.img_dir = self.filenames[self.filename]
            self.image_path = os.path.join(self.img_dir, self.filename)
            self.image = Image.open(self.image_path)
            file_stats = os.stat(self.image_path)
            self.lb_filesize.setText(
                f'{lang1["lb_filesize"][cur_lang]}'
                f'{round(file_stats.st_size / (1024 * 1024), 3)} MBytes')
            self.lb_ratio.setText(
                f'{lang1["lb_ratio"][cur_lang]}'
                f'{self.image.size[0]} x {self.image.size[1]}')
            self.lb_data.setText(
                f'{lang1["lb_data"][cur_lang]} {self.get_imagedate()}')
            self.show_image()

    def show_image(self):
        self.lb_image.hide()
        pixmapimage = QPixmap(self.image_path)
        w, h = self.lb_image.width(), self.lb_image.height()
        pixmapimage = pixmapimage.scaled(w, h, Qt.KeepAspectRatio)
        self.lb_image.setPixmap(pixmapimage)
        self.lb_image.show()

    def save_image(self):
        """сохраняет копию файла в подпапке"""
        path = os.path.join(self.dir, self.save_dir)
        if not (os.path.exists(path) or os.path.isdir(path)):
            os.mkdir(path)
        image_path = os.path.join(path, self.filename)
        self.image.save(image_path)

    def get_imagedate(self):
        """Returns the date and time from image(if available) from
            Orthallelous original source
            https://orthallelous.wordpress.com/2015/04/19/extracting-\
            date-and-time-from-images-with-python/"""
        dat = None
        # for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2,
        # 2.3
        tags = [(36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
                                 # when img taken
                (36868, 37522),  # (DateTimeDigitized, SubsecTimeDigitized)
                                 # when img stored digitally
                (306, 37520), ]  # (DateTime, SubsecTime)#when file was changed
        exif = self.image._getexif()
        if exif:
            for t in tags:
                dat = exif.get(t[0])
                # sub = exif.get(t[1], 0)
                # PIL.PILLOW_VERSION >= 3.0 returns a tuple
                dat = dat[0] if type(dat) == tuple else dat
                # sub = sub[0] if type(sub) == tuple else sub
                if dat is not None:
                    break
            if dat is None:
                t = os.path.getmtime(self.image_path)
                return str(datetime.datetime.fromtimestamp(t))[:16]
            if str(dat)[:4] != '0000':
                return '{}'.format(dat)
        t = os.path.getmtime(self.image_path)
        return str(datetime.datetime.fromtimestamp(t))[:16]

    def show_chosen_image(self):
        if self.lw_files.selectedItems():
            self.filename = self.lw_files.selectedItems()[0].text()
            ext = os.path.splitext(self.filename.lower())[1]
            if ext != "" and ext in img_ext:
                self.load_image()
            else:
                self.lb_image.clear()
                self.lb_image.setText(lang1["lb_image"][cur_lang])
                file_stats = os.stat(self.image_path)
                self.lb_filesize.setText(
                    f'{lang1["lb_filesize"][cur_lang]}'
                    f'{round(file_stats.st_size / (1024 * 1024), 3)} MBytes')
                self.lb_ratio.setText(lang1["lb_ratio"][cur_lang])
                self.lb_data.setText(lang1["lb_data"][cur_lang])


class QApp(QApplication):
    def __init__(self, list_str):
        super().__init__(list_str)
        self.set_fusion_style()

    def set_fusion_style(self):
        self.setStyle("Fusion")

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(dark_palette)

        self.setStyleSheet("QToolTip { color: #ffffff; "
                           "background-color: #2a82da; "
                           "border: 1px solid white; }")
        font = self.font()
        font.setPointSize(14)
        QApplication.instance().setFont(font)


def main():
    app = QApp([])
    mw = MainWindow()
    mw.show()
    app.exec_()


main()
