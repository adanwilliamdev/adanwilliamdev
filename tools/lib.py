"""
Biblioteca de geração de SVG para a nova identidade (patch panel).
Todo texto é convertido em curvas: o GitHub bloqueia fontes embutidas em SVG,
então esta é a única forma de a tipografia aparecer igual em qualquer máquina.
"""
import os
import re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen  # noqa: F401  (reservado)

# ---------------------------------------------------------------- paleta
COBALT = "#1F36F5"      # jaqueta do cabo azul
COBALT_D = "#1429D1"    # sombra do cobalto (orelhas de rack)
INK = "#0B1485"         # "preto" desta identidade: azul-tinta profundo
YELLOW = "#FFD21F"      # fita de etiqueta
ORANGE = "#F2461E"      # laranja-sinal (acento)
ORANGE_T = "#FF9B73"    # laranja suave para chips
GREEN = "#12B76A"       # LED de link
PANEL = "#EDEFF7"       # cinza de equipamento de rack
WHITE = "#FFFFFF"
INK_SOFT = "#3B46A8"    # texto secundário sobre claro


def _lum(h):
    h = h.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted([_lum(a), _lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------- fontes
class Font:
    def __init__(self, key, path):
        self.key = key
        self.tt = TTFont(path)
        self.upem = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.hmtx = self.tt["hmtx"]
        self.gs = self.tt.getGlyphSet()
        self.cap = getattr(self.tt["OS/2"], "sCapHeight", 0.7 * self.upem) / self.upem
        self.xh = getattr(self.tt["OS/2"], "sxHeight", 0.5 * self.upem) / self.upem
        self._kern_subs = self._load_kern()
        self._pathcache = {}

    # --- kerning GPOS (PairPos 1 e 2)
    def _load_kern(self):
        subs = []
        if "GPOS" not in self.tt:
            return subs
        g = self.tt["GPOS"].table
        idx = set()
        for fr in g.FeatureList.FeatureRecord:
            if fr.FeatureTag == "kern":
                idx.update(fr.Feature.LookupListIndex)
        for li in sorted(idx):
            lk = g.LookupList.Lookup[li]
            for st in lk.SubTable:
                t = lk.LookupType
                if t == 9:
                    t = st.ExtensionLookupType
                    st = st.ExtSubTable
                if t != 2:
                    continue
                cov = set(st.Coverage.glyphs)
                if st.Format == 1:
                    d = {}
                    for gl, ps in zip(st.Coverage.glyphs, st.PairSet):
                        for pv in ps.PairValueRecord:
                            v = pv.Value1.XAdvance if pv.Value1 and hasattr(pv.Value1, "XAdvance") else 0
                            d[(gl, pv.SecondGlyph)] = v or 0
                    subs.append(("1", cov, d))
                else:
                    c1 = st.ClassDef1.classDefs
                    c2 = st.ClassDef2.classDefs
                    subs.append(("2", cov, (c1, c2, st.Class1Record)))
        return subs

    def kern(self, l, r):
        for kind, cov, data in self._kern_subs:
            if l not in cov:
                continue
            if kind == "1":
                if (l, r) in data:
                    return data[(l, r)]
            else:
                c1, c2, recs = data
                rec = recs[c1.get(l, 0)].Class2Record[c2.get(r, 0)]
                v = rec.Value1.XAdvance if rec.Value1 and hasattr(rec.Value1, "XAdvance") else 0
                if v:
                    return v
        return 0

    def glyph(self, ch):
        gn = self.cmap.get(ord(ch))
        if gn is None:
            raise KeyError(f"{self.key} não tem glifo para {ch!r}")
        return gn

    def layout(self, s, tracking=0.0):
        """retorna [(glyphname, x_units)], largura_units"""
        out, x, prev = [], 0.0, None
        for ch in s:
            gn = self.glyph(ch)
            if prev is not None:
                x += self.kern(prev, gn)
            out.append((gn, x))
            x += self.hmtx[gn][0] + tracking * self.upem
            prev = gn
        if out:
            x -= tracking * self.upem
        return out, x

    def width(self, s, size, tracking=0.0):
        return self.layout(s, tracking)[1] * size / self.upem

    def path(self, gn):
        if gn not in self._pathcache:
            pen = SVGPathPen(self.gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
            self.gs[gn].draw(pen)
            self._pathcache[gn] = pen.getCommands()
        return self._pathcache[gn]


HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONTS = {
    "d": Font("d", os.path.join(HERE, "Lora-Bold.ttf")),          # display
    "r": Font("r", os.path.join(HERE, "Carlito-Regular.ttf")),    # texto
    "b": Font("b", os.path.join(HERE, "Carlito-Bold.ttf")),       # texto forte
}


# ---------------------------------------------------------------- canvas
class Svg:
    def __init__(self, w, h, title, desc=None):
        self.w, self.h = w, h
        self.title, self.desc = title, desc
        self.defs = {}      # id -> d
        self.css = ""
        self.body = []

    def add(self, s):
        self.body.append(s)

    # --- texto
    def text(self, fk, s, x, y, size, fill, tracking=0.0, anchor="start", opacity=None, cls=None):
        f = FONTS[fk]
        glyphs, wu = f.layout(s, tracking)
        k = size / f.upem
        wpx = wu * k
        if anchor == "middle":
            x -= wpx / 2
        elif anchor == "end":
            x -= wpx
        uses = []
        for gn, gx in glyphs:
            if gn == "space" or f.path(gn) == "":
                continue
            gid = f"{fk}{re.sub(r'[^A-Za-z0-9]', '_', gn)}"
            self.defs.setdefault(gid, f.path(gn))
            uses.append(f'<use xlink:href="#{gid}" x="{gx:.1f}"/>')
        op = f' opacity="{opacity}"' if opacity is not None else ""
        c = f' class="{cls}"' if cls else ""
        self.add(f'<g{c} fill="{fill}"{op} transform="translate({x:.2f} {y:.2f}) scale({k:.5f} {-k:.5f})">{"".join(uses)}</g>')
        return wpx

    def rich(self, line, x, y, size, fill, strong_fill=None):
        """line = [(texto, fk)] já com espaços; escreve em sequência"""
        cx = x
        for txt, fk in line:
            w = self.text(fk, txt, cx, y, size, strong_fill if (fk == "b" and strong_fill) else fill)
            cx += w
        return cx - x

    def render(self, extra_css=""):
        defs = "".join(f'<path id="{i}" d="{d}"/>' for i, d in self.defs.items())
        desc = f"<desc>{esc(self.desc)}</desc>" if self.desc else ""
        css = f"<style>{self.css}{extra_css}@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}</style>" if (self.css or extra_css) else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" role="img" aria-label="{esc(self.title)}">'
            f"<title>{esc(self.title)}</title>{desc}{css}<defs>{defs}</defs>{''.join(self.body)}</svg>"
        )


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------------------------------------------------------- quebra de texto
def words(text):
    """'a **b**. c' -> [[('a','r')], [('b','b'),('.','r')], [('c','r')]] (palavra = lista de runs)"""
    chars, bold = [], False
    i = 0
    while i < len(text):
        if text.startswith("**", i):
            bold = not bold
            i += 2
            continue
        chars.append((text[i], bold))
        i += 1
    out, cur = [], []
    for ch, bd in chars:
        if ch.isspace():
            if cur:
                out.append(cur)
                cur = []
            continue
        fk = "b" if bd else "r"
        if cur and cur[-1][1] == fk:
            cur[-1] = (cur[-1][0] + ch, fk)
        else:
            cur.append((ch, fk))
    if cur:
        out.append(cur)
    return out


def wrap(text, size, maxw, base="r"):
    """quebra com métricas reais; devolve linhas = [[(texto, fk), ...], ...]"""
    ws = words(text)
    sp = FONTS[base].width(" ", size)
    lines, cur, curw = [], [], 0.0
    for w in ws:
        ww = sum(FONTS["b" if fk == "b" else base].width(t, size) for t, fk in w)
        add = ww if not cur else sp + ww
        if cur and curw + add > maxw:
            lines.append(cur)
            cur, curw = [], 0.0
            add = ww
        cur.append(w)
        curw += add
    if cur:
        lines.append(cur)
    res = []
    for ln in lines:
        runs = []
        for i, w in enumerate(ln):
            for j, (t, fk) in enumerate(w):
                if j == len(w) - 1 and i < len(ln) - 1:
                    t += " "
                runs.append((t, "b" if fk == "b" else base))
        res.append(runs)
    return res


# ---------------------------------------------------------------- hardware
def screw(cx, cy, r=6, fill=INK, slot="#FFFFFF", rot=35):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
        f'<path d="M{cx - r * .62:.1f} {cy}H{cx + r * .62:.1f}" stroke="{slot}" stroke-width="{max(1.4, r * .26):.1f}" '
        f'stroke-linecap="round" transform="rotate({rot} {cx} {cy})" opacity=".85"/>'
    )


def led(cx, cy, color=GREEN, r=6.5, stroke=INK):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="{color}" opacity=".22"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" stroke="{stroke}" stroke-width="1.8"/>'
        f'<circle cx="{cx - r * .32:.1f}" cy="{cy - r * .32:.1f}" r="{r * .28:.1f}" fill="#fff" opacity=".9"/>'
    )


