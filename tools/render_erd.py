"""Render a compact evidence image from the StarUML ER model for the report."""

import json
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
model = json.loads((ROOT / "docs/costs_database.mdj").read_text(encoding="utf-8"))
entities = {
    item["name"]: item
    for item in model["ownedElements"][0]["ownedElements"]
    if item["_type"] == "ERDEntity"
}
out = ROOT / "docs/screenshots/lab2_corrections/erd.svg"
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="770" height="460" viewBox="0 0 770 460">',
    '<rect width="770" height="460" fill="#ffffff"/>',
    '<text x="26" y="27" font-family="Arial" font-size="19" font-weight="bold">ER-диаграмма: издержки</text>',
    '<g fill="none" stroke="#425466" stroke-width="2">',
    '<path d="M339 102 H382"/><path d="M185 144 V322"/><path d="M550 278 V362 H387"/>',
    '</g>',
]


def draw_entity(name, x, y, width):
    columns = entities[name]["columns"]
    row = 19
    height = 36 + row * len(columns)
    marker_width = 65
    type_width = 120
    parts.extend([
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="5" fill="#fff" stroke="#1b3047" stroke-width="1.5"/>',
        f'<path d="M{x} {y+30} H{x+width}" stroke="#1b3047" stroke-width="1.5"/>',
        f'<path d="M{x+marker_width} {y+30} V{y+height} M{x+width-type_width} {y+30} V{y+height}" stroke="#a7b4c1"/>',
        f'<text x="{x+10}" y="{y+21}" font-family="Arial" font-size="15" font-weight="bold">{escape(name)}</text>',
    ])
    for i, column in enumerate(columns):
        baseline = y + 47 + i * row
        tags = [flag for flag, key in (("PK", "primaryKey"), ("FK", "foreignKey"), ("N", "nullable"), ("U", "unique"))
                if (not column[key] if key == "nullable" else column[key])]
        ctype = column["type"] + (f'({column["length"]})' if column.get("length") else "")
        parts.append(f'<text x="{x+6}" y="{baseline}" font-family="Arial" font-size="11" fill="#365a7d">{escape(" ".join(tags))}</text>')
        parts.append(f'<text x="{x+marker_width+7}" y="{baseline}" font-family="Arial" font-size="12">{escape(column["name"])}</text>')
        parts.append(f'<text x="{x+width-type_width+7}" y="{baseline}" font-family="Arial" font-size="11" fill="#596b7c">{escape(ctype)}</text>')


draw_entity("users", 26, 49, 313)
draw_entity("costs", 382, 49, 362)
draw_entity("cost_likes", 69, 322, 318)
parts.append('</svg>')
out.write_text("\n".join(parts), encoding="utf-8")
