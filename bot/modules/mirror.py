from base64 import b64encode
from requests import utils as rutils
from re import T, match as re_match, search as re_search, split as re_split
from time import sleep, time
from os import path as ospath, remove as osremove, listdir, walk,rename
from shutil import rmtree
from threading import Thread
from subprocess import run as srun,Popen
from pathlib import PurePath
from html import escape
from telegram.ext import CommandHandler
from telegram import InlineKeyboardMarkup
import random

import string

from bot import AUTODELETE_USERS, HASH_USERS, Interval,AUTHORIZED_CHATS, INDEX_URL,INDEX_BACKUP,IRAN_INDEX_BACKUP, VIEW_LINK, aria2, QB_SEED, dispatcher, DOWNLOAD_DIR, \
                download_dict, download_dict_lock, TG_SPLIT_SIZE, LOGGER, MEGA_KEY, DB_URI, INCOMPLETE_TASK_NOTIFIER,app,MAX_SPLIT_SIZE
from bot.helper.ext_utils.bot_utils import is_url, is_magnet, is_mega_link, is_gdrive_link, get_content_type
from bot.helper.ext_utils.fs_utils import get_base_name, get_path_size, split_file, clean_download,get_path_md5_sha,VIDEO_SUFFIXES
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException, NotSupportedExtractionArchive
from bot.helper.mirror_utils.download_utils.aria2_download import add_aria2c_download,Multi_Zip_Function
from bot.helper.mirror_utils.download_utils.gd_downloader import add_gd_download
from bot.helper.mirror_utils.download_utils.qbit_downloader import QbDownloader
from bot.helper.mirror_utils.download_utils.mega_downloader import MegaDownloader
from bot.helper.mirror_utils.download_utils.direct_link_generator import direct_link_generator
from bot.helper.mirror_utils.download_utils.telegram_downloader import TelegramDownloadHelper,MultiZip_Telegram
from bot.helper.mirror_utils.status_utils.extract_status import ExtractStatus
from bot.helper.mirror_utils.status_utils.zip_status import ZipStatus
from bot.helper.mirror_utils.status_utils.extract_audio_status import ExtractAudio_Status
from bot.helper.mirror_utils.status_utils.softsub_status import SoftSub_Status
from bot.helper.mirror_utils.status_utils.split_status import SplitStatus
from bot.helper.mirror_utils.status_utils.upload_status import UploadStatus
from bot.helper.mirror_utils.status_utils.tg_upload_status import TgUploadStatus
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.mirror_utils.upload_utils.pyrogramEngine import TgUploader
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage,copyMessageToPv, sendMarkup,sendMarkupLog,copyLeechToPv, delete_all_messages, update_all_messages
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.ext_utils.db_handler import DbManger
from bot.helper.ext_utils.telegraph_helper import telegraph
from bot.modules.multizip_listener import Multi_Listener_Telegram_Runner
def CheckName(checkingname):
    PORNfilter = ['clubseventeen', 'virgin', 'xxx', 'xxx', 'porn',
            'porn', 'porn', 'blacked', 'onlyfans', 'sex', 'step','vixen', 'tushyraw',
            'pussy', 'brazzers', 'cock', 'dick', 'creampie', 'erotic',
            'hentie', 'blowjoblesbian', 'gay', 'bisexual', 'nudes',
            'wtf', 'bdsm', 'ass', 'boobs', 'anal', 'nsfw',
            'hardcore', 'cuck', 'penis', 'fuck','cock', 'deepthroat',
            'dick', 'cumshot', 'tasty', 'baby', 'wet', 'fuck', 'sperm',
            'jerk off', 'naked', 'ass', 'tits', 'fingering', 'masturbate',
            'bitch', 'blowjob', 'prostitute', 'shit', 'bullshit', 'dumbass',
            'dickhead', 'pussy', 'piss', 'asshole', 'boobs', 'butt', 'booty',
            'dildo', 'erection', 'foreskin', 'gag', 'handjob', 'licking', 'nude',
            'penis', 'porn', 'vibrator', 'viagra', 'virgin', 'vagina', 'vulva',
            'wet dream', 'threesome', 'orgy', 'bdsm', 'hickey', 'condom',
            'sexting', 'squirt', 'testicles', 'anal', 'bareback', 'bukkake',
            'creampie', 'stripper', 'strap-on', 'missionary', 'make out',
            'clitoris', 'cock ring', 'sugar daddy', 'cowgirl', 'reach-around',
            'doggy style', 'fleshlight', 'contraceptive', 'makeup sex', 'lingerie',
            'butt plug', 'moan', 'milf', 'wank', 'oral', 'sucking', 'kiss', 'dirty talk',
            'straddle', 'blindfold', 'bondage', 'orgasm', 'french kiss', 'scissoring',
            'hard', 'deeper', "don't stop", 'slut', 'cumming', 'tasty', 'dirty', 'ode', 'dog',
            "men's milk", 'pound', 'jerk', 'prick', 'cunt', 'bastard', 'faggot', 'anal', 'anus']
    for i in PORNfilter:
        part1 = '.'+i+'.'
        part2 = i+'.'
        part3 = '.'+i
        if part1 in checkingname:
            filter_message = f"<br>Bot has problem with this word containing your download's name : {part1}<br>\n\n<br>Changed Files/Folders:<br>\n\n"
            filter_message += f"\n<br>If You Have Problem with this Then Use ZipMirror (It's Better if you use coustom name with ZipMirror command)<br>\n\n"
            return True,filter_message
        elif part2 in checkingname:
            filter_message = f"<br>Bot has problem with this word containing your download's name : {part2}<br>\n\n<br>Changed Files/Folders:<br>\n\n"
            filter_message += f"\n<br>If You Have Problem with this Then Use ZipMirror (It's Better if you use coustom name with ZipMirror command)<br>\n\n"
            return True,filter_message
        elif part3 in checkingname:
            filter_message = f"<br>Bot has problem with this word containing your download's name : {part3}<br>\n\n<br>Changed Files/Folders:<br>\n\n"
            filter_message += f"<br>If You Have Problem with this Then Use ZipMirror (It's Better if you use coustom name with ZipMirror command)<br>\n\n"
            return True,filter_message
    return [False]
    
