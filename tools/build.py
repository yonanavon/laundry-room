#!/usr/bin/env python3
"""Generates index.html: laundry-room layout options drawn to scale (units = cm)."""
from pathlib import Path

W, D, H = 214, 274, 260  # room width, depth, assumed ceiling height
OUT = Path(__file__).resolve().parent.parent / "index.html"


# ---------- plan (top view) ----------
# Room coords: x = 0..214 from the left wall, y = 0..274 from the door wall.
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


def plan(parts, title):
    t = 10  # wall thickness
    s = [f'<svg class="plan" viewBox="-34 -26 284 342" role="img" aria-label="{title}">']
    s.append(f'<rect class="wall" x="{-t}" y="{-t}" width="{W + 2 * t}" height="{D + 2 * t}"/>')
    s.append(f'<rect class="floor" x="0" y="0" width="{W}" height="{D}"/>')
    s.append(f'<rect class="floor" x="0" y="{D - 1}" width="80" height="{t + 2}"/>')  # door opening
    s.append(f'<rect class="corr" x="{-t}" y="{D + t}" width="{W + 2 * t}" height="22"/>')
    s.append(f'<text class="sub" x="{W / 2 + 40}" y="{D + t + 14}" font-size="6">מסדרון (101)</text>')
    s.append(swing(0, 0, 80, 0, 0, 80))
    s.append(f'<text class="sub" x="40" y="{D + 7.5}" font-size="5.5">כניסה ~80</text>')
    s.extend(parts)
    s.append(dim(0, -16, W, -16, "214", room=False))
    s.append(dim(-22, 0, -22, D, "274", room=False))
    s.append("</svg>")
    return "".join(s)


# ---------- elevation (front view of one wall) ----------
def elev(length, parts, title, marks):
    s = [f'<svg class="elev" viewBox="-40 -14 {length + 52} 290" role="img" aria-label="{title}">']
    s.append(f'<rect class="floor" x="0" y="0" width="{length}" height="{H}"/>')
    s.append(f'<line class="ceil" x1="0" y1="0" x2="{length}" y2="0"/>')
    s.append(f'<line class="ground" x1="-6" y1="{H}" x2="{length + 6}" y2="{H}"/>')
    s.append(f'<line class="edge" x1="0" y1="0" x2="0" y2="{H}"/>'
             f'<line class="edge" x1="{length}" y1="0" x2="{length}" y2="{H}"/>')
    s.append(f'<text class="sub" x="{length / 2}" y="-5" font-size="6">תקרה ~{H}</text>')
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
        ty = Y + 10
        s += label(X + w / 2, ty, text, size=8) if text else ""
        if sub:
            s += f'<text class="sub" x="{X + w / 2}" y="{Y + h - 5}" font-size="6">{sub}</text>'
        return s
    if text:
        s += label(X + w / 2, Y + h / 2, text, sub, rotate=w < 40 and h > 1.8 * w, size=size)
    return s


def plinth(a0, a1, z1=40):
    return e("store", a0, a1, 0, z1, "מגירת בסיס", size=5.5)


def baskets(a_starts, z0=6):
    return "".join(e("basket", a, a + 35, z0, z0 + 57, "סל", size=6) for a in a_starts)


def door_open(a0, a1):
    return (f'<rect class="opening" x="{a0}" y="{H - 210}" width="{a1 - a0}" height="210"/>'
            + label((a0 + a1) / 2, H - 105, "פתח הדלת", size=6))


# =============== Option A: galley ===============
A_plan = plan([
    zone(50, 68, 142, 192, "מעבר 92"),
    item("freezer", 142, 3, 214, 65, "מקפיא", "60×70 · 155"),
    swing(142, 65, 142, 5, 82, 65),
    item("machine", 142, 68, 214, 130, "כביסה", "מוגבהת 40", port=True),
    item("machine", 142, 130, 214, 192, "מייבש", "מוגבה 40", port=True),
    item("store", 142, 194, 214, 274, "ארון גבוה", "80×70 · עד התקרה"),
    item("counter", 0, 92, 50, 274),
    item("basket", 3, 100, 47, 135, "סל", size=6),
    item("basket", 3, 137, 47, 172, "סל", size=6),
    item("basket", 3, 174, 47, 209, "סל", size=6),
    item("store", 3, 212, 47, 271, "מגירות", size=6),
    f'<line class="flap" x1="52" y1="{ry(100)}" x2="52" y2="{ry(266)}"/>',
    item("loft", 0, 0, 140, 50, "בוידעם מעל הדלת", "גובה 215+", size=5.5),
    dim(50, 182, 142, 182, "92"),
], "חלופה א׳ – תכנית")

