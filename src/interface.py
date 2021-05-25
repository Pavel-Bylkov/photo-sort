# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QProgressBar,
    QPushButton, QLineEdit, QGroupBox,
    QCheckBox, QRadioButton, QListWidget,
    QHBoxLayout, QVBoxLayout, QAbstractItemView)
from PyQt5.QtGui import QPalette, QColor

from src.languages import lang1, lang2
from src.config import lang, win_title, win_width, win_height


class Progress(QWidget):
    def __init__(self, title, parent=None, flags=Qt.WindowFlags()):
        """Окно для визуализации прогресса"""
        super().__init__(parent=parent, flags=flags)
        # создаём и настраиваем графические элементы:
        self.init_ui()
        # устанавливает, как будет выглядеть окно (надпись, размер)
        self.set_appear(title)
        self.lb_pbar.setText(title)
        # старт:
        self.show()

    def init_ui(self):
        """Создаем виджеты"""
        self.lb_pbar = QLabel("Процесс")
        self.pbar = QProgressBar(self)
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

    def set_appear(self, title):
        """устанавливает, как будет выглядеть окно (надпись, размер)"""
        self.setWindowTitle(title)
        self.resize(700, 300)


class MainWindow(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        """Главное окно программы"""
        super().__init__(parent=parent, flags=flags)
        # создаём и настраиваем графические элементы:
        self.widgets = {}
        self.init_ui()
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
        self.lb_main = QLabel(lang1["lb_main"][lang])
        self.widgets["lb_main"] = self.lb_main
        self.lb_image = QLabel(lang1["lb_image"][lang])
        self.widgets["lb_image"] = self.lb_image
        self.lb_from = QLabel(lang1["lb_from"][lang])
        self.widgets["lb_from"] = self.lb_from
        self.btn_from = QPushButton(lang1["btn_from"][lang])
        self.widgets["btn_from"] = self.btn_from
        self.path_from = QLineEdit("")
        self.path_from.setPlaceholderText(lang2["path_holder"][lang])
        self.lb_to = QLabel(lang1["lb_to"][lang])
        self.widgets["lb_to"] = self.lb_to
        self.btn_to = QPushButton(lang1["btn_to"][lang])
        self.widgets["btn_to"] = self.btn_to
        self.path_to = QLineEdit("")
        self.path_to.setPlaceholderText(lang2["path_holder"][lang])
        self.lb_dirs = QLabel(lang1["lb_dirs"][lang])
        self.widgets["lb_dirs"] = self.lb_dirs
        self.lw_dirs = QListWidget()
        self.lb_files = QLabel(lang1["lb_files"][lang])
        self.widgets["lb_files"] = self.lb_files
        self.lw_files = QListWidget()
        self.lb_ext = QLabel(lang1["lb_ext"][lang])
        self.widgets["lb_ext"] = self.lb_ext
        self.lw_ext = QListWidget()
        # setting selection mode property
        self.lw_ext.setSelectionMode(QAbstractItemView.MultiSelection)
        self.lb_info = QLabel(lang2["lb_info"][lang].format(0))
        self.file_info = QGroupBox(lang2["file_info"][lang])
        self.lb_filesize = QLabel(lang1["lb_filesize"][lang])
        self.widgets["lb_filesize"] = self.lb_filesize
        self.lb_filesize_data = QLabel("")
        self.lb_ratio = QLabel(lang1["lb_ratio"][lang])
        self.widgets["lb_ratio"] = self.lb_ratio
        self.lb_ratio_data = QLabel("")
        self.lb_data = QLabel(lang1["lb_data"][lang])
        self.widgets["lb_data"] = self.lb_data
        self.lb_data_data = QLabel("")
        self.btn_disable = QPushButton(lang1["btn_disable"][lang])
        self.widgets["btn_disable"] = self.btn_disable
        self.btn_del = QPushButton(lang1["btn_del"][lang])
        self.widgets["btn_del"] = self.btn_del
        self.chbx_all_files = QCheckBox(lang1["chbx_all_files"][lang])
        self.chbx_all_files.setChecked(True)
        self.widgets["chbx_all_files"] = self.chbx_all_files
        self.gb_mode = QGroupBox(lang2["gb_mode"][lang])
        self.rbtn_move = QRadioButton(lang1["rbtn_move"][lang])
        self.rbtn_move.setChecked(True)
        self.widgets["rbtn_move"] = self.rbtn_move
        self.rbtn_move_to = QRadioButton(lang1["rbtn_move_to"][lang])
        self.widgets["rbtn_move_to"] = self.rbtn_move_to
        self.rbtn_copy_to = QRadioButton(lang1["rbtn_copy_to"][lang])
        self.widgets["rbtn_copy_to"] = self.rbtn_copy_to
        self.gb_video = QGroupBox(lang2["gb_video"][lang])
        self.rbtn_1 = QRadioButton(lang1["rbtn_1"][lang])  # Вместе с фото
        self.rbtn_1.setChecked(True)
        self.widgets["rbtn_1"] = self.rbtn_1
        self.rbtn_2 = QRadioButton(lang1["rbtn_2"][lang])  # В подпапки
        self.widgets["rbtn_2"] = self.rbtn_2
        self.rbtn_3 = QRadioButton(lang1["rbtn_3"][lang])  # Разделить на Фото и Видео
        self.widgets["rbtn_3"] = self.rbtn_3
        self.btn_run = QPushButton(lang1["btn_run"][lang])
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
        col1.addWidget(self.chbx_all_files)
        col1.addWidget(self.lb_image, 90)  # alignment=Qt.AlignCenter

        row5 = QHBoxLayout()
        row5.addWidget(self.btn_disable)
        row5.addWidget(self.btn_del)
        col1.addLayout(row5)
        row2.addLayout(col1, 55)
        col3 = QVBoxLayout()

        col_box_info = QVBoxLayout()
        col_box_info.addWidget(self.lb_filesize, alignment=Qt.AlignLeft)
        col_box_info.addWidget(self.lb_filesize_data, alignment=Qt.AlignCenter)
        col_box_info.addWidget(self.lb_ratio, alignment=Qt.AlignLeft)
        col_box_info.addWidget(self.lb_ratio_data, alignment=Qt.AlignCenter)
        col_box_info.addWidget(self.lb_data, alignment=Qt.AlignLeft)
        col_box_info.addWidget(self.lb_data_data, alignment=Qt.AlignCenter)
        self.file_info.setLayout(col_box_info)
        col3.addWidget(self.file_info)
        row2.addLayout(col3)

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

    def set_appear(self):
        """устанавливает, как будет выглядеть окно (надпись, размер)"""
        self.setWindowTitle(win_title)
        self.resize(win_width, win_height)


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

if __name__ == '__main__':
    app = QApp([])
    mw = MainWindow()
    mw.show()

    app.exec_()
