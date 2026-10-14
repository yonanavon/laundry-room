#!/usr/bin/env python3
"""Generates index.html: laundry-room layout options drawn to scale (units = cm), with a 3D view."""
import json
from pathlib import Path

W, D, H = 214, 274, 247  # room width, depth, ceiling height
TOP = 245  # top of upper cabinets
OUT = Path(__file__).resolve().parent.parent / "index.html"


# ---------- plan (top view) ----------
# Room coords: x = 0..214 from the left wall, y = 0..274 from the door wall (negative y = corridor).
# SVG: X = x, Y = 274 - y, so the door wall is at the bottom, as in the original drawing.
def ry(y):
    return D - y


def label(x, y, text, sub=None, rotate=False, size=8.5):
    t = f'<g transform="translate({x:.1f} {y:.1f}){" rotate(-90)" if rotate else ""}">'
    if sub:
        t += f'<text class="lbl" y="-1.5" font-size="{size}">{text}</text>'
        t += f'<text class="sub" y="{size - 0.5:.1f}" font-size="{size * 0.78:.1f}">{sub}</text>'
    else:
        t += f'<text class="lbl" y="{size * 0.35:.1f}" font-size="{size}">{text}</text>'
    return t + "</g>"


def item(kind, x0, y0, x1, y1, text="", sub=None, port=False, size=8.5):
    X, Y, w, h = x0, ry(y1), x1 - x0, y1 - y0
    s = f'<rect class="k-{kind}" x="{X}" y="{Y}" width="{w}" height="{h}" rx="1"/>'
    if port:
        s += f'<circle class="port" cx="{X + w / 2}" cy="{Y + h / 2}" r="{min(w, h) * 0.3:.1f}"/>'
    if text:
        s += label(X + w / 2, Y + h / 2, text, sub, rotate=w < 46 and h > 1.8 * w, size=size)
    return s


def zone(x0, y0, x1, y1, text):
    X, Y, w, h = x0, ry(y1), x1 - x0, y1 - y0
    return (f'<rect class="zone" x="{X}" y="{Y}" width="{w}" height="{h}"/>'
            + label(X + w / 2, Y + h / 2, text, size=6.5).replace('class="lbl"', 'class="zlbl"'))


def swing(hx, hy, cx, cy, ox, oy):
    """Door: hinge, closed-leaf end, open-leaf end (room coords)."""
    H_, C_, O_ = (hx, ry(hy)), (cx, ry(cy)), (ox, ry(oy))
    r = ((cx - hx) ** 2 + (cy - hy) ** 2) ** 0.5
    sx, sy = C_[0] - H_[0], C_[1] - H_[1]
    ex, ey = O_[0] - H_[0], O_[1] - H_[1]
    sweep = 1 if sx * ey - sy * ex > 0 else 0
    return (f'<path class="arc" d="M{C_[0]} {C_[1]} A{r:.0f} {r:.0f} 0 0 {sweep} {O_[0]} {O_[1]}"/>'
            f'<line class="leaf" x1="{H_[0]}" y1="{H_[1]}" x2="{O_[0]}" y2="{O_[1]}"/>')


def dim(x1, y1, x2, y2, text, room=True):
    if room:
        y1, y2 = ry(y1), ry(y2)
    vertical = x1 == x2
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    tk = 3
    if vertical:
        ticks = (f'<line class="dim" x1="{x1 - tk}" y1="{y1}" x2="{x1 + tk}" y2="{y1}"/>'
                 f'<line class="dim" x1="{x2 - tk}" y1="{y2}" x2="{x2 + tk}" y2="{y2}"/>')
        txt = f'<text class="dimt" transform="translate({mx - 2.5} {my}) rotate(-90)">{text}</text>'
    else:
        ticks = (f'<line class="dim" x1="{x1}" y1="{y1 - tk}" x2="{x1}" y2="{y1 + tk}"/>'
                 f'<line class="dim" x1="{x2}" y1="{y2 - tk}" x2="{x2}" y2="{y2 + tk}"/>')
        txt = f'<text class="dimt" x="{mx}" y="{my - 2.5}">{text}</text>'
    return f'<line class="dim" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>{ticks}{txt}'


def fan(x0, x1):
    """Extractor fan high on the door wall, ducted out to the corridor."""
    return (f'<rect class="fan" x="{x0}" y="{D - 2}" width="{x1 - x0}" height="14"/>'
            f'<text class="sub" x="{(x0 + x1) / 2}" y="{D + 21}" font-size="5.5">ונטה (גובה ~230)</text>')


def plan(parts, title):
    t = 10  # wall thickness
    s = [f'<svg class="plan" viewBox="-34 -26 284 412" role="img" aria-label="{title}">']
    s.append(f'<rect class="corr" x="{-t - 20}" y="{D + t}" width="{W + 2 * t + 20}" height="91"/>')
    s.append(f'<text class="sub" x="{W / 2 + 30}" y="{D + t + 80}" font-size="6.5">מסדרון (101)</text>')
    s.append(f'<rect class="wall" x="{-t}" y="{-t}" width="{W + 2 * t}" height="{D + 2 * t}"/>')
    s.append(f'<rect class="floor" x="0" y="0" width="{W}" height="{D}"/>')
    s.append(f'<rect class="floor" x="0" y="{D - 1}" width="80" height="{t + 2}"/>')  # door opening
    s.append(swing(0, -t, 80, -t, 0, -t - 80))  # door opens outward, into the corridor
    s.append(f'<text class="sub" x="44" y="{D + 30}" font-size="5.5">דלת 80, נפתחת החוצה</text>')
    s.extend(parts)
    s.append(dim(0, -16, W, -16, "214", room=False))
    s.append(dim(-22, 0, -22, D, "274", room=False))
    s.append("</svg>")
    return "".join(s)


# ---------- elevation (front view of one wall) ----------
def elev(length, parts, title, marks):
    s = [f'<svg class="elev" viewBox="-40 -14 {length + 52} {H + 30}" role="img" aria-label="{title}">']
    s.append(f'<rect class="floor" x="0" y="0" width="{length}" height="{H}"/>')
    s.append(f'<line class="ceil" x1="0" y1="0" x2="{length}" y2="0"/>')
    s.append(f'<line class="ground" x1="-6" y1="{H}" x2="{length + 6}" y2="{H}"/>')
    s.append(f'<line class="edge" x1="0" y1="0" x2="0" y2="{H}"/>'
             f'<line class="edge" x1="{length}" y1="0" x2="{length}" y2="{H}"/>')
    s.append(f'<text class="sub" x="{length / 2}" y="-5" font-size="6">תקרה {H}</text>')
    s.extend(parts)
    for z in marks:
        s.append(f'<line class="dim" x1="-8" y1="{H - z}" x2="-2" y2="{H - z}"/>'
                 f'<text class="dimt" x="-20" y="{H - z + 2}" font-size="6">{z}</text>')
    s.append("</svg>")
    return "".join(s)


def e(kind, a0, a1, z0, z1, text="", sub=None, port=False, size=8.5):
    X, Y, w, h = a0, H - z1, a1 - a0, z1 - z0
    s = f'<rect class="k-{kind}" x="{X}" y="{Y}" width="{w}" height="{h}" rx="0.8"/>'
    if port:
        cz = H - (z0 + 48)
        s += f'<circle class="port" cx="{X + w / 2}" cy="{cz}" r="17"/>'
        s += f'<circle class="portc" cx="{X + w / 2}" cy="{cz}" r="1.4"/>'
        s += label(X + w / 2, Y + 10, text, size=8) if text else ""
        if sub:
            s += f'<text class="sub" x="{X + w / 2}" y="{Y + h - 5}" font-size="6">{sub}</text>'
        return s
    if text:
        s += label(X + w / 2, Y + h / 2, text, sub, rotate=w < 40 and h > 1.8 * w, size=size)
    return s


def note(a, z, text, size=7):
    return f'<text class="sub" x="{a}" y="{H - z}" font-size="{size}">{text}</text>'


def plinth(a0, a1, z1=40):
    return e("store", a0, a1, 0, z1, "מגירת בסיס", size=5.5)


def baskets(a_starts, z0=6):
    return "".join(e("basket", a, a + 35, z0, z0 + 57, "סל", size=6) for a in a_starts)


def door_open(a0, a1):
    return (f'<rect class="opening" x="{a0}" y="{H - 210}" width="{a1 - a0}" height="210"/>'
            + label((a0 + a1) / 2, H - 105, "פתח הדלת", size=6))


def efan(a0, a1):
    return f'<rect class="fan" x="{a0}" y="{H - 240}" width="{a1 - a0}" height="20"/>' + note((a0 + a1) / 2, 243, "ונטה", 5.5)


# ---------- storage volumes ----------
def vol(rows):
    """rows: (name, (w, d, h), easy, minus_litres). Returns (html table, total, hard-to-reach total)."""
    out, total, hard = [], 0, 0
    for name, (w, d, h), easy, minus in rows:
        v = round(w * d * h / 1000 - minus)
        total += v
        hard += 0 if easy else v
        dims = f"{w}×{d}×{h}"
        pill = "" if easy else "<span class=pill>גישה פחות נוחה</span>"
        out.append(f'<tr><td>{name} <span class="mono dimsz">{dims}</span></td><td class="num">{v:,}</td><td>{pill}</td></tr>')
    html = (f'<table class="vol"><thead><tr><th>רכיב אחסון</th><th class="num">ליטר (ברוטו)</th><th></th></tr></thead>'
            f'<tbody>{"".join(out)}</tbody><tfoot><tr><td>סה״כ</td><td class="num">{total:,}</td><td></td></tr></tfoot></table>')
    return html, total, hard


UF = ("ארון עמוק מעל המקפיא", (62, 60, TOP - 165), False, 0)
LOFT_DOOR = ("בוידעם מעל הדלת", (95, 50, 30), False, 0)
A_vol = vol([("מגירות בבסיס המוגבה", (124, 65, 36), True, 0), ("ארון עליון מעל המכונות", (124, 40, TOP - 140), True, 0),
             ("ארון גבוה בפינה", (80, 68, TOP), True, 0), ("מגירות במשטח", (94, 48, 80), True, 0),
             ("ארונות עליונים מעל המשטח", (212, 35, TOP - 145), True, 0), UF, LOFT_DOOR])