A_e1 = elev(274, [
    e("store", 0, 80, 0, 255, "ארון גבוה", "80×70"),
    plinth(82, 144), plinth(144, 206),
    e("machine", 82, 144, 40, 125, "מייבש", port=True),
    e("machine", 144, 206, 40, 125, "כביסה", port=True),
    e("store", 82, 206, 140, 255, "ארון עליון (עומק 40)"),
    e("freezer", 209, 271, 0, 155, "מקפיא"),
    e("upper2", 209, 271, 165, 255, "ארון עמוק", size=6),
    f'<text class="sub" x="144" y="{H - 62}" font-size="6.5">מרכז הפתח ≈90</text>',
], "חלופה א׳ – חזית הקיר הימני", [40, 90, 125, 140, 155, 255])

A_e2 = elev(274, [
    e("loft", 0, 50, 215, 255, "בוידעם", size=5.5),
    e("counter", 92, 274, 87, 90),
    e("base", 92, 274, 0, 87),
    baskets([100, 137, 174]),
    e("store", 212, 274, 6, 84, "מגירות", size=6),
    e("store", 92, 274, 145, 255, "ארונות עליונים (עומק 35)"),
    f'<text class="sub" x="183" y="{H - 95}" font-size="7">משטח 182 · גובה 90 · כנף מתקפלת 20</text>',
], "חלופה א׳ – חזית הקיר השמאלי", [57, 90, 145, 215, 255])

# =============== Option B: machines facing the door ===============
B_plan = plan([
    zone(0, 60, 214, 202, "שטח פנוי 142 × 214"),
    item("store", 0, 202, 22, 274, "שולף", size=6),
    item("machine", 22, 202, 84, 274, "כביסה", "מוגבהת 40", port=True),
    item("machine", 84, 202, 146, 274, "מייבש", "מוגבה 40", port=True),
    item("freezer", 149, 202, 214, 274, "מקפיא"),
    swing(149, 202, 209, 202, 149, 142),
    item("counter", 80, 0, 214, 60),
    item("basket", 84, 6, 119, 50, "סל", size=6),
    item("basket", 121, 6, 156, 50, "סל", size=6),
    item("basket", 158, 6, 193, 50, "סל", size=6),
    item("store", 195, 6, 212, 50, "מגשים", size=5),
    item("loft", 0, 0, 50, 202, "בוידעם", "גובה 215+", size=5.5),
    item("loft", 164, 60, 214, 202, "בוידעם", "גובה 215+", size=5.5),
    dim(40, 60, 40, 202, "142"),
], "חלופה ב׳ – תכנית")

B_e1 = elev(214, [
    e("store", 0, 22, 0, 255, "שולף צר", size=6),
    plinth(22, 84), plinth(84, 146),
    e("machine", 22, 84, 40, 125, "כביסה", port=True),
    e("machine", 84, 146, 40, 125, "מייבש", port=True),
    e("store", 22, 146, 140, 255, "ארון עליון"),
    e("freezer", 149, 211, 0, 155, "מקפיא"),
    e("upper2", 149, 211, 165, 255, "ארון עמוק", size=6),
], "חלופה ב׳ – חזית הקיר האחורי", [40, 125, 140, 155, 255])

B_e2 = elev(214, [
    e("counter", 0, 134, 87, 90),
    e("base", 0, 134, 0, 87),
    baskets([21, 58, 95]),
    e("store", 2, 19, 6, 84, "מגשים", size=5),
    e("store", 0, 134, 145, 255, "ארונות עליונים"),
    door_open(134, 214),
    e("loft", 134, 214, 215, 255, "בוידעם", size=5.5),
], "חלופה ב׳ – חזית קיר הדלת", [57, 90, 145, 210, 255])

# =============== Option C: machines under a counter ===============
C_plan = plan([
    zone(40, 68, 142, 192, "מעבר 102"),
    item("freezer", 142, 3, 214, 65, "מקפיא"),
    swing(142, 65, 142, 5, 82, 65),
    item("machine", 142, 68, 214, 130, "כביסה", "על הרצפה", port=True),
    item("machine", 142, 130, 214, 192, "מייבש", "על הרצפה", port=True),
    item("counter", 142, 192, 214, 274),
    item("basket", 145, 196, 189, 231, "סל", size=6),
    item("basket", 145, 233, 189, 268, "סל", size=6),
    f'<line class="flap" x1="140" y1="{ry(70)}" x2="140" y2="{ry(272)}"/>',
    item("store", 0, 92, 40, 274, "ארונות גבוהים", "182×40 · כולל תא לסל 3"),
    item("loft", 0, 0, 140, 50, "בוידעם מעל הדלת", "גובה 215+", size=5.5),
    dim(40, 182, 142, 182, "102"),
], "חלופה ג׳ – תכנית")

