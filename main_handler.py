from imports import *
from common import bot
from xl_parser import get_schedule, Schedule
from keyboards import day_of_week_inline_keyboard, cancel_menu
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import StatesGroup, State
import settings
import pickle
from datetime import datetime, timedelta

router = Router()


class Register(StatesGroup):
    wait_for_group = State()


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
        await message.reply("Введи правильный номер группы (04.3-112 например)")


@router.callback_query(F.data == "change_group")
async def choose_day_of_week(callback_query: CallbackQuery, state: FSMContext):
    user_group = db.get_group(callback_query.from_user.id)
    await callback_query.message.reply("Введи номер своей группы. Пример: 04.3-208 (а)", reply_markup=cancel_menu)
    await state.set_state(Register.wait_for_group)

@router.callback_query(F.data == "cancel")
async def choose_day_of_week(callback_query: CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await state.clear()

@router.callback_query()
async def choose_day_of_week(callback_query: CallbackQuery):
    user_group = db.get_group(callback_query.from_user.id)
    result = get_schedule(user_group, callback_query.data, settings.pickle_file)
    try:
        await callback_query.message.edit_text(result, reply_markup=day_of_week_inline_keyboard)
    except TelegramBadRequest:
        pass


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