def CheckPorn(path):
    for dirpath, subdir, files in walk(path, topdown=False):
        for subdir_ in subdir:
            ipath = ospath.join(dirpath,subdir_)
            up_name = PurePath(ipath).name
            checking_name = up_name.lower()
            verify = CheckName(checking_name)
            if verify[0] == True:
                return True,verify[1]
        for file_ in files:
            f_path = ospath.join(dirpath, file_)
            up_name = PurePath(f_path).name
            checking_name = up_name.lower()
            verify = CheckName(checking_name)
            if verify[0] == True:
                return True,verify[1]
    return [False]




class MirrorListener:
    def __init__(self, bot, message, isZip=False, extract=False, isQbit=False, isLeech=False, pswd=None,tag=None, seed=False,MultiZip=[[],False],MultiUnZip=[[],False],Extract_Audio=False,SoftSub=[[],False]):
        self.bot = bot
        self.message = message
        self.uid = self.message.message_id
        self.extract = extract
        self.isZip = isZip
        self.isQbit = isQbit
        self.isLeech = isLeech
        self.pswd = pswd
        self.tag = tag
        self.MultiZip = MultiZip[1]
        self.MultiUnZip = MultiUnZip[1]
        self.Extract_Audio = Extract_Audio
        self.SoftSub = SoftSub
        self.seed = any([seed, QB_SEED])
        self.isPrivate = self.message.chat.type in ['private', 'group']
        self.NameBeforeChange = ["FileName","Type","Telegraph Page",False]
        self.SubProc = None

    def clean(self):
        try:
            Interval[0].cancel()
            Interval.clear()
            aria2.purge()
            delete_all_messages()
        except:
            pass

    def onDownloadStart(self):
        if INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
            DbManger().add_incomplete_task(self.message.chat.id, self.message.link, self.tag)

    def onDownloadComplete(self,MultiZip_ErroredXI=None,MultiZip_Counter=0):
        if MultiZip_ErroredXI is not None:
            msg = f"{self.tag} You MultiZipping Process Got Error Wiht One/Many Downloading:\n"
            counter = 0
            for index , error in enumerate(MultiZip_ErroredXI,start=1):
                msg += f"{index} - download has been stopped due to: {error}\n"
            sendMessage(msg, self.bot, self.message)
            del msg
            del counter
        with download_dict_lock:
            LOGGER.info(f"Download completed: {download_dict[self.uid].name()}")
            download = download_dict[self.uid]
            name = str(download.name()).replace('/', '')
            gid = download.gid()
            size = download.size_raw()
            if name == "None" or self.isQbit or not ospath.exists(f'{DOWNLOAD_DIR}{self.uid}/{name}'):
                name = listdir(f'{DOWNLOAD_DIR}{self.uid}')[-1]
            m_path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
        if self.Extract_Audio:
            Video_Name = PurePath(m_path).name
            Video_path = f'{DOWNLOAD_DIR}{self.uid}/{Video_Name}'
            if ospath.isfile(Video_path) and Video_Name.upper().endswith(VIDEO_SUFFIXES):
                try:
                    with download_dict_lock:
                        download_dict[self.uid] = ExtractAudio_Status(name, m_path, size)
                    path = ospath.splitext(Video_path)[0]+'-Audio.m4a'
                    LOGGER.info('Extracting Audio')
                    srun(["new-api","-hide_banner","-i",Video_path,"-vn","-c:a","copy",path])
                except FileNotFoundError:
                    LOGGER.info('File to archive not found!')
                    self.onUploadError('Internal error occurred!!')
                    return
            else:
                self.onUploadError("You're Requested For Extract Audio But The File Isn't A Video")
                return
        elif self.SoftSub[1] == True:
            Video_Name = PurePath(m_path).name
            Video_path = f'{DOWNLOAD_DIR}{self.uid}/{Video_Name}'
            Sub_path = f'{DOWNLOAD_DIR}{self.uid}/softsubxi.srt'
            if ospath.isfile(Video_path) and Video_Name.upper().endswith(VIDEO_SUFFIXES):
                try:
                    with download_dict_lock:
                        download_dict[self.uid] = SoftSub_Status(name, m_path, size)
                    path = ospath.splitext(Video_path)[0]+'-SoftSubbed' + ospath.splitext(Video_path)[1]
                    LOGGER.info('Subtitling...')
                    srun(["new-api","-hide_banner","-i",Video_path,'-i',Sub_path,'-c',"copy",path])
                except FileNotFoundError:
                    LOGGER.info('File to archive not found!')
                    self.onUploadError('Internal error occurred!!')
                    return
            else:
                self.onUploadError("You're Requested For Extract Audio But The File Isn't A Video")
                return
        elif self.isZip or self.MultiZip:
            try:
                if self.MultiZip:
                    m_path = f'{DOWNLOAD_DIR}{self.uid}'
                    random_name = ''.join(random.choices(string.ascii_lowercase+string.ascii_letters+string.ascii_uppercase,k=12))
                    path = f'{m_path}/'+random_name+".zip"
                else:
                    path = m_path + ".zip"
                with download_dict_lock:
                    download_dict[self.uid] = ZipStatus(name, m_path,path,gid,self)
                LOGGER.info(f'Zip: orig_path: {m_path}, zip_path: {path}')
                if self.pswd is not None:
                    if self.isLeech and int(size) > TG_SPLIT_SIZE:
                        self.SubProc = Popen(["7z", f"-v{TG_SPLIT_SIZE}b", "a", "-mx=0", f"-p{self.pswd}", path, m_path])
                    else:
                        self.SubProc = Popen(["7z", "a", "-mx=0", f"-p{self.pswd}", path, m_path])
                elif self.isLeech and int(size) > TG_SPLIT_SIZE:
                    self.SubProc = Popen(["7z", f"-v{TG_SPLIT_SIZE}b", "a", "-mx=0", path, m_path])
                else:
                    self.SubProc = Popen(["7z", "a", "-mx=0", path, m_path])
                self.SubProc.wait()
                if self.SubProc.returncode == -9:
                    return
                elif self.SubProc.returncode != 0:
                    LOGGER.error('Unable to extract archive splits!')
            except FileNotFoundError:
                LOGGER.info('File to archive not found!')
                self.onUploadError('Internal error occurred!!')
                return
            if not self.MultiZip:
                if not self.isQbit or not self.seed or self.isLeech:
                    try:
                        rmtree(m_path)
                    except:
                        osremove(m_path)
        elif self.extract or self.MultiUnZip:
            try:
                
                if ospath.isfile(m_path) and not self.MultiUnZip:
                    path = get_base_name(m_path)
                    LOGGER.info(f"Extracting: {name}")
                    with download_dict_lock:
                        download_dict[self.uid] = ExtractStatus(name, m_path, path,gid,self)
                if ospath.isdir(m_path):
                    path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
                    LOGGER.info(f"Extracting: {name}")
                    with download_dict_lock:
                        download_dict[self.uid] = ExtractStatus(name, m_path, path,gid,self)
                    for dirpath, subdir, files in walk(m_path, topdown=False):
                        for file_ in files:
                            if file_.endswith((".zip", ".7z")) or re_search(r'\.part0*1\.rar$|\.7z\.0*1$|\.zip\.0*1$', file_) \
                               or (file_.endswith(".rar") and not re_search(r'\.part\d+\.rar$', file_)):
                                m_path = ospath.join(dirpath, file_)
                                if self.pswd is not None:
                                    self.SubProc = Popen(["7z", "x", f"-p{self.pswd}", m_path, f"-o{dirpath}", "-aot"])
                                else:
                                    self.SubProc = Popen(["7z", "x", m_path, f"-o{dirpath}", "-aot"])
                                self.SubProc.wait()
                                if self.SubProc.returncode == -9:
                                    return
                                elif self.SubProc.returncode != 0:
                                    LOGGER.error('Unable to extract archive splits!')
                        for file_ in files:
                            if file_.endswith((".rar", ".zip", ".7z")) or re_search(r'\.r\d+$|\.7z\.\d+$|\.z\d+$|\.zip\.\d+$', file_):
                                del_path = ospath.join(dirpath, file_)
                                osremove(del_path)
                elif self.MultiUnZip :
                    original_path = f'{DOWNLOAD_DIR}{self.uid}'
                    path = f'{DOWNLOAD_DIR}{self.uid}'
                    LOGGER.info(f"Extracting Multi: {name}")
                    with download_dict_lock:
                        download_dict[self.uid] = ExtractStatus(name, original_path, path,gid,self)
                    counter = 0
                    for dirpath, subdir, files in walk(original_path, topdown=False):
                        for file_ in files:
                            if counter < 1:
                                if file_.endswith((".zip", ".7z")) or re_search(r'\.part0*1\.rar$|\.7z\.0*1$|\.zip\.0*1$', file_) \
                                or (file_.endswith(".rar") and not re_search(r'\.part\d+\.rar$', file_)):
                                    m_path = ospath.join(dirpath, file_)
                                    LOGGER.info(f"Extracting : {m_path}")
                                    if self.pswd is not None:
                                        self.SubProc = Popen(["bash", "pextract", m_path, self.pswd])
                                    else:
                                        self.SubProc = Popen(["7z", "e",f"-o{original_path}", m_path])
                                    self.SubProc.wait()
                                    if self.SubProc.returncode == -9:
                                        return
                                    elif self.SubProc.returncode != 0:
                                        LOGGER.error('Unable to extract archive splits!')
                        for file_ in files:
                            if file_.endswith((".rar", ".zip", ".7z")) or re_search(r'\.r\d+$|\.7z\.\d+$|\.z\d+$|\.zip\.\d+$', file_):
                                del_path = ospath.join(dirpath, file_)
                                osremove(del_path)
                else:
                    if self.pswd is not None:
                        self.SubProc = Popen(["bash", "pextract", m_path, self.pswd])
                    else:
                        self.SubProc = Popen(["bash", "extract", m_path])
                    self.SubProc.wait()
                    if self.SubProc.returncode == -9:
                        return
                    elif self.SubProc.returncode == 0:
                        LOGGER.info(f"Extracted Path: {path}")
                        osremove(m_path)
                    else:
                        LOGGER.error('Unable to extract archive! Uploading anyway')
                        path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
            except NotSupportedExtractionArchive:
                LOGGER.info("Not any valid archive, uploading file as it is.")
                path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
        else:
            path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
        up_name = PurePath(path).name
        up_path = f'{DOWNLOAD_DIR}{self.uid}/{up_name}'
        if ospath.isfile(up_path):
            isfilexi = True
        else:
            isfilexi = False
        if self.isLeech and not self.isZip:
            checked = False
            for dirpath, subdir, files in walk(f'{DOWNLOAD_DIR}{self.uid}', topdown=False):
                for file_ in files:
                    f_path = ospath.join(dirpath, file_)
                    f_size = ospath.getsize(f_path)
                    if int(f_size) > MAX_SPLIT_SIZE:
                        if not checked:
                            checked = True
                            with download_dict_lock:
                                download_dict[self.uid] = SplitStatus(up_name, up_path, size,gid)
                            LOGGER.info(f"Splitting: {up_name}")
                        split_file(f_path, f_size, file_, dirpath, MAX_SPLIT_SIZE,self)
                        osremove(f_path)
        if self.isLeech:
            size = get_path_size(f'{DOWNLOAD_DIR}{self.uid}')
            LOGGER.info(f"Leech Name: {up_name}")
            tg = TgUploader(up_name, self)
            tg_upload_status = TgUploadStatus(tg, size, gid, self)
            with download_dict_lock:
                download_dict[self.uid] = tg_upload_status
            update_all_messages()
            tg.upload()
        else:
            FlagPORN = False
            if self.message.from_user.id in AUTODELETE_USERS:
                FlagPORN = True
                filter_message = f"<br>Bot Changed File Names Because Of Your LeechSetting<br>\n<br>if you don't link it you can change it with command {BotCommands.LeechSetCommand}<br>\n<br>Changed Files/Folders:<br>\n"
            else:
                Checked = CheckPorn(f'{DOWNLOAD_DIR}{self.uid}')
                if Checked[0] == True:
                    FlagPORN = True
                    filter_message = Checked[1]
                else:
                    pass
            if FlagPORN == True:
                for dirpath, subdir, files in walk(f'{DOWNLOAD_DIR}{self.uid}', topdown=False):
                    for subdir_ in subdir:
                        ipath = ospath.join(dirpath,subdir_)
                        dpath = ospath.join(dirpath,'.'.join(subdir_.replace(' ','').replace('.','')))
                        rename(ipath,dpath)
                        filter_message += f"<br>{PurePath(ipath).name} <-ChangedTo-> {PurePath(dpath).name}<br>\n"
                    for file_ in files:
                        f_path = ospath.join(dirpath, file_)
                        fxi , fnamexi = ospath.splitext(f_path)
                        random_name = ''.join(random.choices(string.ascii_letters+string.ascii_lowercase+string.ascii_uppercase+string.digits,k=random.randint(8,16)))+fnamexi
                        rename(f_path,ospath.join(dirpath,random_name))
                        filter_message += f"<br>{PurePath(f_path).name} <-ChangedTo-> {random_name}<br>\n"
                if isfilexi == True:
                    LOGGER.info(f"Torrent/Download is : File[Porn] , {up_path}")
                    self.NameBeforeChange[0] = str(PurePath(path).name)
                    self.NameBeforeChange[1] = "File"
                    up_name = random_name
                    up_path = f'{DOWNLOAD_DIR}{self.uid}/{up_name}'
                else:
                    LOGGER.info(f"Torrent/Download is : Folder[Porn] , {up_path}")
                    up_name = PurePath(path).name
                    self.NameBeforeChange[0] = str(up_name)
                    self.NameBeforeChange[1] = "Folder"
                    up_name = '.'.join(up_name.replace(' ','').replace('.',''))
                    up_path = f'{DOWNLOAD_DIR}{self.uid}/{up_name}'
                filter_url = telegraph.create_page(title='Mirror-Leech-Bot Help',content=filter_message)["path"]
                self.NameBeforeChange[2] = f"https://telegra.ph/{filter_url}"
                self.NameBeforeChange[-1] = True
            size = get_path_size(up_path)
            LOGGER.info(f"Upload Name: {up_name}")
            drive = GoogleDriveHelper(up_name, self)
            upload_status = UploadStatus(drive, size, gid, self)
            with download_dict_lock:
                download_dict[self.uid] = upload_status
            update_all_messages()
            drive.upload(up_name)

    def onDownloadError(self, error):
        error = error.replace('<', ' ').replace('>', ' ')
        clean_download(f'{DOWNLOAD_DIR}{self.uid}')
        with download_dict_lock:
            try:
                del download_dict[self.uid]
            except Exception as e:
                LOGGER.error(str(e))
            count = len(download_dict)
        msg = f"{self.tag} your download has been stopped due to: {error}"
        sendMessage(msg, self.bot, self.message)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

        if INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
            DbManger().rm_complete_task(self.message.link)

    def onUploadComplete(self, link, size, files, folders, typ, name: str):
        if INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
            DbManger().rm_complete_task(self.message.link)
        if self.NameBeforeChange[-1] == True:
            LOGGER.info(self.NameBeforeChange)
            msg = f"<b>Original-Name: </b><code>{self.NameBeforeChange[0]}</code>\n\n<b>Name: </b><code>{escape(name)}</code>\n\n<b>Size: </b>{size}"
            if self.NameBeforeChange[1] == "Folder":
                msg += f"\n\n 🔥❌⚠️ Also Files Got Renamed <a href='{self.NameBeforeChange[2]}'>Here</a>⚠️❌🔥"
        else:
            msg = f"<b>Name: </b><code>{escape(name)}</code>\n\n<b>Size: </b>{size}"
        if self.message.from_user.id in HASH_USERS:
            LOGGER.info(f'Getting Hash For :{DOWNLOAD_DIR}{self.uid}/{name}')
            get_path_hash = get_path_md5_sha(f'{DOWNLOAD_DIR}{self.uid}/{name}')
            if get_path_hash[-1] == True:
                md5 , sha1 , sha256 = get_path_hash[:-1]
                msg += f'\n\nMd5 : {md5}\nSHA1 : {sha1}\nSHA256 : {sha256}'
        if self.isLeech:
            msg += f'\n<b>Total Files: </b>{folders}'
            if typ != 0:
                msg += f'\n<b>Corrupted Files: </b>{typ}'
            msg += f'\n<b>cc: </b>{self.tag}\n\n<b>Thanks For Using Our Group</b>\n<b>Please also share this bot with your friends @MX_TR_Official</b>\n\n'
            if not files:
                sendMessage(msg, self.bot, self.message)
            else:
                for index, (link, name) in enumerate(files.items(), start=1):
                    #Copy Them to PV
                    original = link.split('/')
                    LOGGER.info(('-100'+str(original[-2])))
                    LOGGER.info(original[-1])
                    copyLeechToPv(self.bot, self.message,original)
                fmsg = ''
                for index, (link, name) in enumerate(files.items(), start=1):
                    fmsg += f"{index}. <a href='{link}'>{name}</a>\n"
                    if len(fmsg.encode() + msg.encode()) > 4000:
                        copy = sendMessage(msg + fmsg, self.bot, self.message)
                        #Send Complete Message To PV
                        copyMessageToPv(self.bot,self.message, copy)
                        sleep(1)
                        fmsg = ''
                if fmsg != '':
                    copy = sendMessage(msg + fmsg, self.bot, self.message)
                    #Send Complete Message To PV
                    copyMessageToPv(self.bot,self.message, copy)
        else:
            msg += f'\n\n<b>Type: </b>{typ}'
            if ospath.isdir(f'{DOWNLOAD_DIR}{self.uid}/{name}'):
                msg += f'\n<b>SubFolders: </b>{folders}'
                msg += f'\n<b>Files: </b>{files}'
            buttons = ButtonMaker()
            buttons.buildbutton("☁️ Drive Link", link[0])
            LOGGER.info(f'Done Uploading {name}')
            if INDEX_URL is not None:
                url_path = rutils.quote(f'{name}')
                share_url = f'{INDEX_URL}/{url_path}'
                if ospath.isdir(f'{DOWNLOAD_DIR}/{self.uid}/{name}'):
                    share_url += '/'
                    iran_url = share_url.replace(INDEX_URL,'https://dl1.mxfile-irani.ga/0:')
                    backup_links = f'Main Drive : <code>{share_url}</code>'
                    iran_backup_links = f'Main Drive : <code>{iran_url}</code>'
                    for i in range(1,len(link)):
                        if 'drive.google' in link[i]:
                            backup_links += f'\nDrive {i} : <code>{share_url.replace(INDEX_URL,INDEX_BACKUP[i-1])}</code>'
                            if IRAN_INDEX_BACKUP[i-1] == 'Nothing...':
                                iran_backup_links += f'\nDrive {i} : <code>{share_url.replace(share_url,IRAN_INDEX_BACKUP[i-1])}</code>'
                            else:
                                iran_backup_links += f'\nDrive {i} : <code>{share_url.replace(INDEX_URL,IRAN_INDEX_BACKUP[i-1])}</code>'
                        else:
                            backup_links += f'\nDrive {i} : Error!'
                            iran_backup_links += f'\nDrive {i} : Error!'
                    msg += f'\n\n<b>🇩🇪 لینک تمام بها</b>\n\n{backup_links}\n\n<b>🇮🇷 نیم بها</b>\n\n{iran_backup_links}'
                    msg += f'\n\n<b>cc: </b>{self.tag}\n\n<b>Thanks For Using Our Group</b>\n<b>Please also share this bot with your friends @MX_TR_Official</b>'
                    buttons.buildbutton("⚡ Server (🇩🇪)", share_url)
                    buttons.buildbutton("🇮🇷 نیم بها", iran_url)
                else:
                    iran_url = share_url.replace(INDEX_URL,'https://dl1.mxfile-irani.ga/0:')
                    iran_backup_links = f'Main Drive : <code>{iran_url}</code>'
                    backup_links = f'Main Drive : <code>{share_url}</code>'
                    for i in range(1,len(link)):
                        if 'drive.google' in link[i]:
                            backup_links += f'\nDrive {i} : <code>{share_url.replace(INDEX_URL,INDEX_BACKUP[i-1])}</code>'
                            if IRAN_INDEX_BACKUP[i-1] == 'Nothing...':
                                iran_backup_links += f'\nDrive {i} : <code>{share_url.replace(share_url,IRAN_INDEX_BACKUP[i-1])}</code>'
                            else:
                                iran_backup_links += f'\nDrive {i} : <code>{share_url.replace(INDEX_URL,IRAN_INDEX_BACKUP[i-1])}</code>'
                        else :
                            backup_links += f'\nDrive {i} : Error!'
                            iran_backup_links += f'\nDrive {i} : Error!'
                    msg += f'\n\n<b>🇩🇪 لینک تمام بها</b>\n\n{backup_links}\n\n<b>🇮🇷 نیم بها</b>\n\n{iran_backup_links}'
                    msg += f'\n\n<b>cc: </b>{self.tag}\n\n<b>Thanks For Using Our Group</b>\n<b>Please also share this bot with your friends @MX_TR_Official</b>'
                    buttons.buildbutton("⚡ Server (🇩🇪)", share_url)
                    buttons.buildbutton("🇮🇷 نیم بها", iran_url)
                    if VIEW_LINK:
                        share_urls = f'{INDEX_URL}/{url_path}?a=view'
                        buttons.buildbutton("🌐 View Link", share_urls)
            sendMarkup(msg, self.bot, self.message, InlineKeyboardMarkup(buttons.build_menu(2)))
            if self.isQbit and self.seed and not self.extract:
                if self.isZip:
                    try:
                        osremove(f'{DOWNLOAD_DIR}{self.uid}/{name}')
                    except:
                        pass
                return
        clean_download(f'{DOWNLOAD_DIR}{self.uid}')
        with download_dict_lock:
            try:
                del download_dict[self.uid]
            except Exception as e:
                LOGGER.error(str(e))
            count = len(download_dict)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

    def onUploadError(self, error):
        e_str = error.replace('<', '').replace('>', '')
        clean_download(f'{DOWNLOAD_DIR}{self.uid}')
        with download_dict_lock:
            try:
                del download_dict[self.uid]
            except Exception as e:
                LOGGER.error(str(e))
            count = len(download_dict)
        sendMessage(f"{self.tag} {e_str}", self.bot, self.message)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

        if INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
            DbManger().rm_complete_task(self.message.link)

