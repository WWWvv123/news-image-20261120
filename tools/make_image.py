#!/usr/bin/env python3
"""Draw the 20 November 2026 world-news poster for the make.fun bounty.

Reads nothing from the network. Every story below was checked against news
reports of Friday 20 November 2026 before it was written into the picture:

  1. Trump, Xi and Putin hold their first three-way summit in Shenzhen and
     issue a joint "peace declaration" (Fox News, Le Monde, BBC).
  2. Anthropic lists on the Nasdaq (ticker ANT): IPO price $83, opened at
     $111.50, closed at $97.17, up 17%, the largest IPO on record at $81bn
     (WSJ, Investopedia, Barron's, Morningstar). The Nasdaq fell 2.3% the
     same day.
  3. The International Court of Justice rules Myanmar committed genocide
     against the Rohingya in its 2017 crackdown, 9 votes to 6 (UN News, BBC).
  4. Taiwan stocks plunge 2,200 points intraday as AI-bubble fears hit Asian
     markets; regulators unveil rescue measures (SimpleLife News).
  5. The UK pledges 1,000+ long-range drones for Ukraine in a 260m pound
     package as Europe readies new peace talks with Russia.
  6. The COP31 draft deal drops its fossil-fuel wording (UN News).

Output: entry.png, 1024x1024, under 1 MiB. Run: python3 tools/make_image.py
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952

PAPER = (248, 245, 238)
INK = (25, 25, 25)
NAVY = (22, 50, 79)
NAVY_LIGHT = (215, 222, 232)
RED = (179, 38, 30)
RED_LIGHT = (255, 157, 138)
MUTED = (90, 90, 90)
PANEL = (255, 255, 255)
BORDER = (217, 211, 195)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Split text into lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, color, max_w, leading):
    """Draw wrapped text; return the y just below the block."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=color, anchor="la")
        y += leading
    return y


def draw_globe(d, cx, cy, r, color, width=5):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
              outline=color, width=3)
    d.line([cx - r, cy, cx + r, cy], fill=color, width=3)
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55],
          start=200, end=340, fill=color, width=3)
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55],
          start=20, end=160, fill=color, width=3)
    for dx, dy in ((-0.45, -0.35), (0.5, 0.1), (-0.1, 0.55)):
        px, py = cx + dx * r, cy + dy * r
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED)


def draw_bars_up(d, x, y, w, h, color):
    n, gap = 4, 10
    bw = (w - gap * (n - 1)) // n
    heights = [h * 0.35, h * 0.55, h * 0.75, h]
    for i, bh in enumerate(heights):
        bx = x + i * (bw + gap)
        fill = RED if i == n - 1 else color
        d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=fill)


def draw_scales(d, x, y, s, color):
    cx, cy = x + s // 2, y + s // 2
    d.line([cx, y + 8, cx, y + s - 14], fill=color, width=4)
    d.line([x + 8, y + 22, x + s - 8, y + 22], fill=color, width=4)
    d.line([x + 14, y + s - 6, x + s - 14, y + s - 6], fill=color, width=4)
    for sx in (x + 8, x + s - 8):
        d.line([sx, y + 22, sx - 14, y + 52], fill=color, width=3)
        d.line([sx, y + 22, sx + 14, y + 52], fill=color, width=3)
        d.arc([sx - 14, y + 40, sx + 14, y + 68], start=0, end=180,
              fill=color, width=3)
    d.ellipse([cx - 6, y + 2, cx + 6, y + 14], fill=color)


def draw_chart_down(d, x, y, w, h, color):
    pts = [(x, y + 10), (x + w * 0.3, y + h * 0.35),
           (x + w * 0.55, y + h * 0.3), (x + w * 0.8, y + h * 0.7),
           (x + w, y + h - 6)]
    d.line(pts, fill=color, width=6, joint="curve")
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 16, ey - 2), (ex - 4, ey - 16)], fill=RED)
    d.line([x, y + h + 12, x + w, y + h + 12], fill=(180, 180, 180), width=2)


