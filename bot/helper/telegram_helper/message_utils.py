from time import sleep, time
from telegram import InlineKeyboardMarkup
from telegram.message import Message
from telegram.error import RetryAfter
from pyrogram.errors import FloodWait
from os import remove

from bot import AUTO_DELETE_MESSAGE_DURATION, LOGGER, status_reply_dict, status_reply_dict_lock, \
                Interval, DOWNLOAD_STATUS_UPDATE_INTERVAL, RSS_CHAT_ID, bot, rss_session,INDEX_URL
from bot.helper.ext_utils.bot_utils import get_readable_message, setInterval


def sendMessage(text: str, bot, message: Message):
    try:
        return bot.sendMessage(message.chat_id,
                            reply_to_message_id=message.message_id,
                            text=text, allow_sending_without_reply=True, parse_mode='HTML', disable_web_page_preview=True)
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return sendMessage(text, bot, message)
    except Exception as e:
        LOGGER.error(str(e))
        return

def sendMarkup(text: str, bot, message: Message, reply_markup: InlineKeyboardMarkup):
    try:
        return bot.sendMessage(message.chat_id,
                            reply_to_message_id=message.message_id,
                            text=text, reply_markup=reply_markup, allow_sending_without_reply=True,
                            parse_mode='HTML', disable_web_page_preview=True)
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return sendMarkup(text, bot, message, reply_markup)
    except Exception as e:
        LOGGER.error(str(e))
        return

def editMessage(text: str, message: Message, reply_markup=None):
    try:
        bot.editMessageText(text=text, message_id=message.message_id,
                              chat_id=message.chat.id,reply_markup=reply_markup,
                              parse_mode='HTML', disable_web_page_preview=True)
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return editMessage(text, message, reply_markup)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