def mustjoin(idmustjoin):
    Flag = False
    for Memberin in app.get_chat_members('@MX_TR_Official'):
        if idmustjoin == Memberin.user.id:
            Flag = True
    if Flag == True:
        for Memberin in app.get_chat_members(-1001727312001):
            if idmustjoin == Memberin.user.id:
                return True
    return False

def message_deleter(user_id: int,message):
    if user_id in AUTODELETE_USERS:
        sleep(2)
        message.delete()

def _mirror(bot, message, isZip=False, extract=False, isQbit=False, isLeech=False, pswd=None, multi=0, qbsd=False,MultiZip=[[],False],MultiUnZip=[[],False],Extract_Audio=False,SoftSub=[[],False],MultiTelegram=False):
    idmustjoin = message.from_user.id
    if mustjoin(idmustjoin) == True:
        mesg = message.text.split('\n')
        if MultiZip[1] == True :
            MultiZip[0] = mesg[1:]
        elif MultiUnZip[1] == True :
            MultiUnZip[0] = mesg[1:]
        elif SoftSub[1] == True :
            SoftSub[0] = mesg[1:]
        message_args = mesg[0].split(maxsplit=1)
        name_args = mesg[0].split('|', maxsplit=1)
        qbsel = False
        index = 1

        if len(message_args) > 1:
            args = mesg[0].split(maxsplit=3)
            if "s" in [x.strip() for x in args]:
                qbsel = True
                index += 1
            if "d" in [x.strip() for x in args]:
                qbsd = True
                index += 1
            message_args = mesg[0].split(maxsplit=index)
            if len(message_args) > index:
                link = message_args[index].strip()
                if link.isdigit():
                    multi = int(link)
                    link = ''
                elif link.startswith(("|", "pswd:")):
                    link = ''
            else:
                link = ''
        else:
            link = ''

        if len(name_args) > 1:
            name = name_args[1]
            name = name.split(' pswd:')[0]
            name = name.strip()
        else:
            name = ''

        link = re_split(r"pswd:|\|", link)[0]
        link = link.strip()

        pswd_arg = mesg[0].split(' pswd: ')
        if len(pswd_arg) > 1:
            pswd = pswd_arg[1]
        
        if message.from_user.username:
            tag = f"@{message.from_user.username}"
        else:
            tag = message.from_user.mention_html(message.from_user.first_name)

        reply_to = message.reply_to_message
        if reply_to is not None:
            file = None
            media_array = [reply_to.document, reply_to.video, reply_to.audio]
            for i in media_array:
                if i is not None:
                    file = i
                    break

            if not reply_to.from_user.is_bot:
                if reply_to.from_user.username:
                    tag = f"@{reply_to.from_user.username}"
                else:
                    tag = reply_to.from_user.mention_html(reply_to.from_user.first_name)

            if (
                not is_url(link)
                and not is_magnet(link)
                or len(link) == 0
            ):

                if file is None:
                    reply_text = reply_to.text.split(maxsplit=1)[0].strip()
                    if is_url(reply_text) or is_magnet(reply_text):
                        link = reply_text
                elif file.mime_type != "application/x-bittorrent" and not isQbit:
                    listener = MirrorListener(bot, message, isZip=isZip, extract=extract, isQbit=isQbit, isLeech=isLeech, pswd=pswd, tag=tag,MultiZip=MultiZip,MultiUnZip=MultiUnZip,Extract_Audio=Extract_Audio)
                    if MultiTelegram == False:
                        Thread(target=TelegramDownloadHelper(listener).add_download, args=(message, f'{DOWNLOAD_DIR}{listener.uid}/', name)).start()
                    if multi > 1:
                        sleep(4)
                        nextmsg = type('nextmsg', (object, ), {'chat_id': message.chat_id, 'message_id': message.reply_to_message.message_id + 1})
                        nextmsg = sendMessage(message_args[0], bot, nextmsg)
                        nextmsg.from_user.id = message.from_user.id
                        multi -= 1
                        sleep(4)
                        Thread(target=_mirror, args=(bot, nextmsg, isZip, extract, isQbit, isLeech, pswd, multi)).start()
                        message_deleter(idmustjoin,message)
                    return
                else:
                    link = file.get_file().file_path

        if not is_url(link) and not is_magnet(link) and not ospath.exists(link) and not MultiTelegram:
            help_msg = "<b>Send link along with command line:</b>"
            help_msg += "\n<code>/command</code> {link} |newname pswd: xx [zip/unzip]"
            help_msg += "\n\n<b>By replying to link or file:</b>"
            help_msg += "\n<code>/command</code> |newname pswd: xx [zip/unzip]"
            help_msg += "\n\n<b>Direct link authorization:</b>"
            help_msg += "\n<code>/command</code> {link} |newname pswd: xx\nusername\npassword"
            help_msg += "\n\n<b>Qbittorrent selection and seed:</b>"
            help_msg += "\n<code>/qbcommand</code> <b>s</b>(for selection) <b>d</b>(for seeding) {link} or by replying to {file/link}"
            help_msg += "\n\n<b>Multi links only by replying to first link or file:</b>"
            help_msg += "\n<code>/command</code> 10(number of links/files)"
            return sendMessage(help_msg, bot, message)

        LOGGER.info(link)

        if not is_mega_link(link) and not isQbit and not MultiTelegram and not is_magnet(link) \
            and not is_gdrive_link(link) and not link.endswith('.torrent'):
            content_type = get_content_type(link)
            if content_type is None or re_match(r'text/html|text/plain', content_type):
                try:
                    link = direct_link_generator(link)
                    LOGGER.info(f"Generated link: {link}")
                except DirectDownloadLinkException as e:
                    LOGGER.info(str(e))
                    if str(e).startswith('ERROR:'):
                        return sendMessage(str(e), bot, message)

        listener = MirrorListener(bot, message, isZip=isZip, extract=extract, isQbit=isQbit, isLeech=isLeech, pswd=pswd, tag=tag, seed=qbsd,MultiZip=MultiZip,MultiUnZip=MultiUnZip,SoftSub=SoftSub,Extract_Audio=Extract_Audio)

        if MultiTelegram:
            Thread(target=Multi_Listener_Telegram_Runner,args=(message,listener.uid,bot,DOWNLOAD_DIR,name,listener)).start()
            return

        if is_gdrive_link(link):
            if not isZip and not extract and not isLeech:
                gmsg = f"Use /{BotCommands.CloneCommand} to clone Google Drive file/folder\n\n"
                gmsg += f"Use /{BotCommands.ZipMirrorCommand} to make zip of Google Drive folder\n\n"
                gmsg += f"Use /{BotCommands.UnzipMirrorCommand} to extracts Google Drive archive file"
                sendMessage(gmsg, bot, message)
            else:
                Thread(target=add_gd_download, args=(link, listener)).start()
                message_deleter(idmustjoin,message)
        elif is_mega_link(link):
            if MEGA_KEY is not None:
                Thread(target=MegaDownloader(listener).add_download, args=(link, f'{DOWNLOAD_DIR}{listener.uid}/')).start()
                message_deleter(idmustjoin,message)
            else:
                sendMessage('MEGA_API_KEY not Provided!', bot, message)
        elif isQbit:
            Thread(target=QbDownloader(listener).add_qb_torrent, args=(link, f'{DOWNLOAD_DIR}{listener.uid}', qbsel)).start()
            message_deleter(idmustjoin,message)
        else:
            if MultiZip[1] == False and MultiUnZip[1] == False and SoftSub[1] == False:
                if len(mesg) > 1:
                    try:
                        ussr = mesg[1]
                    except:
                        ussr = ''
                    try:
                        pssw = mesg[2]
                    except:
                        pssw = ''
                    auth = f"{ussr}:{pssw}"
                    auth = "Basic " + b64encode(auth.encode()).decode('ascii')
                else:
                    auth = ''
                Thread(target=add_aria2c_download, args=(link, f'{DOWNLOAD_DIR}{listener.uid}', listener, name, auth)).start()
                message_deleter(idmustjoin,message)
            elif MultiZip[1] == True:
                MultiZip[0].append(link)
                Thread(target=Multi_Zip_Function, args=(MultiZip[0], f'{DOWNLOAD_DIR}{listener.uid}', listener)).start()
            elif MultiUnZip[1] == True:
                MultiUnZip[0].append(link)
                Thread(target=Multi_Zip_Function, args=(MultiUnZip[0], f'{DOWNLOAD_DIR}{listener.uid}', listener)).start()
            elif SoftSub[1] == True:
                SoftSub[0].append(link)
                Thread(target=Multi_Zip_Function, args=(SoftSub[0], f'{DOWNLOAD_DIR}{listener.uid}', listener,True)).start()
            

        if multi > 1:
            sleep(4)
            nextmsg = type('nextmsg', (object, ), {'chat_id': message.chat_id, 'message_id': message.reply_to_message.message_id + 1})
            msg = message_args[0]
            if len(mesg) > 2:
                msg += '\n' + mesg[1] + '\n' + mesg[2]
            nextmsg = sendMessage(msg, bot, nextmsg)
            nextmsg.from_user.id = message.from_user.id
            multi -= 1
            sleep(4)
            Thread(target=_mirror, args=(bot, nextmsg, isZip, extract, isQbit, isLeech, pswd, multi,)).start()
            message_deleter(idmustjoin,message)
    elif mustjoin(idmustjoin) == False:
        buttons = ButtonMaker()
        buttons.buildbutton("Channel", "https://t.me/MX_TR_Official")
        buttons.buildbutton("Group", "https://t.me/+xNDVQdjEoOpmYTRk")
        buttons.buildbutton("Owner", "https://t.me/MahdiXi021")
        reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
        sendMarkup('شما در گروه و چنل ربات عضو نیستید\nبرای استفاده از ربات در هردو عضو شوید :)', bot,message, reply_markup)