def draw_drone(d, cx, cy, color):
    d.rounded_rectangle([cx - 26, cy - 12, cx + 26, cy + 12], radius=10,
                        fill=color)
    for dx, dy in ((-38, -22), (38, -22), (-38, 22), (38, 22)):
        d.line([cx, cy, cx + dx, cy + dy], fill=color, width=4)
        d.ellipse([cx + dx - 11, cy + dy - 5, cx + dx + 11, cy + dy + 5],
                  outline=color, width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.text((MARGIN, 38), "THE WORLD IN ONE PICTURE", font=font(BOLD, 27),
           fill=NAVY, anchor="la")
    d.text((MARGIN, 72), "Friday, 20 November 2026", font=font(SERIF_BOLD, 62),
           fill=INK, anchor="la")
    d.line([MARGIN, 158, MARGIN + CW, 158], fill=INK, width=3)
    d.line([MARGIN, 164, MARGIN + CW, 164], fill=INK, width=1)

    # ---- lead story: the Shenzhen summit ----
    lead = (MARGIN, 180, MARGIN + CW, 420)
    d.rounded_rectangle(lead, radius=8, fill=NAVY)
    tx = MARGIN + 26
    d.text((tx, 198), "SUMMIT IN SHENZHEN", font=font(BOLD, 25),
           fill=RED_LIGHT, anchor="la")
    y = text_block(d, tx, 232, "TRUMP, XI AND PUTIN MEET \u2014 AND DECLARE PEACE",
                   font(BOLD, 40), (255, 255, 255), 680, 48)
    text_block(d, tx, y + 12,
               "First three-way summit of the three leaders ends with a joint "
               "\u2018peace declaration\u2019.",
               font(REG, 25), NAVY_LIGHT, 680, 32)
    draw_globe(d, 880, 300, 92, (235, 240, 246))

    # ---- story panels ----
    def panel(x, y, w, h, kicker, headline, summary, icon):
        d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=PANEL,
                            outline=BORDER, width=2)
        icon(d, x + 18, y + 22, 84, 84, NAVY)
        tx = x + 118
        d.text((tx, y + 20), kicker, font=font(BOLD, 20), fill=RED, anchor="la")
        y2 = text_block(d, tx, y + 48, headline, font(BOLD, 28), INK, w - 134, 34)
        text_block(d, tx, y2 + 8, summary, font(REG, 21), (60, 60, 60),
                   w - 134, 26)

    def icon_bars(d, x, y, w, h, color):
        draw_bars_up(d, x, y + 18, w, h - 30, color)

    def icon_scales(d, x, y, w, h, color):
        draw_scales(d, x, y + 6, min(w, h) - 6, color)

    def icon_down(d, x, y, w, h, color):
        draw_chart_down(d, x + 4, y + 14, w - 8, h - 44, color)

    def icon_drone(d, x, y, w, h, color):
        draw_drone(d, x + w // 2, y + h // 2, color)

    pw, ph, gap = 468, 240, 16
    panel(MARGIN, 432, pw, ph, "MARKETS \u00b7 NEW YORK",
          "ANTHROPIC SHARES UP 17%",
          "Record $81bn IPO priced at $83; shares close at $97, up 17%.",
          icon_bars)
    panel(MARGIN + pw + gap, 432, pw, ph, "JUSTICE \u00b7 THE HAGUE",
          "MYANMAR GUILTY OF GENOCIDE",
          "World Court rules the 2017 crackdown on the Rohingya was genocide, 9\u20136.",
          icon_scales)
    panel(MARGIN, 688, pw, ph, "MARKETS \u00b7 ASIA",
          "TAIWAN PLUNGES 2,200 POINTS",
          "AI-bubble fears hit Asian markets; regulators unveil rescue measures.",
          icon_down)
    panel(MARGIN + pw + gap, 688, pw, ph, "UKRAINE \u00b7 LONDON",
          "1,000+ UK DRONES FOR UKRAINE",
          "A \u00a3260m package of long-range drones as Europe readies new Russia talks.",
          icon_drone)

    # ---- footer ----
    f1 = "ALSO: COP31 draft drops fossil-fuel wording \u00b7 Fiona the hippo dies at Cincinnati Zoo"
    fw = d.textlength(f1, font=font(REG, 20))
    d.text(((W - fw) / 2, 946), f1, font=font(REG, 20), fill=MUTED, anchor="la")
    f2 = "All events as reported on Friday, 20 November 2026."
    fw2 = d.textlength(f2, font=font(REG, 17))
    d.text(((W - fw2) / 2, 976), f2, font=font(REG, 17), fill=(140, 140, 140),
           anchor="la")

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
