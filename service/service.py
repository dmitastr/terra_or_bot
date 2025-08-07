import json
import logging
from typing import Any, List, Tuple, Callable

import arrow
import requests
from datasource.db_controller import YDataBase
from common.config import SLOTS, GAMEMASTERS_MAPPING, TIME_PERIOD_NAMES

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Service:
    def __init__(self, db: YDataBase, api_key: str):
        self.api_key = api_key
        self.db = db
        self.shift_table = 'shifts_available'
        self.schedule_create_url = 'https://functions.yandexcloud.net/d4eg0vivihaseh8igag4'

    def save_shifts(self, shifts: dict[str, Any]) -> None:
        user_id = shifts.get('user_id')
        username = shifts.get('username')
        if user_id and username:
            new_row = {'user_id': user_id,
                       'username': username,
                       'week_number': self.get_current_week_number(),
                       'data': json.dumps(shifts.get('selected_options', {}))}

            self.db.insert_row(table_name=self.shift_table, new_row=new_row)

    def get_current_week_number(self) -> int:
        return arrow.get().isocalendar()[1]

    def get_shifts(self) -> List[dict[str, Any]]:
        current_week = self.get_current_week_number()
        shifts = self.db.get_fields_equal(
            table_name=self.shift_table, field_filter={'week_number': [current_week]})
        for shift in shifts:
            if shift.get("data"):
                shift['data'] = json.loads(shift['data'])

        shifts = self.shifts_add_bes_roma(shifts)

        return shifts

    # заполнить пустые смены Беса и Ромы
    def shifts_add_bes_roma(self, shifts: List[dict[str, Any]]) -> List[dict[str, Any]]:
        bes: str = "besionish"
        roma: str = "milkymarss"

        usernames = [shift['username'] for shift in shifts]
        if bes not in usernames:
            shifts.append({'username': bes, 'week_number': self.get_current_week_number(),
                           'data': {'wants': ['13', '23', '33', '43', '53', '55'], 'cans': [], 'comment': 'autogenerate'}})

        if roma not in usernames:
            shifts.append({'username': roma, 'week_number': self.get_current_week_number(),
                           'data': {'wants': SLOTS, 'cans': [], 'comment': 'autogenerate'}})

        return shifts

    def shifts_to_table(self, shifts: dict[str, List[int]]) -> Tuple[List[str], dict[str, dict[str, str]]]:
        days_names = self.get_next_week_dates()
        blank_shift = {
            day_name: ''
            for day_name in days_names.values()
        }
        days: List[str] = [day[1] for day in sorted(
            list(days_names.items()), key=self.tuple_sort_func(0))]

        shifts_obj: dict[str, dict[str, str]] = {}
        for gm, gm_shifts in shifts.items():
            collapsed = self.collapse_shifts(gm_shifts)
            collapsed_with_names: dict[str, str] = {
                days_names[day]: shift_name
                for day, shift_name in collapsed.items()
            }

            for day_name in days_names.values():
                if day_name not in collapsed_with_names:
                    collapsed_with_names[day_name] = ""

            gm_name = GAMEMASTERS_MAPPING[gm][1]
            shifts_obj[gm_name] = collapsed_with_names

        for gm_name in self.get_gm_human_names():
            if gm_name not in shifts_obj:
                shifts_obj[gm_name] = blank_shift

        logger.info(f"Created shifts table: {shifts_obj}")
        return days, shifts_obj

    def get_gm_human_names(self) -> List[str]:
        gm_names: List[str] = sorted(
            GAMEMASTERS_MAPPING.values(), key=self.tuple_sort_func(0))
        return [gm[1] for gm in gm_names]

    def collapse_shifts(self, shifts: List[int]) -> dict[int, str]:
        shifts = sorted(shifts)
        shifts_info: List[Shift] = [Shift(s) for s in shifts]
        collapsed_shifts: dict[int, str] = {}
        if len(shifts_info) == 1:
            shift = shifts_info[0]
            return {shift.day: TIME_PERIOD_NAMES[shift.time_period].join(' - ')}

        start_shift = shifts_info[0]
        end_shift = start_shift
        for i in range(1, len(shifts_info)):
            shift = shifts_info[i]
            if shift.day == start_shift.day:
                end_shift = shift
                continue
            tp_start = TIME_PERIOD_NAMES[start_shift.time_period][0]
            tp_end = TIME_PERIOD_NAMES[end_shift.time_period][1]
            collapsed_shifts[start_shift.day] = f"{tp_start} - {tp_end}"
            start_shift = shift
            end_shift = shift

        tp_start = TIME_PERIOD_NAMES[start_shift.time_period][0]
        tp_end = TIME_PERIOD_NAMES[end_shift.time_period][1]
        collapsed_shifts[start_shift.day] = f"{tp_start} - {tp_end}"

        return collapsed_shifts

    def tuple_sort_func(self, idx: int) -> Callable:
        def sort_func(value: Tuple[Any]) -> Any:
            return value[idx]
        return sort_func

    def schedule_create(self) -> Tuple[List[str], dict[str, dict[str, str]]]:
        with requests.Session() as s:
            s.headers.update({'Authorization': f'Bearer {self.api_key}',
                             'Content-Type': 'application/json', 'Accept': 'application/json'})
            shifts = self.get_shifts()
            if not shifts:
                logger.error('no shifts for next week')
                return

            response: requests.Response = s.post(
                self.schedule_create_url, data=json.dumps(shifts))

            if response.status_code != 200:
                logger.error(f"error while creating schedule: {response.text}")
                return

            schedule: dict = response.json()
            dates, table = self.shifts_to_table(schedule)
            return dates, table

    def get_next_week_dates(self) -> dict[int, str]:
        # Словарь сокращений дней недели на русском
        weekdays = {
            0: "пн",
            1: "вт",
            2: "ср",
            3: "чт",
            4: "пт",
            5: "сб",
            6: "вс",
        }

        today: arrow.Arrow = arrow.now()
        # Найдём следующий понедельник
        days_until_next_monday: int = (7 - today.weekday()) % 7
        next_monday: arrow.Arrow = today.shift(
            days=+days_until_next_monday).floor('day')

        result = {}
        for i in range(7):
            day = next_monday.shift(days=+i)
            weekday_name = weekdays[i]
            formatted_date = day.format("DD.MM")
            result[i + 1] = f"{weekday_name} {formatted_date}"

        return result


class Shift:
    def __init__(self, id: int):
        self.id = id
        self.day = int(id/10)
        self.time_period = id % 10
