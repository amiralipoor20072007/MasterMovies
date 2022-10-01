from time import sleep

from bot import aria2, download_dict_lock, download_dict, STOP_DUPLICATE, LOGGER
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.ext_utils.bot_utils import is_magnet, getDownloadByGid, new_thread
from bot.helper.mirror_utils.status_utils.aria_download_status import AriaDownloadStatus,get_download
from bot.helper.telegram_helper.message_utils import sendMarkup, sendStatusMessage, sendMessage,sendSearchMessage
from bot.helper.ext_utils.fs_utils import get_base_name
from os import path as ospath
from subprocess import run as srun

@new_thread
def __onDownloadStarted(api, gid):
    try:
        if STOP_DUPLICATE:
            download = api.get_download(gid)
            if download.is_metadata:
                LOGGER.info(f'onDownloadStarted: {gid} Metadata')
                return
            elif not download.is_torrent:
                sleep(3)
                download = api.get_download(gid)
            LOGGER.info(f'onDownloadStarted: {gid}')
            dl = getDownloadByGid(gid)
            if not dl or dl.getListener().isLeech or dl.getListener_MultiZip() is not None:
                return
            LOGGER.info('Checking File/Folder if already in Drive...')
            LOGGER.info(f'{download} , {download.name}')
            sname = download.name
            if dl.getListener().isZip:
                sname = sname + ".zip"
            elif dl.getListener().extract:
                try:
                    sname = get_base_name(sname)
                except:
                    sname = None
            LOGGER.info(f'Checking File/Folder if already in Drive... : {sname}')
            if sname is not None:
                search_list, f_name = GoogleDriveHelper().drive_list(sname, True)
                if search_list:
                    dl.getListener().onDownloadError('File/Folder already available in Drive.\n\n')
                    api.remove([download], force=True, files=True)
                    sendSearchMessage(dl.getListener().message,dl.getListener().bot,search_list,f_name)
                    return
    except Exception as e:
        LOGGER.error(f"{e} onDownloadStart: {gid} stop duplicate didn't pass")

@new_thread
def __onDownloadComplete(api, gid):
    dl = getDownloadByGid(gid)
    LOGGER.info(f"onDownloadComplete: {gid}")
    download = api.get_download(gid)
    if download.followed_by_ids:
        new_gid = download.followed_by_ids[0]
        LOGGER.info(f'Changed gid from {gid} to {new_gid}')
    elif dl is not None:
        if dl.getListener_MultiZip() is not None and gid in dl.getListener_MultiZip().gids:
            multiple_gids = dl.getListener_MultiZip().gids
            if gid in multiple_gids:
                dl.getListener_MultiZip().Next_Download()
        else:
            dl.getListener().onDownloadComplete()

@new_thread
def __onDownloadStopped(api, gid):
    sleep(6)
    dl = getDownloadByGid(gid)
    if dl:
        if dl.getListener_MultiZip() is not None and gid in dl.getListener_MultiZip().gids:
            multiple_gids = dl.getListener_MultiZip().gids
            if gid in multiple_gids:
                dl.getListener_MultiZip().Add_Corrupted('Dead torrent!')
                dl.getListener_MultiZip().Next_Download()
        else:
            dl.getListener().onDownloadError('Dead torrent!')

@new_thread
def __onDownloadError(api, gid):
    LOGGER.info(f"onDownloadError: {gid}")
    sleep(0.5)
    dl = getDownloadByGid(gid)
    try:
        download = api.get_download(gid)
        error = download.error_message
        LOGGER.info(f"Download Error: {error}")
    except:
        pass
    if dl:
        if dl.getListener_MultiZip() is not None and gid in dl.getListener_MultiZip().gids:
            multiple_gids = dl.getListener_MultiZip().gids
            if gid in multiple_gids:
                dl.getListener_MultiZip().Add_Corrupted(error)
                dl.getListener_MultiZip().Next_Download()
        else:
            dl.getListener().onDownloadError(error)

