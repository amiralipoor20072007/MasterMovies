from bot.helper.ext_utils.bot_utils import get_readable_file_size, MirrorStatus
from bot import LOGGER

class SplitStatus:
    def __init__(self, name, path, size, gid):
        self.__name = name
        self.__path = path
        self.__size = size
        self.__gid = gid

    def gid(self):
        return self.__gid

    def progress(self):
        return '0'

    def speed(self):
        return '0'

    def name(self):
        return self.__name

    def path(self):
        return self.__path

    def size(self):
        return get_readable_file_size(self.__size)

    def eta(self):
        return '0s'

    def status(self):
        return MirrorStatus.STATUS_SPLITTING

    def processed_bytes(self):
        return 0

    def download(self):
        return self

    def cancel_download(self):
        LOGGER.info(f'Cancelling Split: {self.__name}')
        if self.__listener.SubProc is not None:
            self.__listener.SubProc.kill()
        self.__listener.onUploadError('Splitting stopped by user!')