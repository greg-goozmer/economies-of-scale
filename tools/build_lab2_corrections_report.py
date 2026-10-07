"""Build a simple Word report from the actual LR2 screenshots (stdlib only)."""

import struct
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "docs/screenshots/lab2_corrections"
OUTPUT = ROOT / "docs/lab2_corrections_report.docx"
FIGURES = [
    ("costs_list.png", "Файлы, модели и маршруты переименованы на costs; кнопки удаления приведены к общему стилю.", "Рисунок 1 - изменение названий, адреса каталога и кнопок удаления"),
    ("feed.png", "На карточке ленты теперь видны тип издержки и её код. Удалённая карточка перенаправляет в каталог.", "Рисунок 2 - изменение ленты: значения параметров показаны на карточке"),
    ("draft.png", "На странице добавления сохранён выбор медиафайлов без загрузки изображения до следующей ЛР.", "Рисунок 3 - изменение страницы добавления с выбором изображения и видео"),
    ("erd.png", "В модели StarUML таблица costs, убраны названия связей и сетка, добавлено поле пароля; URL медиа обязательны.", "Рисунок 4 - изменение ER-диаграммы и обязательных полей базы данных"),
]


def paragraph(text, *, center=False, bold=False, size=24):
    align = '<w:pPr><w:jc w:val="center"/></w:pPr>' if center else ""
    weight = "<w:b/>" if bold else ""
    return (f'<w:p>{align}<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
            f'{weight}<w:sz w:val="{size}"/></w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


def image_paragraph(index, filename):
    image_bytes = (SHOTS / filename).read_bytes()
    width_px, height_px = struct.unpack(">II", image_bytes[16:24])
    width = 5_490_000  # 15.25 cm
    height = round(width * height_px / width_px)
    drawing = f'''<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing>
    <wp:inline distT="0" distB="0" distL="0" distR="0">
    <wp:extent cx="{width}" cy="{height}"/><wp:docPr id="{index}" name="{escape(filename)}"/>
    <a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
    <pic:pic><pic:nvPicPr><pic:cNvPr id="{index}" name="{escape(filename)}"/><pic:cNvPicPr/></pic:nvPicPr>
    <pic:blipFill><a:blip r:embed="rId{index}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
    <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{width}" cy="{height}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>
    </a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''
    return drawing


body = [
    paragraph("Исправления второй лабораторной работы", center=True, bold=True, size=32),
    paragraph("Тема: база данных издержек. Внесены замечания преподавателя к ЛР2."),
]
for index, (filename, note, caption) in enumerate(FIGURES, 1):
    body.extend((paragraph(note), image_paragraph(index, filename), paragraph(caption, center=True)))
body.append('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1020" w:right="1134" w:bottom="1020" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>')

document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
            ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
            ' xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"'
            ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
            ' xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<w:body>' + "".join(body) + '</w:body></w:document>')
relationships = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(
    f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image{i}.png"/>'
    for i in range(1, len(FIGURES) + 1)) + '</Relationships>'

with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
    archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    archive.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    archive.writestr("word/document.xml", document)
    archive.writestr("word/_rels/document.xml.rels", relationships)
    for index, (filename, _, _) in enumerate(FIGURES, 1):
        archive.write(SHOTS / filename, f"word/media/image{index}.png")

print(OUTPUT)
