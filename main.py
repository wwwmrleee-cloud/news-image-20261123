# news-image-20261123 -- one 1024x1024 image summing up the world news of
# Monday 23 November 2026: 50 sourced stories across 7 regions, 3 lead
# stories, a timeline, a numbers band and a date check.
#
# Pure Python 3 standard library only: a hand-made 5x7 pixel font and a
# small PNG encoder written here. No fonts, no images, no network, no clock,
# no randomness -- two runs write byte-identical files.
#
# Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
BG      = (13, 21, 38)     # deep navy page
PANEL   = (16, 29, 51)     # panel navy
PANEL2  = (21, 36, 63)     # lighter panel
GOLD    = (245, 184, 29)   # lead gold
WHITE   = (242, 245, 249)
MUTED   = (159, 176, 199)
FAINT   = (120, 136, 160)
RED     = (235, 87, 87)
GREEN   = (86, 204, 132)
BLUE    = (96, 165, 250)
ORANGE  = (251, 146, 60)
PURPLE  = (192, 132, 252)
TEAL    = (45, 212, 191)
PINK    = (244, 114, 182)

REGION_COLORS = {
    "NORTH AMERICA": BLUE,
    "LATIN AMERICA": GREEN,
    "EUROPE": GOLD,
    "AFRICA": ORANGE,
    "MIDDLE EAST": RED,
    "ASIA-PACIFIC": TEAL,
    "GLOBAL": PURPLE,
}

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 pixels, '#' = on, '.' = off.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "[": ("####.", "#....", "#....", "#....", "#....", "#....", "####."),
    "]": (".####", "....#", "....#", "....#", "....#", "....#", ".####."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    r, g, b = color
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i] = r
            px[i + 1] = g
            px[i + 2] = b


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def draw_text(x, y, text, color, scale=1):
    """Uppercase-only 5x7 font. Returns width drawn."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    if scale == 1:
                        set_px(cx + col, y + row, color)
                    else:
                        fill_rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
        cx += 6 * scale
    return cx - x


def text_w(text, scale=1):
    return len(text) * 6 * scale - scale


def wrap(text, max_chars):
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- data
# (region, headline, source, confidence) -- confidence HIGH: wire service or
# major outlet (AP, AFP, Reuters, NYT, CNN, WSJ, BBC); MED: any other outlet.
STORIES = [
    ("NORTH AMERICA",
     "Nvidia board brings back Jensen Huang as CEO; Trump says he convinced the board",
     "USATODAY", "HIGH"),
    ("NORTH AMERICA",
     "Trump condemns Newsom death-row commutations on Justice Dept visit",
     "CNN", "HIGH"),
    ("NORTH AMERICA",
     "Trump halts Iowa lead azide detonation; appeals court lifts the stay",
     "DM REGISTER", "HIGH"),
    ("NORTH AMERICA",
     "Rep. Jimmy Gomez resigns after ethics panel finds sexual misconduct",
     "AP", "HIGH"),
    ("NORTH AMERICA",
     "Pentagon rebukes Canada over defence spending and F-35 review",
     "AP", "HIGH"),
    ("NORTH AMERICA",
     "US drone over Mexico helped capture Sinaloa drug lord",
     "AP", "HIGH"),
    ("NORTH AMERICA",
     "Two killed in shooting at US university",
     "ACCESS24", "MED"),
    ("LATIN AMERICA",
     "Mexico confirms 4 soldiers, 7 gunmen killed in Sinaloa kingpin arrest",
     "BREITBART", "MED"),
    ("LATIN AMERICA",
     "Bolsonaro taken to ICU with acute bowel obstruction",
     "BREITBART", "MED"),
    ("LATIN AMERICA",
     "Bukele seeks third term as El Salvador president",
     "BREITBART", "MED"),
    ("LATIN AMERICA",
     "Bukele says 3 Salvadoran soldiers died in Haiti blast",
     "AP", "HIGH"),
    ("LATIN AMERICA",
     "Mexico and China agree to form trade working group",
     "STD TOPIC", "MED"),
    ("LATIN AMERICA",
     "Argentina borrowing costs rise as Milei popularity falls",
     "FT", "HIGH"),
    ("EUROPE",
     "COP31 ends with no climate pact; EU rejects deal; Guterres deeply disappointed",
     "UN NEWS", "HIGH"),
    ("EUROPE",
     "Central European leaders reject EU budget proposal",
     "REUTERS", "HIGH"),
    ("EUROPE",
     "France rejects EU budget over farmer income guarantees",
     "MENAFN", "MED"),
    ("EUROPE",
     "Merz: mistake not to admit Ukraine to NATO in 2008",
     "EURONEWS", "MED"),
    ("EUROPE",
     "Von der Leyen and Kushner clash over peace talks sequence",
     "EURONEWS", "MED"),
    ("EUROPE",
     "Finland summons Russian ambassador over airspace violation",
     "EURONEWS", "MED"),
    ("EUROPE",
     "EU opens antitrust probe into Coca-Cola distributor",
     "EURONEWS", "MED"),
    ("EUROPE",
     "Analysis puts Russian war dead above 700,000",
     "RFE/RL", "HIGH"),
    ("EUROPE",
     "Russian drone briefly violated Polish airspace",
     "LIVEUAMAP", "MED"),
    ("EUROPE",
     "EU to bar Russians from company posts, ex-combatants from entry",
     "LIVEUAMAP", "MED"),
    ("AFRICA",
     "Ukraine sinks Russian corvette Merkury off Benghazi; Zelensky claims attack",
     "CNN", "HIGH"),
    ("AFRICA",
     "UN mission in Libya urges probe into Benghazi port attacks",
     "UN NEWS", "HIGH"),
    ("AFRICA",
     "Tripoli condemns Ukraine attack, demands clarifications",
     "NYT", "HIGH"),
    ("AFRICA",
     "Kenya and DR Congo restore full diplomatic relations",
     "FRANCE24", "HIGH"),
    ("AFRICA",
     "DR Congo reimposes cobalt export ban",
     "FT", "HIGH"),
    ("AFRICA",
     "Heavy fighting in Ituri traps Ebola responders",
     "WHO", "HIGH"),
    ("AFRICA",
     "US diplomat Boulos regrets continuing Sudan violence",
     "PANA", "MED"),
    ("AFRICA",
     "South Africa's first female deputy president dies",
     "NYT", "HIGH"),
    ("MIDDLE EAST",
     "Three tankers hit naval mines in Strait of Hormuz; attacks at wartime high",
     "CBS", "HIGH"),
    ("MIDDLE EAST",
     "Houthis say Saudi strike on Hodeidah kills 17",
     "AFP", "HIGH"),
    ("MIDDLE EAST",
     "Israeli strike kills UNRWA worker in Gaza; second strike kills 2",
     "REUTERS", "HIGH"),
    ("MIDDLE EAST",
     "Eisenkot condemns settler arson attacks in West Bank",
     "BWORLD", "MED"),
    ("MIDDLE EAST",
     "Trump warns Iran of very traumatic outcome if nuclear deal fails",
     "ACCESS24", "MED"),
    ("MIDDLE EAST",
     "Yemen government claims 647 strikes against Houthi targets",
     "CBS", "HIGH"),
    ("ASIA-PACIFIC",
     "China unveils Shenzhou-24 crew, first foreign astronaut aboard station",
     "AP", "HIGH"),
    ("ASIA-PACIFIC",
     "India gives Nepal $1.62bn flood-recovery package",
     "BWORLD", "MED"),
    ("ASIA-PACIFIC",
     "Nepal and India launch direct rail service",
     "STD TOPIC", "MED"),
    ("ASIA-PACIFIC",
     "Indonesia factory fire kills 24, about 30 missing",
     "AP", "HIGH"),
    ("ASIA-PACIFIC",
     "South Korea education minister quits over exam cheating",
     "BWORLD", "MED"),
    ("ASIA-PACIFIC",
     "South Korea says Russian aircraft entered air defence zone",
     "AP", "HIGH"),
    ("ASIA-PACIFIC",
     "China sentences official to death for leaking secrets",
     "AP", "HIGH"),
    ("ASIA-PACIFIC",
     "US lead over China in Asia narrows to record low",
     "LOWY", "MED"),
    ("GLOBAL",
     "Anthropic shares slide after debut",
     "STD TOPIC", "MED"),
    ("GLOBAL",
     "Treasury sanctions Iran-linked money-movers",
     "STD TOPIC", "MED"),
    ("GLOBAL",
     "Guterres urges greater AI regulation at Barbados summit",
     "UN NEWS", "HIGH"),
    ("GLOBAL",
     "Oil prices ease toward three-month low",
     "STD TOPIC", "MED"),
    ("GLOBAL",
     "Hunger Games prequel tops box office with $120m",
     "STD TOPIC", "MED"),
]

LEADS = [
    ("1  NVIDIA BRINGS BACK HUANG", "Board unanimously reinstates Jensen Huang as CEO 11 days after he quit; Trump says he convinced the board; shares jump about 30%. USATODAY"),
    ("2  UKRAINE SINKS WARSHIP OFF LIBYA", "Naval drones sink Russian corvette Merkury at Benghazi and hit cargo ship MV Angara; Zelensky claims the attack; Libya demands answers. CNN"),
    ("3  COP31 ENDS WITH NO DEAL", "Climate talks in Antalya collapse as the EU rejects a pact that drops fossil fuels; Guterres deeply disappointed; longest COP ever. UN NEWS"),
]

TIMELINE = [
    ("SUN 22 NOV ANTALYA", "COP31 ends with no climate pact"),
    ("MON 23 NOV JAKARTA", "Indonesia factory fire kills 24"),
    ("MON 23 NOV BENGHAZI", "Zelensky claims Ukraine sank corvette"),
    ("MON 23 NOV NEW YORK", "Nvidia brings back Jensen Huang"),
    ("MON 23 NOV BRATISLAVA", "Central Europe rejects EU budget"),
]

NUMBERS = [
    ("50", "STORIES"),
    ("7", "REGIONS"),
    ("+30%", "NVIDIA SHARES"),
    ("700K+", "RUSSIAN WAR DEAD"),
    ("24", "INDONESIA FIRE DEAD"),
    ("$1.62BN", "INDIA-NEPAL AID"),
    ("$120M", "HUNGER GAMES"),
    ("647", "YEMEN STRIKES"),
]

# ---------------------------------------------------------------- layout
def draw_header():
    fill_rect(0, 0, W, 104, PANEL)
    fill_rect(0, 104, W, 4, GOLD)
    draw_text(16, 14, "WORLD NEWS", GOLD, scale=3)
    draw_text(16, 50, "MONDAY 23 NOVEMBER 2026", WHITE, scale=2)
    draw_text(16, 78, "50 SOURCED STORIES  -  7 REGIONS  -  EVERY STORY MARKED WITH SOURCE AND CONFIDENCE",
              MUTED, scale=1)
    # date-check box, right side
    fill_rect(724, 14, 284, 76, PANEL2)
    draw_text(736, 22, "DATE CHECK", GOLD, scale=1)
    draw_text(736, 36, "MONDAY 23 NOV 2026", WHITE, scale=1)
    draw_text(736, 50, "DAY 327 OF 2026 - 38 DAYS LEFT", WHITE, scale=1)
    draw_text(736, 64, "EVENTS OF 23 NOV 2026", FAINT, scale=1)


def draw_leads():
    y = 116
    draw_text(16, y, "THE DAY IN THREE STORIES", GOLD, scale=1)
    y += 18
    col_w = 328
    for i, (title, body) in enumerate(LEADS):
        x = 16 + i * (col_w + 8)
        fill_rect(x, y, col_w, 62, PANEL2)
        fill_rect(x, y, 4, 62, GOLD)
        draw_text(x + 12, y + 8, title, GOLD, scale=1)
        for j, line in enumerate(wrap(body, 50)):
            draw_text(x + 12, y + 22 + j * 10, line, WHITE, scale=1)
    return y + 62


def draw_stories(top):
    left_regions = ["NORTH AMERICA", "LATIN AMERICA", "EUROPE"]
    right_regions = ["AFRICA", "MIDDLE EAST", "ASIA-PACIFIC", "GLOBAL"]
    col_x = [16, 524]
    col_w = 484
    max_chars = 78
    bottoms = []
    for ci, regions in enumerate((left_regions, right_regions)):
        x = col_x[ci]
        y = top
        for region in regions:
            color = REGION_COLORS[region]
            count = sum(1 for s in STORIES if s[0] == region)
            fill_rect(x, y, col_w, 16, PANEL)
            fill_rect(x, y, 4, 16, color)
            draw_text(x + 10, y + 4, "%s  (%d)" % (region, count), color, scale=1)
            y += 18
            for (reg, headline, source, conf) in STORIES:
                if reg != region:
                    continue
                tag = " [%s - %s]" % (source, conf[0])
                lines = wrap(headline, max_chars)
                lines = lines[:2]
                if len(lines) == 2:
                    # squeeze the source tag onto line 2 when it fits
                    room = max_chars - len(lines[1])
                    if len(tag) <= room:
                        lines[1] = lines[1] + tag
                    else:
                        lines[1] = lines[1][: max_chars - len(tag)] + tag
                else:
                    lines.append(tag)
                draw_text(x + 2, y, lines[0], WHITE, scale=1)
                if len(lines) > 1:
                    draw_text(x + 2, y + 10, lines[1], MUTED, scale=1)
                y += 21
            y += 2
        bottoms.append(y)
    return max(bottoms)


def draw_timeline(top):
    y = top + 6
    fill_rect(0, y, W, 4, GOLD)
    y += 12
    draw_text(16, y, "TIMELINE  -  23 NOVEMBER 2026", GOLD, scale=1)
    y += 18
    col_w = 200
    for i, (when, what) in enumerate(TIMELINE):
        x = 16 + i * (col_w + 4)
        draw_text(x, y, when, WHITE, scale=1)
        for j, line in enumerate(wrap(what, 30)):
            draw_text(x, y + 10 + j * 10, line, MUTED, scale=1)
    return y + 30


def draw_numbers(top):
    y = top + 4
    fill_rect(16, y, 992, 46, PANEL2)
    x = 28
    for value, label in NUMBERS:
        draw_text(x, y + 6, value, GOLD, scale=2)
        draw_text(x, y + 28, label, MUTED, scale=1)
        x += max(text_w(value, 2), text_w(label, 1)) + 30
    return y + 46


def draw_footer(top):
    y = top + 6
    draw_text(16, y, "SOURCES: AP, AFP, REUTERS, NYT, CNN, USATODAY, FT, UN NEWS, WHO, PANA, CBS,",
              FAINT, scale=1)
    draw_text(16, y + 11,
              "BWORLD, ACCESS24, MENAFN, EURONEWS, LIVEUAMAP, FRANCE24, LOWY, STD TOPIC, BREITBART, DM REGISTER",
              FAINT, scale=1)
    draw_text(16, y + 22,
              "CONFIDENCE: HIGH = WIRE SERVICE OR MAJOR OUTLET. MED = OTHER OUTLET. NUMBERS AS REPORTED 23 NOV 2026.",
              FAINT, scale=1)
    draw_text(16, y + 33, "PROGRAM-GENERATED IMAGE  -  NO PHOTOS  -  NEWS-IMAGE-20261123  -  MAKE.FUN",
              GOLD, scale=1)
    return y + 33


# ---------------------------------------------------------------- PNG
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += px[yy * W * 3:(yy + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    return data


def main():
    fill_rect(0, 0, W, H, BG)
    draw_header()
    y = draw_leads()
    y = draw_stories(y + 8)
    y = draw_timeline(y)
    y = draw_numbers(y)
    end = draw_footer(y)
    assert end < H, "layout overflows: footer ends at %d" % end
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png())
    print("wrote %s (%dx%d), footer ends at y=%d" % (path, W, H, end))


if __name__ == "__main__":
    main()