B_vol = vol([("מגירות בבסיס המוגבה", (124, 65, 36), True, 0), ("ארון עליון מעל המכונות", (124, 40, TOP - 140), True, 0),
             ("שולף צר עד התקרה", (22, 68, TOP), True, 0), ("שולף מגשים במשטח", (15, 55, 80), True, 0),
             ("ארונות עליונים מעל המשטח", (134, 35, TOP - 145), True, 0), UF,
             ("בוידעם קיר שמאל", (202, 50, 30), False, 0), ("בוידעם קיר ימין", (142, 50, 30), False, 0)])
C_vol = vol([("ארונות עליונים מעל המשטח", (208, 35, TOP - 145), True, 0),
             ("ארונות גבוהים בקיר השמאלי (בניכוי תא הסל)", (214, 40, TOP), True, 96), UF, LOFT_DOOR])
D_vol = vol([("ארון מעל המגדל", (62, 60, TOP - 185), False, 0), ("שולף במשטח", (21, 60, 80), True, 0),
             ("ארונות עליונים מעל המשטח", (140, 35, TOP - 145), True, 0),
             ("ארונות גבוהים בקיר השמאלי", (214, 40, TOP), True, 0), UF, LOFT_DOOR])


E_vol = vol([("מגירות בבסיס המוגבה", (124, 65, 36), True, 0), ("ארון עליון מעל המכונות", (124, 40, TOP - 140), True, 0),
             ("שולף צר עד התקרה", (22, 68, TOP), True, 0), ("שולף מגשים במשטח", (11, 55, 80), True, 0),
             ("ארונות עליונים מעל המשטח הפעיל", (130, 35, TOP - 145), True, 0), ("ארון צר בקיר השמאלי", (30, 56, 215), True, 0),
             ("ארון עמוק מעל המקפיא", (66, 60, TOP - 165), False, 0),
             ("2 פינות עיוורות מתחת למשטח (72×58×80 כל אחת)", (144, 58, 80), False, 0),
             ("ארונות עליונים בפינות", (144, 35, TOP - 145), False, 0), ("בוידעם קיר שמאל", (126, 50, 30), False, 0)])


def approx(v):
    return f"≈{int(round(v / 50.0) * 50):,}"


# =============== Option A: galley ===============
A_plan = plan([
    zone(50, 68, 142, 192, "מעבר 92"),
    item("freezer", 142, 3, 214, 65, "מקפיא", "60×70 · 155"),
    swing(142, 65, 142, 5, 82, 65),
    item("machine", 142, 68, 214, 130, "כביסה", "מוגבהת 40", port=True),
    item("machine", 142, 130, 214, 192, "מייבש", "מוגבה 40", port=True),
    item("store", 142, 194, 214, 274, "ארון גבוה", "80×70 · עד התקרה"),
    item("counter", 0, 62, 50, 274),
    item("basket", 3, 65, 47, 100, "סל", size=6),
    item("basket", 3, 103, 47, 138, "סל", size=6),
    item("basket", 3, 141, 47, 176, "סל", size=6),
    item("store", 3, 179, 47, 271, "מגירות", size=6),
    f'<line class="flap" x1="52" y1="{ry(66)}" x2="52" y2="{ry(270)}"/>',
    item("loft", 0, 0, 95, 50, "בוידעם", "גובה 215+", size=5.5),
    fan(100, 120),
    dim(50, 182, 142, 182, "92"),
], "חלופה א׳ – תכנית")

A_e1 = elev(274, [
    e("store", 0, 80, 0, TOP, "ארון גבוה", "80×70"),
    plinth(82, 144), plinth(144, 206),
    e("machine", 82, 144, 40, 125, "מייבש", port=True),
    e("machine", 144, 206, 40, 125, "כביסה", port=True),
    e("store", 82, 206, 140, TOP, "ארון עליון (עומק 40)"),
    e("freezer", 209, 269, 0, 155, "מקפיא"),
    e("upper2", 209, 271, 165, TOP, "ארון עמוק", size=6),
    note(144, 62, "מרכז הפתח ≈88", 6.5),
], "חלופה א׳ – חזית הקיר הימני", [40, 88, 125, 140, 155, 245])

A_e2 = elev(274, [
    e("loft", 0, 50, 215, TOP, "בוידעם", size=5.5),
    e("counter", 62, 274, 87, 90),
    e("base", 62, 274, 0, 87),
    baskets([65, 103, 141]),
    e("store", 179, 274, 6, 84, "מגירות", size=6),
    e("store", 62, 274, 145, TOP, "ארונות עליונים (עומק 35)"),
    note(168, 95, "משטח 212 · גובה 90 · כנף מתקפלת 20"),
], "חלופה א׳ – חזית הקיר השמאלי", [57, 90, 145, 215, 245])

# =============== Option B: machines facing the door ===============
B_plan = plan([
    zone(0, 60, 214, 202, "שטח פנוי 142 × 214"),
    item("store", 0, 202, 22, 274, "שולף", size=6),
    item("machine", 22, 202, 84, 274, "כביסה", "מוגבהת 40", port=True),
    item("machine", 84, 202, 146, 274, "מייבש", "מוגבה 40", port=True),
    item("freezer", 149, 202, 214, 274, "מקפיא"),
    swing(150, 202, 210, 202, 150, 142),
    item("counter", 80, 0, 214, 60),
    item("basket", 83, 14, 118, 58, "סל", size=6),
    item("basket", 122, 14, 157, 58, "סל", size=6),
    item("basket", 161, 14, 196, 58, "סל", size=6),
    item("store", 199, 2, 213, 58, "מגשים", size=5),
    item("loft", 0, 0, 50, 202, "בוידעם", "גובה 215+", size=5.5),
    item("loft", 164, 60, 214, 202, "בוידעם", "גובה 215+", size=5.5),
    fan(55, 75),
    dim(40, 60, 40, 202, "142"),
], "חלופה ב׳ – תכנית")

B_e1 = elev(214, [
    e("store", 0, 22, 0, TOP, "שולף צר", size=6),
    plinth(22, 84), plinth(84, 146),
    e("machine", 22, 84, 40, 125, "כביסה", port=True),
    e("machine", 84, 146, 40, 125, "מייבש", port=True),
    e("store", 22, 146, 140, TOP, "ארון עליון"),
    e("freezer", 150, 210, 0, 155, "מקפיא"),
    e("upper2", 148, 214, 165, TOP, "ארון עמוק", size=6),
], "חלופה ב׳ – חזית הקיר האחורי", [40, 125, 140, 155, 245])

B_e2 = elev(214, [
    e("counter", 0, 134, 87, 90),
    e("base", 0, 134, 0, 87),
    baskets([18, 57, 96]),
    e("store", 1, 15, 6, 84, "מגשים", size=5),
    e("store", 0, 134, 145, TOP, "ארונות עליונים"),
    door_open(134, 214),
    efan(139, 159),
    e("loft", 164, 214, 215, TOP, "בוידעם", size=5.5),
], "חלופה ב׳ – חזית קיר הדלת", [57, 90, 145, 210, 245])

# =============== Option C: machines under a counter ===============
C_plan = plan([
    zone(40, 68, 142, 192, "מעבר 102"),
    item("freezer", 142, 3, 214, 65, "מקפיא"),
    swing(142, 65, 142, 5, 82, 65),
    item("machine", 142, 68, 214, 130, "כביסה", "על הרצפה", port=True),
    item("machine", 142, 130, 214, 192, "מייבש", "על הרצפה", port=True),
    item("counter", 142, 192, 214, 274),
    item("basket", 145, 195, 189, 230, "סל", size=6),
    item("basket", 145, 234, 189, 269, "סל", size=6),
    f'<line class="flap" x1="140" y1="{ry(68)}" x2="140" y2="{ry(272)}"/>',
    item("store", 0, 60, 40, 274, "ארונות גבוהים", "214×40 · כולל תא לסל 3"),
    item("loft", 0, 0, 95, 50, "בוידעם", "גובה 215+", size=5.5),
    fan(100, 120),
    dim(40, 182, 142, 182, "102"),
], "חלופה ג׳ – תכנית")

C_e1 = elev(274, [
    e("base", 0, 82, 0, 87),
    baskets([5, 44]),
    e("counter", 0, 208, 87, 90),
    e("machine", 83, 143, 0, 85, "מייבש", port=True),
    e("machine", 145, 205, 0, 85, "כביסה", port=True),
    e("store", 0, 208, 145, TOP, "ארונות עליונים"),
    e("freezer", 209, 269, 0, 155, "מקפיא"),
    e("upper2", 209, 271, 165, TOP, "ארון עמוק", size=6),
    note(104, 95, "משטח רציף 208 · גובה 90"),
], "חלופה ג׳ – חזית הקיר הימני", [48, 90, 145, 155, 245])


def left_tall(basket):
    parts = [e("loft", 0, 50, 215, TOP, "בוידעם", size=5.5),
             e("store", 60, 274, 70, TOP, "ארונות גבוהים · עומק 40")]
    if basket:
        parts += [e("store", 60, 274, 0, 68), e("basket", 62, 106, 6, 63, "סל 3", size=5.5),
                  e("store", 110, 274, 4, 66, "שואב · קרש גיהוץ · דליים", size=5.5)]
    else:
        parts += [e("store", 60, 274, 0, 68, "שואב · קרש גיהוץ · דליים", size=5.5)]
    return elev(274, parts, "חזית הקיר השמאלי – ארונות גבוהים", [68, 215, 245])