def port(x, y, w=32, h=27, body=INK, hole=PANEL, pins=YELLOW):
    """porta RJ45 vista de frente (x,y = canto superior esquerdo)"""
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{body}"/>']
    ix, iy = x + 3.5, y + 4
    iw, ih = w - 7, h - 8
    nw = iw * 0.42
    nx = x + (w - nw) / 2
    s.append(
        f'<path d="M{ix:.1f} {iy + ih:.1f}V{iy + 5:.1f}H{nx:.1f}V{iy:.1f}H{nx + nw:.1f}V{iy + 5:.1f}H{ix + iw:.1f}V{iy + ih:.1f}Z" fill="{hole}"/>'
    )
    n = 8
    gap = (iw - 6) / (n - 1)
    for i in range(n):
        px = ix + 3 + i * gap - 0.7
        s.append(f'<rect x="{px:.1f}" y="{iy + ih - 8:.1f}" width="1.5" height="6.5" fill="{pins}"/>')
    return "".join(s)


def plug(x, y, boot=COBALT, w=46, h=28, ink=INK):
    """plugue RJ45 apontando para a direita; (x,y) = centro vertical, borda esquerda"""
    top = y - h / 2
    s = []
    # boot (capa colorida)
    s.append(f'<rect x="{x}" y="{top - 3:.1f}" width="22" height="{h + 6}" rx="3" fill="{boot}" stroke="{ink}" stroke-width="2.4"/>')
    # corpo transparente
    s.append(f'<rect x="{x + 22}" y="{top:.1f}" width="{w - 22}" height="{h}" fill="{WHITE}" stroke="{ink}" stroke-width="2.4"/>')
    # trava
    s.append(f'<path d="M{x + 28} {top:.1f}V{top - 6:.1f}H{x + 40} V{top:.1f}" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linejoin="round"/>')
    # contatos
    for i in range(6):
        px = x + 26 + i * 3.4
        s.append(f'<path d="M{px:.1f} {y - 5:.1f}V{y + 6:.1f}" stroke="{YELLOW}" stroke-width="1.8"/>')
    s.append(f'<rect x="{x + 25}" y="{y - 6:.1f}" width="{w - 29}" height="13" fill="none" stroke="{ink}" stroke-width="0.8" opacity=".35"/>')
    return "".join(s)


def tape(x, y, w, h, fill=YELLOW, shadow=INK, sh=4, stroke=None, rot=0, ox=None, oy=None):
    """tira de etiqueta com sombra dura. retorna (svg_open, svg_close) para agrupar conteúdo"""
    cx = x + (ox if ox is not None else w / 2)
    cy = y + (oy if oy is not None else h / 2)
    tr = f' transform="rotate({rot} {cx:.1f} {cy:.1f})"' if rot else ""
    st = f' stroke="{stroke}" stroke-width="2.4"' if stroke else ""
    open_ = (
        f"<g{tr}>"
        + (f'<rect x="{x + sh}" y="{y + sh}" width="{w}" height="{h}" fill="{shadow}"/>' if shadow else "")
        + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{st}/>'
    )
    return open_, "</g>"
