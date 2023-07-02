from background import keep_alive
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor, exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import aioschedule
import re
import configparser
import os
import json
import datetime
from keyboards import kb_help, kb_start, kb_teacher, kb_value_group, kb_key_group

from other import save_json
import schedule1022
import db
from throttling import ThrottlingMiddleware

read_config = configparser.ConfigParser()
read_config.read("settings.ini")
group = read_config['settings']['default_group']
adm_id = read_config['settings']['admin_id']
token = os.getenv('KEYBOT')

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
  if not db.exists_user(message.from_user.id):
    db.add_user(message.from_user.id, message.from_user.username)
    await bot.send_message(
      adm_id,
      f'В бд добавлен новый пользователь - @{message.from_user.username}')
  await message.answer('Привет! Все комманды - /help', reply_markup=kb_help())


@dp.message_handler(commands='search')
async def cmd_search(message: types.Message):
  if message.get_args():
    if re.fullmatch(r'\w{4,6}-\d{3,4}', message.get_args()):
      await bot.send_message(message.chat.id,
                             text=schedule1022.get_schedule(
                               message.get_args()),
                             parse_mode='Markdown')
    else:
      await bot.send_message(message.chat.id,
                             text=r"*Ошибка.* Пример: `/search 1ОИБАС-1022`",
                             parse_mode='Markdown')
  else:
    await bot.send_message(message.chat.id,
                           text=schedule1022.get_schedule(group),
                           parse_mode='Markdown')


@dp.message_handler(commands='help')
@dp.callback_query_handler(text="help")
async def cmd_help(message: types.Message):
  text = '/schedule - Получить расписание\n\
/teacher - Получить расписание для преподавателя\n\
/auto_schedule - Автоматическая рассылка расписания\n\
/auto_teacher - Автоматическая рассылка расписания для преподавателя\n\
/search [группа] - Поиск расписания по группе'
  if isinstance(message, types.CallbackQuery):
    await message.message.edit_text(text, reply_markup=kb_start())
  else:
    await message.answer(text, reply_markup=kb_start())


@dp.message_handler(commands='schedule')
@dp.callback_query_handler(text="back_key")
async def cmd_schedule(message):
  keyboard = kb_key_group()
  if isinstance(message, types.CallbackQuery):
    await message.message.edit_text(text='Выберите курс:',
                                    reply_markup=keyboard)
  else:
    await message.answer('Выберите курс:', reply_markup=keyboard)


@dp.message_handler(commands='auto_teacher')
@dp.callback_query_handler(text="back_tsub_key")
async def cmd_subschedule(message):
  _list = schedule1022.get_list_of_teacher()[:10]
  keyboard = kb_teacher('ts', _list)  # другая
  keyboard.row(InlineKeyboardButton("Вперед >>>", callback_data="next:1:ts"))
  
  subtext = ''
  if isinstance(message, types.CallbackQuery):
    if db.exists_tsub(message.message.chat.id):
      keyboard.row(InlineKeyboardButton(text='Отменить рассылку', callback_data='cancel_teacher_key'))
      teacher = db.db['tsub'][str(message.message.chat.id)]
      subtext = f'Вы подписаны на автоматическую рассылку расписания преподавателя {teacher}\n'
    else:
      subtext = 'Вы не подписаны на автоматическую рассылку расписания преподавателя.\n'
    await message.message.edit_text(text=subtext +
                                    'Выберите преподавателя для рассылки:',
                                    reply_markup=keyboard)
  else:
    if db.exists_tsub(message.chat.id):
      keyboard.row(InlineKeyboardButton(text='Отменить рассылку', callback_data='cancel_teacher_key'))
      teacher = db.db['tsub'][str(message.chat.id)]
      subtext = f'Вы подписаны на автоматическую рассылку расписания преподавателя {teacher}.\n'
    else:
      subtext = 'Вы не подписаны на автоматическую рассылку преподавателя.\n'
    await message.answer(subtext + 'Выберите преподавателя для рассылки:',
                         reply_markup=keyboard)