# =============== Option D: stacked tower ===============
D_plan = plan([
    zone(40, 68, 142, 132, "מעבר 102"),
    item("freezer", 142, 3, 214, 65, "מקפיא"),
    swing(142, 65, 142, 5, 82, 65),
    item("machine", 142, 68, 214, 132, "מגדל", "כביסה+מייבש", port=True),
    item("counter", 150, 134, 214, 274),
    item("basket", 153, 137, 197, 172, "סל", size=6),
    item("basket", 153, 176, 197, 211, "סל", size=6),
    item("basket", 153, 215, 197, 250, "סל", size=6),
    item("store", 153, 253, 197, 272, "שולף", size=5),
    item("store", 0, 60, 40, 274, "ארונות גבוהים", "214×40"),
    item("loft", 0, 0, 95, 50, "בוידעם", "גובה 215+", size=5.5),
    fan(100, 120),
    dim(40, 74, 142, 74, "102"),
], "חלופה ד׳ – תכנית")

D_e1 = elev(274, [
    e("base", 0, 140, 0, 87),
    baskets([24, 63, 102]),
    e("store", 1, 21, 6, 84, "שולף", size=5),
    e("counter", 0, 140, 87, 90),
    e("store", 0, 140, 145, TOP, "ארונות עליונים"),
    e("machine", 144, 204, 0, 85, "כביסה", port=True),
    e("machine", 144, 204, 87, 172, "מייבש", port=True),
    e("store", 142, 206, 185, TOP, "ארון", size=6),
    e("freezer", 209, 269, 0, 155, "מקפיא"),
    e("upper2", 209, 271, 165, TOP, "ארון עמוק", size=6),
], "חלופה ד׳ – חזית הקיר הימני", [85, 135, 172, 245])


# =============== Option E: B with the freezer on the door wall and a full right-wall unit ===============
E_plan = plan([
    zone(30, 72, 154, 202, "שטח פנוי 124 × 130"),
    item("store", 0, 202, 22, 274, "שולף", size=6),
    item("machine", 22, 202, 84, 274, "כביסה", "מוגבהת 40", port=True),
    item("machine", 84, 202, 146, 274, "מייבש", "מוגבה 40", port=True),
    item("freezer", 82, 2, 142, 72, "מקפיא", "60×70 · 155"),
    swing(82, 72, 142, 72, 82, 132),
    item("counter", 154, 0, 214, 274),
    item("upper2", 157, 3, 211, 69, "פינה עיוורת", "מכסה במשטח", size=6),
    item("upper2", 157, 205, 211, 271, "פינה עיוורת", "מכסה במשטח", size=6),
    item("basket", 156, 75, 200, 110, "סל", size=6),
    item("basket", 156, 114, 200, 149, "סל", size=6),
    item("basket", 156, 153, 200, 188, "סל", size=6),
    item("store", 156, 191, 211, 201),
    item("store", 0, 76, 30, 132, "ארון צר", size=5.5),
    item("loft", 0, 140, 50, 202, "בוידעם", "גובה 215+", size=5.5),
    fan(20, 40),
    dim(30, 92, 154, 92, "124"),
    dim(142, 72, 142, 202, "130"),
], "חלופה ה׳ – תכנית")

E_e1 = elev(274, [
    e("base", 0, 274, 0, 87),
    e("upper2", 2, 70, 4, 84, "פינה עיוורת", "מכסה במשטח", size=6),
    e("upper2", 204, 272, 4, 84, "פינה עיוורת", "מכסה במשטח", size=6),
    baskets([86, 125, 164]),
    e("store", 73, 83, 6, 84),
    e("counter", 0, 274, 87, 90),
    e("upper2", 0, 72, 145, TOP, "פינה", size=6),
    e("store", 72, 202, 145, TOP, "ארונות עליונים (עומק 35)"),
    e("upper2", 202, 274, 145, TOP, "פינה", size=6),
    note(137, 95, "משטח לכל אורך הקיר · גובה 90 · 130 ס״מ פעילים"),
], "חלופה ה׳ – חזית הקיר הימני", [57, 90, 145, 245])

E_e0 = elev(214, [
    e("store", 0, 22, 0, TOP, "שולף צר", size=6),
    plinth(22, 84), plinth(84, 146),
    e("machine", 22, 84, 40, 125, "כביסה", port=True),
    e("machine", 84, 146, 40, 125, "מייבש", port=True),
    e("store", 22, 146, 140, TOP, "ארון עליון (עומק 40)"),
    note(84, 62, "מרכז הפתח ≈88", 6.5),
    e("base", 154, 214, 0, 87), e("counter", 154, 214, 87, 90),
    e("upper2", 154, 214, 4, 84, "פינה עיוורת", "מכסה במשטח", size=5.5),
    e("upper2", 179, 214, 145, TOP, "פינה", size=5.5),
    note(184, 95, "קצה היחידה הימנית", 5.5),
], "חלופה ה׳ – חזית הקיר האחורי (המכונות)", [40, 88, 125, 140, 245])

E_e2 = elev(214, [
    e("base", 0, 60, 0, 87), e("counter", 0, 60, 87, 90),
    e("upper2", 0, 35, 145, TOP, "", size=6),
    e("freezer", 72, 132, 0, 155, "מקפיא"),
    e("upper2", 66, 132, 165, TOP, "ארון עמוק", size=6),
    door_open(134, 214),
    efan(174, 194),
], "חלופה ה׳ – חזית קיר הדלת", [87, 155, 210, 245])


# ---------- 3D scene data ----------
# Each entry: ["b", kind, x0, y0, z0, x1, y1, z1] (room coords, z = height) or
# ["port", face, cx, cy, cz] or ["person", x, y].
def B3(kind, x0, y0, z0, x1, y1, z1):
    return ["b", kind, x0, y0, z0, x1, y1, z1]


def cab(x0, y0, z0, x1, y1, z1, n=1, axis="y", kind="cab"):
    """Cabinet split into n door/drawer fronts along an axis, with small gaps."""
    lo, hi = {"x": (x0, x1), "y": (y0, y1), "z": (z0, z1)}[axis]
    step, g = (hi - lo) / n, 0.4
    out = []
    for i in range(n):
        a, b = lo + i * step + (g if i else 0), lo + (i + 1) * step
        c = {"x": (a, y0, z0, b, y1, z1), "y": (x0, a, z0, x1, b, z1), "z": (x0, y0, a, x1, y1, b)}[axis]
        out.append(B3(kind, c[0], c[1], c[2], c[3], c[4], c[5]))
    return out


def machine3(x0, y0, x1, y1, z0, h, face):
    """Front-loader. face 'x-': front at x0. face 'y-': front at y0."""
    z1 = z0 + h
    out = [B3("machine", x0, y0, z0, x1, y1, z1)]
    if face == "x-":
        out += [B3("panel", x0 - 0.6, y0 + 2, z1 - 12, x0, y1 - 2, z1 - 2), ["port", face, x0, (y0 + y1) / 2, z0 + 48]]
    else:
        out += [B3("panel", x0 + 2, y0 - 0.6, z1 - 12, x1 - 2, y0, z1 - 2), ["port", face, (x0 + x1) / 2, y0, z0 + 48]]
    return out


def freezer3(x0, y0, x1, y1, face, handle_at):
    out = [B3("freezer", x0, y0, 0, x1, y1, 155)]
    if face == "x-":
        out.append(B3("trim", x0 - 3, handle_at, 85, x0, handle_at + 2.5, 145))
    elif face == "y+":
        out.append(B3("trim", handle_at, y1, 85, handle_at + 2.5, y1 + 3, 145))
    else:
        out.append(B3("trim", handle_at, y0 - 3, 85, handle_at + 2.5, y0, 145))
    return out


def loft3(x0, y0, x1, y1, cases):
    out = [B3("loft", x0, y0, 213, x1, y1, 215)]
    out += [B3("suitcase", *c) for c in cases]
    return out


def fan3(x0, x1):
    return [B3("fan", x0, 0, 220, x1, 1.5, 240)]


