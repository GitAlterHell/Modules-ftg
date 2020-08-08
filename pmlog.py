#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import logging

from telethon import types

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class PMLogMod(loader.Module):
    """Logs unwanted PMs to a channel"""
    strings = {"name": "PM Logger",
               "start": "<b>Ваш разговор в настроящее время логируется</b>",
               "not_pm": "<b>Вы не можете логировать группу</b>",
               "stopped": "<b>Логирование разговора завершено</b>",
               "log_group_cfg_doc": "Идентификатор группы или канала, куда отправлять логи разговора"}

    def __init__(self):
        self.config = loader.ModuleConfig("LOG_GROUP", None, lambda m: self.strings("log_group_cfg_doc", m))

    async def logpmcmd(self, message):
        """Begins logging PMs"""
        if not message.is_private or message.to_id.user_id == (await message.client.get_me(True)).user_id:
            await utils.answer(message, self.strings("not_pm", message))
            return
        self._db.set(__name__, "users", list(set(self._db.get(__name__, "users", []) + [message.to_id.user_id])))
        msgs = await utils.answer(message, self.strings("start", message))
        await asyncio.sleep(1)
        await message.client.delete_messages(message.to_id, msgs)

    async def unlogpmcmd(self, message):
        """Stops logging PMs"""
        if not message.is_private or message.to_id.user_id == (await message.client.get_me(True)).user_id:
            await utils.answer(message, self.strings("not_pm", message))
            return
        self._db.set(__name__, "users",
                     list(set(self._db.get(__name__, "users", [])).difference([message.to_id.user_id])))
        await utils.answer(message, self.strings("stopped", message))

    async def watcher(self, message):
        if not message.is_private or not isinstance(message, types.Message):
            return
        if self.config["LOG_GROUP"] and utils.get_chat_id(message) in self._db.get(__name__, "users", []):
            await message.forward_to(self.config["LOG_GROUP"])

    async def client_ready(self, client, db):
        self._db = db
