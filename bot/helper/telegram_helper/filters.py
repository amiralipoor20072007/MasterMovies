from telegram.ext import MessageFilter
from telegram import Message
from bot import AUTHORIZED_CHATS, SUDO_USERS, OWNER_ID,app


class CustomFilters:
    class __OwnerFilter(MessageFilter):
        def filter(self, message: Message):
            return message.from_user.id == OWNER_ID

    owner_filter = __OwnerFilter()

    class __AuthorizedUserFilter(MessageFilter):
        def filter(self, message: Message):
            id = message.from_user.id
            return id in AUTHORIZED_CHATS or id in SUDO_USERS or id == OWNER_ID

    authorized_user = __AuthorizedUserFilter()

    class __AuthorizedChat(MessageFilter):
        def filter(self, message: Message):
            return message.chat.id in AUTHORIZED_CHATS

    authorized_chat = __AuthorizedChat()

    class __MemberInGroup(MessageFilter):
        def filter(self, message: Message):
            id = message.from_user.id
            Flag = False
            for Memberin in app.get_chat_members('@MX_TR_Official'):
                if id == Memberin.user.id:
                    Flag = True
            if Flag == True:
                for AuthorizedChat in AUTHORIZED_CHATS:
                    for Memberin in app.get_chat_members(AuthorizedChat):
                        if id == Memberin.user.id:
                            return True
            return False
    
    mebmer_in_group = __MemberInGroup()

    class __SudoUser(MessageFilter):
        def filter(self, message: Message):
            return message.from_user.id in SUDO_USERS

    sudo_user = __SudoUser()

    @staticmethod
    def _owner_query(user_id):
        return user_id == OWNER_ID or user_id in SUDO_USERS

