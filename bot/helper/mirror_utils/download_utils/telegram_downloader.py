from logging import getLogger, WARNING
from time import sleep, time
from threading import RLock, Lock

from bot import LOGGER, download_dict, download_dict_lock, STOP_DUPLICATE, app,Premuim_app
from ..status_utils.telegram_download_status import TelegramDownloadStatus
from bot.helper.telegram_helper.message_utils import sendMarkup, sendMessage, sendStatusMessage,sendSearchMessage
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
if Premuim_app == None:
    Tapp = app
else:
    Tapp = Premuim_app
global_lock = Lock()
GLOBAL_GID = set()
getLogger("pyrogram").setLevel(WARNING)


class TelegramDownloadHelper:

    def __init__(self, listener,MultiZipTelegram=None):
        self.name = ""
        self.size = 0
        self.progress = 0
        self.downloaded_bytes = 0
        self.__start_time = time()
        self.__listener = listener
        self.MultiZipTelegram = MultiZipTelegram
        self.__id = ""
        self.__is_cancelled = False
        self.__resource_lock = RLock()

    @property
    def download_speed(self):
        with self.__resource_lock:
            return self.downloaded_bytes / (time() - self.__start_time)

    def __onDownloadStart(self, name, size, file_id):
        with global_lock:
            GLOBAL_GID.add(file_id)
        with self.__resource_lock:
            self.name = name
            self.size = size
            self.__id = file_id
        with download_dict_lock:
            download_dict[self.__listener.uid] = TelegramDownloadStatus(self, self.__listener, self.__id)
        if self.MultiZipTelegram is None:
            self.__listener.onDownloadStart()
        sendStatusMessage(self.__listener.message, self.__listener.bot)

    def __onDownloadProgress(self, current, total):
        if self.__is_cancelled:
            Tapp.stop_transmission()
            return
        with self.__resource_lock:
            self.downloaded_bytes = current
            try:
                self.progress = current / self.size * 100
            except ZeroDivisionError:
                pass

    def __onDownloadError(self, error):
        with global_lock:
            try:
                GLOBAL_GID.remove(self.__id)
            except:
                pass
        if self.MultiZipTelegram is not None and self.__id in self.MultiZipTelegram.gids:
                self.MultiZipTelegram.Add_Corrupted(error)
                self.MultiZipTelegram.Next_Download()
        else:
            self.__listener.onDownloadError(error)

    def __onDownloadComplete(self):
        with global_lock:
            GLOBAL_GID.remove(self.__id)
        if self.MultiZipTelegram is not None and self.__id in self.MultiZipTelegram.gids:
            self.MultiZipTelegram.Next_Download()
        else:
            self.__listener.onDownloadComplete()

    def __download(self, message, path,file_id=None):
        try:
            download = message.download(file_name=path, progress=self.__onDownloadProgress)
        except Exception as e:
            LOGGER.error(str(e))
            return self.__onDownloadError(str(e))
        if download is not None:
            self.__onDownloadComplete()
        elif not self.__is_cancelled:
            self.__onDownloadError('Internal error occurred')

    def add_download(self, message, path, filename,MultiZip_Id =None):
        if self.MultiZipTelegram is not None:
            self.__is_cancelled = False
            self.__start_time = time()
            _dmsg = Tapp.get_messages(message.chat.id, message_ids=MultiZip_Id)
            media = None
            media_array = [_dmsg.document, _dmsg.video, _dmsg.audio]
            for i in media_array:
                if i is not None:
                    media = i
                    break
            if media is not None:
                with global_lock:
                    # For avoiding locking the thread lock for long time unnecessarily
                    download = media.file_unique_id not in GLOBAL_GID
                if filename == "":
                    name = media.file_name
                else:
                    name = filename
                    path = path + name
                if download:
                    size = media.file_size
                    self.MultiZipTelegram.Add_gid(media.file_unique_id)
                    self.__onDownloadStart(name, size, media.file_unique_id)
                    LOGGER.info(f'Downloading Telegram file with id: {media.file_unique_id}')
                    self.__download(_dmsg, path,media.file_unique_id)
                else:
                    self.__onDownloadError('File already being downloaded!')
            else:
                self.__onDownloadError('No document in the replied message')
        else:
            _dmsg = Tapp.get_messages(message.chat.id, reply_to_message_ids=message.message_id)
            media = None
            media_array = [_dmsg.document, _dmsg.video, _dmsg.audio]
            for i in media_array:
                if i is not None:
                    media = i
                    break
            if media is not None:
                with global_lock:
                    # For avoiding locking the thread lock for long time unnecessarily
                    download = media.file_unique_id not in GLOBAL_GID
                if filename == "":
                    name = media.file_name
                else:
                    name = filename
                    path = path + name

                if download:
                    size = media.file_size
                    if dl.__listener.isZip:
                        sname = sname + ".zip"
                    elif dl.__listener.extract:
                        try:
                            sname = get_base_name(sname)
                        except:
                            sname = None
                    if STOP_DUPLICATE and not self.__listener.isLeech:
                        LOGGER.info('Checking File/Folder if already in Drive...')
                        search_list, f_name = GoogleDriveHelper().drive_list(sname, True, True)
                        if search_list:
                            sendSearchMessage(self.__listener.message,self.__listener.bot,search_list,f_name)
                    self.__onDownloadStart(name, size, media.file_unique_id)
                    LOGGER.info(f'Downloading Telegram file with id: {media.file_unique_id}')
                    self.__download(_dmsg, path)
                else:
                    self.__onDownloadError('File already being downloaded!')
            else:
                self.__onDownloadError('No document in the replied message')

    def cancel_download(self):
        LOGGER.info(f'Cancelling download on user request: {self.__id}')
        self.__is_cancelled = True
        self.__onDownloadError('Cancelled by user!')