def mirror(update, context):
    _mirror(context.bot, update.message)

def multizip_mirror(update, context):
    _mirror(context.bot, update.message,MultiZip=[[],True])

def multizip_leech(update, context):
    _mirror(context.bot, update.message,isLeech=True,MultiZip=[[],True])

def multiunzip_mirror(update, context):
    _mirror(context.bot, update.message,MultiUnZip=[[],True])

def multiunzip_leech(update, context):
    _mirror(context.bot, update.message,MultiUnZip=[[],True],isLeech=True)

def multizip_telegram(update, context):
    _mirror(context.bot, update.message,MultiZip=[[],True],MultiTelegram=True)

def multizip_telegram_leech(update, context):
    _mirror(context.bot, update.message,MultiZip=[[],True],MultiTelegram=True,isLeech=True)

def multiunzip_telegram(update, context):
    _mirror(context.bot, update.message,MultiUnZip=[[],True],MultiTelegram=True)

def multiunzip_telegram_leech(update, context):
    _mirror(context.bot, update.message,MultiUnZip=[[],True],MultiTelegram=True,isLeech=True)

def audioextract_mirror(update, context):
    _mirror(context.bot, update.message,Extract_Audio=True)

def softsub_leech(update, context):
    _mirror(context.bot, update.message,SoftSub=[[],True],isLeech=True)

