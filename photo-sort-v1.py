# -*- coding: utf-8 -*-
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog,QMessageBox
from PyQt5.QtGui import QPixmap

from datetime import datetime as dt

from src.class_file import File
from src.languages import lang1, lang2
from src.interface import QApp, MainWindow, Progress
from src.config import img_ext, video_ext, ignor_ext, lang, log_save


class Sort(Progress):
    def __init__(self, title, selected_files, new_path, action, video_folder,
                 parent=None, flags=Qt.WindowFlags()):
        """Окно для визуализации прогресса"""
        super().__init__(title, parent=parent, flags=flags)

        self.selected_files = selected_files
        self.filenames = list(selected_files.keys())
        self.new_path = new_path
        self.action = action
        self.video_folder = video_folder
        self.pause = False
        self.step = 0
        self.max_step = len(self.selected_files)
        self.pbar.setRange(0, self.max_step - 1)
        self.pbar.setValue(0)
        self.run = True

        # устанавливает связи между элементами
        self.connects()

        self.process()

    def connects(self):
        self.btn_pause.clicked.connect(self.do_pause)
        self.btn_cancel.clicked.connect(self.stop)

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
            error = file.copy(self.new_path, self.video_folder)
        else:
            error = file.move(self.new_path, self.video_folder)
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


class OpenFolder(Progress):
    def __init__(self, title, max_step, parent=None, flags=Qt.WindowFlags()):
        """Окно для визуализации прогресса"""
        super().__init__(title, parent=parent, flags=flags)

        self.pause = False
        self.step = 0
        self.max_step = max_step
        self.pbar.setRange(0, self.max_step - 1)
        self.pbar.setValue(0)
        self.run = True

        # устанавливает связи между элементами
        self.connects()

        self.process()


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
            error = file.copy(self.new_path, self.video_folder)
        else:
            error = file.move(self.new_path, self.video_folder)
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


