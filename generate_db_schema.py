"""
Generate db-schema.jpg — an Entity-Relationship diagram of the XYZShop database.

Renders every model/table (auth User, products, orders apps) with its columns,
primary/foreign/unique keys and the relationships between them, then writes a
high-resolution JPG to the project root.

Pure-Pillow implementation (no Graphviz/matplotlib required).

Usage:
    .venv\\Scripts\\python.exe generate_db_schema.py
"""
from __future__ import annotations

from datetime import date
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Rendering configuration
# ---------------------------------------------------------------------------
S = 2                       # supersampling factor (drawn big, then downscaled)
W, H = 1860, 1560           # logical canvas size
OUT = "db-schema.jpg"

# App / entity colours
BLUE   = (37, 99, 235)      # products app
GREEN  = (5, 150, 105)      # auth app (User)
ORANGE = (234, 88, 12)      # orders app

BG      = (247, 249, 252)
BORDER  = (51, 65, 85)
ROW_A   = (255, 255, 255)
ROW_B   = (241, 245, 249)
TITLE_C = (15, 23, 42)
SUB_C   = (100, 116, 139)

TAG_COLORS = {
    "PK": (185, 28, 28),
    "FK": (124, 58, 237),
    "UQ": (8, 145, 178),
}

ROW_H   = 30
HEAD_H  = 40
PAD     = 14
TAG_W   = 46
GAP     = 22


def s(v: float) -> int:
    return int(round(v * S))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = (["arialbd.ttf", "seguisb.ttf"] if bold else ["arial.ttf", "segoeui.ttf"])
    for n in names:
        try:
            return ImageFont.truetype(n, s(size))
        except OSError:
            continue
    return ImageFont.load_default()


F_TITLE = font(30, True)
F_SUB   = font(15)
F_HEAD  = font(17, True)
F_NAME  = font(14, True)
F_TYPE  = font(13)
F_TAG   = font(11, True)
F_CARD  = font(15, True)
F_NOTE  = font(12)
F_LEG   = font(14)
F_LEGB  = font(15, True)