def softsub_mirror(update, context):
    _mirror(context.bot, update.message,SoftSub=[[],True])

def audioextract_leech(update, context):
    _mirror(context.bot, update.message,isLeech=True,Extract_Audio=True)

def unzip_mirror(update, context):
    _mirror(context.bot, update.message, extract=True)

def zip_mirror(update, context):
    _mirror(context.bot, update.message, True)

def qb_mirror(update, context):
    _mirror(context.bot, update.message, isQbit=True)

def qb_unzip_mirror(update, context):
    _mirror(context.bot, update.message, extract=True, isQbit=True)

def qb_zip_mirror(update, context):
    _mirror(context.bot, update.message, True, isQbit=True)

def leech(update, context):
    _mirror(context.bot, update.message, isLeech=True)

def unzip_leech(update, context):
    _mirror(context.bot, update.message, extract=True, isLeech=True)

def zip_leech(update, context):
    _mirror(context.bot, update.message, True, isLeech=True)

def qb_leech(update, context):
    _mirror(context.bot, update.message, isQbit=True, isLeech=True)

def qb_unzip_leech(update, context):
    _mirror(context.bot, update.message, extract=True, isQbit=True, isLeech=True)

def qb_zip_leech(update, context):
    _mirror(context.bot, update.message, True, isQbit=True, isLeech=True)