C_e1 = elev(274, [
    e("base", 0, 82, 0, 87),
    baskets([6, 43]),
    e("counter", 0, 206, 87, 90),
    e("machine", 82, 144, 0, 85, "מייבש", port=True),
    e("machine", 144, 206, 0, 85, "כביסה", port=True),
    e("store", 0, 206, 145, 255, "ארונות עליונים"),
    e("freezer", 209, 271, 0, 155, "מקפיא"),
    e("upper2", 209, 271, 165, 255, "ארון עמוק", size=6),
    f'<text class="sub" x="103" y="{H - 95}" font-size="7">משטח רציף 206 · גובה 90</text>',
], "חלופה ג׳ – חזית הקיר הימני", [48, 90, 145, 155, 255])

LEFT_TALL = elev(274, [
    e("loft", 0, 50, 215, 255, "בוידעם", size=5.5),
    e("store", 92, 274, 70, 255, "ארונות גבוהים · עומק 40"),
    e("store", 92, 274, 0, 68),
    e("basket", 96, 131, 6, 63, "סל 3", size=5.5),
    e("store", 135, 274, 4, 66, "שואב · קרש גיהוץ · דליים", size=5.5),
], "חזית הקיר השמאלי – ארונות גבוהים", [68, 215, 255])

# =============== Option D: stacked tower ===============
D_plan = plan([
    zone(40, 68, 142, 132, "מעבר 102"),
    item("freezer", 142, 3, 214, 65, "מקפיא"),
    swing(142, 65, 142, 5, 82, 65),
    item("machine", 142, 68, 214, 132, "מגדל", "כביסה+מייבש", port=True),
    item("counter", 150, 134, 214, 274),
    item("basket", 153, 138, 197, 173, "סל", size=6),
    item("basket", 153, 175, 197, 210, "סל", size=6),
    item("basket", 153, 212, 197, 247, "סל", size=6),
    item("store", 153, 249, 197, 272, "שולף", size=5),
    item("store", 0, 92, 40, 274, "ארונות גבוהים", "182×40"),
    item("loft", 0, 0, 140, 50, "בוידעם מעל הדלת", "גובה 215+", size=5.5),
    dim(40, 74, 142, 74, "102"),
], "חלופה ד׳ – תכנית")

D_e1 = elev(274, [
    e("base", 0, 140, 0, 87),
    baskets([27, 64, 101]),
    e("store", 2, 25, 6, 84, "שולף", size=5),
    e("counter", 0, 140, 87, 90),
    e("store", 0, 140, 145, 255, "ארונות עליונים"),
    e("machine", 142, 206, 0, 85, "כביסה", port=True),
    e("machine", 142, 206, 87, 172, "מייבש", port=True),
    e("store", 142, 206, 185, 255, "ארון", size=6),
    e("freezer", 209, 271, 0, 155, "מקפיא"),
    e("upper2", 209, 271, 165, 255, "ארון עמוק", size=6),
], "חלופה ד׳ – חזית הקיר הימני", [85, 135, 172, 255])

LEGEND = "".join(
    f'<span class="lg"><svg viewBox="0 0 14 10" aria-hidden="true"><rect class="k-{k}" x="1" y="1" width="12" height="8" rx="1"/></svg>{t}</span>'
    for k, t in [("machine", "מכונות"), ("freezer", "מקפיא"), ("counter", "משטח קיפול"), ("basket", "סל כביסה"),
                 ("store", "אחסון"), ("loft", "בוידעם (גבוה, גישה פחות נוחה)"), ("zone", "אזור עבודה/מעבר פנוי")]
)


def storage(rows):
    total = sum(v for _, v, _ in rows)
    body = "".join(
        f'<tr><td>{n}</td><td class="num">{v:,}</td><td>{"" if easy else "<span class=pill>גישה פחות נוחה</span>"}</td></tr>'
        for n, v, easy in rows)
    return (f'<table class="vol"><thead><tr><th>רכיב אחסון</th><th class="num">ליטר (ברוטו)</th><th></th></tr></thead>'
            f'<tbody>{body}</tbody><tfoot><tr><td>סה״כ</td><td class="num">{total:,}</td><td></td></tr></tfoot></table>')


A_vol = storage([("מגירות בבסיס המוגבה (124×65×36)", 290, True), ("ארון עליון מעל המכונות (124×40×115)", 570, True),
                 ("ארון גבוה בפינה (80×68×255)", 1387, True), ("מגירות במשטח (67×48×80)", 257, True),
                 ("ארונות עליונים מעל המשטח (182×35×110)", 701, True), ("ארון עמוק מעל המקפיא (62×60×90)", 335, False),
                 ("בוידעם מעל הדלת (140×50×40)", 280, False)])