SC_A = (
    freezer3(142, 5, 212, 65, "x-", 8)
    + cab(142, 68, 0, 214, 192, 40, 2, "y")
    + machine3(142, 69, 204, 129, 40, 85, "x-") + machine3(142, 132, 204, 191, 40, 85, "x-")
    + cab(174, 68, 140, 214, 192, TOP, 4, "y")
    + cab(152, 3, 165, 214, 65, TOP, 1)
    + cab(144, 194, 0, 214, 274, TOP, 2, "y")
    + [B3("counter", 0, 62, 87, 50, 274, 90), B3("counter", 50, 66, 67, 52, 270, 87)]
    + [B3("cab", 0, 62, 0, 48, 178, 6)]
    + [B3("cab", 0, a, 6, 48, a + 2, 87) for a in (62, 100.5, 139, 177)]
    + [B3("basket", 3, a, 6, 47, a + 35, 63) for a in (64.5, 103, 141.5)]
    + cab(0, 179, 0, 48, 274, 87, 3, "z")
    + cab(0, 62, 145, 35, 274, TOP, 5, "y")
    + loft3(0, 0, 95, 50, [(4, 6, 215, 58, 44, 238), (62, 8, 215, 92, 46, 233)])
    + fan3(100, 120)
    + [["person", 96, 112]]
)
SC_B = (
    cab(0, 202, 0, 22, 272, TOP, 1)
    + cab(22, 202, 0, 146, 274, 40, 2, "x")
    + machine3(23, 202, 83, 264, 40, 85, "y-") + machine3(85, 202, 145, 264, 40, 85, "y-")
    + freezer3(150, 202, 210, 272, "y-", 205)
    + cab(22, 234, 140, 146, 274, TOP, 4, "x")
    + cab(148, 212, 165, 214, 274, TOP, 1)
    + [B3("counter", 80, 0, 87, 214, 60, 90), B3("cab", 80, 0, 0, 199, 58, 6)]
    + [B3("cab", a, 0, 6, a + 2, 58, 87) for a in (80, 119.5, 158.5, 197)]
    + [B3("basket", a, 14, 6, a + 35, 58, 63) for a in (83, 122, 161)]
    + cab(199, 0, 0, 214, 58, 87, 1)
    + cab(80, 0, 145, 214, 35, TOP, 4, "x")
    + loft3(0, 0, 50, 202, [(5, 20, 215, 45, 75, 238), (5, 90, 215, 45, 140, 235)])
    + loft3(164, 60, 214, 202, [(168, 120, 215, 210, 175, 236)])
    + fan3(55, 75)
    + [["person", 100, 140]]
)
SC_C = (
    freezer3(142, 5, 212, 65, "x-", 8)
    + machine3(142, 69, 204, 129, 0, 85, "x-") + machine3(142, 132, 204, 191, 0, 85, "x-")
    + [B3("counter", 142, 66, 87, 214, 274, 90), B3("cab", 142, 192, 0, 214, 274, 6)]
    + [B3("cab", 142, a, 6, 214, a + 2, 87) for a in (192, 231.5, 271)]
    + [B3("basket", 145, a, 6, 189, a + 35, 63) for a in (195, 234)]
    + cab(179, 66, 145, 214, 274, TOP, 5, "y")
    + cab(152, 3, 165, 214, 65, TOP, 1)
    + cab(0, 60, 70, 40, 274, TOP, 5, "y")
    + [B3("cab", 0, 60, 0, 40, 110, 6), B3("cab", 0, 108, 6, 40, 110, 70)]
    + [B3("basket", 3, 62, 6, 38, 106, 63)]
    + cab(0, 110, 0, 40, 274, 68, 4, "y")
    + loft3(0, 0, 95, 50, [(4, 6, 215, 58, 44, 238)])
    + fan3(100, 120)
    + [["person", 92, 112]]
)
SC_D = (
    freezer3(142, 5, 212, 65, "x-", 8)
    + machine3(142, 70, 204, 130, 0, 85, "x-") + [B3("trim", 142, 70, 85, 204, 130, 87)]
    + machine3(142, 70, 204, 130, 87, 85, "x-")
    + cab(152, 68, 185, 214, 132, TOP, 1)
    + [B3("counter", 150, 134, 87, 214, 274, 90), B3("cab", 150, 134, 0, 214, 253, 6)]
    + [B3("cab", 150, a, 6, 214, a + 2, 87) for a in (134, 173, 212, 251)]
    + [B3("basket", 153, a, 6, 197, a + 35, 63) for a in (136.5, 175.5, 214.5)]
    + cab(150, 253, 0, 214, 274, 87, 1)
    + cab(179, 134, 145, 214, 274, TOP, 4, "y")
    + cab(152, 3, 165, 214, 65, TOP, 1)
    + cab(0, 60, 0, 40, 274, TOP, 5, "y")
    + loft3(0, 0, 95, 50, [(4, 6, 215, 58, 44, 238)])
    + fan3(100, 120)
    + [["person", 92, 100]]
)
SC_E = (
    cab(0, 202, 0, 22, 272, TOP, 1)
    + cab(22, 202, 0, 146, 274, 40, 2, "x")
    + machine3(23, 202, 83, 264, 40, 85, "y-") + machine3(85, 202, 145, 264, 40, 85, "y-")
    + cab(22, 234, 140, 146, 274, TOP, 4, "x")
    + freezer3(82, 2, 142, 72, "y+", 137)
    + cab(82, 0, 165, 148, 60, TOP, 1)
    + [B3("counter", 154, 0, 87, 214, 274, 90), B3("cab", 154, 0, 0, 214, 72, 87), B3("cab", 154, 202, 0, 214, 274, 87)]
    + [B3("cab", 154, 72, 0, 214, 191, 6)]
    + [B3("cab", 154, a, 6, 214, a + 2, 87) for a in (72, 111.5, 150.5)]
    + [B3("basket", 156, a, 6, 200, a + 35, 63) for a in (75, 114, 153)]
    + cab(154, 189.5, 0, 214, 202, 87, 1)
    + cab(179, 0, 145, 214, 274, TOP, 7, "y")
    + cab(0, 76, 0, 30, 132, 215, 1)
    + loft3(0, 140, 50, 202, [(5, 145, 215, 45, 198, 238)])
    + fan3(20, 40)
    + [["person", 100, 150]]
)
SCENES = json.dumps({"a": SC_A, "b": SC_B, "c": SC_C, "d": SC_D, "e": SC_E}, separators=(",", ":"))

LEGEND = "".join(
    f'<span class="lg"><svg viewBox="0 0 14 10" aria-hidden="true"><rect class="k-{k}" x="1" y="1" width="12" height="8" rx="1"/></svg>{t}</span>'
    for k, t in [("machine", "מכונות"), ("freezer", "מקפיא"), ("counter", "משטח קיפול"), ("basket", "סל כביסה"),
                 ("store", "אחסון"), ("loft", "בוידעם (גבוה, גישה פחות נוחה)"), ("zone", "אזור עבודה/מעבר פנוי")]
)


def option(oid, letter, name, tag, desc, drawings, pros, cons, volume, extra=""):
    fig = lambda c, svg: f'<figure><figcaption>{c}</figcaption><div class="scroll">{svg}</div></figure>'
    figs = fig(*drawings[0]) + '<div class="elevs">' + "".join(fig(*d) for d in drawings[1:]) + "</div>"
    li = lambda xs: "".join(f"<li>{x}</li>" for x in xs)
    return f'''
<section class="opt" id="{oid}">
  <header class="opt-h"><span class="letter">{letter}</span><div><h2>{name}</h2>{tag}</div></header>
  <p class="desc">{desc}</p>
  <div class="figs">{figs}</div>
  <div class="pc">
    <div><h3 class="pro">מעלות</h3><ul>{li(pros)}</ul></div>
    <div><h3 class="con">חסרונות</h3><ul>{li(cons)}</ul></div>
  </div>
  {extra}
  <p><a class="to3d" href="#view3d" data-opt="{oid}">לצפייה בהדמיה התלת-ממדית של חלופה {letter}׳</a></p>
  <details><summary>פירוט נפח האחסון</summary>{volume[0]}</details>
</section>'''


