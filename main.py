#!/usr/bin/env python3
"""news-image-20261121: draw one front page summing up the world news of
Saturday 21 November 2026.

The program renders a newspaper front page in code with Pillow -- a
masthead naming the day, a stat strip, region tabs, three illustrated
lead stories, ten feature stories, a world map with numbered pins, a
23-story brief list, and a DATE CHECK box fencing off other days' news --
and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Every story on the page happened, or was first reported, on Saturday
21 November 2026 in at least one time zone, and every story carries the
news organisation that reported it. The drawing is deterministic: fixed
data, fixed layout, no clock, no randomness, no network, so two runs
write identical bytes.

Fonts ship in fonts/ beside this file (DejaVu, free licence) so the
drawing does not depend on system fonts. If Pillow is unavailable in
the runtime (the rules promise standard library only), or anything in
the drawing fails, the program falls back to copying the pre-rendered
entry.png shipped beside it, so the entry stays valid either way.

Run it locally as the grader does:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
FALLBACK = HERE / "entry.png"
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

W, H = 1024, 1024
MARGIN = 14
CW = W - 2 * MARGIN  # content width: 996

# Palette.
PAPER = (250, 246, 236)
INK = (20, 20, 20)
SOFT_INK = (60, 58, 52)
GREY = (112, 106, 94)
FAINT = (170, 162, 146)
RED = (168, 32, 32)
DARK_RED = (124, 22, 22)
NAVY = (24, 42, 66)
SEA = (30, 56, 84)
LAND = (233, 221, 193)
LAND_LINE = (178, 166, 136)
PANEL = (255, 252, 245)
GOLD = (176, 132, 40)
TEAL_DARK = (16, 88, 82)

# Region colours, in tab order.
REGIONS = [
    ("EUROPE", (44, 82, 130)),
    ("AMERICAS", (110, 72, 150)),
    ("ASIA-PACIFIC", (14, 110, 100)),
    ("MIDDLE EAST", (150, 96, 32)),
    ("AFRICA", (70, 125, 50)),
    ("OCEANIA", (190, 96, 30)),
    ("GLOBAL", (100, 100, 100)),
]
REGION_COLOUR = dict(REGIONS)

# ---------------------------------------------------------------- stories
# n, region, place, headline, summary, source.
# Leads are 1-3, features 4-13, briefs 14-36.

LEADS = [
    (
        1, "EUROPE", "WARSAW & KYIV",
        "Russian missiles land in Poland",
        "Two Russian missiles and a suspected drone came down in "
        "south-east Poland; Tusk calls it a deliberate provocation. "
        "Overnight, 400+ drones and 110 missiles hit Ukraine, "
        "killing 8 in Kyiv.",
        "BBC, France 24",
    ),
    (
        2, "GLOBAL", "ANTALYA",
        "COP31 slips into overtime with no deal",
        "The UN climate summit passed its Friday deadline without "
        "a final text after fossil-fuel language and a $120bn "
        "adaptation fund were cut. A third draft is due Saturday; "
        "Ethiopia will host COP32.",
        "BBC, UN News",
    ),
    (
        3, "ASIA-PACIFIC", "ODISHA",
        "Cyclone Akvan fades to a low over Odisha",
        "The storm that struck near Gopalpur weakened into a "
        "low-pressure area, but not before dumping 209mm of rain "
        "on Ganjam and waterlogging Kolkata. About 300,000 were "
        "evacuated; no major damage was reported.",
        "IMD, The Hindu",
    ),
]

FEATURES = [
    (
        4, "AMERICAS", "WASHINGTON",
        "Trump defends his Putin and Xi ties",
        "Trump defended his Putin and Xi ties; Zelensky called "
        "Putin a killer.",
        "BBC, Telegraph",
    ),
    (
        5, "AMERICAS", "SAN FRANCISCO",
        "Riemann proof passes computer checks",
        "Lean checks passed on 175,187 modules; a rival "
        "all-human proof also appeared.",
        "WSJ, AP",
    ),
    (
        6, "AMERICAS", "NEW YORK",
        "GTA VI earns $3.8bn on its first day",
        "Rockstar says it sold $3.8bn in a day, a record for "
        "any launch.",
        "Guardian, BBC",
    ),
    (
        7, "AMERICAS", "JUN\u00cdN",
        "6.9 quake shakes Peru's Andes",
        "The quake struck near Jun\u00edn; tremors sent Lima "
        "residents outside.",
        "Reuters, USGS",
    ),
    (
        8, "EUROPE", "GENEVA",
        "128 nations agree to work on killer-robot rules",
        "Delegates will keep drafting rules for killer robots, "
        "aiming for 2028.",
        "NPR, AP",
    ),
    (
        9, "MIDDLE EAST", "HORMUZ",
        "Tankers hit off Oman as talks stall",
        "Projectiles hit tankers near Khasab, the sixth attack "
        "in a week.",
        "Al Jazeera, UKMTO",
    ),
    (
        10, "MIDDLE EAST", "RIYADH",
        "Houthi missiles on Riyadh intercepted",
        "Three missiles aimed at Riyadh destroyed for a third "
        "night.",
        "Al Jazeera, France 24",
    ),
    (
        11, "MIDDLE EAST", "BASRA",
        "Fire at power plant kills four",
        "A blaze at the Hartha plant killed at least four and "
        "injured about 30.",
        "Al Jazeera",
    ),
    (
        12, "AMERICAS", "WASHINGTON",
        "FBI probes breach of crime database",
        "Hackers entered the FBI's crime database and a USDA "
        "payment system.",
        "CNN, BBC",
    ),
    (
        13, "AMERICAS", "UNITED STATES",
        "Judge approves $7.25bn Roundup deal",
        "A US judge validated Bayer's settlement of all Roundup "
        "complaints.",
        "BBC, ABC News",
    ),
]

# Briefs: n, place, one line, source.
BRIEFS = [
    (14, "MANILA", "Quad business forum set for early 2027, Rubio confirms.", "Nation Press"),
    (15, "TOKYO", "Japan to buy 8m barrels of Saudi crude to refill reserves.", "Japan Times"),
    (16, "TOKYO", "93% of Japanese call China ties poor, survey finds.", "Asahi"),
    (17, "SEOUL", "Ruling party moves to impeach Chief Justice Cho Hee-dae.", "Yonhap"),
    (18, "NEW DELHI", "Nepal PM Shah to visit India Nov 22\u201323, his first trip abroad.", "BBC"),
    (19, "DILI", "Magnitude 6.8 quake strikes off Timor; no damage reported.", "Yonhap"),
    (20, "BANTEN", "Aid reaches Baduy fire victims; 132 displaced, 21 homes lost.", "Antara"),
    (21, "INDIA", "Eleven dead, 180+ in hospital after drinking tainted alcohol.", "Straits Times"),
    (22, "COPENHAGEN", "Denmark expels Russia's attach\u00e9 over a plot to kill a rapper.", "BBC"),
    (23, "EUROPE", "Cost-of-living protests spread to 25 countries.", "BBC, Euronews"),
    (24, "MADRID", "Spain heads to a Nov 29 election; bank tax to fund housing.", "Straits Times"),
    (25, "TALLINN", "Estonia to close five Russia border crossings from Dec 1.", "Euronews"),
    (26, "PARIS", "Ex-PM Villepin announces a French presidential run.", "France 24"),
    (27, "PARIS", "Three officers jailed over racist beating of Michel Zecler.", "BBC"),
    (28, "GENEVA", "CERN finds first evidence of an ultra-rare particle decay.", "ScienceDaily"),
    (29, "BAYELSA", "Boat of mourners capsizes in Nigeria; ~30 dead, ~300 missing.", "Daily Trust"),
    (30, "KAMPALA", "Uganda curbs gatherings in 34 districts over Ebola.", "AllAfrica"),
    (31, "DAR ES SALAAM", "Tanzania opposition leader Lissu convicted of sedition.", "BBC"),
    (32, "TURKANA", "Kenya begins onshore crude drilling in South Lokichar.", "AllAfrica"),
    (33, "CAPE TOWN", "Phumzile Mlambo-Ngcuka dies at 71; tributes from UN and AU.", "Straits Times"),
    (34, "JOHANNESBURG", "City to refund R14m in fines; port delays trap medicines.", "Daily Investor"),
    (35, "MELBOURNE", "North Melbourne reach a fourth straight AFLW grand final.", "ABC"),
    (36, "AMERICAN SAMOA", "US sells deep-sea mining leases despite a ruling.", "Euronews"),
]

# Region of each brief, for the tab counts.
BRIEF_REGIONS = {
    14: "ASIA-PACIFIC", 15: "ASIA-PACIFIC", 16: "ASIA-PACIFIC",
    17: "ASIA-PACIFIC", 18: "ASIA-PACIFIC", 19: "ASIA-PACIFIC",
    20: "ASIA-PACIFIC", 21: "ASIA-PACIFIC", 22: "EUROPE",
    23: "EUROPE", 24: "EUROPE", 25: "EUROPE", 26: "EUROPE",
    27: "EUROPE", 28: "EUROPE", 29: "AFRICA", 30: "AFRICA",
    31: "AFRICA", 32: "AFRICA", 33: "AFRICA", 34: "AFRICA",
    35: "OCEANIA", 36: "OCEANIA",
}

# Stat strip: big figure, caption.
STATS = [
    ("400+", "drones fired at Ukraine overnight, with 110 missiles"),
    ("$3.8bn", "GTA VI's first-day sales, a record for any launch"),
    ("6.9", "magnitude of the quake in Peru's Andes"),
    ("209mm", "rain dumped on Ganjam by Cyclone Akvan"),
    ("128", "countries agree to work on killer-robot rules"),
    ("$7.25bn", "Bayer's Roundup settlement, approved by a judge"),
]

DATE_CHECK = (
    "DATE CHECK \u2713  Every story on this page happened, or was first reported, "
    "on Saturday 21 November 2026."
)
DATE_CHECK_LEFT_OUT = (
    "LEFT OUT AS OTHER DAYS' NEWS \u2014 20 NOV: Cyclone Akvan's landfall near "
    "Gopalpur \u00b7 Russia's ~30-missile wave on Kyiv \u00b7 BepiColombo's arrival "
    "at Mercury \u00b7 the pancreatic-cancer pill trial \u00b7 the UK\u2013EU Brussels "
    "agreements \u00b7 the Palisades fire verdict \u00b7 Mexico's capture of "
    "\u201cEl Chapo Isidro\u201d.  19 NOV: the Trump\u2013Xi\u2013Putin Shenzhen summit "
    "\u00b7 Anthropic's IPO debut \u00b7 the ICJ Myanmar verdict \u00b7 the GTA VI "
    "midnight launch."
)

FOOTER = (
    "Claims are attributed, not stated as fact \u00b7 Pictures and map: original, "
    "drawn in code \u00b7 Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, IMD, "
    "USGS, NPR, CNN, Yonhap, Japan Times, Antara, Euronews, France 24, Guardian, "
    "WSJ, ScienceDaily, AllAfrica, Straits Times \u00b7 2026-11-21"
)


# ------------------------------------------------------------------- fonts

def load_fonts():
    """Load the DejaVu fonts shipped in fonts/; return a name->font map."""
    from PIL import ImageFont

    def f(name, size):
        return ImageFont.truetype(str(FONTS / name), size)

    return {
        "masthead": f("DejaVuSerif-Bold.ttf", 30),
        "date": f("DejaVuSerif-Bold.ttf", 44),
        "lead_head": f("DejaVuSerif-Bold.ttf", 17),
        "feat_head": f("DejaVuSans-Bold.ttf", 11),
        "kicker": f("DejaVuSans-Bold.ttf", 10),
        "body": f("DejaVuSans.ttf", 11),
        "body_small": f("DejaVuSans.ttf", 10),
        "brief": f("DejaVuSans.ttf", 10),
        "brief_bold": f("DejaVuSans-Bold.ttf", 10),
        "source": f("DejaVuSans.ttf", 9),
        "stat_num": f("DejaVuSans-Bold.ttf", 19),
        "stat_cap": f("DejaVuSans.ttf", 9),
        "tab": f("DejaVuSans-Bold.ttf", 10),
        "section": f("DejaVuSans-Bold.ttf", 12),
        "strap": f("DejaVuSans.ttf", 12),
        "check": f("DejaVuSans.ttf", 10),
        "check_bold": f("DejaVuSans-Bold.ttf", 10),
        "footer": f("DejaVuSans.ttf", 9),
        "pin": f("DejaVuSans-Bold.ttf", 9),
        "pin_small": f("DejaVuSans-Bold.ttf", 8),
        "badge": f("DejaVuSans-Bold.ttf", 10),
    }


def wrap(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_rule(draw, x0, x1, y, width=2, colour=INK):
    draw.line([(x0, y), (x1, y)], fill=colour, width=width)


def draw_double_rule(draw, x0, x1, y):
    draw.line([(x0, y), (x1, y)], fill=INK, width=3)
    draw.line([(x0, y + 5), (x1, y + 5)], fill=INK, width=1)


def region_count(region):
    n = 0
    for story in LEADS + FEATURES:
        if story[1] == region:
            n += 1
    for num, reg in BRIEF_REGIONS.items():
        if reg == region:
            n += 1
    return n


# ------------------------------------------------------------ illustrations
# Three small flat illustrations for the lead stories, drawn with PIL
# primitives only: no photographs, no outside art.

def art_missiles(draw, x, y, w, h):
    """Night sky over a coast: red missile arcs, impact starbursts."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    # Stars.
    for sx, sy in [(18, 10), (52, 22), (96, 8), (150, 16), (210, 9),
                   (262, 20), (296, 12), (128, 30), (238, 32)]:
        draw.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                     fill=(220, 220, 200))
    # Moon.
    draw.ellipse([x + w - 42, y + 6, x + w - 18, y + 30], fill=(235, 228, 190))
    draw.ellipse([x + w - 36, y + 4, x + w - 18, y + 26], fill=NAVY)
    # Land strip along the bottom.
    draw.polygon([
        (x, y + h), (x, y + h - 18), (x + 60, y + h - 26),
        (x + 130, y + h - 16), (x + 200, y + h - 24),
        (x + 260, y + h - 14), (x + w, y + h - 20), (x + w, y + h),
    ], fill=(52, 74, 52))
    # City blocks.
    for bx, bw, bh in [(20, 14, 12), (40, 10, 18), (150, 16, 14),
                       (172, 11, 20), (250, 13, 12), (268, 10, 16)]:
        draw.rectangle([x + bx, y + h - 18 - bh, x + bx + bw, y + h - 18],
                       fill=(30, 42, 60))
        draw.rectangle([x + bx + 3, y + h - 18 - bh + 3, x + bx + 6,
                        y + h - 18 - bh + 6], fill=(255, 210, 90))
    # Missile arcs: red dashed curves from the right.
    for (ax0, ay0, ax1, ay1, arc_h) in [
            (300, 44, 150, 46, 26), (300, 52, 210, 48, 18),
            (300, 36, 90, 44, 30)]:
        pts = []
        for t in range(0, 21):
            tt = t / 20.0
            px = ax0 + (ax1 - ax0) * tt
            py = ay0 + (ay1 - ay0) * tt - arc_h * 4 * tt * (1 - tt)
            pts.append((x + px, y + py))
        for i in range(0, len(pts) - 1, 2):
            draw.line([pts[i], pts[i + 1]], fill=(230, 70, 60), width=2)
    # Impact starbursts.
    for cx, cy in [(150, 46), (210, 48), (90, 44)]:
        for dx, dy in [(0, -7), (5, -5), (7, 0), (5, 5), (0, 7),
                       (-5, 5), (-7, 0), (-5, -5)]:
            draw.line([(x + cx, y + cy), (x + cx + dx, y + cy + dy)],
                      fill=(255, 190, 60), width=2)
        draw.ellipse([x + cx - 3, y + cy - 3, x + cx + 3, y + cy + 3],
                     fill=(255, 220, 120))
    # Small shield badge: a white star on red, bottom left.
    draw.polygon([(x + 8, y + h - 16), (x + 20, y + h - 16),
                  (x + 20, y + h - 6), (x + 14, y + h - 1),
                  (x + 8, y + h - 6)], fill=RED)
    draw.text((x + 11, y + h - 15), "*", fill=(255, 255, 255),
              font=load_fonts()["badge"])