B_vol = storage([("מגירות בבסיס המוגבה", 290, True), ("ארון עליון מעל המכונות", 570, True),
                 ("שולף צר עד התקרה (22×68×255)", 381, True), ("שולף מגשים במשטח", 84, True),
                 ("ארונות עליונים מעל המשטח (134×35×110)", 516, True), ("ארון עמוק מעל המקפיא", 335, False),
                 ("בוידעם קיר שמאל (202×50×40)", 404, False), ("בוידעם קיר ימין (142×50×40)", 284, False)])
C_vol = storage([("ארונות עליונים מעל המשטח (206×35×110)", 793, True),
                 ("ארונות גבוהים בקיר השמאלי (182×40×255, בניכוי תא הסל)", 1760, True),
                 ("ארון עמוק מעל המקפיא", 335, False), ("בוידעם מעל הדלת", 280, False)])
D_vol = storage([("ארון מעל המגדל (62×60×70)", 260, False), ("שולף במשטח", 110, True),
                 ("ארונות עליונים מעל המשטח (140×35×110)", 539, True),
                 ("ארונות גבוהים בקיר השמאלי (182×40×255)", 1856, True),
                 ("ארון עמוק מעל המקפיא", 335, False), ("בוידעם מעל הדלת", 280, False)])


def option(oid, letter, name, tag, desc, drawings, pros, cons, vol, extra=""):
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
  <details><summary>פירוט נפח האחסון</summary>{vol}</details>
