from imports import *
from common import bot
from xl_parser import get_schedule, Schedule
from keyboards import day_of_week_inline_keyboard, cancel_menu, feedback_menu, days_of_week
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.state import StatesGroup, State
import settings
import pickle
from datetime import datetime, timedelta
from sqlite3 import IntegrityError

router = Router()


class Register(StatesGroup):
    wait_for_group = State()

class Feedback(StatesGroup):
    wait_for_detail = State()


@router.message(Command("start"))
async def echo_start(message: Message, state: FSMContext):
    db.add_user(message.from_user)
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer("Привет! Введи номер своей группы. Пример: 04.3-208 (а)")
    await state.set_state(Register.wait_for_group)

@router.message(Command("groups"))
async def echo_start(message: Message):
    await message.answer(str(get_groups(settings.pickle_file)))


@router.message(F.text.regexp(r"04\.3-\d{3}( \([аб]\))?"))
@router.message(Register.wait_for_group)
async def receive_group_name(message: Message, state: FSMContext):
    if check_for_group_validity(message.text):
        db.insert_group(message.from_user.id, message.text)
        await message.reply("Выбери день", reply_markup=day_of_week_inline_keyboard)
        await state.clear()
    else:
        await message.reply("Введи правильный номер группы\n\nНапример 04.3-112 или 04.3-205 (а), если есть подгруппа)")


@router.callback_query(F.data == "change_group")
async def choose_day_of_week(callback_query: CallbackQuery, state: FSMContext):
    user_group = db.get_group(callback_query.from_user.id)
    await callback_query.message.reply("Введи номер своей группы. Пример: 04.3-208 (а)", reply_markup=cancel_menu)
    await state.set_state(Register.wait_for_group)

@router.callback_query(F.data == "cancel")
async def choose_day_of_week(callback_query: CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await state.clear()


@router.callback_query(F.data.in_(days_of_week))
async def choose_day_of_week(callback_query: CallbackQuery):
    user_group = db.get_group(callback_query.from_user.id)
    result = get_schedule(user_group, callback_query.data, settings.pickle_file)
    try:
        await callback_query.message.edit_text(result, reply_markup=day_of_week_inline_keyboard)
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "yes")
async def send_feedback_yes_no(callback_query: CallbackQuery):
    db.insert_feedback(callback_query.from_user.id,
                       db.get_group(callback_query.from_user.id),
                       callback_query.data,
                       str(callback_query.from_user)
                       )
    await bot.send_message(callback_query.message.chat.id, "Спасибо за ответ!")
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@router.callback_query(F.data == "no")
async def elaborate(callback_query: CallbackQuery, state: FSMContext):
    message = await callback_query.message.answer("Расскажи, что можно улучшить?")
    await state.update_data(message_to_delete=[callback_query.message.message_id, message.message_id])
    await state.set_state(Feedback.wait_for_detail)


@router.message(Feedback.wait_for_detail)
async def send_feedback_detail(message: Message, state: FSMContext):
    db.insert_feedback(message.from_user.id, db.get_group(message.from_user.id), message.text, str(message.from_user))
    data = await state.get_data()
    await bot.delete_message(message.chat.id, data["message_to_delete"][0])
    await bot.delete_message(message.chat.id, data["message_to_delete"][1])
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer("Спасибо за отзыв!")
    await state.clear()


@router.message(Command("feedback"))
async def cast_feedback(message: Message):
    if message.from_user.id in settings.admins:
        for user in db.get_users():
            try:
                db.insert_feedback(user, db.get_group(user))
                try:
                    await bot.send_message(user, "Бот работает правильно? Верное ли расписание?",
                                           reply_markup=feedback_menu)
                except TelegramForbiddenError:
                    print("User " + str(user) + " blocked the bot")
            except IntegrityError:
                pass

        await bot.send_message(message.from_user.id, "Всем отправил")
    else:
        await bot.delete_message(message.chat.id, message.message_id)

@router.message(Command("me"))
async def show_json(message: Message):
    await message.reply(str(message.from_user))


def get_schedule(group_name: str, day: str, pickle_file) -> str:
    with ((open(pickle_file, "rb")) as f):
        for group in pickle.load(f):
            if group.header is not None:
                if group_name in group.name:
                    schedule: dict = group.schedule[day]
                    now = (datetime.now() - timedelta(days=datetime.now().weekday()))
                    then = (datetime(2023, 9, 2) - timedelta(days=datetime(2023, 9, 2).weekday()))
                    week_no = int((now - then).days / 7 + 1)
                    #damn
                    return f"💬 День {day}\n💬 Группа {group_name}\n💬 Неделя {week_no}\n\n" + \
                    "".join(["[{}] {}\n\n".format(time, "❌ Нет пары" if course is None else "✅" + course) for time, course in schedule.items()])

def check_for_group_validity(group: str) -> bool:
    return group in get_groups(settings.pickle_file)

def get_groups(pickle_file) -> list:
    with (open(pickle_file, "rb")) as f:
        data = pickle.load(f)
        return [_.name for _ in data]


if __name__=="__main__":
    print(get_groups(settings.pickle_file))
