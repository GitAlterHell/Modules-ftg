# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#

from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types.messages import ChatFull
from telethon.tl.types import Channel, User, ChatInviteExported

from userbot import CMD_HELP
from userbot.events import register

from re import findall, match
from typing import List
from typing import Union

from telethon.events import NewMessage
from telethon.tl.custom import Message
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    MessageEntityMentionName,
    ChannelParticipantsAdmins,
    ChannelParticipantsBots,
    MessageEntityMention,
    InputPeerChannel,
    InputPeerChat)


def parse_arguments(message: str, valid: List[str]) -> (dict, str):
    options = {}

    # Handle boolean values
    for opt in findall(r'([.!]\S+)', message):
        if opt[1:] in valid:
            if opt[0] == '.':
                options[opt[1:]] = True
            elif opt[0] == '!':
                options[opt[1:]] = False
            message = message.replace(opt, '')

    # Handle key/value pairs
    for opt in findall(r'(\S+):(?:"([\S\s]+)"|(\S+))', message):
        key, val1, val2 = opt
        value = val2 or val1[1:-1]
        if key in valid:
            if value.isnumeric():
                value = int(value)
            elif match(r'[Tt]rue|[Ff]alse', value):
                match(r'[Tt]rue', value)
            options[key] = value
            message = message.replace(f"{key}:{value}", '')

    return options, message.strip()


def freeze(d):
    if isinstance(d, dict):
        return frozenset((key, freeze(value)) for key, value in d.items())
    elif isinstance(d, list):
        return tuple(freeze(value) for value in d)
    return d


def extract_urls(message):
    matches = findall(r'(https?://\S+)', str(message))
    return list(matches)


async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None

    return user_obj


async def get_user_from_event(event: NewMessage.Event, **kwargs):
    """ Get the user from argument or replied message. """
    reply_msg: Message = await event.get_reply_message()
    user = kwargs.get('user', None)

    if user:
        # First check for a user id
        if user.isnumeric():
            user = int(user)

        # Then check for a user mention (@username)
        elif event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user

        try:
            user_object = await event.client.get_entity(user)
            replied_user = await event.client(
                GetFullUserRequest(user_object.id))
        except (TypeError, ValueError) as err:
            return None

    # Check for a forwarded message
    elif (reply_msg and
          reply_msg.forward and
          reply_msg.forward.sender_id and
          kwargs['forward']):
        forward = reply_msg.forward
        replied_user = await event.client(GetFullUserRequest(forward.sender_id))

    # Check for a replied to message
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        replied_user = await event.client(GetFullUserRequest(previous_message.from_id))

    # Last case scenario is to get the current user
    else:
        self_user = await event.client.get_me()
        replied_user = await event.client(GetFullUserRequest(self_user.id))

    return replied_user


async def get_chat_from_event(event: NewMessage.Event, **kwargs):
    reply_msg: Message = await event.get_reply_message()
    chat = kwargs.get('chat', None)

    if chat:
        try:
            input_entity = await event.client.get_input_entity(chat)
            if isinstance(input_entity, InputPeerChannel):
                return await event.client(GetFullChannelRequest(input_entity.channel_id))
            elif isinstance(input_entity, InputPeerChat):
                return await event.client(GetFullChatRequest(input_entity.chat_id))
            else:
                return None
        except(TypeError, ValueError):
            return None
    # elif reply_msg and reply_msg.forward:
    #     return None
    else:
        chat = await event.get_chat()
        return await event.client(GetFullChannelRequest(chat.id))


async def list_admins(event):
    adms = await event.client.get_participants(event.chat, filter=ChannelParticipantsAdmins)
    adms = map(lambda x: x if not x.bot else None, adms)
    adms = [i for i in list(adms) if i]
    return adms


async def list_bots(event):
    bots = await event.client.get_participants(event.chat, filter=ChannelParticipantsBots)
    return bots


def make_mention(user):
    if user.username:
        return f"@{user.username}"
    else:
        return inline_mention(user)


def inline_mention(user):
    full_name = user_full_name(user) or "No Name"
    return f"[{full_name}](tg://user?id={user.id})"


def user_full_name(user):
    names = [user.first_name, user.last_name]
    names = [i for i in list(names) if i]
    full_name = ' '.join(names)
    return full_name


class FormattedBase:
    text: str

    def __add__(self, other: Union[str, 'FormattedBase']) -> str:
        return str(self) + str(other)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.text})'

    def __str__(self) -> str:
        return self.text


class String(FormattedBase):

    def __init__(self, text: Union[str, int]) -> None:
        self.text = str(text)


class Bold(FormattedBase):

    def __init__(self, text: Union[str, int]) -> None:
        self.text = f'**{text}**'


class Italic(FormattedBase):

    def __init__(self, text: Union[str, int]) -> None:
        self.text = f'__{text}__'


class Code(FormattedBase):

    def __init__(self, text: Union[str, int]) -> None:
        self.text = f'`{text}`'


class Pre(FormattedBase):

    def __init__(self, text: Union[str, int]) -> None:
        self.text = f'```{text}```'


