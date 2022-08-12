from bot.helper.ext_utils.bot_utils import get_readable_file_size, MirrorStatus, get_readable_time
from bot.helper.ext_utils.fs_utils import get_path_size
from bot import LOGGER
from time import time
from threading import RLock
from os import path as ospath
class ZipStatus:
    def __init__(self, name,m_path, path,listener):
        self.__name = name
        self.__path = path
        self.__mpath = m_path
        self.__size = get_path_size(self.__mpath)
        self.__start_time = time()
        self.__uploaded_bytes = 0
        self.listener = listener
        self.message = listener.message

    def progress(self):
        x = round(self.progress_raw(), 2)
        return f'{x}%'

    def speed(self):
        x = get_readable_file_size(self.speed_raw())
        return f'{x}/s'

    def name(self):
        return self.__name

    def path(self):
        return self.__path
    
    def size_raw(self):
        return self.__size

    def size(self):
        x = get_readable_file_size(self.__size)
        return x

    def eta(self):
        try:
            seconds = (self.__size - self.uploaded_bytes()) / self.speed_raw()
            x = get_readable_time(seconds)
            return f'{x}'
        except ZeroDivisionError:
            return '-'

    def speed_raw(self):
        try:
            return self.uploaded_bytes() / (time() - self.__start_time)
        except ZeroDivisionError:
            return 0

    def status(self):
        return MirrorStatus.STATUS_ARCHIVING

    def processed_bytes(self):
        x = self.uploaded_bytes()
        return x

    def uploaded_bytes(self):
        try:
            self.__uploaded_bytes = get_path_size(self.__path)
        except FileNotFoundError:
            try:
                self.__uploaded_bytes = get_path_size(self.__path+'.tmp')
            except:
                return 0
        return self.__uploaded_bytes

    def progress_raw(self):
        try:
            return self.uploaded_bytes() / self.__size * 100
        except ZeroDivisionError:
            return 0
