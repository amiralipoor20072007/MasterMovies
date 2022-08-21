from requests import get as requestsget
from bs4 import BeautifulSoup
from bot import LOGGER , dispatcher
from telegram.ext import CommandHandler
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import sendMessage

def remove_blanks(List : list):
    while True:
        try:
            List.remove('')
        except:
            break
    return List



def oghatsharei(update,context):
    LOGGER.info('Oghat Sharei')
    page = requestsget('https://badesaba.ir/owghat/284/%D8%AA%D9%87%D8%B1%D8%A7%D9%86')
    soup = BeautifulSoup(page.text,'html.parser')
    forum = soup.find('div',attrs={'class':'col-12 col-lg'}).text.split('  ')
    msg = '<b>اوقات شرعی تهران :</b>\n'
    msg +=f'<b>{forum[0]}</b>\n\n'
    for i in range(1,16,2):
        msg += f'<b>{forum[i+1]}</b> : <b>{forum[i]}</b>\n\n'
    sendMessage(msg,context.bot,update.message)

oghatsharei_handler = CommandHandler(BotCommands.OghatSharei,oghatsharei,run_async=True)
dispatcher.add_handler(oghatsharei_handler)