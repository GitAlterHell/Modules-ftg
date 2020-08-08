import time
from .. import loader, utils

import logging


from telethon import types

logger = logging.getLogger(__name__)

@loader.tds
class AFKMod(loader.Module):
    """Посылает нахуй при вашем теге"""
    strings = {"name": "RFD",
               "gone": "Режим авто-пидара включе́н",
               "back": "Режим авто-пидара выключен",
               "afk": "<b>Меня нет на месте...</b>",
               "afk_reason": "{}"}

    async def client_ready(self, client, db):
        self._db = db
        self._me = await client.get_me()

    async def rfdcmd(self, message):
        """.rfd [текст]"""
        if utils.get_args_raw(message):
            self._db.set(__name__, "afk", utils.get_args_raw(message))
        else:
            self._db.set(__name__, "afk", True)
        self._db.set(__name__, "gone", time.time())
        await self.allmodules.log("afk", data=utils.get_args_raw(message) or None)
        await utils.answer(message, self.strings("gone", message))

    async def unrfdcmd(self, message):
        """Перестаёт писать"""
        self._db.set(__name__, "afk", False)
        self._db.set(__name__, "gone", None)
        await self.allmodules.log("unafk")
        await utils.answer(message, self.strings("back", message))

    async def watcher(self, message):
        if not isinstance(message, types.Message):
            return
        if message.mentioned or getattr(message.to_id, "user_id", None) == self._me.id:
            if self.get_afk() != False:
                afk_state = self.get_afk()
                ret = self.strings("afk_reason", message).format(afk_state)
                await utils.answer(message, ret)
            else:
                return

    def get_afk(self):
        return self._db.get(__name__, "afk", False)