@dp.message_handler(commands='auto_schedule')
@dp.callback_query_handler(text="back_sub_key")
async def cmd_sub_schedule(message):
  keyboard = kb_key_group('sub')
  cancel_key = InlineKeyboardButton(text='Отменить рассылку',
                                    callback_data='cancel_key')
  keyboard.row(cancel_key)
  subtext = ''
  if isinstance(message, types.CallbackQuery):
    if db.exists_sub(message.message.chat.id):
      group = db.db['sub'][str(message.message.chat.id)]
      subtext = f'Вы подписаны на автоматическую рассылку расписания на группу {group}.\n'
    else:
      subtext = 'Вы не подписаны на автоматическую рассылку расписания.\n'
    await message.message.edit_text(text=subtext +
                                    'Выберите курс для рассылки:',
                                    reply_markup=keyboard)
  else:
    if db.exists_sub(message.chat.id):
      group = db.db['sub'][str(message.chat.id)]
      subtext = f'Вы подписаны на автоматическую рассылку расписания на группу {group}.\n'
    else:
      subtext = 'Вы не подписаны на автоматическую рассылку расписания.\n'
    await message.answer(subtext + 'Выберите курс для рассылки:',
                         reply_markup=keyboard)


@dp.callback_query_handler(text_startswith="t:")
async def handle_teacher_callback(query: CallbackQuery):
  key = query.data.split(':')
  back_key = InlineKeyboardButton(text='Назад', callback_data='tback_key')
  keyboard = InlineKeyboardMarkup().add(back_key)
  name = schedule1022.get_teacher(key[2])
  if key[1] == 'ts':
    db.set_tsub(query.message.chat.id, name)
    await query.message.edit_text(
      text=
      f'Вы подписались на автоматическую рассылку расписания преподавателя {name}',
      reply_markup=None)
    return
    
  await query.message.edit_text(
    text=schedule1022.get_schedule_for_teacher(name),
    reply_markup=keyboard,
    parse_mode='Markdown')


@dp.message_handler(commands='dl_a')
async def cmd_dla(message):
  if message.from_user.id == int(adm_id):
    schedule1022.download_pdf()
    await bot.send_message(adm_id, text="downloaded and convert")


### TEACHER ###
@dp.callback_query_handler(text_startswith="prev")
async def prev_page(call: types.CallbackQuery):
  await call.answer()
  data = int(call.data.split(":")[1]) - 1
  theme = call.data.split(":")[2]
  _list = schedule1022.get_list_of_teacher()[(data - 1) * 10:data * 10]
  markup = kb_teacher(theme, _list)
  if data > 1:
    markup.row(
      InlineKeyboardButton("<<< Назад", callback_data=f"prev:{data}:{theme}"),
      InlineKeyboardButton("Вперед >>>", callback_data=f"next:{data}:{theme}"))
  else:
    markup.row(InlineKeyboardButton("Вперед >>>",
                                    callback_data=f"next:{data}:{theme}"))

  await call.message.edit_text('Выберите преподавателя:', reply_markup=markup)


@dp.callback_query_handler(text_startswith="next")
async def next_page(call: types.CallbackQuery):
  await call.answer()
  data = int(call.data.split(":")[1]) + 1
  _list = schedule1022.get_list_of_teacher()
  max = len(_list) // 10
  _list = _list[(data - 1) * 10:data * 10]
  theme = call.data.split(":")[2]
  markup = kb_teacher(theme, _list)
  if data <= max:
    markup.row(
      InlineKeyboardButton("<<< Назад", callback_data=f"prev:{data}:{theme}"),
      InlineKeyboardButton("Вперед >>>", callback_data=f"next:{data}:{theme}"))
  else:
    markup.row(InlineKeyboardButton("<<< Назад", callback_data=f"prev:{data}:{theme}"))

  await call.message.edit_text('Выберите преподавателя:', reply_markup=markup)


@dp.message_handler(commands='teacher')
@dp.callback_query_handler(text="tback_key")
async def teacher_handler(message: types.Message):
  if isinstance(message, types.CallbackQuery):
    func_message = message.message.edit_text
  else:
    func_message = message.answer
  _list = schedule1022.get_list_of_teacher()[:10]
  keyboard = kb_teacher('st', _list)
  keyboard.row(InlineKeyboardButton("Вперед >>>", callback_data="next:1:st"))
  await func_message('Выберите преподавателя:', reply_markup=keyboard)


### ADM ###
@dp.message_handler(commands='dl_g')
async def cmd_dlg(message):
  if message.from_user.id == int(adm_id):
    global list_if_group
    list_if_group = save_json()
    await bot.send_message(adm_id, text=list_if_group)


@dp.message_handler(commands='all_users')
async def cmd_allusers(message):
  if message.from_user.id == int(adm_id):
    users = ''
    for i in db.iter_users():
      uname = i[1]
      if uname is None:
        uname = "None"
      users += f'{i[0]} - @{uname}\n'
    await bot.send_message(adm_id, users)


@dp.message_handler(commands='all_chats')
async def cmd_allchats(message):
  if message.from_user.id == int(adm_id):
    chats = ''
    for i in db.iter_sub():
      chats += f'{i[0]} - {i[1]}\n'
    await bot.send_message(adm_id, chats)