class Link(FormattedBase):

    def __init__(self, label: String, url: str) -> None:
        self.text = f'[{label}]({url})'


class Mention(Link):

    def __init__(self, label: String, uid: int):
        super().__init__(label, f'tg://user?id={uid}')


class KeyValueItem(FormattedBase):

    def __init__(self, key: Union[str, FormattedBase],
                 value: Union[str, FormattedBase]) -> None:
        self.key = key
        self.value = value
        self.text = f'{key}: {value}'


class Item(FormattedBase):

    def __init__(self, text: Union[str, int]) -> None:
        self.text = str(text)


class Section:

    def __init__(self,
                 *args: Union[String,
                              'FormattedBase'],
                 spacing: int = 1,
                 indent: int = 4) -> None:
        self.header = args[0]
        self.items = list(args[1:])
        self.indent = indent
        self.spacing = spacing

    def __add__(self, other: Union[String, 'FormattedBase']) -> str:
        return str(self) + '\n\n' + str(other)

    def __str__(self) -> str:
        return ('\n' *
                self.spacing).join([str(self.header)] +
                                   [' ' *
                                    self.indent +
                                    str(item) for item in self.items if item is not None])


class SubSection(Section):

    def __init__(self,
                 *args: Union[String,
                              'SubSubSection'],
                 indent: int = 8) -> None:
        super().__init__(*args, indent=indent)


class SubSubSection(SubSection):

    def __init__(self, *args: String, indent: int = 12) -> None:
        super().__init__(*args, indent=indent)


class TGDoc:

    def __init__(self, *args: Union[String, 'Section']) -> None:
        self.sections = args

    def __str__(self) -> str:
        return '\n\n'.join([str(section) for section in self.sections])


@register(outgoing=True, pattern=r"^\.c(?:hat)?(\s+[\S\s]+|$)")
async def chat_info(e):
    params = e.pattern_match.group(1) or ""
    args, chat = parse_arguments(
        params, ['id', 'general', 'admins', 'bots', 'all'])
    args['chat'] = chat

    if isinstance(e.chat, User):
        from .user_info import fetch_info as fetch_user_info
        replied_user = await e.client(GetFullUserRequest(e.chat.id))
        response = await fetch_user_info(replied_user, **args)
    else:
        full_chat: ChatFull = await get_chat_from_event(e, **args)

        await e.edit("**Fetching chat info...**")
        response = await fetch_info(e, full_chat, **args)

    await e.edit(str(response))


async def fetch_info(event, full_chat, **kwargs):
    chat = full_chat.chats[0]

    show_all = kwargs.get('all', False)
    id_only = kwargs.get('id', False)
    show_general = kwargs.get('general', True)
    show_admins = kwargs.get('admins', False)
    show_bots = kwargs.get('bots', False)

    is_private = False
    if isinstance(chat, Channel) and chat.username:
        name = chat.title if chat.title else chat.username
        title = Link(name, f"https://t.me/{chat.username}")
    elif chat.title:
        is_private = True
        title = Bold(chat.title)
    else:
        is_private = True
        title = Bold(f"Chat {chat.id}")

    if show_all:
        show_general = True
        show_admins = True
        show_bots = True
    elif id_only:
        return KeyValueItem(title, Code(str(chat.id)))

    admin_list = await list_admins(event)

    if show_general:
        exported_invite = full_chat.full_chat.exported_invite
        invite_link = exported_invite.link if isinstance(
            exported_invite, ChatInviteExported) else None
        admin_count = full_chat.full_chat.admins_count or len(admin_list)

        general = SubSection(Bold("general"),
                             KeyValueItem("id",
                                          Code(str(chat.id))),
                             KeyValueItem("title",
                                          Code(chat.title)),
                             KeyValueItem("private",
                                          Code(str(is_private))),
                             KeyValueItem("invite link",
                                          Link(invite_link.split('/')[-1],
                                               invite_link)) if invite_link else None,
                             SubSubSection("participants",
                                           KeyValueItem("admins",
                                                        Code(str(admin_count))),
                                           KeyValueItem("online",
                                                        Code(str(full_chat.full_chat.online_count))),
                                           KeyValueItem("total",
                                                        Code(str(full_chat.full_chat.participants_count)))))
    else:
        general = None

    if show_admins:
        admins = SubSection(Bold("admins"))
        for admin in admin_list:
            admins.items.append(String(inline_mention(admin)))
        if not admins:
            admins.items.append(String("No admins"))

    if show_bots:
        bots_list = await list_bots(event)
        bots = SubSection(Bold("bots"))
        for bot in bots_list:
            bots.items.append(String(inline_mention(bot)))
        if not bots:
            bots.items.append(String("No bots"))

    return TGDoc(Section(title,
                         general if show_general else None,
                         admins if show_admins else None,
                         bots if show_bots else None))


CMD_HELP.update({
    "chatinfo":
    "Returns stats for the current chat"
    "\n.chat [options]"
    "\n\n.id: Return only the id."
    "\n.general: Show general information related to the chat."
    "\n.admins: Show chat admins (does not mention them)."
    "\n.all: Show everything."
})
