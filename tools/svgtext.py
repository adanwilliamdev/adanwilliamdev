"""Mini engine: texto -> contornos SVG (paths), com kerning do GPOS.

Como o texto vira desenho, os SVGs ficam idênticos em qualquer navegador/tema
do GitHub, sem depender de fontes instaladas.
"""
from pathlib import Path
from functools import lru_cache
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = Path(__file__).parent / "fonts"


def _n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Font:
    def __init__(self, file, wght=None):
        tt = TTFont(FONT_DIR / file)
        if wght is not None and "fvar" in tt:
            tt = instancer.instantiateVariableFont(tt, {"wght": wght}, inplace=False)
        self.tt = tt
        self.upem = tt["head"].unitsPerEm
        self.cmap = tt.getBestCmap()
        self.gs = tt.getGlyphSet()
        self.hmtx = tt["hmtx"]
        self.kern = self._load_kern()
        self._cache = {}

    # ---- kerning (GPOS PairPos, formatos 1 e 2) ----
    def _load_kern(self):
        tt = self.tt
        if "GPOS" not in tt:
            return []
        gpos = tt["GPOS"].table
        idx = set()
        for fr in gpos.FeatureList.FeatureRecord:
            if fr.FeatureTag == "kern":
                idx.update(fr.Feature.LookupListIndex)
        subs = []
        for i in sorted(idx):
            lk = gpos.LookupList.Lookup[i]
            for st in lk.SubTable:
                if lk.LookupType == 9:
                    st = st.ExtSubTable
                if hasattr(st, "Coverage") and hasattr(st, "Format") and (
                        hasattr(st, "PairSet") or hasattr(st, "Class1Record")):
                    subs.append(st)
        return subs

    @lru_cache(maxsize=None)
    def _pair(self, a, b):
        for st in self.kern:
            cov = st.Coverage.glyphs
            if a not in cov:
                continue
            if st.Format == 1:
                ps = st.PairSet[cov.index(a)]
                for rec in ps.PairValueRecord:
                    if rec.SecondGlyph == b:
                        return getattr(rec.Value1, "XAdvance", 0) or 0
            elif st.Format == 2:
                c1 = st.ClassDef1.classDefs.get(a, 0)
                c2 = st.ClassDef2.classDefs.get(b, 0)
                v = st.Class1Record[c1].Class2Record[c2].Value1
                x = getattr(v, "XAdvance", 0) or 0
                if x:
                    return x
        return 0

    def gname(self, ch):
        return self.cmap.get(ord(ch), ".notdef")

    def width(self, text, size, ls=0.0):
        s = size / self.upem
        w = 0.0
        prev = None
        for ch in text:
            g = self.gname(ch)
            if prev is not None:
                w += self._pair(prev, g) * s
            w += self.hmtx[g][0] * s + ls
            prev = g
        return w - (ls if text else 0)

    def glyph_d(self, g):
        if g not in self._cache:
            pen = SVGPathPen(self.gs, ntos=lambda v: str(int(round(v))))
            self.gs[g].draw(pen)
            self._cache[g] = pen.getCommands()
        return self._cache[g]

    def run(self, text, size, ls=0.0):
        """Posições (glyph, x em unidades da fonte) e largura total em px."""
        s = size / self.upem
        lsu = ls / s
        pos, cx, prev = [], 0.0, None
        for ch in text:
            g = self.gname(ch)
            if prev is not None:
                cx += self._pair(prev, g)
            if ch != " ":
                pos.append((g, cx))
            cx += self.hmtx[g][0] + lsu
            prev = g
        return pos

    def path(self, text, x, y, size, ls=0.0, anchor="start"):
        """Retorna 'd' do path com o texto na linha de base (x, y)."""
        w = self.width(text, size, ls)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        s = size / self.upem
        out = []
        cx = x
        prev = None
        for ch in text:
            g = self.gname(ch)
            if prev is not None:
                cx += self._pair(prev, g) * s
            if ch != " ":
                pen = SVGPathPen(self.gs, ntos=_n)
                tp = TransformPen(pen, (s, 0, 0, -s, cx, y))
                self.gs[g].draw(tp)
                out.append(pen.getCommands())
            cx += self.hmtx[g][0] * s + ls
            prev = g
        return "".join(out)


# ---------- fontes do projeto ----------
SERIF = Font("Lora-Variable.ttf", 400)
SERIF_M = Font("Lora-Variable.ttf", 500)
SERIF_B = Font("Lora-Variable.ttf", 700)
SERIF_I = Font("Lora-Italic-Variable.ttf", 400)
SERIF_BI = Font("Lora-Italic-Variable.ttf", 700)
MONO = Font("lmmono10-regular.otf")
MONO_B = Font("lmmonolt10-bold.otf")

