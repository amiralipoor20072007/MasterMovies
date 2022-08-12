from bot.helper.ext_utils.bot_utils import get_readable_file_size, MirrorStatus, get_readable_time
from bot.helper.ext_utils.fs_utils import get_path_size
from time import time
from threading import RLock
from os import path as ospath
class ZipStatus:
    def __init__(self, name,m_path, path, size):
        self.__name = name
        self.__path = path
        self.__mpath = m_path
        self.__size = get_path_size(self.__mpath)
        self.__start_time = time()
        self.__uploaded_bytes = 0

    def progress(self):
        return f'{round(self.progress_raw(), 2)}%'

    def speed(self):
        return f'{get_readable_file_size(self.speed_raw())}/s'

    def name(self):
        return self.__name

    def path(self):
        return self.__path
    
    def size_raw(self):
        return self.__size

    def size(self):
        return get_readable_file_size(self.__size)

    def eta(self):
        try:
            seconds = (self.__size - self.uploaded_bytes()) / self.speed_raw()
            return f'{get_readable_time(seconds)}'
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
        return self.uploaded_bytes()

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