class MultiZip_Telegram():
    def __init__(self,DOWNLOAD_DIR,message,name,links_list,listener):
        self.DOWNLOAD_DIR = DOWNLOAD_DIR
        self.message = message
        self.links_list = links_list
        self.downs = len(links_list)
        self.name = name
        self.listener = listener
        self.gids = []
        self.desription =[]
        self.Telegram_Helper = None
        self.counter = 0
    
    def Add_gid(self,gid):
        self.gids.append(gid)

    def Next_Link(self):
        for link in range(len(self.links_list)):
            x = self.links_list[link]
            del self.links_list[link]
            self.counter += 1
            return x

    def Add_Corrupted(self,error):
        self.desription.append(error)
        
    def Next_Download(self):
        if self.downs != self.counter:
            sleep(5)
            #Get Next Link
            MultiZip_Id = self.Next_Link()
            sleep(5)
            self.Telegram_Helper.add_download(self.message, f'{self.DOWNLOAD_DIR}{self.listener.uid}/', self.name,MultiZip_Id)
        else:
            if len(self.desription) == self.downs:
                self.listener.onDownloadError('All Of Links is broken')
                return
            if self.desription != []:
                self.listener.onDownloadComplete(self.desription)
            else:
                self.listener.onDownloadComplete()


    def run(self):
        if self.downs != self.counter:
            self.listener.onDownloadStart()
            MultiZip_Id = self.Next_Link()
            sleep(5)
            self.Telegram_Helper = TelegramDownloadHelper(self.listener,self)
            self.Telegram_Helper.add_download(self.message,f'{self.DOWNLOAD_DIR}{self.listener.uid}/',self.name,MultiZip_Id)
        else:
            if len(self.desription) == self.downs:
                self.listener.onDownloadError('All Of Links is broken\nOr\nYour Download Completly Cancelled')
                return
            if self.desription != []:
                self.listener.onDownloadComplete(self.desription)
            else:
                self.listener.onDownloadComplete()
