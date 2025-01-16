from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from inline_kbs.kb_commands import COMMAND_CANCEL


def build_choice_ip_kb(ips_and_ports: list) -> InlineKeyboardMarkup:
    kb = []
    for ipp in ips_and_ports:
        kb.append([InlineKeyboardButton(
            text=ipp,
            callback_data=ipp
        )])
    kb.append([InlineKeyboardButton(
        text=COMMAND_CANCEL.label,
        callback_data=COMMAND_CANCEL.data
    )])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def build_choice_command_kb(commands=None) -> InlineKeyboardMarkup:
    if commands is None:
        commands = []

    kb = []
    for command in commands:
        kb.append([InlineKeyboardButton(
            text=command.label,
            callback_data=command.data
        )])
    kb.append([InlineKeyboardButton(
        text=COMMAND_CANCEL.label,
        callback_data=COMMAND_CANCEL.data
    )])
    return InlineKeyboardMarkup(inline_keyboard=kb)