</section>'''


OPTS = "".join([
    option("a", "א", "גלריה: מכונות מוגבהות מול משטח הקיפול", '<span class="badge">מומלץ</span>',
           "לאורך הקיר הימני (274): המקפיא ראשון ליד הכניסה, אחריו מכונת הכביסה והמייבש על בסיס מוגבה 40 ס״מ עם מגירות, "
           "ובפינה האחורית ארון גבוה 80×70 עד התקרה. לאורך הקיר השמאלי: משטח קיפול 182×50 בגובה 90 עם כנף מתקפלת של 20 ס״מ "
           "(70 ס״מ עומק בזמן קיפול), 3 תאי סלים ומגירות מתחתיו. מעל: ארונות מעל המכונות, מעל המשטח ומעל המקפיא, ובוידעם מעל הדלת.",
           [("תכנית (מבט מלמעלה)", A_plan), ("חזית הקיר הימני: מקפיא, מכונות, ארון גבוה", A_e1),
            ("חזית הקיר השמאלי: משטח, סלים, ארונות", A_e2)],
           ["המכונות מוגבהות זו לצד זו, כפי שביקשת.",
            "נפח האחסון הגדול ביותר מבין החלופות (כ-3,800 ליטר), כולל ארון גבוה ועמוק לשואב אבק, קרש גיהוץ ומזוודה.",
            "זרימה קצרה: לוקחים סל, מסתובבים לכביסה, מעבירים למייבש, מסתובבים למשטח ומקפלים לתוך הסל.",
            "המקפיא ראשון בכניסה, כך שמי שבא להוציא משהו מהמקפיא לא נכנס לאזור העבודה.",
            "משטח 182 ס״מ, הרבה מעבר ל-120 הנדרשים. אפשר גם להוסיף סל רביעי במקום חלק מהמגירות.",
            "שום פריט לא חוסם פריט אחר. דלת הכניסה נפתחת פנימה לאזור שממילא פנוי."],
           ["מעבר של 92 ס״מ מול המכונות: עומד במינימום המקובל (90) אבל לא מרווח, ושני אנשים לא יעברו בו בנוחות.",
            "כשהכנף פתוחה המעבר יורד ל-72 ס״מ. זה בסדר בזמן קיפול, ומקפלים אותה בסיום.",
            "הארון שמעל המקפיא עמוק וגבוה, ומתאים רק לדברים שמוציאים לעיתים רחוקות.",
            "דורש נגרות בהתאמה: בסיס מוגבה יציב ומשטח עם תאי סלים."],
           A_vol,
           '<div class="note"><b>וריאנט א2: סלים מתחת למכונות.</b> בסיס בגובה 60 ס״מ ברוחב 124 מכיל 3 תאי סלים (כל תא 37 ס״מ). '
           'כך כל הארון שמתחת למשטח מתפנה למגירות (תוספת של כ-250 ליטר), אבל מרכז פתח התוף עולה לכ-108 ס״מ וראש המכונות ל-145. '
           'מתאים רק אם המשתמשים העיקריים בגובה 180 ס״מ ומעלה.<br><b>טיפ:</b> ארגז הזנה וניקוז שקוע בקיר מאחורי המכונות חוסך 5–8 ס״מ עומק, '
           'והמעבר גדל ל-97–100 ס״מ.</div>'),
    option("b", "ב", "מול הדלת: מכונות על הקיר האחורי", '<span class="badge soft">הכי מרווח</span>',
           "על הקיר האחורי (214): שולף צר בפינה, מכונת כביסה ומייבש מוגבהים 40, ומקפיא בפינה הימנית. על קיר הדלת, מימין לדלת: "
           "משטח 134×60 עם 3 סלים ושולף מגשים. מעל המכונות והמשטח ארונות, ולאורך שני הקירות הארוכים בוידעם (מדף בעומק 50 בגובה 215 ומעלה).",
           [("תכנית (מבט מלמעלה)", B_plan), ("חזית הקיר האחורי", B_e1), ("חזית קיר הדלת", B_e2)],
           ["שטח פנוי של 142×214 ס״מ באמצע: הכי נוח לטעינה, ויש מקום למתקן ייבוש מתקפל.",
            "מכונות מוגבהות זו לצד זו.",
            "משטח בעומק 60, הכי נוח לקיפול.",
            "המכונות גלויות מהכניסה וקל לשים לב כשמחזור מסתיים."],
           ["נפח האחסון הנמוך ביותר (כ-2,900 ליטר), וכמעט שליש ממנו בבוידעם גבוה.",
            "הקירות הארוכים כמעט לא מנוצלים בגובה הרצפה.",
            "משטח 134 ס״מ, מעט מעל הדרישה.",
            "המקפיא בעומק החדר, וכל גישה אליו עוברת דרך אזור העבודה.",
            "הסלים יושבים ליד הכניסה, בצד הנגדי למכונות."],
           B_vol),
    option("c", "ג", "מכונות על הרצפה מתחת למשטח רציף", "",
           "לאורך הקיר הימני: המקפיא, ואחריו משטח רציף באורך 206 ס״מ בעומק 72 ובגובה 90. מתחתיו מכונת כביסה ומייבש, "
           "ובסוף תא לשני סלים. לאורך הקיר השמאלי ארונות גבוהים בעומק 40 עד התקרה, עם תא לסל שלישי בתחתית.",
           [("תכנית (מבט מלמעלה)", C_plan), ("חזית הקיר הימני", C_e1), ("חזית הקיר השמאלי", LEFT_TALL)],
           ["משטח העבודה הארוך ביותר: 206 ס״מ.",
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
           [("תכנית (מבט מלמעלה)", D_plan), ("חזית הקיר הימני", D_e1), ("חזית הקיר השמאלי", LEFT_TALL)],
           ["3 סלים מתחת למשטח, ומשטח נפרד מהמכונות.",
            "מעבר של 102 ס״מ.",
            "נפח אחסון טוב (כ-3,400 ליטר)."],
           ["מכונת הכביסה על הרצפה (כפיפה), ופתח המייבש בגובה כ-135 ס״מ, כלומר פריקה מעל גובה החזה.",
            "צריך ערכת חיבור (stacking kit) ומכונות שמתאימות לה.",
            "הארון שמעל המגדל נמוך וגבוה מאוד."],
           D_vol),
])

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
  --zone: #C2563B; --zone-f: rgba(194,86,59,.07);
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
  --zone: #F08A6E; --zone-f: rgba(240,138,110,.08); color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #141816; --paper: #1C211F; --fg: #E5E9E6; --muted: #9AA39E; --line: #313834;
  --accent: #7CC2B8; --accent-soft: #23403C; --pro: #7FCB98; --con: #EE9A84;
  --wall: #5D635F; --floor: #222826; --corr: #1A1E1C;
  --machine: #9DB6D6; --machine-f: #2A3546; --freezer: #7CC7D6; --freezer-f: #1F3A40;
  --counter: #D7AE7C; --counter-f: #4A3A26; --basket: #E0B677; --basket-f: #5A4422;
  --store: #A6C394; --store-f: #2A3A25; --loft: #B5B9A3; --loft-f: #30332A;
  --zone: #F08A6E; --zone-f: rgba(240,138,110,.08); color-scheme: dark; }}
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
nav {{ display: flex; flex-wrap: wrap; gap: 8px; }}
nav a {{ color: var(--fg); text-decoration: none; border: 1px solid var(--line); background: var(--paper); padding: 6px 12px; border-radius: 999px; font-size: 15px; }}
nav a:hover, nav a:focus-visible {{ border-color: var(--accent); outline: none; }}
.rec {{ background: var(--accent-soft); border-inline-start: 4px solid var(--accent); padding: 16px 18px; border-radius: 4px; }}
.rec b {{ color: var(--accent); }}
.sheet {{ background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 22px; display: grid; gap: 14px; min-width: 0; }}
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
details summary {{ cursor: pointer; color: var(--accent); font-weight: 600; }}
details[open] summary {{ margin-bottom: 8px; }}
.pill {{ font-size: 12px; background: var(--loft-f); color: var(--fg); border: 1px solid var(--loft); padding: 1px 8px; border-radius: 999px; white-space: nowrap; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 14px; color: var(--muted); }}
.lg {{ display: inline-flex; align-items: center; gap: 6px; }}
.lg svg {{ width: 20px; height: 14px; }}
.cmp td:first-child {{ font-weight: 600; white-space: nowrap; }}
.cmp .best {{ color: var(--pro); font-weight: 700; }}
.cmp .weak {{ color: var(--con); }}
ol.q {{ margin: 0; padding-inline-start: 22px; display: grid; gap: 6px; }}
.src {{ font-size: 14px; color: var(--muted); }}
.src a {{ color: var(--accent); }}
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
.zone {{ fill: var(--zone-f); stroke: var(--zone); stroke-width: .6; stroke-dasharray: 2.5 2; }}
.zlbl {{ fill: var(--zone); font-family: var(--body); font-weight: 700; text-anchor: middle; }}
.port {{ fill: none; stroke: var(--machine); stroke-width: .7; }}
.portc {{ fill: var(--machine); }}
.arc {{ fill: none; stroke: var(--muted); stroke-width: .5; stroke-dasharray: 1.5 1.2; }}
.leaf {{ stroke: var(--fg); stroke-width: 1.6; }}
.flap {{ stroke: var(--counter); stroke-width: .8; stroke-dasharray: 3 1.5; }}
.opening {{ fill: var(--bg); stroke: var(--muted); stroke-width: .5; stroke-dasharray: 2 1.5; }}
.dim {{ stroke: var(--muted); stroke-width: .45; }}
.dimt {{ direction: rtl; unicode-bidi: plaintext; fill: var(--muted); font-family: var(--mono); font-size: 7.5px; text-anchor: middle; }}
.lbl, .sub, .zlbl {{ direction: rtl; unicode-bidi: plaintext; }}
.lbl {{ fill: var(--fg); font-family: var(--body); font-weight: 700; text-anchor: middle; }}
.sub {{ fill: var(--muted); font-family: var(--body); text-anchor: middle; }}
.ceil {{ stroke: var(--muted); stroke-width: .5; stroke-dasharray: 3 2; }}
.ground {{ stroke: var(--fg); stroke-width: 1.4; }}
.edge {{ stroke: var(--line); stroke-width: .6; }}
@media (max-width: 520px) {{ .sheet, .opt {{ padding: 16px; }} body {{ font-size: 16px; }} }}
</style>

<main dir="rtl" lang="he">
  <header style="display:grid;gap:10px">
    <h1>תכנון חדר הכביסה</h1>
    <p class="lede">חדר נטו <span class="mono">214×274</span> ס״מ (5.86 מ״ר). ארבע חלופות סידור, כולן משורטטות בקנה מידה, עם מעלות, חסרונות ונפח אחסון.</p>
  </header>

  <div class="rec"><p><b>ההמלצה: חלופה א׳ (גלריה).</b> מקפיא, מכונת כביסה ומייבש מוגבהים לאורך הקיר הימני, משטח קיפול עם 3 סלים לאורך הקיר השמאלי, וארון גבוה בפינה האחורית.
  זו החלופה היחידה שעומדת בכל הדרישות עם מכונות מוגבהות זו לצד זו, והיא גם נותנת את נפח האחסון הגדול ביותר (כ-3,800 ליטר).
  אם חשוב לך מרחב פתוח יותר, או מקום למתקן ייבוש, חלופה ב׳ היא השנייה בדירוג.</p></div>

  <nav aria-label="חלופות"><a href="#basis">הנחות</a><a href="#height">גובה ההגבהה</a><a href="#a">א׳ גלריה</a><a href="#b">ב׳ מול הדלת</a><a href="#c">ג׳ מתחת למשטח</a><a href="#d">ד׳ מגדל</a><a href="#compare">השוואה</a><a href="#build">ביצוע</a><a href="#questions">שאלות</a></nav>

  <section class="sheet" id="basis">
    <h2>הנחות ומידות עבודה</h2>
    <div class="grid2">
      <dl>
        <div><dt>החדר</dt><dd>214 (רוחב) × 274 (עומק) נטו. הנחתי גובה תקרה של 260 ס״מ.</dd></div>
        <div><dt>הדלת</dt><dd>כ-80 ס״מ, צמודה לפינה השמאלית בקיר הקצר. בכל החלופות היא יכולה להיפתח <b>פנימה</b> עם ציר בקיר השמאלי, כי האזור הזה נשאר פנוי ממילא. כך היא לא חוסמת את המסדרון (101 ס״מ). גם דלת הזזה לתוך הקיר מתאימה.</dd></div>
        <div><dt>מכונות</dt><dd>רוחב 60, עומק עד 62, גובה 85, ועוד 8–10 ס״מ מאחור לצנרת. עומק הנישה 72, ו-2 ס״מ בין המכונות.</dd></div>
      </dl>
      <dl>
        <div><dt>מקפיא Beko</dt><dd>60×70×155, ועוד כ-3 ס״מ אוורור מכל צד ומאחור (לבדוק בהוראות של הדגם). <b>הציר בצד הרחוק מהקיר</b>, כדי שהדלת תיפתח מעבר ל-90° והמגירות ייצאו עד הסוף.</dd></div>
        <div><dt>סלים</dt><dd>35×44, גובה 57. כל סל צריך תא ברוחב 37 על מסילות. מתחת למשטח בגובה 90 נשאר מרווח מעל הסל.</dd></div>
        <div><dt>מרווחי עבודה</dt><dd>מול מכונה עם דלת פתוחה: 90 ס״מ לפחות, ו-100 ומעלה נוח. מול המקפיא: כ-90. משטח קיפול בגובה 90.</dd></div>
      </dl>
    </div>
    <div class="legend">{LEGEND}</div>
  </section>

  <section class="sheet" id="height">
    <h2>מה גובה ההגבהה האידיאלי?</h2>
    <p>המטרה היא להגיע לתחתית התוף עם כיפוף קל של המרפק, בלי להתכופף בגב. במכונה פתח-חזית רגילה בגובה 85, מרכז הפתח נמצא כ-45–50 ס״מ מעל בסיס המכונה.
    גובה המרפק של אדם הוא בערך 63% מגובהו, ונוח כשמרכז הפתח נמצא כ-15–20 ס״מ מתחת למרפק. בסיסים של יצרנים נעים בדרך כלל בין 30 ל-40 ס״מ, וזה מתיישב עם החישוב.</p>
    <div class="scroll"><table>
      <thead><tr><th>גובה המשתמש העיקרי</th><th class="num">גובה מרפק</th><th class="num">הגבהה מומלצת</th><th class="num">מרכז הפתח</th><th class="num">ראש המכונה</th></tr></thead>
      <tbody>
        <tr><td>155–165</td><td class="num">98–104</td><td class="num">30–35</td><td class="num">≈80–85</td><td class="num">115–120</td></tr>
        <tr><td><b>165–178</b></td><td class="num">104–112</td><td class="num"><b>40</b></td><td class="num">≈90</td><td class="num">125</td></tr>
        <tr><td>178–190</td><td class="num">112–120</td><td class="num">45–50</td><td class="num">≈95–100</td><td class="num">130–135</td></tr>
      </tbody></table></div>
    <p><b>ההמלצה: 40 ס״מ</b>, אלא אם כל המשתמשים נמוכים או גבוהים במיוחד. בבסיס כזה נכנסת מגירה עם כ-30 ס״מ גובה פנימי לאבקות ולמרככים.
    ארונות עליונים מעל המכונות כדאי להתחיל ב-140 לפחות. הבסיס צריך להיות מבנה קשיח (בנוי או שלד מחוזק) והמכונות צריכות להיות מקובעות אליו, כי מכונה מוגבהת רועדת יותר בסחיטה.
    יש יצרני מעמדות שממליצים על 60 ס״מ, אבל בגובה הזה מרכז הפתח מגיע לכ-108, וזה נוח רק לגבוהים.</p>
  </section>

  {OPTS}

  <section class="sheet" id="compare">
    <h2>השוואה</h2>
    <div class="scroll"><table class="cmp">
      <thead><tr><th></th><th>א׳ גלריה</th><th>ב׳ מול הדלת</th><th>ג׳ מתחת למשטח</th><th>ד׳ מגדל</th></tr></thead>
      <tbody>
        <tr><td>סידור המכונות</td><td class="best">מוגבהות זו לצד זו</td><td class="best">מוגבהות זו לצד זו</td><td class="weak">על הרצפה</td><td class="weak">זו מעל זו</td></tr>
        <tr><td>מרווח מול המכונות</td><td class="num">92</td><td class="num best">142</td><td class="num">102</td><td class="num">102</td></tr>
        <tr><td>משטח קיפול</td><td class="num">182×50 (+20)</td><td class="num">134×60</td><td class="num best">206×72</td><td class="num">140×64</td></tr>
        <tr><td>סלים במקום ייעודי</td><td>3, אפשר 4</td><td>3</td><td>2+1 בארון</td><td>3</td></tr>
        <tr><td>נפח אחסון משוער</td><td class="num best">≈3,800 ל׳</td><td class="num weak">≈2,900 ל׳</td><td class="num">≈3,200 ל׳</td><td class="num">≈3,400 ל׳</td></tr>
        <tr><td>מתוכו בגישה פחות נוחה</td><td class="num">≈600 ל׳</td><td class="num">≈1,000 ל׳</td><td class="num">≈600 ל׳</td><td class="num">≈900 ל׳</td></tr>
        <tr><td>תחושת מרחב</td><td>בינונית</td><td class="best">גבוהה</td><td>טובה</td><td>טובה</td></tr>
        <tr><td>מורכבות ועלות נגרות</td><td>בינונית-גבוהה</td><td>בינונית</td><td class="best">נמוכה</td><td>בינונית</td></tr>
      </tbody></table></div>
    <p class="src">הנפחים הם ברוטו (מידות חוץ של הארונות), ומיועדים להשוואה בין החלופות. הנפח השימושי יהיה קטן בכ-15–20%.</p>
  </section>

  <section class="sheet" id="build">
    <h2>המלצות ביצוע (החדר בשלב בנייה)</h2>
    <div class="grid2">
      <dl>
        <div><dt>מים וניקוז</dt><dd>ארגז הזנה וניקוז שקוע בקיר מאחורי המכונות, בגובה של כ-100 (מאחורי המכונה המוגבהת). הוא חוסך עומק, וגם המעבר גדל. מומלץ מחסום רצפה ליד המכונות למקרה של נזילה, וניקוז מי העיבוי של המייבש לאותו ארגז.</dd></div>
        <div><dt>חשמל</dt><dd>שקע נפרד לכל מכונה ושקע נפרד למקפיא, רצוי במעגל משלו. שקע לשימוש כללי מעל המשטח, ותאורה גם מתחת לארונות העליונים.</dd></div>
      </dl>
      <dl>
        <div><dt>מייבש</dt><dd>מייבש עם משאבת חום (בלי צינור פליטה החוצה) מתאים לחדר סגור ופנימי.</dd></div>
        <div><dt>אוורור</dt><dd>מקפיא ומייבש בחדר של 6 מ״ר מחממים את החדר ומוסיפים לחות. כדאי מאוורר יניקה, או סבכה בדלת אם אין חלון. כדאי לוודא שסיווג האקלים של המקפיא מתאים לחדר חם (SN-T או T).</dd></div>
        <div><dt>מרווחים</dt><dd>2 ס״מ בין המכונות לבין ארונות סמוכים, כדי שהרעידות לא יעברו לארונות. בין המייבש למקפיא יש מכונת כביסה, וזה טוב.</dd></div>
      </dl>
    </div>
  </section>

  <section class="sheet" id="questions">
    <h2>שאלות שישפיעו על הדיוק</h2>
    <ol class="q">
      <li>מה גובה התקרה? הנחתי 260. התשובה קובעת את הבוידעם ואת הארונות העליונים.</li>
      <li>מה הגובה של מי שמשתמש בעיקר במכונות? הוא קובע אם ההגבהה תהיה 35, 40 או 45–50.</li>
      <li>מה רוחב הדלת המדויק, ואפשר להזיז אותה או להחליף לדלת הזזה? הזזה של 30–40 ס״מ ימינה פותחת אפשרויות לאורך הקיר השמאלי.</li>
      <li>האם אחד הקירות חיצוני, או שיש חלון? זה חשוב לאוורור ולסוג המייבש.</li>
      <li>האם אתם תולים כביסה לייבוש? אם כן, חלופה ב׳ מקבלת משקל נוסף.</li>
      <li>מה הדגם המדויק של המקפיא? צריך לבדוק את מרווחי האוורור ואת זווית פתיחת הדלת שהמגירות דורשות.</li>
    </ol>
  </section>

  <p class="src">מקורות לגובה ההגבהה:
    <a href="https://producthelp.whirlpool.com/Laundry/Washers/Front_Load_Washers/Other/Pedestal_Question_or_Concerns/Pedestal_Questions_for_Front_Load_Washer_or_Dryer">Whirlpool, שאלות על בסיסים למכונות</a> ·
    <a href="https://www.journeymanhq.com/?p=145197">Journeyman HQ, התאמת גובה הבסיס</a> ·
    <a href="https://waschturm.de/en_DE/frequently-asked-questions/dimensions/what-is-the-ideal-height-for-a-washing-machine/">Waschturm (יצרן מעמדות, ממליץ על 60 ס״מ)</a>.
    כל המידות בס״מ.</p>
</main>
'''

OUT.write_text(PAGE, encoding="utf-8")
print(f"wrote {OUT} ({len(PAGE):,} bytes)")
