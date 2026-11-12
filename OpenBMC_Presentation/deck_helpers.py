"""Shared drawing helpers for the OpenBMC architecture deck (native, editable shapes)."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls


def rgb(h):
    return RGBColor.from_string(h)


NAVY, BLUE, SKY, TEAL = rgb("0B2A4A"), rgb("1F6FB2"), rgb("4A9FD8"), rgb("138A85")
GREEN, ORANGE, RED, PURPLE = rgb("3A8F55"), rgb("D9822B"), rgb("C0392B"), rgb("6C4BA0")
GREY, DARK, LIGHT, PALE = rgb("6B7785"), rgb("1E2833"), rgb("EEF3F8"), rgb("DCE8F4")
WHITE, AMBER, MINT, LILAC = rgb("FFFFFF"), rgb("FFF4D6"), rgb("E3F4EC"), rgb("ECE6F6")
FONT, MONO = "Segoe UI", "Consolas"
CENTER, LEFT, RIGHT = PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.RIGHT
TOP, MIDDLE, BOTTOM = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM
RECT, ROUND, OVAL = MSO_SHAPE.RECTANGLE, MSO_SHAPE.ROUNDED_RECTANGLE, MSO_SHAPE.OVAL


def _runs(p, text, size, color, bold=False, font=FONT):
    # "**x**" marks bold spans inside a line
    for i, part in enumerate(text.split("**")):
        if not part:
            continue
        r = p.add_run()
        r.text = part
        f = r.font
        f.size, f.name, f.bold = Pt(size), font, bold or i % 2 == 1
        f.color.rgb = color


def _fill(tf, text, size, color, bold=False, align=CENTER, font=FONT, anchor=MIDDLE, spacing=0):
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = tf.margin_bottom = Inches(0.04)
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if spacing:
            p.space_after = Pt(spacing)
        _runs(p, line, size, color, bold, font)


def box(s, x, y, w, h, t="", fill=BLUE, fg=WHITE, size=14, bold=False, align=CENTER,
        shape=ROUND, line=None, font=FONT, anchor=MIDDLE, lw=1.25, spacing=0):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.shadow.inherit = False
    if shape == ROUND:
        sh.adjustments[0] = 0.12
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    if t:
        _fill(sh.text_frame, t, size, fg, bold, align, font, anchor, spacing)
    return sh


def text(s, x, y, w, h, t, size=14, color=DARK, bold=False, align=LEFT, font=FONT,
         anchor=TOP, bg=None, spacing=0):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if bg is not None:
        tb.fill.solid()
        tb.fill.fore_color.rgb = bg
    _fill(tb.text_frame, t, size, color, bold, align, font, anchor, spacing)
    return tb


def arrow(s, x1, y1, x2, y2, color=GREY, width=2, head=True, tail=False, dash=False,
          label=None, lsize=11, lcolor=DARK, lw=None, bg=None, loff=0.0):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    if dash:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    ln = c.line._get_or_add_ln()
    if tail:
        ln.append(parse_xml('<a:headEnd %s type="triangle" w="med" len="med"/>' % nsdecls("a")))
    if head:
        ln.append(parse_xml('<a:tailEnd %s type="triangle" w="med" len="med"/>' % nsdecls("a")))
    if label:
        w = lw or max(abs(x2 - x1), 1.8)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        text(s, mx - w / 2, my - 0.5 + loff, w, 0.46, label, size=lsize, color=lcolor,
             align=CENTER, anchor=BOTTOM, bg=bg)
    return c


def bullets(s, x, y, w, h, items, size=16, color=DARK, gap=8, mark=BLUE):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        sub = item.startswith("- ")
        p.space_after = Pt(gap)
        r = p.add_run()
        r.text = "      \u2013 " if sub else "\u25A0  "
        r.font.size, r.font.color.rgb, r.font.name = Pt(size - (3 if sub else 6)), mark, FONT
        _runs(p, item[2:] if sub else item, size - 2 if sub else size, color)
    return tb


def table(s, x, y, w, rows, col_w=None, row_h=0.42, size=12, head_fill=NAVY, mono_cols=()):
    nr, nc = len(rows), len(rows[0])
    t = s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr)).table
    if col_w:
        for i, cw in enumerate(col_w):
            t.columns[i].width = Inches(cw)
    for r in range(nr):
        t.rows[r].height = Inches(row_h)
        for c in range(nc):
            cell = t.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = head_fill if r == 0 else (LIGHT if r % 2 == 0 else WHITE)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MIDDLE
            cell.text_frame.word_wrap = True
            font = MONO if (c in mono_cols and r > 0) else FONT
            _runs(cell.text_frame.paragraphs[0], str(rows[r][c]), size,
                  WHITE if r == 0 else DARK, bold=(r == 0), font=font)
    return t


def note(s, x, y, w, h, t, size=14, fill=AMBER, accent=ORANGE):
    box(s, x, y, w, h, fill=fill, shape=RECT)
    box(s, x, y, 0.09, h, fill=accent, shape=RECT)
    text(s, x + 0.2, y, w - 0.3, h, t, size=size, anchor=MIDDLE)


def code(s, x, y, w, h, t, size=12):
    return box(s, x, y, w, h, t, fill=rgb("1E2430"), fg=rgb("E6EDF3"), size=size, align=LEFT,
               shape=RECT, font=MONO, anchor=TOP)


def flow(s, x, y, labels, w, h, gap=0.4, colors=None, size=13, fg=WHITE):
    out = []
    for i, lab in enumerate(labels):
        bx = x + i * (w + gap)
        col = colors[i % len(colors)] if colors else BLUE
        out.append(box(s, bx, y, w, h, lab, fill=col, fg=fg, size=size))
        if i:
            arrow(s, bx - gap + 0.04, y + h / 2, bx - 0.04, y + h / 2)
    return out


def vflow(s, x, y, labels, w, h, gap=0.3, colors=None, size=13, fg=WHITE):
    for i, lab in enumerate(labels):
        by = y + i * (h + gap)
        col = colors[i % len(colors)] if colors else BLUE
        box(s, x, by, w, h, lab, fill=col, fg=fg, size=size)
        if i:
            arrow(s, x + w / 2, by - gap + 0.03, x + w / 2, by - 0.03)


def stack(s, x, y, w, layers, h=0.62, gap=0.08, size=14):
    for i, (t, col) in enumerate(layers):
        box(s, x, y + i * (h + gap), w, h, t, fill=col, size=size)


def sequence(s, x, y, w, h, actors, msgs, colors=None, size=11, head_h=0.62):
    """msgs: (from, to, label[, is_return]); from == to draws a note on that lifeline."""
    n = len(actors)
    col = w / n
    cx = [x + col * i + col / 2 for i in range(n)]
    for i, a in enumerate(actors):
        box(s, cx[i] - col / 2 + 0.06, y, col - 0.12, head_h, a,
            fill=colors[i] if colors else NAVY, size=12, bold=True)
        arrow(s, cx[i], y + head_h, cx[i], y + h, color=rgb("A9B4C0"), width=1.25, head=False, dash=True)
    step = (h - head_h - 0.3) / len(msgs)
    for k, m in enumerate(msgs):
        a, b, t = m[:3]
        ret = len(m) > 3 and m[3]
        yy = y + head_h + 0.5 + step * k
        if a == b:
            nw = min(col * 1.1, 3.0)
            nx = cx[a] + 0.08 if a < n - 1 else cx[a] - 0.08 - nw
            box(s, nx, yy - 0.24, nw, 0.42, t, fill=AMBER, fg=DARK, size=size - 1, shape=RECT)
        else:
            arrow(s, cx[a], yy, cx[b], yy, color=GREY if ret else BLUE, width=1.75, dash=ret,
                  label=t, lsize=size, lw=abs(cx[b] - cx[a]) - 0.1)


class Deck:
    def __init__(self, footer="OpenBMC Architecture"):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        self.blank = self.prs.slide_layouts[6]
        self.n = 0
        self.footer = footer

    def raw(self, notes=""):
        s = self.prs.slides.add_slide(self.blank)
        self.n += 1
        if notes:
            s.notes_slide.notes_text_frame.text = notes
        return s

    def slide(self, title, subtitle=None, section="", notes=""):
        s = self.raw(notes)
        box(s, 0, 0, 13.333, 1.05, fill=NAVY, shape=RECT)
        box(s, 0, 1.05, 13.333, 0.05, fill=SKY, shape=RECT)
        text(s, 0.45, 0.08 if subtitle else 0.2, 12.4, 0.6, title, size=28, color=WHITE, bold=True)
        if subtitle:
            text(s, 0.45, 0.6, 12.4, 0.4, subtitle, size=14, color=rgb("BFD7EE"))
        text(s, 0.45, 7.08, 9, 0.3, f"{self.footer}  |  {section}", size=10, color=GREY)
        text(s, 11.9, 7.08, 1.0, 0.3, str(self.n), size=10, color=GREY, align=RIGHT)
        return s

    def save(self, path):
        self.prs.save(path)