def start_listener():
    aria2.listen_to_notifications(threaded=True, on_download_start=__onDownloadStarted,
                                  on_download_error=__onDownloadError,
                                  on_download_stop=__onDownloadStopped,
                                  on_download_complete=__onDownloadComplete,
                                  timeout=20)

def add_aria2c_download(link: str, path, listener, filename, auth):
    if is_magnet(link):
        download = aria2.add_magnet(link, {'dir': path})
    else:
        download = aria2.add_uris([link], {'dir': path, 'out': filename, 'header': f"authorization: {auth}"})
    if download.error_message:
        error = str(download.error_message).replace('<', ' ').replace('>', ' ')
        LOGGER.info(f"Download Error: {error}")
        return sendMessage(error, listener.bot, listener.message)
    with download_dict_lock:
        download_dict[listener.uid] = AriaDownloadStatus(download.gid, listener)
        LOGGER.info(f"Started: {download.gid} DIR: {download.dir} ")
    listener.onDownloadStart()
    sendStatusMessage(listener.message, listener.bot)

class Multi_Zip():
    def __init__(self,links: list, path, listener,softsub=False):
        self.links = links
        self.links_rate = len(links)
        self.path = path
        self.listener = listener
        self.counter = 0
        self.gids=[]
        self.desription =[]
        self.softsub = softsub

    def Download(self,link,path):
        if is_magnet(link):
            download = aria2.add_magnet(link, {'dir': path})
        else:
            if self.softsub and self.counter == 1:
                download = aria2.add_uris([link], {'dir': path,'out': 'softsubxi.srt'})
            else:
                download = aria2.add_uris([link], {'dir': path})
        if download.error_message:
            error = str(download.error_message).replace('<', ' ').replace('>', ' ')
            LOGGER.info(f"Download Error: {error}")
            return sendMessage(error, self.listener.bot, self.listener.message)
        self.gids.append(download.gid)
        with download_dict_lock:
            download_dict[self.listener.uid] = AriaDownloadStatus(download.gid, self.listener,self)
            LOGGER.info(f"Started: {download.gid} DIR: {download.dir} ")
        sendStatusMessage(self.listener.message, self.listener.bot)
    
    def Next_Link(self):
        for link in range(len(self.links)):
            x = self.links[link]
            del self.links[link]
            self.counter += 1
            return x

    def Add_Corrupted(self,error):
        self.desription.append(error)
        
    def Next_Download(self):
        if self.links_rate != self.counter:
            next_link = self.Next_Link()
            sleep(5)
            self.Download(next_link,self.path)
        else:
            if len(self.desription) == self.links_rate:
                self.listener.onDownloadError('All Of Links is broken')
                return
            if self.desription != []:
                download = get_download(self.gids[-1])
                Counter =-2
                while download is None:
                    with download_dict_lock:
                        download_dict[self.listener.uid] = AriaDownloadStatus(self.gids[Counter], self.listener,self)
                    download = get_download(self.gids[Counter])
                    Counter -= 1
                self.listener.onDownloadComplete(self.desription)
            else:
                self.listener.onDownloadComplete()

    def run(self):
        if self.links_rate != self.counter:
            self.listener.onDownloadStart()
            next_link = self.Next_Link()
            sleep(5)
            self.Download(next_link,self.path)
        else:
            if len(self.desription) == self.links_rate:
                self.listener.onDownloadError('All Of Links is broken')
                return
            if self.desription != []:
                download = get_download(self.gids[-1])
                Counter =-2
                while download is None:
                    with download_dict_lock:
                        download_dict[self.listener.uid] = AriaDownloadStatus(self.gids[Counter], self.listener,self)
                    download = get_download(self.gids[Counter])
                    Counter -= 1
                self.listener.onDownloadComplete(self.desription)
            else:
                self.listener.onDownloadComplete()

def Multi_Zip_Function(links: list, path, listener,softsub=False):
    multi_zip = Multi_Zip(links, path, listener,softsub)
    multi_zip.run()

start_listener()