class Window(MainWindow):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        """Главное окно программы"""
        super().__init__(parent=parent, flags=flags)

        self.lang_switch.setStyleSheet('''
                    QCheckBox::indicator:unchecked {
                        image: url(src/sw_left.png);
                    }
                    QCheckBox::indicator:checked {
                        image: url(src/sw_right.png);
                    }''')

        self.workdir = ""
        self.new_dir = ""
        self.filename = ""
        self.current_file = None
        self.all_files = 0
        self.files = {}
        self.selected_files = {}

        # устанавливает связи между элементами
        self.connects()

    def connects(self):
        self.btn_run.clicked.connect(self.run_click)
        self.path_from.editingFinished.connect(self.open_folder_from2)
        self.btn_from.clicked.connect(self.open_folder_from)
        self.lw_files.itemClicked.connect(self.show_chosen_image)
        self.lw_ext.itemClicked.connect(self.filter)
        self.lw_dirs.doubleClicked.connect(self.change_folder_from)
        self.lang_switch.clicked.connect(self.lang_click)
        self.rbtn_move.toggled.connect(self.set_folder_to)
        self.chbx_all_files.clicked.connect(self.set_all_files)
        self.path_to.editingFinished.connect(self.choose_folder_to2)
        self.btn_to.clicked.connect(self.choose_folder_to)
        self.btn_disable.clicked.connect(self.del_from_files)
        self.btn_del.clicked.connect(self.del_from_disk)

    def run_click(self):
        action = "copy" if self.rbtn_copy_to.isChecked() else "move"
        video_folder = "all"
        if self.rbtn_2.isChecked():
            video_folder = "into"
        if self.rbtn_3.isChecked():
            video_folder = "outside"
        if self.new_dir:
            title = lang2["copy"][lang] if action == "copy" else lang2["move"][lang]
            self.progress = Sort(title, self.selected_files, self.new_dir, action, video_folder)
        else:
            QMessageBox.warning(
                self, lang2["msg"][lang], lang2["msg_path"][lang])

    def lang_click(self):
        global lang
        lang = 'ru' if lang == 'en' else 'en'
        for key in lang1:
            if key in self.widgets and key in lang1:
                self.widgets[key].setText(lang1[key][lang])
        self.path_from.setPlaceholderText(lang2["path_holder"][lang])
        self.path_to.setPlaceholderText(lang2["path_holder"][lang])
        self.lb_info.setText(
            lang2["lb_info"][lang].format(len(self.selected_files)))
        self.gb_video.setTitle(lang2["gb_video"][lang])
        self.file_info.setTitle(lang2["file_info"][lang])

    def choose_workdir(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.workdir = QFileDialog.getExistingDirectory(parent=self, options=options)
        #self.workdir = QFileDialog.getExistingDirectory(parent=self)
        if self.workdir is None or self.workdir == "":
            return False
        return True

    def update_lw_files(self):
        self.lw_files.clear()
        self.lw_files.addItems(self.selected_files)
        self.lw_files.sortItems()
        self.lb_info.setText(
            lang2["lb_info"][lang].format(len(self.selected_files)))

    def filter(self):
        """ Функция вызывается при выборе типа файла в списке Типов файлов, меняет
        содержимое списка Выбранных файлов и вызывает обновление списка файлов в виджете lw_files"""
        if self.lw_ext.selectedItems():
            self.selected_ext = [item.text() for item in self.lw_ext.selectedItems()]
            self.selected_files = {
                filename: self.files[filename] for filename in self.files
                if self.files[filename].ext in self.selected_ext}
            self.update_lw_files()

    def add_in_files(self, root, files):
        for filename in files:
            f = File(root, filename)
            if f.ext in img_ext or f.ext in video_ext:
                if filename not in self.files:
                    self.files[filename] = f
                elif not self.files[filename] == f:
                    new_name = f.rename()
                    self.files[new_name] = f
                if f.ext not in self.extensions:
                    self.extensions.append(f.ext)

    def del_from_files(self):
        if self.lw_files.selectedItems():
            del self.selected_files[self.filename]
            self.filename = ""
            self.current_file = None
            self.update_lw_files()
            self.lb_image.clear()
            self.lb_image.setText(lang1["lb_image"][lang])
            self.lb_ratio_data.setText("")
            self.lb_filesize_data.setText('')
            self.lb_data_data.setText('')

    def del_from_disk(self):
        if self.lw_files.selectedItems():
            file = self.selected_files[self.filename]
            self.del_from_files()
            error = file.kill()
            if error == "Error":
                log_save(f"Ошибка удаления {file.abs_path}.")
                QMessageBox.warning(self, f"Ошибка удаления {file.abs_path}.")


    def set_all_files(self):
        if self.workdir:
            self.set_folder_from()

    def set_folder_from(self):
        self.lw_dirs.clear()
        self.lw_ext.clear()
        self.lw_files.clear()
        self.all_files = sum((len(files) for _, _, files in os.walk(self.workdir)))
        self.path_from.setText(self.workdir)
        self.extensions = []
        self.files = {}
        self.dirs = []
        for root, dirs, files in os.walk(self.workdir):
            if self.chbx_all_files.isChecked() or root == self.workdir:
                    self.add_in_files(root, files)
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
                self, lang2["msg"][lang], lang2["msg_path"][lang])

    def open_folder_from2(self):
        if self.path_from.text():
            if os.path.exists(self.path_from.text()):
                self.workdir = self.path_from.text()
                self.set_folder_from()
                self.set_folder_to()
            else:
                QMessageBox.warning(
                    self, lang2["msg"][lang], lang2["msg_path"][lang])

    def choose_folder_to(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.new_dir = QFileDialog.getExistingDirectory(parent=self, options=options)
        if self.new_dir is not None and self.new_dir != "":
            self.path_to.setText(self.new_dir)
        else:
            QMessageBox.warning(
                self, lang2["msg"][lang], lang2["msg_path"][lang])

    def choose_folder_to2(self):
        if self.path_to.text():
            self.new_dir = self.path_to.text()
        else:
            QMessageBox.warning(
                self, lang2["msg"][lang], lang2["msg_path"][lang])

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

    def show_image(self):
        if self.current_file.is_image:
            try:
                self.lb_image.hide()
                pixmapimage = QPixmap(self.current_file.abs_path)
                w, h = self.lb_image.width(), self.lb_image.height()
                pixmapimage = pixmapimage.scaled(w, h, Qt.KeepAspectRatio)
                self.lb_image.setPixmap(pixmapimage)
                self.lb_image.show()
            except:
                self.lb_image.setText(lang1["lb_image"][lang])
                self.lb_image.show()

    def show_chosen_image(self):
        if self.lw_files.selectedItems():
            self.filename = self.lw_files.selectedItems()[0].text()
            self.current_file = self.selected_files[self.filename]
            if self.current_file.open_image():
                self.lb_ratio_data.setText(f'{self.current_file.img_size}')
                self.show_image()
            else:
                self.lb_image.clear()
                self.lb_image.setText(lang1["lb_image"][lang])
                self.lb_ratio_data.setText("")
            self.lb_filesize_data.setText(
                f'{round(self.current_file.size, 3)} MBytes')
            self.lb_data_data.setText(f'{self.current_file.date}')


def main():
    log_save(f"Start session {dt.strftime(dt.now(), '%A, %d %B %Y %I:%M%p')}")
    app = QApp([])
    mw = Window()
    mw.show()

    app.exec_()


main()