OPTS = "".join([
    option("e", "ה", "ב׳ משודרגת: מקפיא ליד הדלת וקיר ארונות ימני", '<span class="badge">מומלץ</span><span class="badge soft">ההצעה שלך</span>',
           "המכונות נשארות מוגבהות על הקיר האחורי, כמו בחלופה ב׳. המקפיא עובר לקיר הדלת, צמוד מימין לדלת, עם ציר בצד הקרוב לדלת. "
           "לאורך כל הקיר הימני (274) יש יחידה רציפה בעומק 60: ארון בסיס עם משטח בגובה 90, 3 סלים במרכז, ומעליה ארונות עליונים עד התקרה. "
           "בקיר השמאלי יש ארון צר לשואב, לקרש גיהוץ ולמטאטא, ומעליו בוידעם.",
           [("תכנית (מבט מלמעלה)", E_plan), ("חזית הקיר האחורי: המכונות המוגבהות", E_e0), ("חזית הקיר הימני: יחידה רציפה", E_e1), ("חזית קיר הדלת: מקפיא ודלת", E_e2)],
           ["מכונות מוגבהות זו לצד זו, ו-130 ס״מ פנויים מולן (בחלופה א׳ יש 92).",
            f"נפח האחסון הכולל ({approx(E_vol[1])} ליטר) כמו בחלופה א׳, ושתיהן מובילות.",
            "המקפיא ראשון בכניסה, ומי שבא רק להוציא משהו מהמקפיא לא נכנס לאזור העבודה.",
            "המייבש צמוד למשטח: מוציאים, מסתובבים רבע סיבוב ומקפלים לתוך הסל.",
            "שתי פינות עיוורות בגודל 72×58×80 מתאימות בדיוק למזוודות ולציוד עונתי."],
           [f"כ-{approx(E_vol[2])[1:]} ליטר מהאחסון בגישה פחות נוחה: פינות עיוורות, ארון מעל המקפיא ובוידעם. בחלופה א׳ יש כ-450 ליטר כאלה.",
            "קטע העבודה המלא של המשטח הוא 130 ס״מ (בחלופה א׳: 212). בקצוות יש עוד משטח להנחת דברים.",
            "דלת המקפיא הפתוחה חוסמת לרגע את המעבר מהכניסה.",
            "אין מקום לסל רביעי."],
           E_vol,
           '<div class="note"><b>למה יש פינות עיוורות?</b> המקפיא עומד 12 ס״מ מהיחידה הימנית, אז לפינה שמאחוריו אי אפשר לפתוח דלת מלפנים. '
           'בפינה האחורית המייבש צמוד ליחידה, ושם אותו מצב. הפתרון הוא חלק במשטח שמתרומם על צירים, כך שהפינה נפתחת מלמעלה כמו ארגז. '
           'זה מקום טוב למזוודות, לציוד חגים ולמלאי של חומרי ניקוי. בקיר השמאלי הארון הצר מתחיל רק 76 ס״מ מהדלת, כדי שלא ייווצר צוואר בקבוק מול המקפיא.</div>'),
    option("a", "א", "גלריה: מכונות מוגבהות מול משטח הקיפול", '<span class="badge soft">הכי הרבה אחסון נוח</span>',
           "לאורך הקיר הימני (274): המקפיא ראשון ליד הכניסה, אחריו מכונת הכביסה והמייבש על בסיס מוגבה 40 ס״מ עם מגירות, "
           "ובפינה האחורית ארון גבוה 80×70 עד התקרה. לאורך הקיר השמאלי: משטח קיפול 212×50 בגובה 90 עם כנף מתקפלת של 20 ס״מ "
           "(70 ס״מ עומק בזמן קיפול), 3 תאי סלים ומגירות מתחתיו. מעל: ארונות מעל המכונות, מעל המשטח ומעל המקפיא, ובוידעם מעל הדלת.",
           [("תכנית (מבט מלמעלה)", A_plan), ("חזית הקיר הימני: מקפיא, מכונות, ארון גבוה", A_e1),
            ("חזית הקיר השמאלי: משטח, סלים, ארונות", A_e2)],
           ["המכונות מוגבהות זו לצד זו, כפי שביקשת.",
            f"נפח האחסון הגדול ביותר מבין החלופות ({approx(A_vol[1])} ליטר), כולל ארון גבוה ועמוק לשואב אבק, קרש גיהוץ ומזוודה.",
            "זרימה קצרה: לוקחים סל, מסתובבים לכביסה, מעבירים למייבש, מסתובבים למשטח ומקפלים לתוך הסל.",
            "המקפיא ראשון בכניסה, כך שמי שבא להוציא משהו מהמקפיא לא נכנס לאזור העבודה.",
            "משטח 212 ס״מ, הרבה מעבר ל-120 הנדרשים. אפשר גם להוסיף סל רביעי במקום חלק מהמגירות.",
            "שום פריט לא חוסם פריט אחר."],
           ["מעבר של 92 ס״מ מול המכונות: עומד במינימום המקובל (90) אבל לא מרווח, ושני אנשים לא יעברו בו בנוחות.",
            "כשהכנף פתוחה המעבר יורד ל-72 ס״מ. זה בסדר בזמן קיפול, ומקפלים אותה בסיום.",
            "הארון שמעל המקפיא עמוק וגבוה, ומתאים רק לדברים שמוציאים לעיתים רחוקות.",
            "דורש נגרות בהתאמה: בסיס מוגבה יציב ומשטח עם תאי סלים."],
           A_vol,
           '<div class="note"><b>וריאנט א2: סלים מתחת למכונות.</b> בסיס בגובה 60 ס״מ ברוחב 124 מכיל 3 תאי סלים (כל תא 37 ס״מ). '
           'אבל אז מרכז פתח התוף עולה לכ-108 ס״מ, וזה גבוה מדי למשתמש בגובה 170. לכן הוא לא מומלץ אצלך.<br><b>טיפ:</b> ארגז הזנה וניקוז שקוע בקיר מאחורי המכונות חוסך 5–8 ס״מ עומק, '
           'והמעבר גדל ל-97–100 ס״מ.</div>'),
    option("b", "ב", "מול הדלת: מכונות על הקיר האחורי", '<span class="badge soft">הכי מרווח</span>',
           "על הקיר האחורי (214): שולף צר בפינה, מכונת כביסה ומייבש מוגבהים 40, ומקפיא בפינה הימנית. על קיר הדלת, מימין לדלת: "
           "משטח 134×60 עם 3 סלים ושולף מגשים. מעל המכונות והמשטח ארונות, ולאורך שני הקירות הארוכים בוידעם (מדף בעומק 50 בגובה 215 ומעלה).",
           [("תכנית (מבט מלמעלה)", B_plan), ("חזית הקיר האחורי", B_e1), ("חזית קיר הדלת", B_e2)],
           ["שטח פנוי של 142×214 ס״מ באמצע: הכי נוח לטעינה ולתנועה.",
            "מכונות מוגבהות זו לצד זו.",
            "משטח בעומק 60, הכי נוח לקיפול.",
            "המכונות גלויות מהכניסה וקל לשים לב כשמחזור מסתיים."],
           [f"נפח האחסון הנמוך ביותר ({approx(B_vol[1])} ליטר), וכשליש ממנו בבוידעם נמוך (30 ס״מ) מתחת לתקרה.",
            "הקירות הארוכים כמעט לא מנוצלים בגובה הרצפה.",
            "משטח 134 ס״מ, מעט מעל הדרישה.",
            "המקפיא בעומק החדר, וכל גישה אליו עוברת דרך אזור העבודה.",
            "הסלים יושבים ליד הכניסה, בצד הנגדי למכונות."],
           B_vol),
    option("c", "ג", "מכונות על הרצפה מתחת למשטח רציף", "",
           "לאורך הקיר הימני: המקפיא, ואחריו משטח רציף באורך 208 ס״מ בעומק 72 ובגובה 90. מתחתיו מכונת כביסה ומייבש, "
           "ובסוף תא לשני סלים. לאורך הקיר השמאלי ארונות גבוהים בעומק 40 עד התקרה, עם תא לסל שלישי בתחתית.",
           [("תכנית (מבט מלמעלה)", C_plan), ("חזית הקיר הימני", C_e1), ("חזית הקיר השמאלי", left_tall(True))],
           ["משטח העבודה הארוך ביותר: 208 ס״מ.",
            "מעבר של 102 ס״מ.",
            "פשוט וזול יותר: אין צורך בבסיס מוגבה.",
            "קיר שלם של ארונות גבוהים בעומק נוח (40)."],
           ["המכונות בגובה הרצפה, ולכן צריך להתכופף בכל טעינה ופריקה.",
            "מקפלים מעל מכונות שרועדות בזמן סחיטה.",
            "רק 2 סלים מתחת למשטח, והשלישי בארון שממול.",
            "בעומק 72 קשה להגיע לארונות העליונים."],
           C_vol),
    option("d", "ד", "מגדל: כביסה ומייבש זו מעל זו", "",
           "לאורך הקיר הימני: מקפיא, מגדל כביסה ומייבש ברוחב 64, ואחריו משטח 140×64 עם 3 סלים ושולף. "
           "לאורך הקיר השמאלי ארונות גבוהים בעומק 40.",
           [("תכנית (מבט מלמעלה)", D_plan), ("חזית הקיר הימני", D_e1), ("חזית הקיר השמאלי", left_tall(False))],
           ["3 סלים מתחת למשטח, ומשטח נפרד מהמכונות.",
            "מעבר של 102 ס״מ.",
            f"נפח אחסון טוב ({approx(D_vol[1])} ליטר)."],
           ["מכונת הכביסה על הרצפה (כפיפה), ופתח המייבש בגובה כ-135 ס״מ, כלומר פריקה בגובה החזה.",
            "צריך ערכת חיבור (stacking kit) ומכונות שמתאימות לה.",
            "הארון שמעל המגדל נמוך וגבוה מאוד."],
           D_vol),
])

v = {k: x for k, x in zip("eabcd", (E_vol, A_vol, B_vol, C_vol, D_vol))}
best = max(v, key=lambda k: v[k][1])
worst = min(v, key=lambda k: v[k][1])
VOL_ROW = "".join(f'<td class="num{" best" if k == best else " weak" if k == worst else ""}">{approx(v[k][1])} ל׳</td>' for k in "eabcd")
HARD_ROW = "".join(f'<td class="num">{approx(v[k][2])} ל׳</td>' for k in "eabcd")

VIEW3D = '''
  <section class="sheet" id="view3d">
    <h2>הדמיה תלת-ממדית</h2>
    <div class="v3-bar">
      <div class="seg" role="group" aria-label="חלופה">
        <button type="button" id="v3-e" data-opt="e" aria-pressed="true">ה׳ ב׳ משודרגת</button>
        <button type="button" id="v3-a" data-opt="a" aria-pressed="false">א׳ גלריה</button>
        <button type="button" id="v3-b" data-opt="b" aria-pressed="false">ב׳ מול הדלת</button>
        <button type="button" id="v3-c" data-opt="c" aria-pressed="false">ג׳ מתחת למשטח</button>
        <button type="button" id="v3-d" data-opt="d" aria-pressed="false">ד׳ מגדל</button>
      </div>
      <div class="seg" role="group" aria-label="זווית מבט">
        <button type="button" id="cam-door" data-cam="door">מהכניסה</button>
        <button type="button" id="cam-corner" data-cam="corner">מהצד</button>
        <button type="button" id="cam-top" data-cam="top">מלמעלה</button>
      </div>
      <label class="chk"><input type="checkbox" id="v3-person" checked> דמות בגובה 170</label>
      <label class="chk"><input type="checkbox" id="v3-upper"> הסתרת ארונות עליונים ובוידעם</label>
    </div>
    <div id="v3d" class="v3d" aria-label="הדמיה תלת-ממדית של החדר"><p class="v3-msg" id="v3-msg">טוען הדמיה…</p></div>
    <p class="hint">גוררים כדי לסובב, גלגלת או צביטה לזום, ושתי אצבעות או קליק ימני להזזה. הקירות שבין המצלמה לחדר מוסתרים, כמו בבית בובות. דלתות הארונות מסומנות בחלוקה בלבד.</p>
  </section>'''

