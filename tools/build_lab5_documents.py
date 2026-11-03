"""Build the Lab5 explanatory note and separate screenshot checklist.

Run with the bundled document Python runtime; render and inspect before delivery.
"""
import re
from pathlib import Path

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'local_lab_artifacts/lab5/documents'
OUT.mkdir(parents=True, exist_ok=True)


def base(title):
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin, section.right_margin = Cm(2.5), Cm(1.5)
    for name in ('Normal', 'Title', 'Heading 1', 'Heading 2', 'Caption'):
        style = doc.styles[name]
        style.font.name = 'Times New Roman'
        style.font.size = Pt(12)
        style.font.color.rgb = RGBColor(0, 0, 0)
    for style in doc.styles:
        for border in list(style.element.iter(qn('w:pBdr'))):
            border.getparent().remove(border)
    doc.styles['Title'].font.size = Pt(18)
    doc.styles['Heading 1'].font.size = Pt(14)
    doc.styles['Heading 2'].font.size = Pt(12)
    normal = doc.styles['Normal'].paragraph_format
    normal.space_after = Pt(6)
    normal.line_spacing = 1.15
    doc.core_properties.title = title
    doc.core_properties.author = 'Жеребенков'
    return doc


def markdown(doc, path, heading_offset=0):
    for raw in path.read_text(encoding='utf-8').splitlines():
        if not raw.strip() or raw.startswith('```'):
            continue
        text = raw.replace('`', '').replace('**', '')
        if path.name == 'lab4_specification.md' and text.startswith('5.1 '):
            text = '5.1 По расчёту раздела 2 РПЗ: сервер с 2 ядрами, 8 ГБ ОЗУ и 2 ТБ SSD, отдельное хранилище резервной копии не менее 2 ТБ. Сценарий: 50 пользователей, 2 карточки в день, хранение 5 лет.'
        match = re.match(r'^(#{1,3}) (.*)', text)
        if match:
            doc.add_heading(match[2], min(2, len(match[1])+heading_offset))
        else:
            doc.add_paragraph(text)


def equation(doc, value):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    math = OxmlElement('m:oMath')
    run = OxmlElement('m:r')
    text = OxmlElement('m:t')
    text.text = value
    run.append(text)
    math.append(run)
    p._p.append(math)


def table(doc, rows):
    result = doc.add_table(rows=0, cols=len(rows[0]))
    result.style = 'Table Grid'
    for index, row in enumerate(rows):
        cells = result.add_row().cells
        for cell, value in zip(cells, row):
            cell.text = value
            borders = OxmlElement('w:tcBorders')
            for side in ('top', 'left', 'bottom', 'right'):
                item = OxmlElement('w:'+side)
                for key, val in (('val','single'),('sz','4'),('color','D9D9D9')):
                    item.set(qn('w:'+key), val)
                borders.append(item)
            cell._tc.get_or_add_tcPr().append(borders)
            if index == 0:
                shade = OxmlElement('w:shd')
                shade.set(qn('w:fill'), 'E7ECE7')
                cell._tc.get_or_add_tcPr().append(shade)
                for run in cell.paragraphs[0].runs:
                    run.bold = True
    return result