# ---------------------------------------------------------------------------
# Schema definition  (tag, column, type)
# ---------------------------------------------------------------------------
TABLES = {
    "user": {
        "title": "User  (auth_user)", "app": GREEN, "pos": (60, 545),
        "fields": [
            ("PK", "id", "AutoField"),
            ("UQ", "username", "varchar(150)"),
            ("", "email", "varchar(254)"),
            ("", "first_name", "varchar(150)"),
            ("", "last_name", "varchar(150)"),
            ("", "password", "varchar(128)"),
            ("", "is_staff", "bool"),
            ("", "is_superuser", "bool"),
            ("", "is_active", "bool"),
            ("", "date_joined", "datetime"),
        ],
    },
    "category": {
        "title": "Category", "app": BLUE, "pos": (60, 150),
        "fields": [
            ("PK", "id", "BigAutoField"),
            ("", "name", "varchar(200)  idx"),
            ("UQ", "slug", "varchar(200)"),
        ],
    },
    "product": {
        "title": "Product", "app": BLUE, "pos": (690, 70),
        "fields": [
            ("PK", "id", "BigAutoField"),
            ("FK", "category_id", "-> Category"),
            ("", "name", "varchar(200)  idx"),
            ("", "slug", "varchar(200)  idx"),
            ("", "image", "varchar(100)"),
            ("", "description", "text"),
            ("", "cost_price", "decimal(10,2)"),
            ("", "price", "decimal(10,2)"),
            ("", "stock", "int unsigned"),
            ("", "available", "bool"),
            ("", "is_online", "bool"),
            ("", "created", "datetime"),
            ("", "updated", "datetime"),
        ],
    },
    "order": {
        "title": "Order", "app": ORANGE, "pos": (690, 800),
        "fields": [
            ("PK", "id", "BigAutoField"),
            ("FK", "user_id", "-> User  (null)"),
            ("", "first_name", "varchar(50)"),
            ("", "last_name", "varchar(50)"),
            ("", "email", "varchar(254)"),
            ("", "address", "varchar(250)"),
            ("", "postal_code", "varchar(20)"),
            ("", "city", "varchar(100)"),
            ("", "created", "datetime"),
            ("", "updated", "datetime"),
            ("", "paid", "bool"),
            ("", "payment_method", "varchar(20)"),
            ("", "payment_id", "varchar(250) null"),
            ("", "status", "varchar(20)"),
        ],
    },
    "review": {
        "title": "ProductReview", "app": BLUE, "pos": (1360, 60),
        "note": "UNIQUE (product_id, user_id)",
        "fields": [
            ("PK", "id", "BigAutoField"),
            ("FK", "product_id", "-> Product"),
            ("FK", "user_id", "-> User"),
            ("", "rating", "smallint (1-5)"),
            ("", "title", "varchar(200)"),
            ("", "comment", "text"),
            ("", "verified_purchase", "bool"),
            ("", "created", "datetime"),
            ("", "updated", "datetime"),
        ],
    },
    "price": {
        "title": "ProductPriceHistory", "app": BLUE, "pos": (1360, 470),
        "fields": [
            ("PK", "id", "BigAutoField"),
            ("FK", "product_id", "-> Product"),
            ("", "cost_price", "decimal(10,2)"),
            ("", "selling_price", "decimal(10,2)"),
            ("FK", "changed_by_id", "-> User  (set null)"),
            ("", "changed_at", "datetime"),
            ("", "reason", "text"),
        ],
    },
    "orderitem": {
        "title": "OrderItem", "app": ORANGE, "pos": (1360, 850),
        "fields": [
            ("PK", "id", "BigAutoField"),
            ("FK", "order_id", "-> Order"),
            ("FK", "product_id", "-> Product"),
            ("", "price", "decimal(10,2)"),
            ("", "quantity", "int unsigned"),
        ],
    },
    "sale": {
        "title": "Sale", "app": BLUE, "pos": (1360, 1130),
        "fields": [
            ("PK", "id", "BigAutoField"),
            ("FK", "order_id", "-> Order  (null)"),
            ("", "date", "datetime"),
            ("FK", "category_id", "-> Category"),
            ("FK", "item_id", "-> Product"),
            ("", "sold_price", "decimal(10,2)"),
            ("", "quantity", "int unsigned"),
        ],
    },
}

# (parent, child) — parent is the "1" side, child is the "many" side
RELATIONS = [
    ("category", "product"),
    ("category", "sale"),
    ("user", "order"),
    ("user", "review"),
    ("user", "price"),
    ("product", "review"),
    ("product", "price"),
    ("product", "sale"),
    ("product", "orderitem"),
    ("order", "orderitem"),
    ("order", "sale"),
]


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
_probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def text_w(txt: str, fnt) -> int:
    return _probe.textbbox((0, 0), txt, font=fnt)[2] // S


for t in TABLES.values():
    name_w = max(text_w(f[1], F_NAME) for f in t["fields"])
    type_w = max(text_w(f[2], F_TYPE) for f in t["fields"])
    title_w = text_w(t["title"], F_HEAD)
    body_w = PAD + TAG_W + name_w + GAP + type_w + PAD
    t["w"] = max(body_w, title_w + 2 * PAD, 300)
    t["h"] = HEAD_H + ROW_H * len(t["fields"])
    t["x"], t["y"] = t["pos"]


def rect(t):
    return t["x"], t["y"], t["x"] + t["w"], t["y"] + t["h"]


# distribute anchor points: parents exit on the RIGHT edge, children enter LEFT
right_conns: dict[str, list] = {k: [] for k in TABLES}
left_conns: dict[str, list] = {k: [] for k in TABLES}
for i, (p, c) in enumerate(RELATIONS):
    right_conns[p].append((TABLES[c]["y"] + TABLES[c]["h"] / 2, i))
    left_conns[c].append((TABLES[p]["y"] + TABLES[p]["h"] / 2, i))