JS3D = r'''
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
(function () {
  const SCENES = __SCENES__;
  const W = 214, D = 274, H = 247;
  const box = document.getElementById('v3d');
  const msg = document.getElementById('v3-msg');
  if (!window.THREE || !THREE.OrbitControls) { msg.textContent = 'ההדמיה לא נטענה. נסו לרענן את הדף.'; return; }
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ antialias: true }); }
  catch (err) { msg.textContent = 'הדפדפן הזה לא תומך בהדמיה תלת-ממדית (WebGL).'; return; }
  msg.remove();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputEncoding = THREE.sRGBEncoding;
  box.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 4 / 3, 5, 4000);
  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI / 2 - 0.02;
  controls.minDistance = 100;
  controls.maxDistance = 1100;

  // room coords (x across, y into the room from the door wall, z up) -> three (X, Y up, Z toward the door)
  const P = (x, y, z) => new THREE.Vector3(x - W / 2, z, D / 2 - y);

  scene.add(new THREE.HemisphereLight(0xffffff, 0xcab89a, 0.72));
  const sun = new THREE.DirectionalLight(0xffffff, 0.6);
  sun.position.set(-160, 520, 260);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -260, right: 260, top: 260, bottom: -260, near: 10, far: 1600 });
  sun.shadow.bias = -0.0006;
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0xfff3e2, 0.25);
  fill.position.set(300, 200, -200);
  scene.add(fill);

  function rand(seed) { return function () { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }; }
  function plankTexture() {
    const c = document.createElement('canvas'); c.width = 512; c.height = 512;
    const g = c.getContext('2d'), r = rand(7);
    g.fillStyle = '#b48a5c'; g.fillRect(0, 0, 512, 512);
    for (let row = 0; row < 8; row++) {
      let x = -r() * 200;
      while (x < 512) {
        const w = 180 + r() * 160, s = 0.88 + r() * 0.18;
        g.fillStyle = 'rgb(' + (205 * s | 0) + ',' + (167 * s | 0) + ',' + (122 * s | 0) + ')';
        g.fillRect(x + 1, row * 64 + 1, w - 2, 62);
        x += w;
      }
    }
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(W / 150, D / 150);
    t.encoding = THREE.sRGBEncoding;
    return t;
  }

  const COL = { machine: 0xf4f5f6, panel: 0xd5dade, trim: 0x8b949c, freezer: 0xe8ecef, counter: 0xc8996a,
    cab: 0xe4e6dc, basket: 0xd2ad78, loft: 0xd9d6cc, suitcase: 0x51627a, fan: 0xc4c9cc };
  const mats = {};
  const mat = k => mats[k] || (mats[k] = new THREE.MeshStandardMaterial({ color: COL[k], roughness: k === 'counter' ? 0.55 : 0.8, metalness: 0.02 }));
  const edgeMat = new THREE.LineBasicMaterial({ color: 0x3a403c, transparent: true, opacity: 0.32 });

  // static shell: floor, inward-facing walls (culled when the camera is behind them), corridor, open door
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(W, D), new THREE.MeshStandardMaterial({ map: plankTexture(), roughness: 0.75 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  const corr = new THREE.Mesh(new THREE.PlaneGeometry(300, 101), new THREE.MeshStandardMaterial({ color: 0xcfc9bd, roughness: 0.9 }));
  corr.rotation.x = -Math.PI / 2; corr.position.set(-20, -0.2, D / 2 + 10 + 50.5); corr.receiveShadow = true; scene.add(corr);
  const wallMat = new THREE.MeshStandardMaterial({ color: 0xf2f0ea, roughness: 0.95, side: THREE.FrontSide });
  function wall(w, h, pos, rotY) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMat);
    m.position.copy(pos); m.rotation.y = rotY; m.receiveShadow = true; scene.add(m);
  }
  wall(W, H, new THREE.Vector3(0, H / 2, -D / 2), 0);
  wall(D, H, new THREE.Vector3(-W / 2, H / 2, 0), Math.PI / 2);
  wall(D, H, new THREE.Vector3(W / 2, H / 2, 0), -Math.PI / 2);
  wall(W - 80, H, new THREE.Vector3(-W / 2 + 80 + (W - 80) / 2, H / 2, D / 2), Math.PI);
  wall(80, H - 210, new THREE.Vector3(-W / 2 + 40, 210 + (H - 210) / 2, D / 2), Math.PI);
  // wall tops as a thin outline so the room reads even where walls are hidden
  const outline = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(W + 20, 0.1, D + 20)),
    new THREE.LineBasicMaterial({ color: 0x6f7570 }));
  outline.position.set(0, 0.2, 0); scene.add(outline);

  function boxMesh(kind, x0, y0, z0, x1, y1, z1) {
    const g = new THREE.BoxGeometry(x1 - x0, z1 - z0, y1 - y0);
    const m = new THREE.Mesh(g, mat(kind));
    m.position.copy(P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2));
    m.castShadow = kind !== 'loft'; m.receiveShadow = true;
    if (kind !== 'panel' && kind !== 'trim') m.add(new THREE.LineSegments(new THREE.EdgesGeometry(g), edgeMat));
    return m;
  }
  const ringMat = new THREE.MeshStandardMaterial({ color: 0x7c8690, roughness: 0.35, metalness: 0.4 });
  const glassMat = new THREE.MeshStandardMaterial({ color: 0x24313d, roughness: 0.15, metalness: 0.1 });
  function port(face, cx, cy, cz) {
    const g = new THREE.Group();
    const ring = new THREE.Mesh(new THREE.TorusGeometry(17, 2.6, 12, 40), ringMat);
    const glass = new THREE.Mesh(new THREE.CircleGeometry(15.5, 40), glassMat);
    g.add(ring, glass);
    g.position.copy(P(cx, cy, cz));
    if (face === 'x-') { g.rotation.y = -Math.PI / 2; g.position.x -= 1.2; } else { g.position.z += 1.2; }
    return g;
  }
  const personMat = new THREE.MeshStandardMaterial({ color: 0x8e9b97, roughness: 0.9, transparent: true, opacity: 0.6 });
  function person(x, y) {
    const g = new THREE.Group();
    const body = new THREE.Mesh(new THREE.CylinderGeometry(15, 13, 142, 24), personMat);
    body.position.y = 71;
    const head = new THREE.Mesh(new THREE.SphereGeometry(12, 24, 16), personMat);
    head.position.y = 158;
    g.add(body, head); g.position.copy(P(x, y, 0));
    g.traverse(o => { o.castShadow = true; });
    return g;
  }

  let group = null, personObj = null, current = 'e';
  const personToggle = document.getElementById('v3-person');
  const hideUpper = document.getElementById('v3-upper');
  function build(opt) {
    if (group) {
      scene.remove(group);
      group.traverse(o => { if (o.geometry) o.geometry.dispose(); });
    }
    group = new THREE.Group(); personObj = null;
    for (const it of SCENES[opt]) {
      if (it[0] === 'b') {
        const m = boxMesh(it[1], it[2], it[3], it[4], it[5], it[6], it[7]);
        if (it[4] >= 135) { m.userData.upper = true; m.visible = !hideUpper.checked; }
        group.add(m);
      }
      else if (it[0] === 'port') group.add(port(it[1], it[2], it[3], it[4]));
      else if (it[0] === 'person') { personObj = person(it[1], it[2]); personObj.visible = personToggle.checked; group.add(personObj); }
    }
    scene.add(group);
    current = opt;
    document.querySelectorAll('#view3d [data-opt]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.opt === opt)));
  }

  const CAMS = {
    door: [[-90, 240, 440], [15, 90, -20]],
    corner: [[-320, 300, 320], [25, 80, -15]],
    top: [[0, 640, 40], [0, 0, 0]],
  };
  function setCam(name) {
    const [p, t] = CAMS[name];
    camera.position.set(p[0], p[1], p[2]); controls.target.set(t[0], t[1], t[2]); controls.update();
  }

  function themeBg() {
    const v = getComputedStyle(document.documentElement).getPropertyValue('--paper').trim() || '#ffffff';
    renderer.setClearColor(new THREE.Color(v));
  }
  themeBg();
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', themeBg);
  new MutationObserver(themeBg).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  function resize() {
    const w = box.clientWidth, h = box.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    renderer.domElement.style.width = '100%'; renderer.domElement.style.height = '100%';
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(box);
  resize();

  document.querySelectorAll('#view3d [data-opt]').forEach(b => b.addEventListener('click', () => build(b.dataset.opt)));
  document.querySelectorAll('#view3d [data-cam]').forEach(b => b.addEventListener('click', () => setCam(b.dataset.cam)));
  document.querySelectorAll('a.to3d').forEach(a => a.addEventListener('click', () => build(a.dataset.opt)));
  personToggle.addEventListener('change', () => { if (personObj) personObj.visible = personToggle.checked; });
  hideUpper.addEventListener('change', () => group.children.forEach(m => { if (m.userData.upper) m.visible = !hideUpper.checked; }));

  build('e'); setCam('door');
  (function loop() { controls.update(); renderer.render(scene, camera); requestAnimationFrame(loop); })();
})();
</script>'''.replace("__SCENES__", SCENES)

