"""Draw original SVG documentation figures; not modified StarUML trial exports."""
from html import escape
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'frontend/docs/figures'
OUT.mkdir(parents=True, exist_ok=True)
parts = []


def line(x, y, xx, yy, dashed=False):
    parts.append(f'<path d="M{x} {y} L{xx} {yy}" fill="none" stroke="black" stroke-width="1.4" {"stroke-dasharray=\"6 4\"" if dashed else ""}/>')


def text(x, y, value, size=18, bold=False):
    for n, row in enumerate(value.split('\n')):
        parts.append(f'<text x="{x}" y="{y+n*(size+5)}" font-family="Arial" font-size="{size}" font-weight="{"bold" if bold else "normal"}">{escape(row)}</text>')


def box(x, y, w, title, rows=(), height=None):
    height = height or 64+len(rows)*27
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{height}" fill="white" stroke="black" stroke-width="1.5"/>')
    text(x+10, y+27, title, 18, True)
    line(x, y+39, x+w, y+39)
    if not rows:
        line(x, y+51, x+w, y+51)
    for i, row in enumerate(rows):
        text(x+10, y+65+i*27, row, 16)


def save(name, h):
    (OUT/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="{h}" viewBox="0 0 760 {h}"><rect width="760" height="{h}" fill="white"/>'+''.join(parts)+'</svg>', encoding='utf-8')
    parts.clear()


box(20, 30, 330, 'users', ['PK user_id INTEGER', 'U user_name VARCHAR(50)', 'user_password_hash VARCHAR(255)'])
box(390, 30, 350, 'costs', ['PK cost_id INTEGER', 'cost_name VARCHAR(100)', 'N cost_description VARCHAR(500)', 'cost_status VARCHAR(10)', 'cost_image_url VARCHAR(500)', 'cost_video_url VARCHAR(500)', 'N cost_behavior VARCHAR(16)', 'N cost_code INTEGER', 'cost_created_at TIMESTAMPTZ', 'FK cost_creator_id INTEGER', 'N cost_formed_at TIMESTAMPTZ'])
box(20, 440, 330, 'cost_likes', ['PK cost_like_id INTEGER', 'FK user_id INTEGER', 'FK cost_id INTEGER', 'U (user_id, cost_id)'])
line(350, 100, 390, 100); text(354, 90, '1  *', 14)
line(185, 175, 185, 440); text(195, 220, '1', 16); text(195, 425, '0..*', 16)
line(350, 520, 560, 520); line(560, 520, 560, 390); text(368, 510, '0..*', 16); text(570, 430, '1', 16)
save('01_database.svg', 650)

box(270, 20, 220, 'Postman', height=65)
line(380, 85, 190, 145); line(380, 85, 570, 145)
box(20, 145, 720, 'Бэкенд FastAPI', height=390)
box(40, 210, 400, 'Домен costs', ['GET /api/costs', 'GET /api/costs/feed', 'GET /api/costs/draft', 'POST /api/costs', 'PUT /api/costs/{cost_id}', 'DELETE /api/costs/{cost_id}', 'POST /api/costs/{cost_id}/likes'])
box(460, 210, 260, 'Домен users', ['POST /api/users', 'POST /api/users/auth', 'POST /api/users/logout'])
text(60, 200, 'API costs', 14); text(480, 200, 'API users', 14)
line(240, 535, 240, 600, True); line(590, 355, 590, 600, True)
box(20, 600, 720, 'Модели SQLAlchemy', height=130)
box(40, 650, 200, 'Cost'); box(280, 650, 200, 'CostLike'); box(520, 650, 200, 'User')
box(20, 790, 720, 'PostgreSQL и сессии Redis', height=160)
box(40, 845, 190, 'costs'); box(260, 845, 220, 'cost_likes'); box(510, 845, 210, 'users')
line(140, 714, 135, 845, True); line(380, 714, 370, 845, True); line(620, 714, 615, 845, True)
save('02_backend.svg', 980)

box(20, 20, 720, 'sd Публикация и просмотр издержки', height=1080)
for x, title in [(40,'Фронтенд'), (290,'Домен users'), (540,'Домен costs')]:
    box(x, 85, 180, title, height=65)
    line(x+90, 150, x+90, 1070, True)
messages = [('POST /api/users/auth (user_name, password)', '200; Set-Cookie: cost_session', 380),
            ('GET /api/costs?min_cost_code=20&max_cost_code=40', '200; издержки[]', 630),
            ('POST /api/costs (cost_name, image, video; Cookie)', '201; черновик (cost_id, URL медиа)', 630),
            ('GET /api/costs/draft (Cookie)', '200; свой черновик или null', 630),
            ('PUT /api/costs/{id} (описание, тип, код; Cookie)', '200; published, cost_formed_at', 630),
            ('GET /api/costs/feed (Cookie)', '200; первая карточка', 630),
            ('GET /api/costs/feed?cost_id=1&next=true (Cookie)', '200; следующая карточка', 630),
            ('POST /api/costs/{id}/likes (is_liked=1; Cookie)', '200; is_liked, like_count', 630)]
for i, (request, response, target) in enumerate(messages):
    y = 220+i*110
    label = '\n'.join(textwrap.wrap(f'{2*i+1} {request}', width=45))
    text(140, y-12-(25 if '\n' in label else 0), label, 18)
    line(130, y, target, y); line(target-9, y-5, target, y); line(target-9, y+5, target, y)
    text(140, y+28, f'{2*i+2} {response}', 17)
    line(target, y+40, 130, y+40, True); line(139, y+35, 130, y+40); line(139, y+45, 130, y+40)
save('03_sequence.svg', 1120)

box(270, 20, 220, 'App')
box(20, 170, 220, 'CostTilesPage'); box(270, 170, 220, 'CostTabBar'); box(520, 170, 220, 'CostFeedPage')
for x in (130,380,630): line(380, 84, x, 170)
box(20, 345, 240, 'CostCodeFilter'); box(290, 345, 200, 'CostCard'); box(520, 345, 220, 'CostVideo')
line(130, 234, 140, 345); line(130, 234, 390, 345); line(630, 234, 630, 345)
box(290, 510, 200, 'CostImage'); line(390, 409, 390, 510)
box(20, 700, 720, 'COSTS_MOCK и public/media', ['Карточки — локальная типизированная коллекция', 'Медиа — файлы проекта без MinIO и API'])
line(390, 574, 390, 700, True); line(630, 409, 630, 700, True)
text(25, 650, 'Общее состояние через props без Context и Redux', 18)
save('04_react.svg', 850)
print(OUT)