anchor_parent: dict[int, tuple] = {}
anchor_child: dict[int, tuple] = {}


def spread(box, count, index):
    y0 = box["y"] + HEAD_H + 6
    y1 = box["y"] + box["h"] - 6
    if count == 1:
        return (y0 + y1) / 2
    return y0 + (y1 - y0) * index / (count - 1)


for k, conns in right_conns.items():
    conns.sort()
    for idx, (_, ri) in enumerate(conns):
        y = spread(TABLES[k], len(conns), idx)
        anchor_parent[ri] = (TABLES[k]["x"] + TABLES[k]["w"], y)

for k, conns in left_conns.items():
    conns.sort()
    for idx, (_, ri) in enumerate(conns):
        y = spread(TABLES[k], len(conns), idx)
        anchor_child[ri] = (TABLES[k]["x"], y)


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------
img = Image.new("RGB", (s(W), s(H)), BG)
d = ImageDraw.Draw(img)


def line(p1, p2, color, width):
    d.line([s(p1[0]), s(p1[1]), s(p2[0]), s(p2[1])], fill=color, width=s(width))


def rrect(box, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = box
    d.rounded_rectangle([s(x0), s(y0), s(x1), s(y1)], radius=s(radius),
                        fill=fill, outline=outline, width=s(width))


# Title
d.text((s(60), s(40)), "XYZShop  \u2014  Database Schema", font=F_TITLE, fill=TITLE_C)
d.text((s(62), s(85)),
       f"Entity\u2013Relationship diagram  \u00b7  Django 6.0 \u00b7 SQLite  \u00b7  generated {date.today():%Y-%m-%d}",
       font=F_SUB, fill=SUB_C)

# 1) relationship lines FIRST so the table boxes occlude the crossings
for i, (p, c) in enumerate(RELATIONS):
    px, py = anchor_parent[i]
    cx, cy = anchor_child[i]
    color = TABLES[p]["app"]
    midx = (px + cx) / 2
    # orthogonal H-V-H routing through the gutter mid-point
    line((px, py), (midx, py), color, 2)
    line((midx, py), (midx, cy), color, 2)
    line((midx, cy), (cx, cy), color, 2)

# 2) table boxes
for t in TABLES.values():
    x0, y0, x1, y1 = rect(t)
    # shadow
    rrect((x0 + 5, y0 + 6, x1 + 5, y1 + 6), 12, fill=(226, 232, 240))
    rrect((x0, y0, x1, y1), 12, fill=ROW_A, outline=BORDER, width=2)
    # header
    d.rounded_rectangle([s(x0), s(y0), s(x1), s(y0 + HEAD_H)], radius=s(12),
                        fill=t["app"])
    d.rectangle([s(x0), s(y0 + HEAD_H - 12), s(x1), s(y0 + HEAD_H)], fill=t["app"])
    d.text((s(x0 + PAD), s(y0 + 11)), t["title"], font=F_HEAD, fill=(255, 255, 255))

    for r, (tag, name, typ) in enumerate(t["fields"]):
        ry = y0 + HEAD_H + r * ROW_H
        if r % 2:
            d.rectangle([s(x0 + 2), s(ry), s(x1 - 2), s(ry + ROW_H)], fill=ROW_B)
        if tag:
            tc = TAG_COLORS[tag]
            rrect((x0 + 8, ry + 6, x0 + 8 + 30, ry + ROW_H - 6), 5, fill=tc)
            tw = text_w(tag, F_TAG)
            d.text((s(x0 + 8 + (30 - tw) / 2), s(ry + 8)), tag, font=F_TAG,
                   fill=(255, 255, 255))
        underline = tag in ("PK", "UQ")
        d.text((s(x0 + PAD + TAG_W), s(ry + 7)), name, font=F_NAME, fill=TITLE_C)
        if underline:
            nw = text_w(name, F_NAME)
            d.line([s(x0 + PAD + TAG_W), s(ry + ROW_H - 6),
                    s(x0 + PAD + TAG_W + nw), s(ry + ROW_H - 6)],
                   fill=TITLE_C, width=s(1))
        d.text((s(x1 - PAD - text_w(typ, F_TYPE)), s(ry + 8)), typ, font=F_TYPE,
               fill=SUB_C)
        d.line([s(x0 + 2), s(ry), s(x1 - 2), s(ry)], fill=(226, 232, 240), width=s(1))

    if t.get("note"):
        d.text((s(x0 + 2), s(y1 + 6)), t["note"], font=F_NOTE, fill=(124, 58, 237))

# 3) cardinality markers ON TOP of the boxes
def crowfoot(x, y, color):
    """three tines pointing into the child's left edge (line comes from left)."""
    b = (x - 18, y)
    for dy in (-9, 0, 9):
        line(b, (x, y + dy), color, 2)
    d.ellipse([s(x - 22), s(y - 3), s(x - 16), s(y + 3)], fill=color)


for i, (p, c) in enumerate(RELATIONS):
    px, py = anchor_parent[i]
    cx, cy = anchor_child[i]
    color = TABLES[p]["app"]
    # "one" side: filled dot + short perpendicular tick
    d.ellipse([s(px - 4), s(py - 4), s(px + 4), s(py + 4)], fill=color)
    line((px + 8, py - 9), (px + 8, py + 9), color, 2)
    d.text((s(px + 12), s(py - 22)), "1", font=F_CARD, fill=color)
    # "many" side: crow's foot + N
    crowfoot(cx, cy, color)
    d.text((s(cx - 34), s(cy - 24)), "N", font=F_CARD, fill=color)

# ---------------------------------------------------------------------------
# Legend
# ---------------------------------------------------------------------------
lx, ly, lw, lh = 60, 1000, 590, 250
rrect((lx, ly, lx + lw, ly + lh), 12, fill=(255, 255, 255), outline=BORDER, width=2)
d.text((s(lx + 16), s(ly + 12)), "Legend", font=F_LEGB, fill=TITLE_C)

rows = [
    ("app", BLUE,  "products app  \u2014  Category, Product, ProductReview,"),
    ("cont", None, "ProductPriceHistory, Sale"),
    ("app", GREEN, "auth app  \u2014  User"),
    ("app", ORANGE, "orders app  \u2014  Order, OrderItem"),
]
yy = ly + 46
for kind, col, txt in rows:
    if kind == "app":
        rrect((lx + 16, yy + 2, lx + 40, yy + 20), 4, fill=col)
        d.text((s(lx + 52), s(yy)), txt, font=F_LEG, fill=TITLE_C)
    else:
        d.text((s(lx + 52), s(yy)), txt, font=F_LEG, fill=TITLE_C)
    yy += 26

yy += 6
for tag in ("PK", "FK", "UQ"):
    tc = TAG_COLORS[tag]
    rrect((lx + 16, yy + 2, lx + 46, yy + 20), 5, fill=tc)
    d.text((s(lx + 22), s(yy + 3)), tag, font=F_TAG, fill=(255, 255, 255))
    label = {"PK": "primary key", "FK": "foreign key", "UQ": "unique"}[tag]
    d.text((s(lx + 58), s(yy)), label, font=F_LEG, fill=TITLE_C)
    yy += 26

d.text((s(lx + 300), s(ly + 130)),
       "1 \u2500\u25c9      one side", font=F_LEG, fill=SUB_C)
d.text((s(lx + 300), s(ly + 156)),
       "N \u2500\u2308      many side (crow's foot)", font=F_LEG, fill=SUB_C)
d.text((s(lx + 300), s(ly + 182)),
       "underline = PK / unique column", font=F_LEG, fill=SUB_C)

# ---------------------------------------------------------------------------
# Save (downscale for anti-aliasing)
# ---------------------------------------------------------------------------
img = img.resize((W, H), Image.LANCZOS)
img.save(OUT, "JPEG", quality=95)
print(f"Wrote {OUT}  ({W}x{H})")