# ---------- paleta ----------
PAPER = "#F3EEE3"
CARD = "#FBF8F0"
INK = "#15120F"
RED = "#FF4B1F"
MUTED = "#5E564A"
TINT = "#E6DDCA"


def _n3(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


class Svg:
    def __init__(self, w, h, label, extra_css=""):
        self.w, self.h, self.label = w, h, label
        self.parts = []
        self.css = extra_css
        self.defs = {}

    def raw(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=0, extra=""):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(
            f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" fill="{fill}"{st}{extra}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=2, extra=""):
        self.parts.append(
            f'<path d="M{_n(x1)} {_n(y1)}L{_n(x2)} {_n(y2)}" stroke="{stroke}" stroke-width="{sw}" fill="none"{extra}/>')

    def gid(self, font, g):
        key = (id(font), g)
        if key not in self.defs:
            self.defs[key] = (f"g{len(self.defs)}", font.glyph_d(g))
        return self.defs[key][0]

    def markup(self, font, s, x, y, size, fill=INK, ls=0, anchor="start"):
        w = font.width(s, size, ls)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        k = size / font.upem
        uses = "".join(f'<use href="#{self.gid(font, g)}" x="{_n(px)}"/>' for g, px in font.run(s, size, ls))
        return f'<g transform="translate({_n(x)} {_n(y)}) scale({_n3(k)} -{_n3(k)})" fill="{fill}">{uses}</g>'

    def text(self, font, s, x, y, size, fill=INK, ls=0, anchor="start", extra=""):
        self.parts.append(self.markup(font, s, x, y, size, fill, ls, anchor))
        return font.width(s, size, ls)

    def arrow(self, x, y, s, color=INK, sw=2.6):
        """Seta ↗ com canto superior-esquerdo em (x, y), tamanho s."""
        self.parts.append(
            f'<path d="M{_n(x)} {_n(y+s)}L{_n(x+s)} {_n(y)}M{_n(x+s*.12)} {_n(y)}H{_n(x+s)}V{_n(y+s*.88)}" '
            f'fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="square"/>')

    def sparkle(self, cx, cy, r, fill=RED, extra=""):
        k = r * .18
        d = (f"M{_n(cx)} {_n(cy-r)}C{_n(cx+k)} {_n(cy-k*1.2)} {_n(cx+k*1.2)} {_n(cy-k)} {_n(cx+r)} {_n(cy)}"
             f"C{_n(cx+k*1.2)} {_n(cy+k)} {_n(cx+k)} {_n(cy+k*1.2)} {_n(cx)} {_n(cy+r)}"
             f"C{_n(cx-k)} {_n(cy+k*1.2)} {_n(cx-k*1.2)} {_n(cy+k)} {_n(cx-r)} {_n(cy)}"
             f"C{_n(cx-k*1.2)} {_n(cy-k)} {_n(cx-k)} {_n(cy-k*1.2)} {_n(cx)} {_n(cy-r)}Z")
        self.parts.append(f'<path d="{d}" fill="{fill}"{extra}/>')

    def render(self):
        css = ("@media (prefers-reduced-motion: reduce){*{animation:none!important}}" + self.css)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_n(self.w)} {_n(self.h)}" '
                f'width="{_n(self.w)}" height="{_n(self.h)}" role="img" aria-label="{esc(self.label)}">'
                f'<title>{esc(self.label)}</title><style>{css}</style>'
                + (("<defs>" + "".join(f'<path id="{i}" d="{d}"/>' for i, d in self.defs.values()) + "</defs>") if self.defs else "")
                + "".join(self.parts) + "</svg>")


# ---------- quebra de linha com runs ----------
def flow(runs, maxw, size):
    """runs: [(font, texto, fill)]. Retorna linhas: [[(font, palavra, fill, x)]], com larguras."""
    toks = []
    for font, text, fill in runs:
        for i, wd in enumerate(text.split(" ")):
            if wd == "":
                continue
            toks.append((font, wd, fill))
    lines, cur, cw = [], [], 0.0
    for font, wd, fill in toks:
        w = font.width(wd, size)
        sp = font.width(" ", size)
        if cur and cw + sp + w > maxw:
            lines.append(cur)
            cur, cw = [], 0.0
        x = cw + (sp if cur else 0)
        cur.append((font, wd, fill, x))
        cw = x + w
    if cur:
        lines.append(cur)
    return lines


def draw_flow(svg, lines, x, y, size, lh):
    """Desenha linhas de flow() e devolve y logo após o bloco."""
    for i, ln in enumerate(lines):
        for font, wd, fill, dx in ln:
            svg.text(font, wd, x + dx, y + i * lh, size, fill)
    return y + (len(lines) - 1) * lh


def fit_size(font, text, maxw, size, minsize=14):
    while size > minsize and font.width(text, size) > maxw:
        size -= 1
    return size
