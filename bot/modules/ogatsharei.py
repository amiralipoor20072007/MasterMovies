from telegram.ext import CommandHandler
from bs4 import BeautifulSoup
from bot.helper.telegram_helper.message_utils import sendMessage
from bot.helper.telegram_helper.bot_commands import BotCommands
import requests
from bot import dispatcher

def remove_blanks(List : list):
    while True:
        try:
            List.remove('')
        except:
            break
    return List



def oghatsharei(update,context):
    page = requests.get('time.ir')
    soup = BeautifulSoup(page,'html.parser')
    forum1 = soup.find_all('div',attrs={'class':'col-sm-6'})[6].text.split('\n')
    forum1 = remove_blanks(forum1)
    forum2 = soup.find_all('div',attrs={'class':'col-sm-6'})[7].text.split('\n')
    forum2 = remove_blanks(forum2)
    msg = '<b>طلوع شرعی تهران :</b>\n'
    for i in [0,2,4]:
        msg += f'<b>{forum1[i]}</b> : <b>{forum1[i+1]}</b>'
        msg += f'<b>{forum2[i]}</b> : <b>{forum2[i+1]}</b>'
    sendMessage(msg,context.bot,update.message)


oghatsharei_handler = CommandHandler(BotCommands.OghatSharei,oghatsharei,run_async=True)
dispatcher.add_handler(oghatsharei_handler)