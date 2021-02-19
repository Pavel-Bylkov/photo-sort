# -*- coding: utf-8 -*-

import os
import time
import datetime
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QGroupBox, QCheckBox,
                             QRadioButton, QListWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QPalette, QColor

from PIL import Image

main_win = None


class FileProcessor:
    def __init__(self):
        self.image = None
        self.workdir = ""
        self.filename = ""
        self.save_dir = ""
        self.img_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        self.numfiles = 0

    def choose_workdir(self):
        self.workdir = QFileDialog.getExistingDirectory()
        if self.workdir is None or self.workdir == "":
            return False
        return True

    def filter(self):
        lw_files.clear()
        self.filenames = {}
        self.extensions = []  # заменить на выделенные
        for root, dirs, files in os.walk(self.workdir):
            for file in files:
                ext = os.path.splitext(file.lower())[1]
                if ext in self.extensions:
                    self.filenames[file] = root
        lw_files.addItems(sorted(self.filenames.keys()))
        self.numfiles = len(self.filenames)
        lb_info.setText(f"Выбрано {self.numfiles} файлов")

    def set_folder_from(self):
        path_from.setText(self.workdir)
        self.extensions = []
        self.filenames = {}
        self.dirs = []
        for root, dirs, files in os.walk(self.workdir):
            for file in files:
                ext = os.path.splitext(file.lower())[1]
                if ext:
                    self.filenames[file] = root
                    if ext not in self.extensions:
                        self.extensions.append(ext)
            if root == self.workdir:
                self.dirs = dirs
        lw_dirs.clear()
        lw_dirs.addItem("..")
        lw_dirs.addItems(sorted(self.dirs))
        lw_files.clear()
        lw_files.addItems(sorted(self.filenames.keys()))
        lw_ext.clear()
        lw_ext.addItems(sorted(self.extensions))
        self.numfiles = len(self.filenames)
        lb_info.setText(f"Выбрано {self.numfiles} файлов")

    def open_folder_from(self):
        if self.choose_workdir():
            self.set_folder_from()
        else:
            QMessageBox.warning(main_win, "Уведомление", "Указан неверный путь! Введите полный путь к папке.")

    def open_folder_from2(self):
        if path_from.text():
            if os.path.exists(path_from.text()):
                self.workdir = path_from.text()
                self.set_folder_from()
            else:
                QMessageBox.warning(main_win, "Уведомление", "Указан неверный путь! Введите полный путь к папке.")

    def change_folder_from(self):
        if lw_dirs.selectedItems():
            key = lw_dirs.selectedItems()[0].text()
            if key == "..":
                self.workdir = self.workdir[:self.workdir.rfind(os.sep)]
            else:
                self.workdir = self.workdir + os.sep + key
            self.set_folder_from()

    def load_image(self):
        if self.filename in self.filenames:
            self.img_dir = self.filenames[self.filename]
            self.image_path = os.path.join(self.img_dir, self.filename)  #
            self.image = Image.open(self.image_path)
        else:
            self.image_path = ""

    def show_image(self):
        if self.image_path:
            lb_image.hide()
            pixmapimage = QPixmap(self.image_path)
            w, h = lb_image.width(), lb_image.height()
            pixmapimage = pixmapimage.scaled(w, h, Qt.KeepAspectRatio)
            lb_image.setPixmap(pixmapimage)
            lb_image.show()

    def save_image(self):
        ''' сохраняет копию файла в подпапке '''
        path = os.path.join(self.dir, self.save_dir)
        if not (os.path.exists(path) or os.path.isdir(path)):
            os.mkdir(path)
        image_path = os.path.join(path, self.filename)
        self.image.save(image_path)

    def get_date_taken(self):
        return self.image._getexif()[36867]  # дату лучше брать из Exif.Image.DateTime

    def show_chosen_image(self):
        if lw_files.selectedItems():
            self.filename = lw_files.selectedItems()[0].text()
            ext = os.path.splitext(self.filename.lower())[1]
            if ext != "" and ext in self.img_ext:
                self.load_image()
                self.show_image()


def create_month_folders():
    """Функция создает папки месяцев от 01 до 12"""
    for x in range(1, 13):  # '{0:02d}'.format(x) где x — месяц от 1 до 12
        # if os.path.exists(f'{i:02}') else os.makedirs(f'{i:02}')
        if x > 9:
            if not os.path.exists(str(x)):
                os.makedirs(str(x))
        else:
            if not os.path.exists(f'0{x}'):
                os.makedirs(f'0{x}')


def mod_date(file):
    t = os.path.getmtime(file)
    return datetime.datetime.fromtimestamp(t)


def create_folders(path_from, path_to):
    """пройдясь по папке, функция соберет все расширения файлов, а заодно,
        определит какой год у файла. Для каждого года будет создана своя папка, а в ней,
        в свою очередь, будут созданы папки с месяцами"""
    os.chdir(path_from)
    a = []  # ['AAE', 'MOV', 'JPG', 'PNG']
    for root, dirs, files in os.walk(path_from):
        for file in files:
            if os.path.splitext(file)[1].lower() not in a:  # проверить нужен ли метод
                a.append(os.path.splitext(file)[1].lower())
            if os.path.splitext(file)[1] in a:
                year = str(mod_date(file))[:10][:4]
                if not os.path.exists(f'{path_to}{os.sep}{year}'):
                    os.makedirs(f'{path_to}{os.sep}{year}')
                os.chdir(f'{path_to}{os.sep}{year}')
                create_month_folders()
                os.chdir(path_from)
    return a


