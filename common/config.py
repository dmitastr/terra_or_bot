from typing import List, Tuple


APPSCRIPT_URL = "https://script.google.com/macros/s/AKfycbzS1DXjSEEnJ18WtmCAj2EBHdFpTQjitsezypLYZ9lHBJnKDoTblBn8flCjo9lk8Wl9/exec"
TECH_SHEETS = [
    "Основной список (BGG рейтинг)",
    "Коэф",
    "Проверка",
    "Данные",
    "Ревизия",
    "Знания-познания",
    "Митап таблица"
]
SHEET_NAMES = [
    "Евро",
    "Кооп",
    "Area",
    "Лайт",
    "Детективы и roll n write",
    "Дуэли",
    "Общий шкаф",
]
DEV_USER_ID = 40322523
GAMEMASTERS_CHAT_IDS = [-950503307, -1001359050637]


GM_CHAT_ID_TEST: str = "-1001359050637:443"
GM_CHAT_ID_PROD: str = "-1002189507151:2"


SLOTS: List[str] = ['13', '23', '33', '43',
                    '53', '55', '61', '63', '65', '71', '73']

GAMEMASTERS_MAPPING: dict[str, Tuple[str, str]] = {
    "oldshpala":           ('04_Egor', 'Егор'),
    "darkkappa":           ('02_Nebesnii', 'Небесный'),
    "kudripizdec":         ('11_Pauline', 'Полина'),
    "mgsnx":               ('05_Alice', 'Алиса'),
    "besionish":           ('01_Bes', 'Бес'),
    "vatacasia":           ('08_Federal', 'Федеральный'),
    "grey_judge":          ('12_Mateo', 'Матвей'),
    "quetzalthegreenbird": ('09_Sergey', 'Сергей'),
    "ffartuc":             ('10_Vlad', 'Влад'),
    "turbooo3333":         ('03_Nochnoy', 'Ночной Александр'),
    "milkymarss":          ('06_Roma', 'CD-Ром'),
    "dmastr":              ('07_Mitya', 'Митя'),
}

EVENING = 3
MORNING = 1
NIGHT = 5

TIME_PERIOD_NAMES: dict[int, List[str]] = {
    EVENING: ['18', '00'],
    MORNING: ['11³⁰', '18'],
    NIGHT: ['00', '06'],
}