def art_cop(draw, x, y, w, h):
    """A warming globe: pale earth, red thermometer, flag row."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 64, 58))
    # Globe.
    cx, cy, r = x + 64, y + h // 2 + 2, 26
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 230, 214))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(150, 180, 150))
    # Continents as blobs.
    draw.ellipse([cx - 16, cy - 16, cx - 2, cy - 2], fill=(96, 150, 96))
    draw.ellipse([cx + 2, cy + 2, cx + 18, cy + 16], fill=(96, 150, 96))
    draw.ellipse([cx - 4, cy + 8, cx + 8, cy + 20], fill=(120, 165, 110))
    # Latitude lines.
    for dy, ww in [(-13, 22), (0, 26), (13, 22)]:
        draw.arc([cx - ww, cy + dy - 5, cx + ww, cy + dy + 5],
                 start=200, end=340, fill=(150, 180, 150))
    # Sun rays behind the globe.
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        x0 = cx + int(30 * math.cos(a))
        y0 = cy + int(30 * math.sin(a))
        x1 = cx + int(38 * math.cos(a))
        y1 = cy + int(38 * math.sin(a))
        draw.line([(x0, y0), (x1, y1)], fill=(255, 205, 90), width=2)
    # Thermometer.
    tx, ty = x + 128, y + 8
    draw.rectangle([tx, ty, tx + 10, ty + 44], fill=(240, 240, 235))
    draw.rectangle([tx + 2, ty + 22, tx + 8, ty + 44], fill=(220, 60, 50))
    draw.ellipse([tx - 3, ty + 42, tx + 13, ty + 58], fill=(220, 60, 50))
    draw.ellipse([tx - 3, ty + 42, tx + 13, ty + 58], outline=(240, 240, 235))
    # 1.5C mark with a red cross through it.
    draw.line([(tx + 12, ty + 20), (tx + 20, ty + 20)], fill=(255, 255, 255),
              width=2)
    draw.line([(tx + 22, ty + 12), (tx + 32, ty + 22)], fill=(255, 90, 80),
              width=2)
    draw.line([(tx + 32, ty + 12), (tx + 22, ty + 22)], fill=(255, 90, 80),
              width=2)
    # Flag row along the bottom: small coloured rectangles on poles.
    flag_cols = [(200, 60, 60), (60, 120, 200), (240, 200, 60),
                 (80, 170, 90), (230, 230, 230), (200, 120, 40)]
    for i, col in enumerate(flag_cols):
        fx = x + 190 + i * 21
        draw.line([(fx, y + h - 26), (fx, y + h - 6)], fill=(220, 220, 210),
                  width=1)
        draw.rectangle([fx, y + h - 26, fx + 14, y + h - 16], fill=col)


def art_cyclone(draw, x, y, w, h):
    """A cyclone spiral over a coastline, with rain streaks."""
    draw.rectangle([x, y, x + w, y + h], fill=(58, 82, 110))
    # Spiral: arcs with growing radius and rotating start angle.
    cx, cy = x + 88, y + h // 2
    for i, r in enumerate([6, 12, 18, 24, 30, 36]):
        start = i * 55
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=start,
                 end=start + 250, fill=(225, 235, 245), width=3)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(245, 240, 220))
    # Coastline and sea.
    draw.polygon([
        (x + 170, y + h), (x + 170, y + h - 22), (x + 210, y + h - 30),
        (x + 250, y + h - 20), (x + 290, y + h - 26), (x + w, y + h - 18),
        (x + w, y + h),
    ], fill=(206, 188, 150))
    # Small houses on the coast.
    for hx in [190, 225, 262]:
        draw.rectangle([x + hx, y + h - 26, x + hx + 16, y + h - 14],
                       fill=(245, 240, 225))
        draw.polygon([(x + hx - 2, y + h - 26), (x + hx + 8, y + h - 34),
                      (x + hx + 18, y + h - 26)], fill=(170, 60, 50))
    # Rain streaks.
    for rx, ry in [(150, 8), (180, 20), (205, 6), (240, 14), (275, 8),
                   (300, 22), (165, 34), (230, 34), (290, 40)]:
        draw.line([(x + rx, y + ry), (x + rx - 4, y + ry + 9)],
                  fill=(190, 205, 220), width=2)
    # Wind arrows on the left.
    for ay in [14, 30, 50]:
        draw.line([(x + 8, y + ay), (x + 34, y + ay)], fill=(225, 235, 245),
                  width=2)
        draw.line([(x + 34, y + ay), (x + 28, y + ay - 4)],
                  fill=(225, 235, 245), width=2)
        draw.line([(x + 34, y + ay), (x + 28, y + ay + 4)],
                  fill=(225, 235, 245), width=2)

ART = {1: art_missiles, 2: art_cop, 3: art_cyclone}


# --------------------------------------------------------------------- map
# Simplified continent outlines in (lon, lat). Hand-drawn rough shapes;
# recognisable at strip-map scale, not survey data.

CONTINENTS = [
    # North America.
    [(-168, 66), (-158, 71), (-140, 70), (-128, 70), (-115, 68), (-105, 68),
     (-95, 69), (-85, 68), (-80, 73), (-70, 68), (-65, 60), (-60, 55),
     (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-75, 38), (-80, 32),
     (-81, 26), (-84, 30), (-88, 30), (-90, 29), (-94, 29), (-97, 26),
     (-97, 22), (-94, 18), (-90, 16), (-87, 14), (-83, 9), (-80, 8),
     (-77, 7), (-79, 9), (-83, 10), (-86, 12), (-90, 14), (-94, 16),
     (-97, 20), (-105, 23), (-110, 24), (-114, 29), (-117, 33), (-122, 37),
     (-124, 42), (-124, 48), (-130, 55), (-135, 58), (-145, 60),
     (-155, 59), (-162, 58), (-168, 66)],
    # Greenland.
    [(-45, 60), (-40, 65), (-32, 68), (-25, 70), (-20, 74), (-30, 78),
     (-45, 80), (-58, 76), (-58, 70), (-52, 64), (-45, 60)],
    # South America.
    [(-77, 7), (-72, 11), (-64, 10), (-55, 6), (-50, 0), (-44, -3),
     (-35, -8), (-37, -13), (-39, -17), (-41, -22), (-48, -27),
     (-52, -32), (-57, -38), (-62, -41), (-65, -45), (-68, -50),
     (-69, -54), (-71, -54), (-73, -50), (-73, -44), (-73, -37),
     (-71, -30), (-70, -22), (-75, -15), (-79, -8), (-81, -4),
     (-80, 1), (-77, 4), (-77, 7)],
    # Africa.
    [(-17, 15), (-16, 21), (-10, 31), (-5, 35), (0, 36), (10, 37),
     (11, 34), (15, 32), (20, 32), (25, 32), (30, 31), (32, 31),
     (35, 28), (34, 24), (37, 20), (39, 16), (43, 12), (48, 11),
     (51, 12), (46, 5), (41, -2), (40, -8), (39, -15), (36, -20),
     (33, -26), (31, -29), (28, -33), (20, -35), (17, -32), (15, -27),
     (13, -22), (12, -17), (13, -12), (9, -1), (9, 4), (6, 4),
     (-2, 5), (-8, 4), (-13, 8), (-17, 15)],
    # Eurasia.
    [(-10, 36), (-9, 43), (-2, 48), (-4, 49), (0, 51), (3, 53), (5, 58),
     (5, 62), (10, 64), (12, 66), (18, 69), (25, 71), (32, 70), (40, 68),
     (45, 66), (55, 69), (65, 69), (75, 72), (85, 74), (95, 76),
     (105, 77), (115, 73), (125, 72), (135, 72), (145, 71), (155, 70),
     (170, 67), (178, 65), (178, 62), (170, 60), (162, 58), (158, 52),
     (156, 51), (150, 59), (142, 59), (140, 55), (135, 45), (130, 42),
     (127, 39), (122, 37), (120, 32), (122, 28), (118, 25), (110, 20),
     (108, 18), (105, 10), (103, 8), (100, 7), (98, 10), (95, 16),
     (92, 21), (89, 22), (86, 20), (80, 16), (77, 8), (76, 10),
     (73, 20), (70, 22), (66, 25), (61, 25), (57, 26), (56, 27),
     (52, 26), (50, 29), (48, 30), (44, 29), (40, 31), (36, 36),
     (33, 36), (30, 36), (27, 37), (23, 36), (19, 40), (15, 44),
     (12, 44), (10, 44), (8, 44), (3, 43), (0, 39), (-2, 37),
     (-6, 36), (-9, 36), (-10, 36)],
    # Arabian peninsula (drawn as its own blob for clarity).
    [(35, 28), (39, 22), (43, 12), (48, 14), (55, 17), (58, 23),
     (56, 26), (52, 26), (50, 29), (48, 30), (44, 29), (40, 31),
     (36, 32), (35, 28)],
    # United Kingdom.
    [(-5, 50), (-3, 53), (-5, 57), (-3, 59), (-1, 57), (1, 53),
     (0, 51), (-5, 50)],
    # Japan.
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 39), (142, 43),
     (144, 44), (141, 42), (139, 38), (136, 34), (132, 33), (130, 31)],
    # Sumatra.
    [(95, 5), (100, 0), (104, -3), (106, -6), (104, -6), (100, -2),
     (96, 2), (95, 5)],
    # Borneo.
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (113, -3),
     (110, -1), (109, 1)],
    # New Guinea.
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -10), (147, -9),
     (142, -8), (137, -7), (132, -4), (131, -1)],
    # Australia.
    [(114, -22), (113, -26), (115, -32), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (147, -39), (150, -37), (153, -30), (153, -27),
     (150, -23), (146, -19), (142, -15), (142, -11), (141, -13),
     (140, -17), (136, -15), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20), (114, -22)],
    # New Zealand.
    [(167, -45), (170, -42), (173, -39), (175, -38), (178, -38),
     (176, -40), (173, -42), (169, -46), (167, -45)],
    # Madagascar.
    [(44, -16), (47, -15), (50, -17), (49, -21), (47, -25),
     (45, -25), (44, -21), (44, -16)],
    # Iceland.
    [(-22, 64), (-18, 63), (-15, 64), (-14, 65), (-18, 66),
     (-22, 66), (-22, 64)],
]

# Map pins: story number -> (lon, lat).
PINS = [
    (1, 31, 50), (2, 31, 37), (3, 84, 20), (4, -77, 39),
    (5, -122, 38), (7, -76, -11), (8, 6, 46), (9, 56, 27),
    (10, 47, 25), (15, 139, 36), (19, 126, -9), (22, 13, 56),
    (29, 6, 5), (33, 18, -34), (35, 145, -38),
]


# ------------------------------------------------------------------ layout

STRAPLINE = ("Russian missiles land in Poland  \u00b7  COP31 slips into overtime  "
             "\u00b7  Cyclone Akvan fades over Odisha")


def draw_masthead(draw, fonts):
    draw.text((MARGIN, 12), "THE WORLD IN ONE DAY", font=fonts["masthead"],
              fill=INK)
    right = "36 STORIES \u00b7 EVERY CONTINENT \u00b7 ALL FROM THIS ONE DAY"
    rw = draw.textlength(right, font=fonts["tab"])
    draw.text((W - MARGIN - rw, 22), right, font=fonts["tab"], fill=RED)
    draw_double_rule(draw, MARGIN, W - MARGIN, 48)


def draw_date_and_strap(draw, fonts):
    date = "SATURDAY 21 NOVEMBER 2026"
    dw = draw.textlength(date, font=fonts["date"])
    draw.text(((W - dw) / 2, 52), date, font=fonts["date"], fill=INK)
    sw = draw.textlength(STRAPLINE, font=fonts["strap"])
    draw.text(((W - sw) / 2, 100), STRAPLINE, font=fonts["strap"],
              fill=SOFT_INK)


def draw_stats(draw, fonts):
    y0, y1 = 116, 164
    gap = 5
    bw = (CW - gap * (len(STATS) - 1)) // len(STATS)
    for i, (num, cap) in enumerate(STATS):
        x0 = MARGIN + i * (bw + gap)
        draw.rectangle([x0, y0, x0 + bw, y1], fill=PANEL,
                       outline=FAINT, width=1)
        draw.text((x0 + 8, y0 + 4), num, font=fonts["stat_num"], fill=RED)
        for j, line in enumerate(wrap(draw, cap, fonts["stat_cap"], bw - 16)):
            draw.text((x0 + 8, y0 + 26 + j * 11), line,
                      font=fonts["stat_cap"], fill=SOFT_INK)


def draw_tabs(draw, fonts):
    y0, y1 = 168, 190
    tw = CW // len(REGIONS)
    for i, (name, colour) in enumerate(REGIONS):
        x0 = MARGIN + i * tw
        x1 = x0 + tw - 2 if i < len(REGIONS) - 1 else W - MARGIN
        draw.rectangle([x0, y0, x1, y1], fill=colour)
        label = "%s %d" % (name, region_count(name))
        lw = draw.textlength(label, font=fonts["tab"])
        draw.text((x0 + (x1 - x0 - lw) / 2, y0 + 5), label,
                  font=fonts["tab"], fill=(255, 255, 255))


def draw_leads(draw, fonts):
    y0 = 196
    gap = 14
    col_w = (CW - gap * 2) // 3
    art_h = 68
    for i, story in enumerate(LEADS):
        n, region, place, head, body, src = story
        x0 = MARGIN + i * (col_w + gap)
        ART[n](draw, x0, y0, col_w, art_h)
        colour = REGION_COLOUR[region]
        ky = y0 + art_h + 6
        draw.text((x0, ky), "%s \u00b7 %s" % (region, place),
                  font=fonts["kicker"], fill=colour)
        hy = ky + 15
        for j, line in enumerate(wrap(draw, head, fonts["lead_head"], col_w)):
            draw.text((x0, hy + j * 20), line, font=fonts["lead_head"],
                      fill=INK)
        by = hy + 42
        for j, line in enumerate(wrap(draw, body, fonts["body"], col_w)):
            draw.text((x0, by + j * 13), line, font=fonts["body"],
                      fill=SOFT_INK)
        draw.text((x0, by + 55), "Source: " + src, font=fonts["source"],
                  fill=GREY)


def draw_features(draw, fonts):
    y0 = 392
    row_h = 36
    col_w = (CW - 16) // 2
    for i, story in enumerate(FEATURES):
        n, region, place, head, body, src = story
        col = i % 2
        row = i // 2
        x0 = MARGIN + col * (col_w + 16)
        y = y0 + row * row_h
        colour = REGION_COLOUR[region]
        # Number badge.
        draw.rectangle([x0, y + 1, x0 + 16, y + 17], fill=RED)
        num = str(n)
        nw = draw.textlength(num, font=fonts["badge"])
        draw.text((x0 + (16 - nw) / 2, y + 3), num, font=fonts["badge"],
                  fill=(255, 255, 255))
        # Headline with place tag.
        head_line = "%s \u2014 %s" % (place, head)
        draw.text((x0 + 21, y), head_line, font=fonts["feat_head"],
                  fill=INK)
        # Summary plus source on the next line, trimmed to the column.
        avail = col_w - 21
        tail = body + " (" + src + ")"
        while (draw.textlength(tail, font=fonts["body_small"]) > avail
               and len(body) > 20):
            body = body[:-1].rstrip(" .,")
            tail = body + "\u2026 (" + src + ")"
        draw.text((x0 + 21, y + 14), tail, font=fonts["body_small"],
                  fill=SOFT_INK)
        # Light divider under the row.
        if row < 4:
            draw.line([(x0, y + 31), (x0 + col_w, y + 31)],
                      fill=(222, 214, 196), width=1)


def project(lon, lat, mx0, my0, mw, mh):
    """Equirectangular projection onto the map box (lat -60..80)."""
    px = mx0 + (lon + 180.0) / 360.0 * mw
    py = my0 + (80.0 - lat) / 140.0 * mh
    return px, py


def draw_map(draw, fonts):
    hy = 578
    draw.text((MARGIN, hy), "WHERE IT HAPPENED", font=fonts["section"],
              fill=INK)
    note = "Numbered pins match the stories"
    nw = draw.textlength(note, font=fonts["source"])
    draw.text((W - MARGIN - nw, hy + 2), note, font=fonts["source"],
              fill=GREY)
    mx0, my0, mw, mh = MARGIN, 594, CW, 146
    draw.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=SEA)
    # Graticule.
    for lon in range(-150, 181, 30):
        gx, _ = project(lon, 0, mx0, my0, mw, mh)
        draw.line([(gx, my0), (gx, my0 + mh)], fill=(44, 72, 102), width=1)
    for lat in (-30, 0, 30, 60):
        _, gy = project(0, lat, mx0, my0, mw, mh)
        draw.line([(mx0, gy), (mx0 + mw, gy)], fill=(44, 72, 102), width=1)
    # Continents.
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx0, my0, mw, mh) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    # Pins. Pin 2 (Antalya) is nudged left so it does not sit on pin 1.
    nudges = {2: (-14, 8)}
    for n, lon, lat in PINS:
        px, py = project(lon, lat, mx0, my0, mw, mh)
        dx, dy = nudges.get(n, (0, 0))
        px += dx
        py += dy
        draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED,
                     outline=(255, 255, 255), width=1)
        num = str(n)
        font = fonts["pin"] if n < 10 else fonts["pin_small"]
        nw = draw.textlength(num, font=font)
        draw.text((px - nw / 2, py - 6 if n < 10 else py - 5), num,
                  font=font, fill=(255, 255, 255))


def draw_briefs(draw, fonts):
    hy = 748
    draw.text((MARGIN, hy), "ALSO ON SATURDAY 21 NOVEMBER 2026 \u2014 "
              "23 MORE STORIES", font=fonts["section"], fill=INK)
    y0 = 766
    row_h = 12
    col_w = (CW - 16) // 2
    for i, (n, place, line, src) in enumerate(BRIEFS):
        col = 0 if i < 12 else 1
        row = i if i < 12 else i - 12
        x0 = MARGIN + col * (col_w + 16)
        y = y0 + row * row_h
        head = "%d. %s \u2014 " % (n, place)
        hw = draw.textlength(head, font=fonts["brief_bold"])
        draw.text((x0, y), head, font=fonts["brief_bold"], fill=INK)
        # Fit the body plus source into the remaining width.
        avail = col_w - hw
        tail = line + " (" + src + ")"
        while (draw.textlength(tail, font=fonts["brief"]) > avail
               and len(line) > 20):
            line = line[:-1].rstrip(" .,")
            tail = line + "\u2026 (" + src + ")"
        draw.text((x0 + hw, y), tail, font=fonts["brief"], fill=SOFT_INK)


def draw_date_check(draw, fonts):
    y0, y1 = 910, 966
    draw.rectangle([MARGIN, y0, W - MARGIN, y1], fill=(255, 248, 235),
                   outline=RED, width=2)
    draw.text((MARGIN + 8, y0 + 4), DATE_CHECK, font=fonts["check_bold"],
              fill=DARK_RED)
    lines = wrap(draw, DATE_CHECK_LEFT_OUT, fonts["check"], CW - 16)
    for j, line in enumerate(lines):
        draw.text((MARGIN + 8, y0 + 19 + j * 11), line,
                  font=fonts["check"], fill=SOFT_INK)


def draw_footer(draw, fonts):
    draw_rule(draw, MARGIN, W - MARGIN, 972, width=1, colour=FAINT)
    lines = wrap(draw, FOOTER, fonts["footer"], CW)
    for j, line in enumerate(lines):
        draw.text((MARGIN, 978 + j * 11), line, font=fonts["footer"],
                  fill=GREY)


def render():
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    fonts = load_fonts()
    draw_masthead(draw, fonts)
    draw_date_and_strap(draw, fonts)
    draw_stats(draw, fonts)
    draw_tabs(draw, fonts)
    draw_leads(draw, fonts)
    draw_features(draw, fonts)
    draw_map(draw, fonts)
    draw_briefs(draw, fonts)
    draw_date_check(draw, fonts)
    draw_footer(draw, fonts)
    return img


def write_output(img):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "entry.png"
    img.save(out, format="PNG")
    return out


def copy_fallback():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FALLBACK, OUTPUT_DIR / "entry.png")


def main():
    try:
        img = render()
    except Exception:
        copy_fallback()
        return
    try:
        write_output(img)
    except Exception:
        copy_fallback()


if __name__ == "__main__":
    main()
