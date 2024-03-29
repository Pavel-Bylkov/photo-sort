# -*- coding: utf-8 -*-
# ToDo Добавить обработку нажатия Кнопок убрать из списка и Удалить
#! ToDo Доработать функции поворота фотографий - затирают метаданные
# возможное решение
# https://stackoverflow.com/questions/8770121/copying-and-writing-exif-information-from-one-image-to-another-using-pyexiv2
# ToDo Добавить Обработку выбора опций с видео файлами и передачу их в Прогресс


import os
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QProgressBar,
    QPushButton, QLineEdit, QGroupBox,
    QCheckBox, QRadioButton, QListWidget,
    QHBoxLayout, QVBoxLayout, QFileDialog,
    QMessageBox, QAbstractItemView)
from PyQt5.QtGui import QPixmap, QPalette, QColor

from PIL import Image
from hashlib import md5
from uuid import uuid4
from datetime import datetime as dt

from src.config import *
from src.languages import lang1, lang2

log_file = "log.txt"

def log_save(msg):
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"{msg}\n")


class File:
    def __init__(self, path, filename):
        """Получить объект с набором необходимых характеристик файла"""
        self.name = filename
        self.path = path
        self.dir = path.split(os.sep)[-1]
        self.abs_path = os.path.join(path, filename)
        self.ext = os.path.splitext(filename.lower())[1]
        self.is_image = self.ext in img_ext
        self.is_video = self.ext in video_ext
        self.date = self.get_date()
        self.year = self.date[:4]
        self.month = self.date[5:7]
        self.size = os.stat(self.abs_path).st_size / (1024 * 1024)
        self.exif = None
        self.info = None

    def __eq__(self, other):
        if self.name.lower() != other.name.lower() or self.size != other.size:
            return False
        with open(self.abs_path, "rb") as test1:
            m = md5()
            m.update(test1.read())
            original_md5 = m.hexdigest()
        with open(other.abs_path, "rb") as test2:
            m = md5()
            m.update(test2.read())
            duplicate_md5 = m.hexdigest()
        return original_md5 == duplicate_md5

    def rename(self):
        unic_key = str(uuid4().hex)[:6]
        new_name = os.path.splitext(self.name)[0] + unic_key + self.ext
        os.rename(self.abs_path, os.path.join(self.path, new_name))
        self.abs_path = os.path.join(self.path, new_name)
        self.name = new_name
        return new_name

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def open_image(self):
        if self.is_image:
            try:
                with Image.open(self.abs_path) as image:
                    self.img_size = f'{image.size[0]} x {image.size[1]}'
                return True
            except:
                log_save(f"Ошибка при просмотре изображения {self.abs_path}")
        return False

    def get_date(self):
        """Returns the date and time from image(if available) from
            Orthallelous original source
            https://orthallelous.wordpress.com/2015/04/19/extracting-\
            date-and-time-from-images-with-python/"""
        if self.is_image:
            dat = None
            # for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2,2.3
            tags = [
                (36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
                # when img taken
                (36868, 37522),  # (DateTimeDigitized, SubsecTimeDigitized)
                # when img stored digitally
                (306, 37520), ]  # (DateTime, SubsecTime)#when file was changed
            try:
                with Image.open(self.abs_path) as image:
                    self.exif = image._getexif()
                    if self.exif:
                        for tag in tags:
                            dat = self.exif.get(tag[0])
                            # sub = exif.get(tag[1], 0)
                            # PIL.PILLOW_VERSION >= 3.0 returns a tuple
                            dat = dat[0] if type(dat) == tuple else dat
                            # sub = sub[0] if type(sub) == tuple else sub
                            if dat is not None:
                                break
                        if dat is None:
                            t = os.path.getmtime(self.abs_path)
                            return str(dt.fromtimestamp(t))[:16]
                        if str(dat)[:4] != '0000':
                            return str(dat)
            except:
                log_save(f"Ошибка при получении даты изображения {self.abs_path}")
        t = os.path.getmtime(self.abs_path)
        return str(dt.fromtimestamp(t))[:16]

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def do_flip(self):
        if self.is_image:
            with Image.open(self.abs_path) as image:
                new_image = image.transpose(Image.FLIP_LEFT_RIGHT)
                new_image._exif = self.exif
                new_image.save(self.abs_path)

    def do_left(self):
        if self.is_image:
            with Image.open(self.abs_path) as image:
                new_image = image.transpose(Image.ROTATE_90)
                new_image._exif = self.exif
                new_image.save(self.abs_path)

    def do_right(self):
        if self.is_image:
            with Image.open(self.abs_path) as image:
                new_image = image.transpose(Image.ROTATE_270)
                new_image._exif = self.exif
                new_image.save(self.abs_path)

    def mkdir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def move(self, new_path):
        """Перемещение файла"""
        try:
            new_path = f'{new_path}{os.sep}{self.year}{os.sep}{self.month}'
            self.mkdir(new_path)
            shutil.move(self.abs_path, f'{new_path}{os.sep}{self.name}')
            return "OK"
        except:
            return "Error 3"

    def copy(self, new_path):
        """Копирование файла. Чтобы сохранить все метаданные файла,
            используется shutil.copy2()"""
        try:
            new_path = f'{new_path}{os.sep}{self.year}{os.sep}{self.month}'
            self.mkdir(new_path)
            shutil.copy2(self.abs_path, f'{new_path}{os.sep}{self.name}')
            return "OK"
        except:
            if shutil.disk_usage(new_path).free < os.stat(self.abs_path).st_size:
                return "Error 1"
            return "Error 2"


class Progress(QWidget):

    def __init__(self, title, selected_files, new_path, action,
                 parent=None, flags=Qt.WindowFlags()):
        """Окно для визуализации прогресса"""
        super().__init__(parent=parent, flags=flags)

        self.selected_files = selected_files
        self.filenames = list(selected_files.keys())
        self.new_path = new_path
        self.action = action
        self.pause = False
        self.step = 0
        self.max_step = len(self.selected_files)
        self.run = True

        # создаём и настраиваем графические элементы:
        self.init_ui()

        # устанавливает связи между элементами
        self.connects()

        # устанавливает, как будет выглядеть окно (надпись, размер)
        self.set_appear(title)

        # старт:
        self.show()
        self.process()

    def init_ui(self):
        """Создаем виджеты"""
        self.lb_pbar = QLabel("Прогресс сортировки:")
        self.pbar = QProgressBar(self)
        self.pbar.setRange(0, self.max_step - 1)
        self.pbar.setValue(0)
        self.btn_pause = QPushButton('Пауза')
        self.btn_cancel = QPushButton('Отмена')
        self.lay_widgets()

    def lay_widgets(self):
        """ Привязка виджетов к линиям и окну"""
        main_col = QVBoxLayout()  # Основная вертикальная линия
        main_col.addWidget(self.lb_pbar)
        main_col.addWidget(self.pbar)
        row = QHBoxLayout()
        row.addWidget(self.btn_pause)
        row.addWidget(self.btn_cancel)
        main_col.addLayout(row)
        self.setLayout(main_col)

    def connects(self):
        self.btn_pause.clicked.connect(self.do_pause)
        self.btn_cancel.clicked.connect(self.stop)


    def set_appear(self, title):
        """устанавливает, как будет выглядеть окно (надпись, размер)"""
        self.setWindowTitle(title)
        self.resize(700, 300)

    def stop(self):
        self.run = False
        self.hide()

    def do_pause(self):
        if self.pause:
            self.pause = False
            self.btn_pause.setText("Пауза")
        else:
            self.pause = True
            self.btn_pause.setText("Продолжить")

    def next_step(self):
        if self.step == self.max_step - 1:
            self.run = False
            self.btn_cancel.setText('Завершить')
            return

        self.step = self.step + 1
        self.pbar.setValue(self.step)

    def process(self):
        while self.run:
            if not self.pause:
                file = self.selected_files[self.filenames[self.step]]
                self.do_action(file)
                self.next_step()

    def do_action(self, file):
        if self.action == "copy":
            error = file.copy(self.new_path)
        else:
            error = file.move(self.new_path)
        if error == "Error 1":
            log_save(f"Ошибка копирования {file.name}. "
                     f"Недостаточно места на диске {self.new_path}")
            self.run = False
            QMessageBox.warning(self, "Ошибка копирования",
                                f"Недостаточно места на диске {self.new_path}")
        elif error == "Error 2":
            log_save(f"Ошибка копирования {file.abs_path} -> {self.new_path}")
        elif error == "Error 3":
            log_save(f"Ошибка перемещения {file.abs_path} -> {self.new_path}")


class MainWindow(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        """Главное окно программы"""
        super().__init__(parent=parent, flags=flags)

        self.workdir = ""
        self.new_dir = ""
        self.filename = ""
        self.widgets = {}
        self.files = {}
        self.selected_files = {}

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
        self.lb_main = QLabel(lang1["lb_main"][cur_lang])
        self.widgets["lb_main"] = self.lb_main
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
        # setting selection mode property
        self.lw_ext.setSelectionMode(QAbstractItemView.MultiSelection)
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
        self.btn_disable = QPushButton(lang1["btn_disable"][cur_lang])
        self.widgets["btn_disable"] = self.btn_disable
        self.btn_del = QPushButton(lang1["btn_del"][cur_lang])
        self.widgets["btn_del"] = self.btn_del
        self.gb_mode = QGroupBox(lang2["gb_mode"][cur_lang])
        self.rbtn_move = QRadioButton(lang1["rbtn_move"][cur_lang])
        self.rbtn_move.setChecked(True)
        self.widgets["rbtn_move"] = self.rbtn_move
        self.rbtn_move_to = QRadioButton(lang1["rbtn_move_to"][cur_lang])
        self.widgets["rbtn_move_to"] = self.rbtn_move_to
        self.rbtn_copy_to = QRadioButton(lang1["rbtn_copy_to"][cur_lang])
        self.widgets["rbtn_copy_to"] = self.rbtn_copy_to
        self.gb_video = QGroupBox(lang2["gb_video"][cur_lang])
        self.rbtn_1 = QRadioButton(lang1["rbtn_1"][cur_lang])
        self.rbtn_1.setChecked(True)
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
        row0.addWidget(self.lb_main, 90, alignment=Qt.AlignCenter)
        row0.addStretch(2)
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
        row6.addStretch(20)
        row6.addWidget(self.btn_left)
        row6.addWidget(self.btn_right)
        row6.addWidget(self.btn_flip)
        row6.addStretch(5)
        row6.addWidget(self.btn_disable)
        row6.addStretch(2)
        row6.addWidget(self.btn_del)
        row6.addStretch(2)
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
        self.gb_video.setLayout(row4)
        row7.addWidget(self.gb_video, 80)
        col6 = QVBoxLayout()
        col6.addWidget(self.btn_run, alignment=Qt.AlignBottom)
        row7.addLayout(col6, 20)

        row8 = QHBoxLayout()
        row8.addWidget(self.rbtn_move_to)
        row8.addWidget(self.rbtn_copy_to)
        row8.addWidget(self.rbtn_move)
        self.gb_mode.setLayout(row8)

        main_col.addLayout(row0)
        main_col.addLayout(row1)
        main_col.addLayout(row2)
        main_col.addWidget(self.gb_mode)
        main_col.addLayout(row3)
        main_col.addLayout(row7)

        self.setLayout(main_col)

    def run_click(self):
        action = "copy" if self.rbtn_copy_to.isChecked() else "move"
        if self.new_dir:
            title = lang2["copy"][cur_lang] if action == "copy" else lang2["move"][cur_lang]
            self.progress = Progress(title, self.selected_files, self.new_dir, action)
        else:
            QMessageBox.warning(
                self, lang2["msg"][cur_lang], lang2["msg_path"][cur_lang])

    def connects(self):
        self.btn_run.clicked.connect(self.run_click)
        self.path_from.editingFinished.connect(self.open_folder_from2)
        self.btn_from.clicked.connect(self.open_folder_from)
        self.btn_flip.clicked.connect(self.do_flip)
        self.btn_left.clicked.connect(self.do_left)
        self.btn_right.clicked.connect(self.do_right)
        self.lw_files.itemClicked.connect(self.show_chosen_image)
        self.lw_ext.itemClicked.connect(self.filter)
        self.lw_dirs.doubleClicked.connect(self.change_folder_from)
        self.lang_switch.clicked.connect(self.lang_click)
        self.rbtn_move.toggled.connect(self.set_folder_to)
        self.path_to.editingFinished.connect(self.choose_folder_to2)
        self.btn_to.clicked.connect(self.choose_folder_to)

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
        self.gb_video.setTitle(lang2["gb_video"][cur_lang])
        self.file_info.setTitle(lang2["file_info"][cur_lang])

    def choose_workdir(self):
        self.workdir = QFileDialog.getExistingDirectory()
        if self.workdir is None or self.workdir == "":
            return False
        return True

    def update_lw_files(self):
        self.lw_files.clear()
        self.lw_files.addItems(self.selected_files)
        self.lw_files.sortItems()
        self.lb_info.setText(
            lang2["lb_info"][cur_lang].format(len(self.selected_files)))

    def filter(self):
        """ Функция вызывается при выборе типа файла в списке Типов файлов, меняет
        содержимое списка Выбранных файлов и вызывает обновление списка файлов в виджете lw_files"""
        if self.lw_ext.selectedItems():
            self.selected_ext = [item.text() for item in self.lw_ext.selectedItems()]
            self.selected_files = {
                filename: self.files[filename] for filename in self.files
                if self.files[filename].ext in self.selected_ext}
            self.update_lw_files()

    def add_in_files(self, root, filename):
        f = File(root, filename)
        if f.ext and f.ext not in ignor_ext:
            if filename not in self.files:
                self.files[filename] = f
            elif not self.files[filename] == f:
                new_name = f.rename()
                self.files[new_name] = f
            if f.ext not in self.extensions:
                self.extensions.append(f.ext)

    def set_folder_from(self):
        self.lw_dirs.clear()
        self.lw_ext.clear()
        self.lw_files.clear()
        self.path_from.setText(self.workdir)
        self.extensions = []
        self.files = {}
        self.dirs = []
        for root, dirs, files in os.walk(self.workdir):
            for file in files:
                self.add_in_files(root, file)
            if root == self.workdir:
                self.dirs = dirs[:]
        self.lw_dirs.addItem("..")
        self.lw_dirs.addItems(sorted(self.dirs))
        self.lw_ext.addItems(sorted(self.extensions))

    def open_folder_from(self):
        if self.choose_workdir():
            self.set_folder_from()
            self.set_folder_to()
        else:
            QMessageBox.warning(
                self, lang2["msg"][cur_lang], lang2["msg_path"][cur_lang])

    def open_folder_from2(self):
        if self.path_from.text():
            if os.path.exists(self.path_from.text()):
                self.workdir = self.path_from.text()
                self.set_folder_from()
                self.set_folder_to()
            else:
                QMessageBox.warning(
                    self, lang2["msg"][cur_lang], lang2["msg_path"][cur_lang])

    def choose_folder_to(self):
        self.new_dir = QFileDialog.getExistingDirectory()
        if self.new_dir is not None and self.new_dir != "":
            self.path_to.setText(self.new_dir)
        else:
            QMessageBox.warning(
                self, lang2["msg"][cur_lang], lang2["msg_path"][cur_lang])

    def choose_folder_to2(self):
        if self.path_to.text():
            self.new_dir = self.path_to.text()
        else:
            QMessageBox.warning(
                self, lang2["msg"][cur_lang], lang2["msg_path"][cur_lang])

    def set_folder_to(self):
        if self.rbtn_move.isChecked():
            self.path_to.setText(self.workdir)
            self.new_dir = self.path_to.text()

    def change_folder_from(self):
        if self.lw_dirs.selectedItems():
            key = self.lw_dirs.selectedItems()[0].text()
            if key == "..":
                self.workdir = self.workdir[:self.workdir.rfind(os.sep)]
            else:
                self.workdir = self.workdir + os.sep + key
            self.set_folder_from()

    def load_image(self):
        file = self.selected_files[self.filename]
        if file.open_image():
            self.lb_ratio.setText(f'{lang1["lb_ratio"][cur_lang]}{file.img_size}')
            self.show_image(file.abs_path)
        else:
            self.lb_image.clear()
            self.lb_image.setText(lang1["lb_image"][cur_lang])
            self.lb_ratio.setText(lang1["lb_ratio"][cur_lang])
        self.lb_filesize.setText(
            f'{lang1["lb_filesize"][cur_lang]}{round(file.size, 3)} MBytes')
        self.lb_data.setText(f'{lang1["lb_data"][cur_lang]} {file.date}')

    def show_image(self, path):
        self.lb_image.hide()
        pixmapimage = QPixmap(path)
        w, h = self.lb_image.width(), self.lb_image.height()
        pixmapimage = pixmapimage.scaled(w, h, Qt.KeepAspectRatio)
        self.lb_image.setPixmap(pixmapimage)
        self.lb_image.show()

    def show_chosen_image(self):
        if self.lw_files.selectedItems():
            self.filename = self.lw_files.selectedItems()[0].text()
            self.load_image()

    def do_flip(self):
        if self.filename:
            file = self.selected_files[self.filename]
            file.do_flip()
            self.load_image()

    def do_left(self):
        if self.filename:
            file = self.selected_files[self.filename]
            file.do_left()
            self.load_image()

    def do_right(self):
        if self.filename:
            file = self.selected_files[self.filename]
            file.do_right()
            self.load_image()

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
    log_save(f"Start session {dt.strftime(dt.now(), '%A, %d %B %Y %I:%M%p')}")
    app = QApp([])
    mw = MainWindow()
    mw.show()

    app.exec_()


main()
