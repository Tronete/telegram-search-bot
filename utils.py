import re
from threading import Thread
import functools
import time
import json
import os

CONFIG_FILE = './config/.config.json'

USERBOT_CHAT_MEMBERS_FILE = '.userbot_chat_members'
USERBOT_ADMIN_FILE = '.userbot_admin'



def delay_delete(bot, chat_id, message_id):
    time.sleep(60)
    bot.delete_message(chat_id=chat_id, message_id=message_id)


def auto_delete(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kw):
        bot = args[1].bot
        sent_message = fn(*args, **kw)
        if sent_message:
            Thread(target=delay_delete, args=[bot, sent_message.chat_id, sent_message.message_id]).start()
        return sent_message

    return wrapper


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


# calculate num of non-ascii characters
def len_non_ascii(data):
    temp = re.findall('[^a-zA-Z0-9.]+', data)
    count = 0
    for i in temp:
        count += len(i)
    return count


def get_bot_user_name(bot):
    return bot.get_me().username


def get_bot_id(bot):
    return bot.get_me().id


def read_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    f = open(CONFIG_FILE)
    config_dict = json.load(f)
    f.close()
    return config_dict


def check_control_permission(from_user_id):
    try:
        config = read_config()
        if config['enable']:
            if from_user_id in config['group_admins']:
                return True
            else:
                return False
        else:
            return None
    except:
        return None


def load_chat_members():
    if not os.path.exists(USERBOT_CHAT_MEMBERS_FILE):
        with open(USERBOT_CHAT_MEMBERS_FILE, 'w') as f:
            json.dump({}, f)

    with open(USERBOT_CHAT_MEMBERS_FILE, 'r') as f:
        chat_members = json.load(f)
    return chat_members


def write_chat_members(chat_members):
    with open(USERBOT_CHAT_MEMBERS_FILE, 'w') as f:
        json.dump(chat_members, f)


def get_filter_chats(user_id):
    filter_chats = []
    chat_members = load_chat_members()
    for chat_id in chat_members:
        if user_id in chat_members[chat_id]['members']:
            filter_chats.append((int(chat_id),chat_members[chat_id]['title']))
    return filter_chats


def is_userbot_mode():
    return os.getenv("USER_BOT")=="1"


def update_userbot_admin_id(user_id):
    current_id = -1
    if os.path.exists(USERBOT_ADMIN_FILE):
        with open(USERBOT_ADMIN_FILE) as f:
            current_id = int(f.read().strip())

    if current_id != user_id:
        with open(USERBOT_ADMIN_FILE, 'w') as f:
            f.write(str(user_id))


def read_userbot_admin_id():
    with open(USERBOT_ADMIN_FILE) as f:
        current_id = int(f.read().strip())
    return current_id