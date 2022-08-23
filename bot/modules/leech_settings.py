from os import remove as osremove, path as ospath, mkdir
from threading import Thread
from PIL import Image
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup

from bot import AS_DOC_USERS, AS_MEDIA_USERS, AUTODELETE_USERS, HASH_USERS, HOW2SEND_COMPLETE_MESSAGE, MULTI_DRIVE_XI,RANDOMNAME_USERS, dispatcher, AS_DOCUMENT, AUTO_DELETE_MESSAGE_DURATION, DB_URI
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, auto_delete_message
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper import button_build
from bot.helper.ext_utils.db_handler import DbManger


def getleechinfo(from_user):
    user_id = from_user.id
    name = from_user.full_name
    buttons = button_build.ButtonMaker()
    thumbpath = f"Thumbnails/{user_id}.jpg"
    if (
        user_id in AS_DOC_USERS
        or user_id not in AS_MEDIA_USERS
        and AS_DOCUMENT
    ):
        ltype = "DOCUMENT"
        buttons.sbutton("Send As Media", f"leechset {user_id} med")
    else:
        ltype = "MEDIA"
        buttons.sbutton("Send As Document", f"leechset {user_id} doc")
    
    if user_id in RANDOMNAME_USERS:
        Random = 'Active 🟢'
        buttons.sbutton('Random Name Deactive 🔴', f"leechset {user_id} rnd")
    else:
        Random = 'Deactive 🔴'
        buttons.sbutton('Random Name Active 🟢', f"leechset {user_id} rna")
    
    if user_id in AUTODELETE_USERS:
        Autodelete = 'Active 🟢'
        buttons.sbutton('Auto Delete Deactive 🔴', f"leechset {user_id} add")
    else:
        Autodelete = 'Deactive 🔴'
        buttons.sbutton('Auto Delete Active 🟢', f"leechset {user_id} ada")
    
    if user_id in HASH_USERS:
        Hash = 'Active 🟢'
        buttons.sbutton('Hash Deactive 🔴', f"leechset {user_id} hd")
    else:
        Hash = 'Deactive 🔴'
        buttons.sbutton('Hash Active 🟢', f"leechset {user_id} ha")
    
    How2Send = HOW2SEND_COMPLETE_MESSAGE.get(user_id,1)

    if How2Send == 1:
        How2Send = 'HyperLink'
        buttons.sbutton('Set How2Send -> Code(قابل کپی)', f"leechset {user_id} h2s 2")
    elif How2Send == 2:
        How2Send = 'Code(قابل کپی)'
        buttons.sbutton('Set How2Send -> Both(HyperLink+Code)', f"leechset {user_id} h2s 3")
    else:
        How2Send = 'Both(HyperLink+Code)'
        buttons.sbutton('Set How2Send -> HyperLink', f"leechset {user_id} h2s 1")
    
    if user_id in MULTI_DRIVE_XI:
        Multi_DRIVE = 'MultiDrive Upload 🟢'
        buttons.sbutton('MultiDrive Deactive 🔴', f"leechset {user_id} mdxd")
    else:
        Multi_DRIVE = 'MultiDrive Upload 🔴'
        buttons.sbutton('MultiDrive Active 🟢', f"leechset {user_id} mdxa")

    if ospath.exists(thumbpath):
        thumbmsg = "Exists"
        buttons.sbutton("Delete Thumbnail", f"leechset {user_id} thumb")
    else:
        thumbmsg = "Not Exists"
    
    if AUTO_DELETE_MESSAGE_DURATION == -1:
        buttons.sbutton("Close", f"leechset {user_id} close")

    button = InlineKeyboardMarkup(buttons.build_menu(1))

    text = f"<u>Leech Settings for <a href='tg://user?id={user_id}'>{name}</a></u>\n"\
           f"Leech Type <b>{ltype}</b>\n"\
           f"<b>Random Name: </b>{Random}\n"\
           f"<b>Auto Delete: </b>{Autodelete}\n"\
           f"<b>Send Hash File: </b>{Hash}\n"\
           f"<b>How2Send(CompleteMessage): </b>{How2Send}\n"\
           f"<b>MultiDrive Uploading: </b>{Multi_DRIVE}\n"\
           f"Custom Thumbnail <b>{thumbmsg}</b>"
    return text, button

def editLeechType(message, query):
    msg, button = getleechinfo(query.from_user)
    editMessage(msg, message, button)

def leechSet(update, context):
    msg, button = getleechinfo(update.message.from_user)
    choose_msg = sendMarkup(msg, context.bot, update.message, button)
    Thread(target=auto_delete_message, args=(context.bot, update.message, choose_msg)).start()

