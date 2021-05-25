import os
import shutil

from PIL import Image
from hashlib import md5
from uuid import uuid4
from datetime import datetime as dt

from src.config import img_ext, video_ext, log_save


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

    def __lt__(self, other):  # file1 < file2
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
                    exif = image._getexif()
                    if exif:
                        for tag in tags:
                            dat = exif.get(tag[0])
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

    def mkdir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def get_new_path(self, new_path, video_folder):
        if video_folder == "all":
            new_path = f'{new_path}{os.sep}{self.year}{os.sep}{self.month}'
        elif video_folder == "into":
            if self.is_image:
                new_path = f'{new_path}{os.sep}{self.year}{os.sep}{self.month}{os.sep}images'
            elif self.is_video:
                new_path = f'{new_path}{os.sep}{self.year}{os.sep}{self.month}{os.sep}video'
        else:
            if self.is_image:
                new_path = f'{new_path}{os.sep}images{os.sep}{self.year}{os.sep}{self.month}'
            elif self.is_video:
                new_path = f'{new_path}{os.sep}video{os.sep}{self.year}{os.sep}{self.month}'
        return new_path

    def move(self, new_path, video_folder):
        """Перемещение файла"""
        try:
            new_path = self.get_new_path(new_path, video_folder)
            self.mkdir(new_path)
            shutil.move(self.abs_path, f'{new_path}{os.sep}{self.name}')
            return "OK"
        except:
            return "Error 3"

    def copy(self, new_path, video_folder):
        """ Копирование файла. Чтобы сохранить все метаданные файла,
            используется shutil.copy2()"""
        try:
            new_path = self.get_new_path(new_path, video_folder)
            self.mkdir(new_path)
            shutil.copy2(self.abs_path, f'{new_path}{os.sep}{self.name}')
            return "OK"
        except:
            if shutil.disk_usage(new_path).free < os.stat(self.abs_path).st_size:
                return "Error 1"
            return "Error 2"

    def kill(self):
        try:
            os.remove(self.abs_path)
            return "OK"
        except:
            return "Error"