mirror_handler = CommandHandler(BotCommands.MirrorCommand, mirror,
                                run_async=True)

multizip_mirror_handler = CommandHandler(BotCommands.MultiZipMirrorCommand, multizip_mirror,
                                run_async=True)
multizip_leech_handler = CommandHandler(BotCommands.MultiZipLeechCommand, multizip_leech,
                                run_async=True)
softsub_mirror_handler = CommandHandler(BotCommands.SoftSubLeechCommand, softsub_leech,
                                run_async=True)
softsub_leech_handler = CommandHandler(BotCommands.SoftSubMirrorCommand, softsub_mirror,
                                run_async=True)
multiunzip_mirror_handler = CommandHandler(BotCommands.MultiUnZipMirrorCommand, multiunzip_mirror,
                                run_async=True)
multiunzip_leech_handler = CommandHandler(BotCommands.MultiUnZipLeechCommand, multiunzip_leech,
                                run_async=True)
multizip_telegram_handler = CommandHandler(BotCommands.MultiZipTelegramCommand, multizip_telegram,
                                run_async=True)
multizip_telegram_leech_handler = CommandHandler(BotCommands.MultiZipTelegramCommand, multizip_telegram_leech,
                                run_async=True)
multiunzip_telegram_handler = CommandHandler(BotCommands.MultiUnZipTelegramCommand, multiunzip_telegram,
                                run_async=True)                      
