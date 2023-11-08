from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from typing import List
from settings import pickle_file
import pickle


class Group:
    def __init__(self, schedule: List[str]):
        self.header = schedule[0]
        self.name = schedule[1]
        self.schedule: Schedule = Schedule(schedule[2:])

    def __str__(self):
        return f"{self.header}\n {self.name}\n {self.schedule}\n"


class Schedule:
    day_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    time = ["8:30 - 10:00",
            "10:10 - 11:40",
            "12:10 - 13:40",
            "13:50 - 15:20",
            "15:50 - 17:20",
            "17:30 - 19:00",
            "19:10 - 20:40"]

    def __init__(self, schedule: List[str]):
        self.schedule: dict = dict(zip(Schedule.day_of_week, self.day(schedule)))

    @staticmethod
    def day(schedule):
        result = []
        for i in range(0, len(schedule) + 1, 7):
            result.append(dict(zip(Schedule.time, schedule[i: i + 7])))
        return result

    def __str__(self):
        result = ""
        for _ in self.schedule:
            result += str(_) + "\n"
        return result

    def __getitem__(self, day):
        return self.schedule[day]


def cell_value(sheet, coord):
    cell = sheet[coord]
    if not isinstance(cell, MergedCell):
        return cell.value

    for range in sheet.merged_cells.ranges:
        if coord in range:
            return range.start_cell.value

    raise AssertionError("Merged cell is not in any merge range!")


def get_schedule(group: str, day: str, data: List[Group] = None) -> str:
    for _ in data:
        if _.header is not None:
            if group in _.name:
                return "\n\n".join([x if x is not None else "Нет пары" for x in _.schedule[day]])


def dump_data_to_pickle():
    """ Loads schedule from Excel to Pickle """

    wb = load_workbook(filename="schedule.xlsx", data_only=True)
    ws = wb["Лист1"]

    group_objects: List[Group] = []

    for _ in [*ws.columns][2:-1]:
        x = Group([cell_value(ws, x.coordinate) if x is not None else "" for x in [*_]][3:])
        group_objects.append(x)

    with open(pickle_file, "wb") as f:
        pickle.dump(group_objects, f)
