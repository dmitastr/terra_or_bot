# main.py

import io
import logging
import os
from typing import Any, TypedDict, List, Tuple
from jinja2 import Environment, FileSystemLoader

from .html_to_image import HtmlToImage
from service.service import Service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ScheduleItem(TypedDict):
    gamemaster_name: str
    date: str
    shift: str


class NameItem(TypedDict):
    gamemaster_name: str
    bgcolor: str


class GmScheduleGenerator:
    def __init__(self, service: Service):
        hi_token = os.environ.get('HI_TOKEN')
        self.hi = HtmlToImage(hi_token)
        self.service = service

    def run(self, dates: List[str], table_data: dict[str, dict[str, str]]) -> Tuple[io.BytesIO, str]:
        html = self.render_html_page(dates, table_data)
        img, url = self.render_html_to_image(html)
        return img, url

    def render_html_page(self, dates: List[str], table_data: dict[str, dict[str, str]]) -> str:
        """
        Генерирует HTML из данных с помощью Jinja2-шаблона.
        """
        names = self.service.get_gm_human_names()
        names_with_color = self.color_alternate(names)

        env = Environment(loader=FileSystemLoader(
            "./gm_schedule_generator/static/templates"))
        template = env.get_template("table_template.html")

        return template.render(
            title="ИГРОВЕДЫ",
            dates=dates,
            names=names_with_color,
            table_data=table_data,
        )

    def color_alternate(self, names: List[str]) -> List[NameItem]:
        return [
            {'gamemaster_name': name, 'bgcolor': '#ffffff' if i % 2 == 0 else '#f4cccc'}
            for i, name in enumerate(names)
        ]

    def normalize_schedule(self, dates: List[str], names: List[str], data: List[ScheduleItem]) -> dict[str, dict[str, str]]:
        """
        Преобразует входные данные в структуру для таблицы.
        Возвращает:
        - список уникальных дат (заголовки колонок)
        - список уникальных гейм-мастеров (заголовки строк)
        - словарь расписания: {имя: {дата: смена}}
        """
        table_data: dict[str, dict[str, str]] = {
            name: {date: "" for date in dates} for name in names}
        for item in data:
            table_data[item["gamemaster_name"]][item["date"]] = item["shift"]

        return table_data

    def render_html_to_image(self, html_content: str) -> Tuple[io.BytesIO, str]:
        img, url = self.hi.html_to_image(html_content)
        return img, url

    def write_file(self, fname: str, data: io.BytesIO):
        with open(fname, 'wb') as f:
            f.write(data.getbuffer())


# if __name__ == '__main__':
#     data: str = '''{
#         "rows_index": ["Бес",	"Небесный",	"Ночной Александр",	"Егор Шпала",	"Алиса",	"CD-Ром",	"Митя",	"Федеральный",	"Сергей",	"Влад",	"Полина"],
#         "cols_index": ["пн 04.08",	"вт 05.08",	"ср 06.08",	"чт 07.08",	"пт 08.08",	"сб 09.08",	"вс 10.08"],
#         "shifts": [
#     {"gamemaster_name": "Бес", "date": "пт 08.08", "shift": "00 - 06"},
#     {"gamemaster_name": "Ночной Александр", "date": "вс 10.08", "shift": "11³⁰ - 18"},
#     {"gamemaster_name": "Ночной Александр", "date": "сб 09.08", "shift": "18 - 00"},
#     {"gamemaster_name": "Егор Шпала", "date": "вт 05.08", "shift": "18 - 00"},
#     {"gamemaster_name": "Егор Шпала", "date": "ср 06.08", "shift": "18 - 00"},
#     {"gamemaster_name": "CD-Ром", "date": "чт 07.08", "shift": "18 - 00"},
#     {"gamemaster_name": "CD-Ром", "date": "пт 08.08", "shift": "00 - 06"},
#     {"gamemaster_name": "Митя", "date": "пт 08.08", "shift": "18 - 00"},
#     {"gamemaster_name": "Федеральный", "date": "сб 09.08", "shift": "11³⁰ - 18"},
#     {"gamemaster_name": "Сергей", "date": "вт 05.08", "shift": "18 - 00"},
#     {"gamemaster_name": "Влад", "date": "чт 07.08", "shift": "18 - 00"},
#     {"gamemaster_name": "Влад", "date": "вс 10.08", "shift": "18 - 00"}
#     ]}'''
#     gm = GmScheduleGenerator()
#     page = gm.generate_html(data)
#     with open("pages/table.html", "w", encoding="utf8") as f:
#         f.write(page)

#     # img, url = gm.render_html_to_image(page)
#     # print(url)
#     # gm.write_file('out.png', img)
