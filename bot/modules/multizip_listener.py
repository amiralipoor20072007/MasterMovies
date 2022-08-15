from time import sleep
from telegram.ext import CommandHandler
from bot import multizip_telegram_download_dict, app,dispatcher
from bot.helper.mirror_utils.download_utils.telegram_downloader import MultiZip_Telegram
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import deleteMessage, sendMessage

class MultiZip_Telegram_GetIDs():

    def __init__(self,user_id,chat_id,firstid,DOWNLOAD_DIR,message,name,listener) -> None:
        self.downloadIDs = []
        self.All_Messages = []
        self.user_id = user_id
        self.chat_id = chat_id
        self.FirstID = firstid
        self.LastID = 0
        self.All_IDs = []
        self.DOWNLOAD_DIR = DOWNLOAD_DIR
        self.message = message
        self.name = name
        self.listener = listener

    def SetLastID(self,id):
        self.LastID = id

    def Add_id(self,message_id):
        self.downloadIDs.append(message_id)
    
    def Get_All_IDs(self):
        for i in range(self.FirstID+1,self.LastID):
            self.All_IDs.append(i)
    
    def Get_Messages(self):
        self.All_Messages = app.get_messages(chat_id=self.chat_id,message_ids=self.All_IDs)
        for message in self.All_Messages:
            media_array = [message.document, message.video, message.audio]
            if message.from_user.id == self.user_id :
                for i in media_array:
                    if i is not None:
                        self.Add_id(message.id)
                        break
    
    def Deliver_To_MultiZip(self):
        Deliver = MultiZip_Telegram(self.DOWNLOAD_DIR,self.message,self.name,self.downloadIDs,self.listener)
        Deliver.run()


def MultiZip_Listener_Telegram_Runner(message,uid,bot,DOWNLOAD_DIR,name,listener):
    help_msg=f"I Got It You Want To Zip Telegram Files\nSo To Do That Just Send Files To Group\n"
    help_msg += f"Then Send {BotCommands.SetLastID} To Confirm Your Downloads And Start Downloading...\n"
    help_msg += f"Tnx For Using Our Group"
    sendMessage(help_msg, bot, message)
    Litsener = MultiZip_Telegram_GetIDs(message.from_user.id,message.chat.id,uid,DOWNLOAD_DIR,message,name,listener)
    multizip_telegram_download_dict[message.from_user.id] = Litsener

def SetLastID(update,context):
    message = update.message
    user_id = message.from_user.id
    bot = context.bot
    confirm = multizip_telegram_download_dict.get(user_id,-1)
    if confirm == -1:
        pass
    else:
        help_msg=f"I Start Mirroring Your Files Please Be Patient"
        temp = sendMessage(help_msg, bot, message)
        sleep(3)
        deleteMessage(bot,temp)
        confirm.SetLastID(message.message_id)
        confirm.Get_All_IDs()
        confirm.Get_Messages()
        confirm.Deliver_To_MultiZip()

multiziptelegram_lastid_handler = CommandHandler(BotCommands.SetLastID,SetLastID,run_async=True)
dispatcher.add_handler(multiziptelegram_lastid_handler)