multiunzip_telegram_leech_handler = CommandHandler(BotCommands.MultiUnZipTelegramLeechCommand, multiunzip_telegram_leech,
                                run_async=True)  
audioextract_leech_handler = CommandHandler(BotCommands.AudioExtractLeechCommand, audioextract_leech,
                                run_async=True)
audioextract_mirror_handler = CommandHandler(BotCommands.AudioExtractMirrorCommand, audioextract_mirror,
                                run_async=True)
unzip_mirror_handler = CommandHandler(BotCommands.UnzipMirrorCommand, unzip_mirror,
                                run_async=True)
zip_mirror_handler = CommandHandler(BotCommands.ZipMirrorCommand, zip_mirror,
                                run_async=True)
qb_mirror_handler = CommandHandler(BotCommands.QbMirrorCommand, qb_mirror,
                                run_async=True)
qb_unzip_mirror_handler = CommandHandler(BotCommands.QbUnzipMirrorCommand, qb_unzip_mirror,
                                run_async=True)
qb_zip_mirror_handler = CommandHandler(BotCommands.QbZipMirrorCommand, qb_zip_mirror,
                                run_async=True)
leech_handler = CommandHandler(BotCommands.LeechCommand, leech,
                                 run_async=True)
unzip_leech_handler = CommandHandler(BotCommands.UnzipLeechCommand, unzip_leech,
                                 run_async=True)