PAGE = f'''<title>תכנון חדר הכביסה</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700&family=Frank+Ruhl+Libre:wght@500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a single reading column of architect's sheets; each option = plan + elevations + verdict */
:root {{
  --bg: #F3F4F1; --paper: #FFFFFF; --fg: #1D2220; --muted: #5C6560; --line: #D5DAD5;
  --accent: #2F6F68; --accent-soft: #DCEBE7; --pro: #2F7A4C; --con: #A2452E;
  --wall: #8C918D; --floor: #FBFAF6; --corr: #ECEDE9;
  --machine: #4E6A8C; --machine-f: #DCE5F0; --freezer: #2F8496; --freezer-f: #D4ECF0;
  --counter: #A87A45; --counter-f: #EBD8BC; --basket: #9A6A2D; --basket-f: #F7E7C8;
  --store: #6B8A5C; --store-f: #E1EAD9; --loft: #8A8F7A; --loft-f: #EEEFE6;
  --zone: #C2563B; --zone-f: rgba(194,86,59,.07); --fan: #6E5AA8;
  --display: "Frank Ruhl Libre", "David", Georgia, serif;
  --body: "Assistant", "Segoe UI", Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #141816; --paper: #1C211F; --fg: #E5E9E6; --muted: #9AA39E; --line: #313834;
  --accent: #7CC2B8; --accent-soft: #23403C; --pro: #7FCB98; --con: #EE9A84;
  --wall: #5D635F; --floor: #222826; --corr: #1A1E1C;
  --machine: #9DB6D6; --machine-f: #2A3546; --freezer: #7CC7D6; --freezer-f: #1F3A40;
  --counter: #D7AE7C; --counter-f: #4A3A26; --basket: #E0B677; --basket-f: #5A4422;
  --store: #A6C394; --store-f: #2A3A25; --loft: #B5B9A3; --loft-f: #30332A;
  --zone: #F08A6E; --zone-f: rgba(240,138,110,.08); --fan: #B5A4EE; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #141816; --paper: #1C211F; --fg: #E5E9E6; --muted: #9AA39E; --line: #313834;
  --accent: #7CC2B8; --accent-soft: #23403C; --pro: #7FCB98; --con: #EE9A84;
  --wall: #5D635F; --floor: #222826; --corr: #1A1E1C;
  --machine: #9DB6D6; --machine-f: #2A3546; --freezer: #7CC7D6; --freezer-f: #1F3A40;
  --counter: #D7AE7C; --counter-f: #4A3A26; --basket: #E0B677; --basket-f: #5A4422;
  --store: #A6C394; --store-f: #2A3A25; --loft: #B5B9A3; --loft-f: #30332A;
  --zone: #F08A6E; --zone-f: rgba(240,138,110,.08); --fan: #B5A4EE; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 17px; line-height: 1.6;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 64px; }}
main {{ max-width: 1080px; margin: 0 auto; display: grid; gap: 28px; }}
h1, h2 {{ font-family: var(--display); text-wrap: balance; line-height: 1.2; margin: 0; }}
h1 {{ font-size: clamp(30px, 5vw, 44px); }}
h2 {{ font-size: clamp(22px, 3vw, 28px); }}
h3 {{ font-size: 16px; margin: 0 0 6px; letter-spacing: .02em; }}
p {{ margin: 0; max-width: 72ch; }}
.lede {{ color: var(--muted); font-size: 18px; }}
.num, .mono {{ font-family: var(--mono); font-variant-numeric: tabular-nums; }}
.dimsz {{ color: var(--muted); font-size: 13px; }}
nav {{ display: flex; flex-wrap: wrap; gap: 8px; }}
nav a {{ color: var(--fg); text-decoration: none; border: 1px solid var(--line); background: var(--paper); padding: 6px 12px; border-radius: 999px; font-size: 15px; }}
nav a:hover, nav a:focus-visible {{ border-color: var(--accent); outline: none; }}
.rec {{ background: var(--accent-soft); border-inline-start: 4px solid var(--accent); padding: 16px 18px; border-radius: 4px; }}
.rec b {{ color: var(--accent); }}
.sheet {{ background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 22px; display: grid; gap: 14px; min-width: 0; scroll-margin-top: 12px; }}
.grid2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px 28px; }}
.grid2 > * {{ min-width: 0; }}
dl {{ margin: 0; display: grid; gap: 8px; }}
dt {{ font-weight: 700; }}
dd {{ margin: 0; color: var(--muted); }}
table {{ border-collapse: collapse; width: 100%; font-size: 15px; }}
th, td {{ text-align: start; padding: 7px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-weight: 700; color: var(--muted); font-size: 13px; letter-spacing: .03em; }}
td.num, th.num {{ text-align: end; }}
tfoot td {{ font-weight: 700; border-bottom: none; }}
tr.you td {{ background: var(--accent-soft); }}
.scroll {{ overflow-x: auto; }}
.opt {{ background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 22px; display: grid; gap: 16px; min-width: 0; scroll-margin-top: 12px; }}
.opt-h {{ display: flex; gap: 14px; align-items: center; }}
.opt-h > div {{ display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; }}
.letter {{ font-family: var(--display); font-weight: 700; font-size: 26px; width: 46px; height: 46px; flex: none; display: grid; place-items: center; border: 2px solid var(--fg); border-radius: 50%; }}
.badge {{ background: var(--accent); color: var(--paper); font-size: 13px; font-weight: 700; padding: 2px 10px; border-radius: 999px; }}
.badge.soft {{ background: var(--accent-soft); color: var(--accent); }}
.figs {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 22px; align-items: start; }}
.elevs {{ display: grid; gap: 18px; min-width: 0; }}
@media (max-width: 760px) {{ .figs {{ grid-template-columns: 1fr; }} }}
figure {{ margin: 0; min-width: 0; }}
figcaption {{ font-size: 13px; color: var(--muted); margin-bottom: 4px; font-weight: 600; letter-spacing: .02em; }}
svg.plan {{ width: 100%; max-width: 500px; min-width: 260px; margin-inline: auto; display: block; direction: ltr; }}
svg.elev {{ width: 100%; min-width: 300px; display: block; direction: ltr; }}
.pc {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 8px 28px; }}
.pc ul {{ margin: 0; padding-inline-start: 20px; display: grid; gap: 4px; }}
.pro {{ color: var(--pro); }} .con {{ color: var(--con); }}
.note {{ background: var(--bg); border: 1px dashed var(--line); padding: 12px 14px; border-radius: 4px; font-size: 15.5px; }}
a.to3d, .src a {{ color: var(--accent); }}
details summary {{ cursor: pointer; color: var(--accent); font-weight: 600; }}
details[open] summary {{ margin-bottom: 8px; }}
.pill {{ font-size: 12px; background: var(--loft-f); color: var(--fg); border: 1px solid var(--loft); padding: 1px 8px; border-radius: 999px; white-space: nowrap; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 14px; color: var(--muted); }}
.lg {{ display: inline-flex; align-items: center; gap: 6px; }}
.lg svg {{ width: 20px; height: 14px; }}
.cmp td:first-child {{ font-weight: 600; white-space: nowrap; }}
.cmp .best {{ color: var(--pro); font-weight: 700; }}
.cmp .weak {{ color: var(--con); }}
.src {{ font-size: 14px; color: var(--muted); }}
/* 3D viewer */
.v3-bar {{ display: flex; flex-wrap: wrap; gap: 10px 16px; align-items: center; }}
.seg {{ display: inline-flex; flex-wrap: wrap; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
.seg button {{ font: inherit; font-size: 15px; background: var(--paper); color: var(--fg); border: 0; border-inline-start: 1px solid var(--line); padding: 6px 12px; cursor: pointer; }}
.seg button:first-child {{ border-inline-start: 0; }}
.seg button[aria-pressed="true"] {{ background: var(--accent); color: var(--paper); font-weight: 700; }}
.seg button:focus-visible, .chk input:focus-visible {{ outline: 2px solid var(--accent); outline-offset: -2px; }}
.chk {{ display: inline-flex; gap: 6px; align-items: center; font-size: 15px; color: var(--muted); }}
.v3d {{ position: relative; width: 100%; aspect-ratio: 4 / 3; max-height: 640px; max-width: 100%; border: 1px solid var(--line); border-radius: 6px; overflow: hidden; background: var(--paper); touch-action: none; }}
.v3d canvas {{ display: block; }}
.v3-msg {{ position: absolute; inset: 0; display: grid; place-items: center; color: var(--muted); }}
.hint {{ font-size: 14px; color: var(--muted); }}
/* SVG drawing classes (units are cm) */
.wall {{ fill: var(--wall); }} .floor {{ fill: var(--floor); }} .corr {{ fill: var(--corr); }}
.k-machine {{ fill: var(--machine-f); stroke: var(--machine); stroke-width: .9; }}
.k-freezer {{ fill: var(--freezer-f); stroke: var(--freezer); stroke-width: .9; }}
.k-counter {{ fill: var(--counter-f); stroke: var(--counter); stroke-width: .9; }}
.k-base {{ fill: var(--counter-f); stroke: var(--counter); stroke-width: .6; opacity: .55; }}
.k-basket {{ fill: var(--basket-f); stroke: var(--basket); stroke-width: .7; }}
.k-store {{ fill: var(--store-f); stroke: var(--store); stroke-width: .8; }}
.k-upper2 {{ fill: var(--loft-f); stroke: var(--loft); stroke-width: .8; }}
.k-loft {{ fill: var(--loft-f); stroke: var(--loft); stroke-width: .8; stroke-dasharray: 2 1.5; fill-opacity: .85; }}
.k-zone {{ fill: var(--zone-f); stroke: var(--zone); stroke-width: .8; stroke-dasharray: 2 1.5; }}
.fan {{ fill: var(--fan); }}
.zone {{ fill: var(--zone-f); stroke: var(--zone); stroke-width: .6; stroke-dasharray: 2.5 2; }}
.zlbl {{ fill: var(--zone); font-family: var(--body); font-weight: 700; text-anchor: middle; }}
.port {{ fill: none; stroke: var(--machine); stroke-width: .7; }}
.portc {{ fill: var(--machine); }}
.arc {{ fill: none; stroke: var(--muted); stroke-width: .5; stroke-dasharray: 1.5 1.2; }}
.leaf {{ stroke: var(--fg); stroke-width: 1.6; }}
.flap {{ stroke: var(--counter); stroke-width: .8; stroke-dasharray: 3 1.5; }}
.opening {{ fill: var(--bg); stroke: var(--muted); stroke-width: .5; stroke-dasharray: 2 1.5; }}
.dim {{ stroke: var(--muted); stroke-width: .45; }}
.lbl, .sub, .zlbl {{ direction: rtl; unicode-bidi: plaintext; }}
.dimt {{ direction: rtl; unicode-bidi: plaintext; fill: var(--muted); font-family: var(--mono); font-size: 7.5px; text-anchor: middle; }}
.lbl {{ fill: var(--fg); font-family: var(--body); font-weight: 700; text-anchor: middle; }}
.sub {{ fill: var(--muted); font-family: var(--body); text-anchor: middle; }}
.ceil {{ stroke: var(--muted); stroke-width: .5; stroke-dasharray: 3 2; }}
.ground {{ stroke: var(--fg); stroke-width: 1.4; }}
.edge {{ stroke: var(--line); stroke-width: .6; }}
@media (max-width: 520px) {{ .sheet, .opt {{ padding: 16px; }} body {{ font-size: 16px; }} .v3d {{ aspect-ratio: 3 / 4; }} }}
</style>

<main dir="rtl" lang="he">
  <header style="display:grid;gap:10px">
    <h1>תכנון חדר הכביסה</h1>
    <p class="lede">חדר נטו <span class="mono">214×274</span> ס״מ (5.86 מ״ר), תקרה <span class="mono">247</span>. חמש חלופות סידור, כולן משורטטות בקנה מידה ומוצגות גם בהדמיה תלת-ממדית, עם מעלות, חסרונות ונפח אחסון.</p>
  </header>

  <div class="rec"><p><b>ההמלצה: חלופה ה׳ (ב׳ משודרגת, ההצעה שלך).</b> המכונות מוגבהות על הקיר האחורי עם 130 ס״מ פנויים מולן. המקפיא מימין לדלת, ולאורך כל הקיר הימני יש יחידה רציפה של משטח, 3 סלים וארונות עד התקרה.
  נפח האחסון הכולל ({approx(E_vol[1])} ליטר) זהה כמעט לחלופה א׳, ושתיהן מובילות. חלק גדול ממנו בפינות שהגישה אליהן פחות נוחה, וזה מתאים למזוודות ולציוד עונתי.
  אם חשוב לך יותר אחסון בגישה נוחה ומשטח ארוך יותר, ומוכן לוותר על מרווח, חלופה א׳ עדיפה.</p></div>

  <nav aria-label="תוכן"><a href="#view3d">הדמיה תלת-ממדית</a><a href="#basis">נתונים</a><a href="#height">גובה ההגבהה</a><a href="#e">ה׳ ב׳ משודרגת</a><a href="#a">א׳ גלריה</a><a href="#b">ב׳ מול הדלת</a><a href="#c">ג׳ מתחת למשטח</a><a href="#d">ד׳ מגדל</a><a href="#compare">השוואה</a><a href="#build">ביצוע</a></nav>

  {VIEW3D}

  <section class="sheet" id="basis">
    <h2>נתונים ומידות עבודה</h2>
    <div class="grid2">
      <dl>
        <div><dt>החדר</dt><dd>214 (רוחב) × 274 (עומק) נטו, תקרה 247. ארונות עליונים מגיעים עד 245, ובוידעם מעל הדלת הוא בגובה 215–245 (30 ס״מ, מספיק למזוודה שוכבת).</dd></div>
        <div><dt>הדלת</dt><dd>80 ס״מ בפינה השמאלית של הקיר הקצר, <b>נפתחת החוצה</b> למסדרון. כך כל השטח שבפנים נשאר לשימוש, והמשטח (בחלופה א׳) או הארונות הגבוהים (ג׳, ד׳) מתחילים כבר 60 ס״מ מהדלת. דלת הזזה לא נדרשת: היא רק תמנע את חסימת המסדרון כשהדלת פתוחה.</dd></div>
        <div><dt>אוורור</dt><dd>אין חלון ואין קיר חיצוני. ונטה גבוה בקיר הדלת, עם יציאה למסדרון, מסומן בכל התכניות. מיקומו נבחר כך שלא יתנגש בבוידעם ובארונות.</dd></div>
      </dl>
      <dl>
        <div><dt>מכונות</dt><dd>רוחב 60, עומק עד 62, גובה 85, ועוד 8–10 ס״מ מאחור לצנרת. עומק הנישה 72, ו-2 ס״מ בין המכונות.</dd></div>
        <div><dt>מקפיא Beko (מידות סטנדרטיות)</dt><dd>60×70×155, ועוד כ-3 ס״מ אוורור מכל צד ומאחור ו-10 ס״מ מעליו. <b>הציר בצד הרחוק מהקיר</b>, כדי שהדלת תיפתח מעבר ל-90° והמגירות ייצאו עד הסוף. ברוב הדגמים אפשר להפוך את כיוון הדלת.</dd></div>
        <div><dt>סלים ומרווחים</dt><dd>סלים 35×44, גובה 57, כל סל בתא ברוחב 37 על מסילות. מול מכונה עם דלת פתוחה צריך 90 ס״מ לפחות, ו-100 ומעלה נוח. משטח הקיפול בגובה 90.</dd></div>
      </dl>
    </div>
    <div class="legend">{LEGEND}<span class="lg"><svg viewBox="0 0 14 10" aria-hidden="true"><rect class="fan" x="1" y="3" width="12" height="4"/></svg>ונטה</span></div>
  </section>

  <section class="sheet" id="height">
    <h2>גובה ההגבהה: 40 ס״מ</h2>
    <p>המטרה היא להגיע לתחתית התוף עם כיפוף קל של המרפק, בלי להתכופף בגב. במכונה פתח-חזית רגילה בגובה 85, מרכז הפתח נמצא כ-48 ס״מ מעל בסיס המכונה.
    גובה המרפק הוא בערך 63% מגובה האדם, ונוח כשמרכז הפתח נמצא כ-15–20 ס״מ מתחת למרפק. בסיסים של יצרנים נעים בדרך כלל בין 30 ל-40 ס״מ, וזה מתיישב עם החישוב.</p>
    <div class="scroll"><table>
      <thead><tr><th>גובה המשתמש</th><th class="num">גובה מרפק</th><th class="num">הגבהה מומלצת</th><th class="num">מרכז הפתח</th><th class="num">ראש המכונה</th></tr></thead>
      <tbody>
        <tr><td>155–165</td><td class="num">98–104</td><td class="num">30–35</td><td class="num">≈80–85</td><td class="num">115–120</td></tr>
        <tr class="you"><td><b>170 (אתה)</b></td><td class="num">≈107</td><td class="num"><b>40</b></td><td class="num">≈88</td><td class="num">125</td></tr>
        <tr><td>178–190</td><td class="num">112–120</td><td class="num">45–50</td><td class="num">≈95–100</td><td class="num">130–135</td></tr>
      </tbody></table></div>
    <p>בבסיס של 40 נכנסת מגירה עם כ-30 ס״מ גובה פנימי לאבקות ולמרככים. הארון שמעל המכונות מתחיל ב-140 ומגיע עד 245.
    הבסיס צריך להיות מבנה קשיח (בנוי או שלד מחוזק) והמכונות צריכות להיות מקובעות אליו, כי מכונה מוגבהת רועדת יותר בסחיטה.</p>
  </section>

  {OPTS}

  <section class="sheet" id="compare">
    <h2>השוואה</h2>
    <div class="scroll"><table class="cmp">
      <thead><tr><th></th><th>ה׳ ב׳ משודרגת</th><th>א׳ גלריה</th><th>ב׳ מול הדלת</th><th>ג׳ מתחת למשטח</th><th>ד׳ מגדל</th></tr></thead>
      <tbody>
        <tr><td>סידור המכונות</td><td class="best">מוגבהות זו לצד זו</td><td class="best">מוגבהות זו לצד זו</td><td class="best">מוגבהות זו לצד זו</td><td class="weak">על הרצפה</td><td class="weak">זו מעל זו</td></tr>
        <tr><td>מרווח מול המכונות</td><td class="num">130</td><td class="num">92</td><td class="num best">142</td><td class="num">102</td><td class="num">102</td></tr>
        <tr><td>משטח קיפול</td><td class="num">130×60 + קצוות</td><td class="num">212×50 (+20)</td><td class="num">134×60</td><td class="num best">208×72</td><td class="num">140×64</td></tr>
        <tr><td>סלים במקום ייעודי</td><td>3</td><td>3, אפשר 4</td><td>3</td><td>2+1 בארון</td><td>3</td></tr>
        <tr><td>נפח אחסון משוער</td>{VOL_ROW}</tr>
        <tr><td>מתוכו בגישה פחות נוחה</td>{HARD_ROW}</tr>
        <tr><td>תחושת מרחב</td><td class="best">גבוהה</td><td>בינונית</td><td class="best">גבוהה</td><td>טובה</td><td>טובה</td></tr>
        <tr><td>מורכבות ועלות נגרות</td><td>בינונית-גבוהה</td><td>בינונית-גבוהה</td><td>בינונית</td><td class="best">נמוכה</td><td>בינונית</td></tr>
      </tbody></table></div>
    <p class="src">הנפחים הם ברוטו (מידות חוץ של הארונות), ומיועדים להשוואה בין החלופות. הנפח השימושי יהיה קטן בכ-15–20%.</p>
  </section>

  <section class="sheet" id="build">
    <h2>המלצות ביצוע (החדר בשלב בנייה)</h2>
    <div class="grid2">
      <dl>
        <div><dt>מים וניקוז</dt><dd>ארגז הזנה וניקוז שקוע בקיר מאחורי המכונות, בגובה של כ-100 (מאחורי המכונה המוגבהת). הוא חוסך עומק, וגם המעבר גדל. מומלץ מחסום רצפה ליד המכונות למקרה של נזילה, וניקוז מי העיבוי של המייבש לאותו ארגז.</dd></div>
        <div><dt>חשמל</dt><dd>שקע נפרד לכל מכונה ושקע נפרד למקפיא, רצוי במעגל משלו. שקע לשימוש כללי מעל המשטח, ותאורה גם מתחת לארונות העליונים. נקודת חשמל לונטה, רצוי עם טיימר המשך פעולה או חיישן לחות.</dd></div>
        <div><dt>מייבש</dt><dd>מאחר שאין קיר חיצוני, <b>רק מייבש עם משאבת חום</b> (או קונדנסור). מייבש עם צינור פליטה לא מתאים לחדר הזה.</dd></div>
      </dl>
      <dl>
        <div><dt>ונטה ואוורור</dt><dd>נפח החדר כ-14.5 מ״ק. ונטה של 100–150 מ״ק לשעה מחליף את האוויר 7–10 פעמים בשעה, וזה מספיק לחדר עם מייבש ומקפיא. צינור של 100–125 מ״מ יוצא מקיר הדלת לתקרה המונמכת במסדרון, ומשם לפיר או לקיר חיצוני. כדי שהאוויר ייכנס, צריך חריץ של 1.5–2 ס״מ מתחת לדלת או סבכה בדלת.</dd></div>
        <div><dt>מקפיא בחדר חם</dt><dd>מקפיא ומייבש מחממים חדר סגור. כדאי לבחור מקפיא שמתאים לטמפרטורת סביבה גבוהה (סיווג אקלים SN-T או T) ולשמור על מרווחי האוורור שלו.</dd></div>
        <div><dt>מרווחים</dt><dd>2 ס״מ בין המכונות לבין ארונות סמוכים, כדי שהרעידות לא יעברו לארונות.</dd></div>
      </dl>
    </div>
  </section>

  <p class="src">מקורות לגובה ההגבהה:
    <a href="https://producthelp.whirlpool.com/Laundry/Washers/Front_Load_Washers/Other/Pedestal_Question_or_Concerns/Pedestal_Questions_for_Front_Load_Washer_or_Dryer">Whirlpool, שאלות על בסיסים למכונות</a> ·
    <a href="https://www.journeymanhq.com/?p=145197">Journeyman HQ, התאמת גובה הבסיס</a> ·
    <a href="https://waschturm.de/en_DE/frequently-asked-questions/dimensions/what-is-the-ideal-height-for-a-washing-machine/">Waschturm (יצרן מעמדות, ממליץ על 60 ס״מ)</a>.
    כל המידות בס״מ.</p>
</main>
{JS3D}
'''

OUT.write_text(PAGE, encoding="utf-8")
print(f"wrote {OUT} ({len(PAGE):,} bytes)")
for k, x in zip("ABCD", (A_vol, B_vol, C_vol, D_vol)):
    print(k, "total", x[1], "hard", x[2])
