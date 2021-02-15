# -*- coding: utf-8 -*-

import os
import time
import datetime
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QGroupBox, QCheckBox,
                            QRadioButton, QListWidget, QHBoxLayout, QVBoxLayout, QFileDialog)
from PyQt5.QtGui import QPixmap # оптимизированная для показа на экране картинка

from PIL import Image


class ImagesProcessor:
    def __init__(self):
        self.image = None
        self.workdir = ""
        self.filename = ""
        self.filenames = []
        self.save_dir = ""
        self.extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    def choose_workdir(self):
        self.workdir = QFileDialog.getExistingDirectory()
        if self.workdir is None or self.workdir == "":
            return False
        return True

    def filter(self):
        for filename in os.listdir(self.workdir):
            for ext in self.extensions:
                if filename.endswith(ext):
                    self.filenames.append(filename)

    def open_folder_from(self):
        if self.choose_workdir():
            self.filter()
            lw_files.clear()
            for filename in self.filenames:
                lw_files.addItem(filename)

    def load_image(self, cur_dir, filename):
        self.dir = cur_dir
        self.filename = filename
        self.image_path = cur_dir + os.sep + filename  # os.path.join(dir, filename)  #
        self.image = Image.open(self.image_path)

    def show_image(self):
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
            if os.path.splitext(file)[1].lower() not in a:   # проверить нужен ли метод
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
        ('Вроде готово') # программа завершается с ошибкой, в цикле не найдя последнего файла


def main():
    def create_widgets():
        """Создаем виджеты для приложения"""
        global lb_image, lb_from, btn_from, path_from, lb_to, btn_to, path_to, lw_dirs, lw_files, file_info, lb_filesize
        global btn_left, btn_right, btn_flip, btn_save, check_copy, rbtn_1, rbtn_2, rbtn_3, RadioGroupBox, lb_ratio, lb_data

        lb_image = QLabel("Выберите файл для просмотра")
        lb_from = QLabel("Источник:")
        btn_from = QPushButton("Выбор папки")
        path_from = QLineEdit("")
        path_from.setPlaceholderText("Введите путь или нажмите выбрать")
        lb_to = QLabel("Результат:")
        btn_to = QPushButton("Выбор папки")
        path_to = QLineEdit("")
        path_to.setPlaceholderText("Введите путь или нажмите выбрать")
        lw_dirs = QListWidget()
        lw_files = QListWidget()

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
        row2.addWidget(lw_dirs, 50)
        row2.addWidget(lw_files, 50)
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
        row2.addLayout(col1, 150)

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
    main_win = QWidget()
    main_win.resize(1600, 900)
    main_win.setWindowTitle('Smart Foto Folder Switcher')

    create_widgets()
    layout_widgets()

    workimages = ImagesProcessor()

    btn_from.clicked.connect(workimages.open_folder_from)

    def show_chosen_image():
        if lw_files.selectedItems():
            name = lw_files.selectedItems()[0].text()
            workimages.load_image(name)
            workimages.show_image()

    lw_files.itemClicked.connect(show_chosen_image)

    main_win.show()
    app.exec_()


main()