@dp.message_handler(commands='all_teachers')
async def cmd_allteachers(message):
  if message.from_user.id == int(adm_id):
    teachers = ''
    for i in db.iter_tsub():
      teachers += f'{i[0]} - {i[1]}\n'
    await bot.send_message(adm_id, teachers)


@dp.message_handler(commands='sc')
async def cmd_sc(message):
  if message.from_user.id == int(adm_id):
    await send_chats()


### OTHER ###
@dp.errors_handler(exception=exceptions.RetryAfter)
async def exception_handler(update: types.Update,
                            exception: exceptions.RetryAfter):
  await bot.send_message(adm_id, ':<')


async def send_group():
  try:
    message = await bot.send_message(-1001740856947,
                                     text=schedule1022.get_schedule(group),
                                     parse_mode='Markdown')
    await bot.pin_chat_message(message.chat.id, message.message_id)
  except:
    await bot.send_message(adm_id, 'не удалось закрепить сообщение')


async def send_chats():
  with open('schedule.json') as f:
    table = json.load(f)

  today = datetime.datetime.today()
  if table[-1].split('(')[0].split(' ')[2] == today.strftime("%d.%m.%Y"):
    for i in db.iter_sub():
      await bot.send_message(i[0],
                             text=schedule1022.get_schedule(i[1]),
                             parse_mode='Markdown')
    if db.len_tsub() > 0:
      try:
        for i in db.iter_tsub():
          await bot.send_message(i[0],
                             text=schedule1022.get_schedule_for_teacher(i[1]),
                             parse_mode='Markdown')
      except:
        pass


@dp.callback_query_handler(text_startswith="group:")
async def handle_group_callback(query: CallbackQuery):
  key = query.data.split(':')
  if key[2] == 'sub':
    db.set_sub(query.message.chat.id, key[1])
    await query.message.edit_text(
      text=
      f'Вы подписались на автоматическую рассылку расписания группы {key[1]}',
      reply_markup=None)
  else:
    back_key = InlineKeyboardButton(text='Назад', callback_data='back_key')
    keyboard = InlineKeyboardMarkup().add(back_key)
    await query.message.edit_text(text=schedule1022.get_schedule(key[1]),
                                  reply_markup=keyboard,
                                  parse_mode='Markdown')


@dp.callback_query_handler(text_startswith="cancel_key")
async def handle_cancel_callback(query: CallbackQuery):
  db.del_sub(query.message.chat.id)
  await query.message.edit_text(text='Вы оменили рассылку', reply_markup=None)

@dp.callback_query_handler(text_startswith="cancel_teacher_key")
async def handle_cancel_teacher_callback(query: CallbackQuery):
  db.del_tsub(query.message.chat.id)
  await query.message.edit_text(text='Вы оменили рассылку преподавателя', reply_markup=None)

@dp.callback_query_handler(text_startswith="key:")
async def handle_key_callback(query: CallbackQuery):
  key = query.data.split(':')
  keyboard = kb_value_group(key[1], key[2])
  if key[2] == 'sub':
    back_key = InlineKeyboardButton(text='Назад', callback_data='back_sub_key')
  else:
    back_key = InlineKeyboardButton(text='Назад', callback_data='back_key')
  keyboard.row(back_key)
  await query.message.edit_text(text='Выберите группу:', reply_markup=keyboard)


async def updater_schedule():
  try:
    schedule1022.download_pdf()
    await bot.send_message(adm_id, 'updated')
  except:
    await bot.send_message(adm_id, 'не удалось скачать')


async def scheduler():
  aioschedule.every().day.at("3:00").do(updater_schedule)
  aioschedule.every().monday.at("3:30").do(send_chats)
  aioschedule.every().tuesday.at("3:30").do(send_chats)
  aioschedule.every().wednesday.at("3:30").do(send_chats)
  aioschedule.every().thursday.at("3:30").do(send_chats)
  aioschedule.every().friday.at("4:30").do(send_chats)
  while True:
    await aioschedule.run_pending()
    await asyncio.sleep(1)


async def on_startup(dp):
  await bot.send_message(adm_id, 'Бот запущен!')
  schedule1022.download_pdf()

  asyncio.create_task(scheduler())


async def on_shutdown(dp):
  await bot.send_message(adm_id, 'Бот умер :(')


if __name__ == '__main__':
  keep_alive()

  dp.middleware.setup(ThrottlingMiddleware())

  executor.start_polling(dp,
                         on_startup=on_startup,
                         on_shutdown=on_shutdown,
                         skip_updates=True)
