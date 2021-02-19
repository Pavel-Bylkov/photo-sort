# -*- coding: utf-8 -*-

import os
import datetime
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QGroupBox, QCheckBox,
                             QRadioButton, QListWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QPalette, QColor

from PIL import Image

win_width, win_height = 1600, 900
win_title = 'Smart PhotoSwitcher'


class ProgressBarr(QWidget):
    def __init__(self, prog_title, parent=None, flags=Qt.WindowFlags()):
        """Окно для визуализации прогресса"""
        super().__init__(parent=parent, flags=flags)
        self.prog_title = prog_title

        # создаём и настраиваем графические элементы:
        self.initUI()

        # устанавливает связи между элементами
        self.connects()

        # устанавливает, как будет выглядеть окно (надпись, размер)
        self.set_appear()

        # старт:
        self.show()

    def initUI(self):
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

        self.image = None
        self.workdir = ""
        self.filename = ""
        self.save_dir = ""
        self.img_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        self.numfiles = 0

        # создаём и настраиваем графические элементы:
        self.initUI()

        # устанавливает связи между элементами
        self.connects()

        # устанавливает, как будет выглядеть окно (надпись, размер)
        self.set_appear()

        # старт:
        self.show()

    def initUI(self):
        """Создаем виджеты для приложения"""
        self.lb_image = QLabel("Выберите файл для просмотра")
        self.lb_from = QLabel("Источник:")
        self.btn_from = QPushButton("Выбор папки")
        self.path_from = QLineEdit("")
        self.path_from.setPlaceholderText("Введите путь или нажмите выбрать")
        self.lb_to = QLabel("Результат:")
        self.btn_to = QPushButton("Выбор папки")
        self.path_to = QLineEdit("")
        self.path_to.setPlaceholderText("Введите путь или нажмите выбрать")
        self.lb_dirs = QLabel("Список папок")
        self.lw_dirs = QListWidget()
        self.lb_files = QLabel("Список файлов(+подпапки)")
        self.lw_files = QListWidget()
        self.lb_ext = QLabel("Список типов файлов")
        self.lw_ext = QListWidget()
        self.lb_info = QLabel("Выбрано 0 файлов")

        self.file_info = QGroupBox("Информация о файле:")
        self.lb_filesize = QLabel('Размер файла:')
        self.lb_ratio = QLabel('Разрешение:')
        self.lb_data = QLabel("Дата и время изменения:")

        self.btn_left = QPushButton("Лево")
        self.btn_right = QPushButton("Право")
        self.btn_flip = QPushButton("Зеркало")
        self.btn_save = QPushButton("Применить")

        self.check_copy = QCheckBox('Сортировать в исходной папке (без копирования)')

        self.RadioGroupBox = QGroupBox("Обработка видео файлов:")
        self.rbtn_1 = QRadioButton('Вместе с фото')
        self.rbtn_2 = QRadioButton('Вместе, но в отдельных папках')
        self.rbtn_3 = QRadioButton('Отсортировать отдельно')

        self.btn_run = QPushButton("Выполнить")
        self.lay_widgets()

    def lay_widgets(self):
        """ Привязка виджетов к линиям и главному окну"""
        main_col = QVBoxLayout()  # Основная вертикальная линия
        row1 = QHBoxLayout()
        row1.addWidget(self.lb_from)
        row1.addWidget(self.path_from)
        row1.addWidget(self.btn_from)

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
        col3.addWidget(self.lb_image, 150, alignment=(Qt.AlignCenter))
        row5.addLayout(col3, 100)
        row6 = QHBoxLayout()
        row6.addWidget(self.btn_left)
        row6.addWidget(self.btn_right)
        row6.addWidget(self.btn_flip)
        row6.addWidget(self.btn_save)
        col1.addLayout(row6)
        col1.addLayout(row5)
        col_box_info = QVBoxLayout()
        col_box_info.addWidget(self.lb_filesize, alignment=(Qt.AlignLeft))
        col_box_info.addWidget(self.lb_ratio, alignment=(Qt.AlignLeft))
        col_box_info.addWidget(self.lb_data, alignment=(Qt.AlignLeft))
        self.file_info.setLayout(col_box_info)
        col1.addWidget(self.file_info)
        row2.addLayout(col1, 70)

        row3 = QHBoxLayout()
        row3.addWidget(self.lb_to)
        row3.addWidget(self.path_to)
        row3.addWidget(self.btn_to)

        row4 = QHBoxLayout()
        row4.addWidget(self.rbtn_1)
        row4.addWidget(self.rbtn_2)
        row4.addWidget(self.rbtn_3)
        self.RadioGroupBox.setLayout(row4)

        main_col.addLayout(row1)
        main_col.addLayout(row2)
        main_col.addWidget(self.check_copy)
        main_col.addLayout(row3)
        main_col.addWidget(self.RadioGroupBox)

        self.setLayout(main_col)

    def run_click(self):
        if self.action == "copy":
            self.progress = ProgressBarr("Копирование файлов")
        else:
            self.progress = ProgressBarr("Перемещение файлов")
        self.progress.exec()
        # self.hide()

    def connects(self):
        self.btn_run.clicked.connect(self.run_click)
        self.path_from.editingFinished.connect(self.open_folder_from2)
        self.btn_from.clicked.connect(self.open_folder_from)
        self.lw_files.itemClicked.connect(self.show_chosen_image)
        self.lw_dirs.doubleClicked.connect(self.change_folder_from)

    def set_appear(self):
        """устанавливает, как будет выглядеть окно (надпись, размер)"""
        self.setWindowTitle(win_title)
        self.resize(win_width, win_height)

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
        self.lb_info.setText(f"Выбрано {self.numfiles} файлов")

    def set_folder_from(self):
        self.path_from.setText(self.workdir)
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
        self.lw_dirs.clear()
        self.lw_dirs.addItem("..")
        self.lw_dirs.addItems(sorted(self.dirs))
        self.lw_files.clear()
        self.lw_files.addItems(sorted(self.filenames.keys()))
        self.lw_ext.clear()
        self.lw_ext.addItems(sorted(self.extensions))
        self.numfiles = len(self.filenames)
        self.lb_info.setText(f"Выбрано {self.numfiles} файлов")

    def open_folder_from(self):
        if self.choose_workdir():
            self.set_folder_from()
        else:
            QMessageBox.warning(self, "Уведомление", "Указан неверный путь! Введите полный путь к папке.")

    def open_folder_from2(self):
        if self.path_from.text():
            if os.path.exists(self.path_from.text()):
                self.workdir = self.path_from.text()
                self.set_folder_from()
            else:
                QMessageBox.warning(self, "Уведомление", "Указан неверный путь! Введите полный путь к папке.")

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
            self.image_path = os.path.join(self.img_dir, self.filename)  #
            self.image = Image.open(self.image_path)
        else:
            self.image_path = ""

    def show_image(self):
        if self.image_path:
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

    def get_date_taken(self):
        return self.image._getexif()[36867]  # дату лучше брать из Exif.Image.DateTime

    def show_chosen_image(self):
        if self.lw_files.selectedItems():
            self.filename = self.lw_files.selectedItems()[0].text()
            ext = os.path.splitext(self.filename.lower())[1]
            if ext != "" and ext in self.img_ext:
                self.load_image()
                self.show_image()


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

        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


def main():
    app = QApp([])
    mw = MainWindow()
    app.exec_()


main()