def sendRss(text: str, bot):
    if rss_session is None:
        try:
            return bot.sendMessage(RSS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
        except RetryAfter as r:
            LOGGER.warning(str(r))
            sleep(r.retry_after * 1.5)
            return sendRss(text, bot)
        except Exception as e:
            LOGGER.error(str(e))
            return
    else:
        try:
            with rss_session:
                return rss_session.send_message(RSS_CHAT_ID, text, disable_web_page_preview=True)
        except FloodWait as e:
            LOGGER.warning(str(e))
            sleep(e.value * 1.5)
            return sendRss(text, bot)
        except Exception as e:
            LOGGER.error(str(e))
            return

def deleteMessage(bot, message: Message):
    try:
        bot.deleteMessage(chat_id=message.chat.id,
                           message_id=message.message_id)
    except Exception as e:
        LOGGER.error(str(e))

def sendLogFile(bot, message: Message):
    with open('log.txt', 'rb') as f:
        bot.sendDocument(document=f, filename=f.name,
                          reply_to_message_id=message.message_id,
                          chat_id=message.chat_id)
        
def sendFile(bot, message: Message, name: str, caption=""):
    try:
        with open(name, 'rb') as f:
            bot.sendDocument(document=f, filename=f.name, reply_to_message_id=message.message_id,
                             caption=caption, parse_mode='HTML',chat_id=message.chat_id)
        remove(name)
        return
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return sendFile(bot, message, name, caption)
    except Exception as e:
        LOGGER.error(str(e))
        return

def sendFile(bot, message: Message, name: str, caption=""):
    try:
        with open(name, 'rb') as f:
            bot.sendDocument(document=f, filename=f.name, reply_to_message_id=message.message_id,
                             caption=caption, parse_mode='HTML',chat_id=message.chat_id)
        remove(name)
        return
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return sendFile(bot, message, name, caption)
    except Exception as e:
        LOGGER.error(str(e))
        return

def auto_delete_message(bot, cmd_message: Message, bot_message: Message):
    if AUTO_DELETE_MESSAGE_DURATION != -1:
        sleep(AUTO_DELETE_MESSAGE_DURATION)
        try:
            # Skip if None is passed meaning we don't want to delete bot xor cmd message
            deleteMessage(bot, cmd_message)
            deleteMessage(bot, bot_message)
        except AttributeError:
            pass

def delete_all_messages():
    with status_reply_dict_lock:
        for data in list(status_reply_dict.values()):
            try:
                deleteMessage(bot, data[0])
                del status_reply_dict[data[0].chat.id]
            except Exception as e:
                LOGGER.error(str(e))

def update_all_messages(force=False):
    with status_reply_dict_lock:
        if not force and (not status_reply_dict or not Interval or time() - list(status_reply_dict.values())[0][1] < 3):
            return
        for chat_id in status_reply_dict:
            status_reply_dict[chat_id][1] = time()

    msg, buttons = get_readable_message()
    if msg is None:
        return
    with status_reply_dict_lock:
        for chat_id in status_reply_dict:
            if status_reply_dict[chat_id] and msg != status_reply_dict[chat_id][0].text:
                if buttons == "":
                    rmsg = editMessage(msg, status_reply_dict[chat_id][0])
                else:
                    rmsg = editMessage(msg, status_reply_dict[chat_id][0], buttons)
                if rmsg == "Message to edit not found":
                    del status_reply_dict[chat_id]
                    return
                status_reply_dict[chat_id][0].text = msg
                status_reply_dict[chat_id][1] = time()

def sendStatusMessage(msg, bot):
    progress, buttons = get_readable_message()
    if progress is None:
        return
    with status_reply_dict_lock:
        if msg.chat.id in status_reply_dict:
            message = status_reply_dict[msg.chat.id][0]
            deleteMessage(bot, message)
            del status_reply_dict[msg.chat.id]
        if buttons == "":
            message = sendMessage(progress, bot, msg)
        else:
            message = sendMarkup(progress, bot, msg, buttons)
        status_reply_dict[msg.chat.id] = [message, time()]
        if not Interval:
            Interval.append(setInterval(DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages))

def sendSearchMessage(message,bot,search_list:list,f_name:str):
    LOGGER.info(f'{search_list}')
    msg = f"Here are the search results for {f_name}:"
    fmsg = ''
    if len(search_list) <10:
        for index,dictionary in enumerate(search_list, start=1):
            index_link = dictionary.get('Index Link',False)
            Drive_link = dictionary.get('Drive Link')
            View_link = dictionary.get('View Link',False)
            Name = dictionary.get('Name')
            fmsg += f"\n\n{index}:{Name}\n<a href='{Drive_link}'>Drive Link</a>"
            if index_link:
                fmsg += f"|<a href='{index_link.replace(INDEX_URL,'https://dl1.mxfile-irani.ga/0:')}'>Link Nimbaha</a>"
                fmsg += f"|<a href='{index_link}'>Index Link</a>"
            if View_link:
                fmsg += f"|<a href='{View_link}'>View Link</a>"
            if len(fmsg.encode() + msg.encode()) > 4000:
                sendMessage(msg + fmsg, bot, message)
                sleep(1)
                fmsg = ''
        if fmsg != '':
            sendMessage(msg + fmsg, bot, message)
    else:
        fileeee_nameeee = f'{f_name}_{time()}.txt'
        with open(fileeee_nameeee,'a') as file:
            for index,dictionary in enumerate(search_list, start=1):
                index_link = dictionary.get('Index Link',False)
                Drive_link = dictionary.get('Drive Link')
                View_link = dictionary.get('View Link',False)
                Name = dictionary.get('Name')
                fmsg += f"\n\n{index}:{Name}\n<a href='{Drive_link}'>Drive Link</a>"
                if index_link:
                    fmsg += f"|<a href='{index_link.replace(INDEX_URL,'https://dl1.mxfile-irani.ga/0:')}'>Link Nimbaha</a>"
                    fmsg += f"|<a href='{index_link}'>Index Link</a>"
                if View_link:
                    fmsg += f"|<a href='{View_link}'>View Link</a>"
            file.write(fmsg)
            file.close()
        sendFile(bot,message,fileeee_nameeee,f"Here are the search results for {f_name}:")