zip_leech_handler = CommandHandler(BotCommands.ZipLeechCommand, zip_leech,
                                 run_async=True)
qb_leech_handler = CommandHandler(BotCommands.QbLeechCommand, qb_leech,
                                 run_async=True)
qb_unzip_leech_handler = CommandHandler(BotCommands.QbUnzipLeechCommand, qb_unzip_leech,
                                 run_async=True)
qb_zip_leech_handler = CommandHandler(BotCommands.QbZipLeechCommand, qb_zip_leech,
                                 run_async=True)

dispatcher.add_handler(softsub_mirror_handler)
dispatcher.add_handler(softsub_leech_handler)
dispatcher.add_handler(multizip_mirror_handler)
dispatcher.add_handler(multizip_leech_handler)
dispatcher.add_handler(multiunzip_mirror_handler)
dispatcher.add_handler(multiunzip_leech_handler)
dispatcher.add_handler(multizip_telegram_handler)
dispatcher.add_handler(multizip_telegram_leech_handler)
dispatcher.add_handler(multiunzip_telegram_handler)
dispatcher.add_handler(multiunzip_telegram_leech_handler)
dispatcher.add_handler(audioextract_mirror_handler)
dispatcher.add_handler(audioextract_leech_handler)
dispatcher.add_handler(mirror_handler)
dispatcher.add_handler(unzip_mirror_handler)
dispatcher.add_handler(zip_mirror_handler)
dispatcher.add_handler(qb_mirror_handler)
dispatcher.add_handler(qb_unzip_mirror_handler)
dispatcher.add_handler(qb_zip_mirror_handler)
dispatcher.add_handler(leech_handler)
dispatcher.add_handler(unzip_leech_handler)
dispatcher.add_handler(zip_leech_handler)
dispatcher.add_handler(qb_leech_handler)
dispatcher.add_handler(qb_unzip_leech_handler)
dispatcher.add_handler(qb_zip_leech_handler)