def move_files(path, a):
    """Функция пройдется по папке со свалкой фото, перенося фото в соответствующие папки"""
    os.chdir(path)
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file[-3:] in a:
                    year = str(mod_date(file))[:10][:4]
                    month = str(mod_date(file))[:10][5:7]  # месяц создания фото
                    shutil.move(file, f'{year}{os.sep}{month}{os.sep}{file}')  # перенос файла в папку
    except EnvironmentError:
        ('Вроде готово')  # программа завершается с ошибкой, в цикле не найдя последнего файла


def main():
    global main_win

    def create_widgets():
        """Создаем виджеты для приложения"""
        global lb_image, lb_from, btn_from, path_from, lb_to, btn_to, path_to, lw_dirs, lw_files, file_info, lb_filesize
        global btn_left, btn_right, btn_flip, btn_save, check_copy, rbtn_1, rbtn_2, rbtn_3, RadioGroupBox, lb_ratio, lb_data
        global lw_ext, lb_dirs, lb_files, lb_ext, lb_info

        lb_image = QLabel("Выберите файл для просмотра")
        lb_from = QLabel("Источник:")
        btn_from = QPushButton("Выбор папки")
        path_from = QLineEdit("")
        path_from.setPlaceholderText("Введите путь или нажмите выбрать")
        lb_to = QLabel("Результат:")
        btn_to = QPushButton("Выбор папки")
        path_to = QLineEdit("")
        path_to.setPlaceholderText("Введите путь или нажмите выбрать")
        lb_dirs = QLabel("Список папок")
        lw_dirs = QListWidget()
        lb_files = QLabel("Список файлов(+подпапки)")
        lw_files = QListWidget()
        lb_ext = QLabel("Список типов файлов")
        lw_ext = QListWidget()
        lb_info = QLabel("Выбрано 0 файлов")

        file_info = QGroupBox("Информация о файле:")
        lb_filesize = QLabel('Размер файла:')
        lb_ratio = QLabel('Разрешение:')
        lb_data = QLabel("Дата и время изменения:")

        btn_left = QPushButton("Лево")
        btn_right = QPushButton("Право")
        btn_flip = QPushButton("Зеркало")
        btn_save = QPushButton("Применить")

        check_copy = QCheckBox('Сортировать в исходной папке (без копирования)')

        RadioGroupBox = QGroupBox("Обработка видео файлов:")
        rbtn_1 = QRadioButton('Вместе с фото')
        rbtn_2 = QRadioButton('Вместе, но в отдельных папках')
        rbtn_3 = QRadioButton('Отсортировать отдельно')

    def layout_widgets():
        """ Привязка виджетов к линиям и главному окну"""
        main_col = QVBoxLayout()  # Основная вертикальная линия
        row1 = QHBoxLayout()
        row1.addWidget(lb_from)
        row1.addWidget(path_from)
        row1.addWidget(btn_from)

        row2 = QHBoxLayout()
        col4 = QVBoxLayout()
        col4.addWidget(lb_dirs)
        col4.addWidget(lw_dirs, 50)
        col4.addWidget(lb_ext)
        col4.addWidget(lw_ext, 50)
        row2.addLayout(col4, 20)
        col5 = QVBoxLayout()
        col5.addWidget(lb_files)
        col5.addWidget(lw_files, 80)
        col5.addWidget(lb_info)
        row2.addLayout(col5, 20)
        col1 = QVBoxLayout()
        row5 = QHBoxLayout()
        col3 = QVBoxLayout()
        col3.addWidget(lb_image, 150, alignment=(Qt.AlignCenter))
        row5.addLayout(col3, 100)
        row6 = QHBoxLayout()
        row6.addWidget(btn_left)
        row6.addWidget(btn_right)
        row6.addWidget(btn_flip)
        row6.addWidget(btn_save)
        col1.addLayout(row6)
        col1.addLayout(row5)
        col_box_info = QVBoxLayout()
        col_box_info.addWidget(lb_filesize, alignment=(Qt.AlignLeft))
        col_box_info.addWidget(lb_ratio, alignment=(Qt.AlignLeft))
        col_box_info.addWidget(lb_data, alignment=(Qt.AlignLeft))
        file_info.setLayout(col_box_info)
        col1.addWidget(file_info)
        row2.addLayout(col1, 70)

        row3 = QHBoxLayout()
        row3.addWidget(lb_to)
        row3.addWidget(path_to)
        row3.addWidget(btn_to)

        row4 = QHBoxLayout()
        row4.addWidget(rbtn_1)
        row4.addWidget(rbtn_2)
        row4.addWidget(rbtn_3)
        RadioGroupBox.setLayout(row4)

        main_col.addLayout(row1)
        main_col.addLayout(row2)
        main_col.addWidget(check_copy)
        main_col.addLayout(row3)
        main_col.addWidget(RadioGroupBox)
        main_win.setLayout(main_col)

    app = QApplication([])

    def set_fusion_style():
        app.setStyle("Fusion")

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

        app.setPalette(dark_palette)

        app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    set_fusion_style()
    main_win = QWidget()
    main_win.resize(1600, 900)
    main_win.setWindowTitle('Smart FotoSwitcher')

    create_widgets()
    layout_widgets()

    workimages = FileProcessor()

    path_from.editingFinished.connect(workimages.open_folder_from2)

    btn_from.clicked.connect(workimages.open_folder_from)

    lw_files.itemClicked.connect(workimages.show_chosen_image)

    lw_dirs.doubleClicked.connect(workimages.change_folder_from)

    main_win.show()
    app.exec_()


main()