def setLeechType(update, context):
    query = update.callback_query
    message = query.message
    user_id = query.from_user.id
    data = query.data
    data = data.split()
    if user_id != int(data[1]):
        query.answer(text="Not Yours!", show_alert=True)
    elif data[2] == "doc":
        if user_id in AS_MEDIA_USERS:
            AS_MEDIA_USERS.remove(user_id)
        AS_DOC_USERS.add(user_id)
        if DB_URI is not None:
            DbManger().user_doc(user_id)
        query.answer(text="Your File Will Deliver As Document!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "med":
        if user_id in AS_DOC_USERS:
            AS_DOC_USERS.remove(user_id)
        AS_MEDIA_USERS.add(user_id)
        if DB_URI is not None:
            DbManger().user_media(user_id)
        query.answer(text="Your File Will Deliver As Media!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "thumb":
        path = f"Thumbnails/{user_id}.jpg"
        if ospath.lexists(path):
            osremove(path)
            if DB_URI is not None:
                DbManger().user_rm_thumb(user_id, path)
            query.answer(text="Thumbnail Removed!", show_alert=True)
            editLeechType(message, query)
        else:
            query.answer(text="Old Settings", show_alert=True)
    elif data[2] == "rna":
        RANDOMNAME_USERS.add(user_id)
        if DB_URI is not None:
            DbManger().user_active_random(user_id)
        query.answer(text="Random Name Acticated!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "rnd":
        RANDOMNAME_USERS.remove(user_id)
        if DB_URI is not None:
            DbManger().user_deactive_random(user_id)
        query.answer(text="Random Name Deactivated!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "ada":
        AUTODELETE_USERS.add(user_id)
        if DB_URI is not None:
            DbManger().user_active_delete(user_id)
        query.answer(text="Auto Delete Acticated!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "add":
        AUTODELETE_USERS.remove(user_id)
        if DB_URI is not None:
            DbManger().user_deactive_delete(user_id)
        query.answer(text="Auto Delete Deactivated!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "ha":
        HASH_USERS.add(user_id)
        if DB_URI is not None:
            DbManger().user_hash(user_id)
        query.answer(text="Hash Acticated!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "hd":
        HASH_USERS.remove(user_id)
        if DB_URI is not None:
            DbManger().user_unhash(user_id)
        query.answer(text="Hash Deactivated!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "h2s":
        how2send = int(data[3])
        HOW2SEND_COMPLETE_MESSAGE[user_id] = how2send
        if DB_URI is not None:
            DbManger().set_how2send(user_id,how2send)
        query.answer(text=f"Set To {how2send}!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == 'mdxa':
        MULTI_DRIVE_XI.add(user_id)
        if DB_URI is not None:
            DbManger().user_multidrive(user_id)
        query.answer(text="MultiDrive Activated!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == 'mdxd':
        MULTI_DRIVE_XI.remove(user_id)
        if DB_URI is not None:
            DbManger().user_unmultidrive(user_id)
        query.answer(text="MultiDrive Deactivated!", show_alert=True)
        editLeechType(message, query)
    else:
        query.answer()
        try:
            query.message.delete()
            query.message.reply_to_message.delete()
        except:
            pass

def setThumb(update, context):
    user_id = update.message.from_user.id
    reply_to = update.message.reply_to_message
    if reply_to is not None and reply_to.photo:
        path = "Thumbnails/"
        if not ospath.isdir(path):
            mkdir(path)
        photo_dir = reply_to.photo[-1].get_file().download()
        des_dir = ospath.join(path, str(user_id) + ".jpg")
        Image.open(photo_dir).convert("RGB").save(des_dir, "JPEG")
        osremove(photo_dir)
        if DB_URI is not None:
            DbManger().user_save_thumb(user_id, des_dir)
        msg = f"Custom thumbnail saved for {update.message.from_user.mention_html(update.message.from_user.first_name)}."
        sendMessage(msg, context.bot, update.message)
    else:
        sendMessage("Reply to a photo to save custom thumbnail.", context.bot, update.message)

leech_set_handler = CommandHandler(BotCommands.LeechSetCommand, leechSet,  run_async=True)
set_thumbnail_handler = CommandHandler(BotCommands.SetThumbCommand, setThumb,  run_async=True)
but_set_handler = CallbackQueryHandler(setLeechType, pattern="leechset", run_async=True)

dispatcher.add_handler(leech_set_handler)
dispatcher.add_handler(but_set_handler)
dispatcher.add_handler(set_thumbnail_handler)