def report():
    doc = base('Разработка гостевого SPA системы Масштаб')
    for text in ('Министерство науки и высшего образования Российской Федерации',
                 'МГТУ имени Н Э Баумана', 'Кафедра ИУ5',
                 'Расчётно пояснительная записка'):
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    doc.add_heading('Разработка гостевого SPA системы Масштаб', 0)
    doc.add_paragraph('Дисциплина Разработка Интернет Приложений\nЛабораторная работа 5\nОценка экономии от масштаба')
    doc.add_paragraph('Выполнил Жеребенков\nГруппа ИУ5 _____\nПроверил Канев А И')
    doc.add_paragraph('Москва 2026')
    doc.add_page_break()
    doc.add_heading('1 Назначение и реализация', 1)
    doc.add_paragraph('Система «Масштаб» предназначена для публикации и просмотра видов постоянных и переменных издержек. Итоговая предметная задача — оценка средних издержек для двух объёмов выпуска; в ЛР5 реализован гостевой каталог издержек, без расчёта заявок и без серверных операций записи.')
    doc.add_paragraph('Фронтенд реализован как самостоятельное SPA на React 19 и TypeScript 5 с Vite 7, React Router 7 и React-Bootstrap 2. Используется локальная mock коллекция; PostgreSQL, Redis, MinIO и API не требуются для запуска этой лабораторной. Код издержки является идентификатором классификации карточки, а не денежной суммой.')
    doc.add_heading('1.1 Страницы и навигация', 2)
    doc.add_paragraph('Плитка /costs показывает карточки в двух колонках. Две числовые границы и двойной слайдер управляют диапазоном кода; кнопка «Применить» фильтрует mock, «Сбросить» возвращает коллекцию. Лента /costs/feed/:costId показывает видео, описание в две строки, раскрытие «Ещё», параметры под иконкой справа и переход к следующей карточке отфильтрованного списка.')
    doc.add_paragraph('Меню внизу содержит Ленту, Добавление, Плитку и Вход. Доступны только Лента и Плитка. Авторизация, добавление и изменение лайков относятся к следующему этапу. Макет фиксирован шириной 390 px и центрируется без адаптивной смены структуры.')
    doc.add_heading('1.2 Компоненты и состояние', 2)
    doc.add_paragraph('App хранит массив costs в useState и передаёт его через props. CostCodeFilter — управляемый компонент: значения и события приходят от CostTilesPage. CostFeedPage использует useParams, useNavigate, useState и useEffect. CostTabBar использует useLocation для активной вкладки. Redux и React Context не используются.')
    doc.add_paragraph('В public/media находятся локальные изображение и видео по умолчанию. У mock карточки «Подписка для кассы» оба URL пустые: CostImage и CostVideo сразу выбирают заглушки. Ошибка загрузки медиа также переключает на локальный файл. Смена страницы выполняется React Router, а не загрузкой нового HTML.')
    doc.add_heading('1.3 Проверка', 2)
    doc.add_paragraph('Предусмотрены автоматические тесты включительного диапазона, пустого результата, сброса, валидации, переходов по непоследовательным ID, раскрытия описания и параметров и медиа по умолчанию. Production сборка проверяется командой npm run build, тесты — npm test. Порядок десяти кадров защиты приведён отдельным документом.')
    doc.add_page_break()
    doc.add_heading('2 Расчёт аппаратных требований', 1)
    hardware_start = len(doc.paragraphs)
    paragraphs = [
        'Проектная оценка итоговой системы: 50 пользователей, по 2 карточки в день, 8 часов работы, 250 рабочих дней в году, срок 5 лет. На карточку: создание 1, черновик 1, публикация 1, список 1, лента 6, лайки 6 — всего 16 HTTP запросов. Пиковый коэффициент 10; 20 запросов/с на ядро — допущение, а не измерение.',
        'Строка costs: два INTEGER ID 8 Б; имя до 400 Б UTF-8; описание до 2000 Б UTF-8; статус до 10 Б ASCII; два URL по 500 Б ASCII; тип до 16 Б ASCII; код INTEGER 4 Б; два TIMESTAMPTZ по 8 Б. Служебные данные и выравнивание — бюджет 64 Б. Итого 3518 Б/строку. Лайк: три INTEGER 12 Б + служебные 28 Б = 40 Б. Индексы: 160 Б на costs и по 64 Б на строку лайка.',
        'На карточку 6 лайков. Пользователи: 50 × (4 + 200 + 255 + 64) = 26150 Б. Сессии Redis: 50 × 512 = 25600 Б. Максимальные размеры строк оценены для планирования, а не как точный pg_column_size.',
        'В S3 целевой средний размер изображения 2 МиБ, видео 8 МиБ; это не размер fixture и не лимит API. Логически удалённые карточки учитываются: физического освобождения файлов нет. Резерв ОС и приложений 20 ГиБ, запас диска 30%.',
        'Итог: 2 ядра, 8 ГБ RAM, 2 ТБ SSD для основного хранилища. Резервная копия отдельно — ещё не менее 2 ТБ. Клиент: современный браузер и 4 ГБ RAM. Перед промышленным запуском требуется нагрузочное тестирование.'
    ]
    doc.add_paragraph(paragraphs[0])
    equation(doc, 'RPS = (50 × 2 × 16) / (8 × 60 × 60) = 0,0556; RPSпик = 0,556')
    equation(doc, 'N = ceil(0,556 / 20) = 1; принимаем 2 ядра; RAM = 2 × 4 = 8 ГБ')
    equation(doc, 'Nкарточек = 50 × 2 × 250 × 5 = 125000')
    doc.add_paragraph(paragraphs[1])
    equation(doc, 'DБД = 125000 × (3518 + 160 + 6 × (40 + 64)) = 537750000 Б')
    doc.add_paragraph(paragraphs[2])
    doc.add_paragraph(paragraphs[3])
    equation(doc, 'DS3 = 125000 × (2 + 8) × 1048576 = 1310720000000 Б')
    equation(doc, 'D = (1310720000000 + 537750000 + 26150 + 25600 + 21474836480) × 1,3')
    equation(doc, 'D ≈ 1,733 ТБ; принимаем SSD 2 ТБ')
    doc.add_paragraph(paragraphs[4])
    for p in doc.paragraphs[hardware_start:]:
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(5)
        for run in p.runs:
            run.font.size = Pt(11)
    images = sorted((ROOT / 'local_lab_artifacts/lab5/figures').glob('*.png'))
    if len(images) != 4:
        raise RuntimeError(f'Expected four native StarUML exports, got {images}')
    titles = {
        '01_database.png': 'Схема базы данных издержек',
        '02_backend.png': 'Структура серверной части',
        '03_sequence.png': 'Последовательность публикации и просмотра издержки',
        '04_react.png': 'Компоненты гостевого React приложения'}
    doc.add_page_break()
    for number, image in enumerate(images, 1):
        if number > 1:
            doc.add_page_break()
        doc.add_heading(f'3.{number} {titles[image.name]}', 2)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Fit portrait diagram within A4 text area without distorting aspect ratio.
        import struct
        width, height = struct.unpack('>II', image.read_bytes()[16:24])
        scale = min(16.5/width, 22.0/height)
        p.add_run().add_picture(str(image), width=Cm(width*scale))
        doc.add_paragraph(f'Рисунок {number} — {titles[image.name]}', 'Caption')
    doc.add_page_break()
    doc.add_heading('Приложение А Техническое задание', 1)
    markdown(doc, ROOT / 'docs/lab4_specification.md', heading_offset=1)
    doc.add_page_break()
    doc.add_heading('Приложение Б Методы веб сервиса', 1)
    doc.add_paragraph('В ЛР5 серверные методы не вызываются. Таблица описывает существующий API для следующего этапа подключения фронтенда. Создание принимает multipart/form-data, остальные тела — JSON. GET списка возвращает 200 и массив карточек, лента и черновик — 200 и одну карточку или null. Создание — 201 и черновик; публикация — 200 и карточку. Лайк — 200 с cost_id, is_liked, like_count; регистрация — 201 с user_id, user_name; вход — 200 с теми же полями и Set-Cookie. Удаление и выход — 204 без тела. Нет сессии — 401, чужая или отсутствующая карточка — 404, конфликт черновика или имени — 409, неверные поля — 422.')
    rows = [('Метод и URL', 'Входные данные')]
    rows.extend([
        ('GET /api/costs', 'min_cost_code, max_cost_code'),
        ('GET /api/costs/feed', 'cost_id, next'),
        ('GET /api/costs/draft', 'Cookie'),
        ('POST /api/costs', 'cost_name, image, video; Cookie'),
        ('PUT /api/costs/{cost_id}', 'cost_description, cost_behavior, cost_code; Cookie'),
        ('DELETE /api/costs/{cost_id}', 'ID в URL; Cookie; soft delete'),
        ('POST /api/costs/{cost_id}/likes', 'is_liked 0/1; Cookie'),
        ('POST /api/users', 'user_name, password'),
        ('POST /api/users/auth', 'user_name, password'),
        ('POST /api/users/logout', 'Cookie')])
    table(doc, rows)
    doc.save(OUT / 'ЛР5_РПЗ_Жеребенков.docx')


def screenshots():
    doc = base('Порядок скриншотов лабораторной работы 5')
    doc.styles['Normal'].font.size = Pt(11)
    doc.styles['Normal'].paragraph_format.line_spacing = 1.05
    doc.styles['Normal'].paragraph_format.space_after = Pt(5)
    markdown(doc, ROOT / 'frontend/docs/lab5_screenshots.md')
    doc.paragraphs[0].style = doc.styles['Title']
    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.keep_together = True
    doc.save(OUT / 'ЛР5_Список_скриншотов.docx')


if __name__ == '__main__':
    report()
    screenshots()
    print(OUT)
