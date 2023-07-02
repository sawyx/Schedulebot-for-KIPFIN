from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import schedule1022
import json

with open('group.json', 'r') as f:
  list_if_group = json.load(f)


def kb_key_group(theme='none'):
  buttons = [
    InlineKeyboardButton(text=key, callback_data=f'key:{key}:{theme}')
    for key in list_if_group.keys()
  ]
  keyboard = InlineKeyboardMarkup(row_width=4)
  keyboard.add(*buttons)
  return keyboard


def kb_value_group(key, theme='none'):
  values = list_if_group[key]
  buttons = [
    InlineKeyboardButton(text=value, callback_data=f'group:{value}:{theme}')
    for value in values
  ]
  keyboard = InlineKeyboardMarkup(row_width=3)
  keyboard.add(*buttons)
  return keyboard

def kb_teacher(key, _list=None):
  if not _list:
    _list = schedule1022.get_list_of_teacher()
  buttons = [
    InlineKeyboardButton(text=k, callback_data=f't:{key}:' + i) for k, i in _list
  ]
  keyboard = InlineKeyboardMarkup(row_width=1)
  keyboard.add(*buttons)
  return keyboard

def kb_start():
  keyboard = InlineKeyboardMarkup(row_width=1)
  keyboard.add(InlineKeyboardButton(text='Расписание', callback_data='back_key'))
  keyboard.add(InlineKeyboardButton(text='Расписание преподавателя', callback_data='tback_key'))
  keyboard.add(InlineKeyboardButton(text='Авто расписание', callback_data='back_sub_key'))
  keyboard.add(InlineKeyboardButton(text='Авто расписание преподавателя', callback_data='back_tsub_key'))
  return keyboard

def kb_help():
  keyboard = InlineKeyboardMarkup(row_width=1)
  keyboard.add(
    InlineKeyboardButton(text='Команды', callback_data='help'))
  return keyboard
