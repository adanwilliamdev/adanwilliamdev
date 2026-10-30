#!/usr/bin/env python3
"""Gera todos os SVGs do perfil em ../brand/. Uso: python3 tools/build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svgtext import *  # noqa

OUT = Path(__file__).parent.parent / "brand"
OUT.mkdir(exist_ok=True)
for old in OUT.glob("*.svg"):
    old.unlink()

W = 1000
M = 48


def save(name, svg):
    (OUT / name).write_text(svg.render(), encoding="utf-8")
    print(f"{name:28s} {svg.w:.0f}x{svg.h:.0f}")


def frame(s, top=0, bottom=0, left=True, right=True, w=None):
    """Moldura em tinta: faz as folhas empilhadas parecerem uma página só."""
    w = w or s.w
    if left:
        s.rect(0, 0, 3, s.h, INK)
    if right:
        s.rect(w - 3, 0, 3, s.h, INK)
    if top:
        s.rect(0, 0, w, top, INK)
    if bottom:
        s.rect(0, s.h - bottom, w, bottom, INK)


def burst(cx, cy, R, n=18, depth=.1):
    pts = []
    import math
    for i in range(n * 2):
        r = R if i % 2 == 0 else R * (1 - depth)
        a = math.pi * i / n
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


# =====================================================================
# HERO
# =====================================================================
def hero():
    headline = [
        [(SERIF_B, "Backend", INK)],
        [(SERIF_B, "que ", INK), (SERIF_BI, "não", RED), (SERIF_B, " cai", INK)],
        [(SERIF_B, "em produção.", INK)],
    ]
    S = 128
    def lw(line, S):
        return sum(f.width(t, S, -S * .02) + (-S * .02) for f, t, _ in line)
    while max(lw(l, S) for l in headline) > W - 2 * M - 40:
        S -= 1
    lh = S * .96
    ticker_h = 48
    meta_y = ticker_h + 44
    b1 = meta_y + 26 + S * .74
    base = [b1 + i * lh for i in range(3)]
    rule_y = base[2] + 44
    y0 = rule_y + 54

    para = [
        (SERIF_B, "Sou Adan William.", INK),
        (SERIF, "Passei mais de 5 anos em infraestrutura crítica de provedores de Internet (N2/N3) "
                "e hoje construo APIs e sistemas completos com Java / Spring Boot, PostgreSQL e Docker, "
                "com foco em regras de negócio, segurança e consistência de dados, levando para o código "
                "a visão de disponibilidade e SLA da operação.", INK),
    ]
    PS, PL = 19, 30
    pl = flow(para, 480, PS)
    para_end = y0 + 14 + (len(pl) - 1) * PL

    fx, fw = 590, 362
    ficha = [("Backend", "Java · Spring Boot · JPA"),
             ("Dados e infra", "PostgreSQL · Redis · Docker"),
             ("Também uso", "Python · React · TypeScript"),
             ("Vim de", "ISP · NOC · Zabbix · PRTG · Linux")]
    RH = 64
    ficha_end = y0 - 8 + 28 + len(ficha) * RH

    band_y = max(para_end, ficha_end) + 46
    band_h = 132
    H = band_y + band_h

    # ticker animado (um bloco em <defs>, repetido com <use>)
    items = ["Java 21", "Spring Boot", "PostgreSQL", "Redis", "Docker", "Testcontainers", "CI/CD", "Zabbix", "WebSocket"]
    s = Svg(W, H, "Adan William. Backend que não cai em produção. Desenvolvedor Java Júnior e Full Stack Júnior, "
                  "mais de 5 anos em infraestrutura e NOC, 12,5 mil clientes monitorados, 11 projetos no GitHub. "
                  "Disponível para vagas.")
    cx, unit, k = 0, [], 8
    for it in items:
        t = it.upper()
        unit.append(s.markup(MONO_B, t, cx, 29, 15, PAPER, 2.2))
        cx += MONO_B.width(t, 15, 2.2) + 26
        unit.append(f'<path transform="translate({cx+k:.1f} 24)" d="M0 -{k}C1 -2 2 -1 {k} 0C2 1 1 2 0 {k}C-1 2 -2 1 -{k} 0C-2 -1 -1 -2 0 -{k}Z" fill="{RED}"/>')
        cx += 2 * k + 26
    P = cx
    reps = 1
    while P * reps < W + P:
        reps += 1
    s.css = (f".tk{{animation:tk 38s linear infinite}}@keyframes tk{{to{{transform:translateX(-{P:.0f}px)}}}}"
             ".bs{transform-box:fill-box;transform-origin:center;animation:sp 36s linear infinite}"
             "@keyframes sp{to{transform:rotate(360deg)}}")
    s.rect(0, 0, W, H, PAPER)
    s.raw(f'<clipPath id="c"><rect width="{W}" height="{ticker_h}"/></clipPath>')
    s.rect(0, 0, W, ticker_h, INK)
    uses = "".join(f'<use href="#tku" x="{r*P:.1f}"/>' for r in range(reps + 1))
    s.raw(f'<defs><g id="tku">{"".join(unit)}</g></defs>')
    s.raw(f'<g clip-path="url(#c)"><g class="tk">{uses}</g></g>')

    s.text(MONO_B, "ADAN WILLIAM", M, meta_y, 16, INK, 2.4)
    s.text(MONO, "JAVA JÚNIOR / FULL STACK JÚNIOR", W - M, meta_y, 16, INK, 2.0, "end")
    s.rect(M, meta_y + 14, W - 2 * M, 2, INK)

    for i, line in enumerate(headline):
        x = M
        for f, t, fill in line:
            s.text(f, t, x, base[i], S, fill, -S * .02)
            x += f.width(t, S, -S * .02) - S * .02

    # selo
    R = 92
    bcx, bcy = W - M - R - 6, base[0] - S * .2
    s.raw(f'<g class="bs"><polygon points="{burst(bcx, bcy, R)}" fill="{RED}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/></g>')
    s.text(SERIF_BI, "Disponível", bcx, bcy - 2, 26, INK, 0, "middle")
    s.text(MONO_B, "PARA VAGAS", bcx, bcy + 26, 15, INK, 2.2, "middle")

    s.rect(M, rule_y, W - 2 * M, 4, INK)

    draw_flow(s, pl, M, y0 + 14, PS, PL)

    s.text(MONO_B, "FICHA TÉCNICA", fx, y0 - 8, 14, RED, 2.4)
    for i, (lab, val) in enumerate(ficha):
        ry = y0 - 8 + 14 + i * RH
        s.rect(fx, ry, fw, 2, INK)
        s.text(MONO, lab.upper(), fx, ry + 26, 13.5, MUTED, 2)
        s.text(SERIF_M, val, fx, ry + 52, 21, INK)
    s.rect(fx, y0 - 8 + 14 + len(ficha) * RH, fw, 2, INK)

    # faixa de números
    s.rect(0, band_y, W, band_h, RED)
    s.rect(0, band_y, W, 4, INK)
    stats = [("5+", "anos em infra e NOC"), ("12,5k+", "clientes monitorados"), ("11", "projetos no GitHub")]
    xs = [M, 358, 668]
    for (v, lab), x in zip(stats, xs):
        s.text(SERIF_B, v, x, band_y + 82, 66, INK, -1.5)
        s.text(MONO_B, lab.upper(), x, band_y + 112, 14, INK, 2)
    for x in (332, 642):
        s.rect(x, band_y + 24, 3, band_h - 40, INK)
    frame(s, top=0, bottom=4)
    save("hero.svg", s)


# =====================================================================
# BOTÕES
# =====================================================================
def button(name, label, fill, arrow="up", h=52):
    tw = SERIF_B.width(label, 19)
    iw = 16
    bw = 24 + tw + 14 + iw + 24
    s = Svg(bw + 9, h + 9, label)
    s.rect(7, 7, bw, h, INK)  # sombra dura
    s.rect(1.5, 1.5, bw, h, fill, INK, 3)
    s.text(SERIF_B, label, 1.5 + 24, 1.5 + h / 2 + 6.5, 19, INK)
    ax, ay = 1.5 + 24 + tw + 14, 1.5 + h / 2 - iw / 2
    if arrow == "up":
        s.arrow(ax, ay, iw)
    else:
        s.raw(f'<path d="M{ax+iw/2:.1f} {ay:.1f}V{ay+iw:.1f}M{ax+1:.1f} {ay+iw*.15+iw*.35:.1f}L{ax+iw/2:.1f} {ay+iw:.1f}L{ax+iw-1:.1f} {ay+iw*.5:.1f}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="square"/>')
    save(name, s)


# =====================================================================
# CABEÇALHO DE SEÇÃO
# =====================================================================
def section(name, num, title):
    H = 118
    s = Svg(W, H, f"{num} — {title}")
    s.rect(0, 0, W, H, PAPER)
    size = 62
    base = 90
    nw = SERIF_BI.width(num, size, -1)
    s.text(SERIF_BI, num, M, base, size, RED, -1)
    tx = M + nw + 22
    s.text(SERIF_B, title, tx, base, size, INK, -1.4)
    ex = tx + SERIF_B.width(title, size, -1.4) + 26
    s.rect(ex, base - 24, W - M - 26 - ex, 5, INK)
    s.sparkle(W - M - 11, base - 21.5, 13, RED)
    frame(s, top=4)
    save(name, s)


# =====================================================================
# STACK
# =====================================================================
STACK = [
    ("Backend", ["Java 17/21", "Spring Boot 3", "Spring Security", "Spring Data JPA", "Hibernate",
                 "Spring Cloud Gateway", "Spring AI", "WebSocket/STOMP", "Maven"]),
    ("Dados e infra", ["PostgreSQL", "Redis", "Flyway", "Docker", "Docker Compose", "GitHub Actions", "Git", "Linux"]),
    ("Frontend", ["React", "TypeScript", "Angular", "Next.js", "Vite", "Tailwind CSS", "Thymeleaf", "Bootstrap"]),
    ("Qualidade", ["JUnit 5", "Mockito", "Testcontainers", "JaCoCo", "Swagger/OpenAPI"]),
    ("Também usei", ["Python (FastAPI)", "Node.js (Express, Prisma)"]),
]


def stack():
    FS, LH, X0 = 22, 38, 300
    maxw = W - M - X0
    rows = []
    for lab, items in STACK:
        lines, cur, cw = [], [], 0
        for i, it in enumerate(items):
            w = SERIF_M.width(it, FS)
            sep = i < len(items) - 1
            full = w + (SERIF_M.width("  /", FS) if sep else 0)
            if cur and cw + 16 + full > maxw:
                lines.append(cur)
                cur, cw = [], 0
            x = cw + (16 if cur else 0)
            cur.append((it, x, w, sep))
            cw = x + full
        lines.append(cur)
        rows.append((lab, lines))
    heights = [max(86, 30 + len(l) * LH + 14) for _, l in rows]
    H = sum(heights) + 4
    s = Svg(W, H, "Stack. " + " ".join(f"{l}: {', '.join(i)}." for l, i in STACK))
    s.rect(0, 0, W, H, PAPER)
    y = 0
    for (lab, lines), h in zip(rows, heights):
        s.rect(M, y, W - 2 * M, 2, INK)
        s.rect(M, y + 34, 11, 11, RED)
        s.text(SERIF_BI, lab, M + 28, y + 46, 31, INK, -.3)
        for li, ln in enumerate(lines):
            by = y + 46 + li * LH
            for it, x, w, sep in ln:
                s.text(SERIF_M, it, X0 + x, by, FS, INK)
                if sep:
                    s.text(SERIF_B, "/", X0 + x + w + 9, by, FS, RED)
        y += h
    s.rect(M, y, W - 2 * M, 2, INK)
    frame(s, bottom=4)
    save("stack.svg", s)


# =====================================================================
# PROJETOS EM DESTAQUE (cards)
# =====================================================================
CARDS = [
    dict(name="AWOS Bank", url="awosbank",
         desc="Internet Banking com dashboard, extrato com filtros e chaves PIX.",
         bullets=["Auditoria append-only: trigger do PostgreSQL bloqueia UPDATE/DELETE e registra também as tentativas que falham",
                  "Testes de concorrência em transferências e Testcontainers com PostgreSQL real",
                  "Cobertura com JaCoCo e CI/CD com GitHub Actions publicando a imagem no GHCR"],
         chips=["Java 17", "Spring Boot", "Spring Security", "PostgreSQL", "Flyway", "Testcontainers", "Docker"]),
    dict(name="Torque Gestão", url="Torque_Gestao",
         desc="Gestão de oficinas: clientes, veículos, orçamentos com aprovação e estoque com movimentações rastreáveis.",
         bullets=["Ordens de serviço com fluxo de estados controlado",
                  "Perfis de acesso: admin, gerente, recepção e mecânico",
                  "Controle de concorrência otimista no estoque",
                  "JWT com refresh token rotativo e CSRF na interface web",
                  "Testes de integração com Testcontainers"],
         chips=["Java 21", "Spring Boot", "Spring Security", "PostgreSQL", "Flyway", "Testcontainers", "Docker"]),
    dict(name="Ticketing System", url="ticketing-system",
         desc="Reservas e pagamentos no estilo Ticketmaster, focado em alta concorrência.",
         bullets=["Lock pessimista no banco e lock distribuído com Redisson/Redis",
                  "Reserva temporária com expiração automática",
                  "Idempotência em pagamentos",
                  "Testes de reserva, expiração, idempotência e falha de gateway"],
         chips=["Java 21", "Spring Boot", "PostgreSQL", "Redis", "Flyway", "Docker", "JUnit 5", "Mockito"]),
    dict(name="OrbNOC", url="OrbNOC",
         desc="Monitoramento de rede em tempo real, nascido da minha rotina de NOC.",
         bullets=["ICMP e TCP: o host só fica offline após N falhas seguidas, sem falsos alarmes",
                  "Painel, mapa e wallboard para TVs de NOC atualizados via WebSocket",
                  "Alertas de queda, recuperação e SLA, com Telegram opcional",
                  "Relatórios de SLA (24h, 7d, 30d) em CSV e Excel; diagnóstico com ping, traceroute, DNS e portas",
                  "Argon2, JWT em cookie httpOnly + SameSite, CSRF por origem e comandos sem shell"],
         chips=["Java 21", "Spring Boot", "Thymeleaf", "PostgreSQL", "WebSocket", "Apache POI", "Docker"]),
]
CW = 500
CHIP_FS = 13.5


def chip_flow(chips, maxw, fs=CHIP_FS, gap=8, pad=11):
    lines, cur, cw = [], [], 0
    for c in chips:
        w = MONO.width(c, fs, .3) + 2 * pad
        if cur and cw + gap + w > maxw:
            lines.append(cur)
            cur, cw = [], 0
        x = cw + (gap if cur else 0)
        cur.append((c, x, w))
        cw = x + w
    lines.append(cur)
    return lines


def card_layout(d, innerw):
    L = {}
    L["nsize"] = fit_size(SERIF_B, d["name"], innerw - 64, 38, 24)
    L["desc"] = flow([(SERIF_I, d["desc"], MUTED)], innerw, 18)
    L["bul"] = [flow([(SERIF, b, INK)], innerw - 24, 16.5) for b in d["bullets"]]
    L["chips"] = chip_flow(d["chips"], innerw)
    y = 30 + 50  # rótulo + nome
    y += 18 + len(L["desc"]) * 26
    y += 22  # tracejado
    for b in L["bul"]:
        y += len(b) * 23 + 12
    y += 8
    y += len(L["chips"]) * 36
    L["h"] = y + 22
    return L


def draw_card(d, idx, L, side, card_h):
    x0 = 26 if side == "L" else 12
    x1 = CW - 12 if side == "L" else CW - 26
    cy = 16
    H = cy + card_h + 8 + 18
    s = Svg(CW, H, f"{d['name']}: {d['desc']} " + " ".join(d["bullets"]) + " Tecnologias: " + ", ".join(d["chips"]))
    s.rect(0, 0, CW, H, PAPER)
    s.rect(x0 + 8, cy + 8, x1 - x0, card_h, INK)
    s.rect(x0 + 1.5, cy + 1.5, x1 - x0 - 3, card_h - 3, CARD, INK, 3)
    px = x0 + 28
    iw = x1 - x0 - 56
    # rótulo + seta
    s.text(MONO_B, f"PROJETO {idx:02d}", px, cy + 40, 14, MUTED, 2.2)
    bx = x1 - 28 - 40
    s.rect(bx, cy + 20, 40, 40, RED, INK, 3)
    s.arrow(bx + 12, cy + 31, 16, INK, 2.8)
    y = cy + 40 + 50
    s.text(SERIF_B, d["name"], px, y, L["nsize"], INK, -.8)
    y += 28
    y = draw_flow(s, L["desc"], px, y, 18, 26) + 26
    s.raw(f'<path d="M{px} {y-8}H{px+iw}" stroke="{INK}" stroke-width="2" stroke-dasharray="1 6" stroke-linecap="round"/>')
    y += 22
    for b in L["bul"]:
        s.rect(px, y - 9, 8, 8, RED, INK, 1.5)
        draw_flow(s, b, px + 24, y, 16.5, 23)
        y += (len(b) - 1) * 23 + 23 + 12 - 2
    y += 4
    for ln in L["chips"]:
        for c, x, w in ln:
            s.rect(px + x + 1, y - 1, w - 2, 28, "none", INK, 2)
            s.text(MONO, c, px + x + w / 2, y + 18.5, CHIP_FS, INK, .3, "middle")
        y += 36
    frame(s, left=(side == "L"), right=(side == "R"))
    return s


def cards():
    for i in (0, 2):
        pair = CARDS[i:i + 2]
        # largura interna igual nos dois lados (L: 26..488, R: 12..474 -> 462)
        iw = (CW - 12 - 26) - 56
        Ls = [card_layout(d, iw) for d in pair]
        card_h = max(l["h"] for l in Ls) + 0
        for k, (d, L) in enumerate(zip(pair, Ls)):
            side = "L" if k == 0 else "R"
            save(f"proj-{d['url'].lower()}.svg", draw_card(d, i + k + 1, L, side, card_h))


# =====================================================================
# OUTROS PROJETOS / IA APLICADA (linhas)
# =====================================================================
def row(fname, idx, name, chips, desc, last=False):
    LX, LW = M, 290
    DX, DW = 400, 480
    nsz = 27
    while max(SERIF_B.width(w, nsz) for w in name.split(" ")) > LW and nsz > 18:
        nsz -= 1
    nl = flow([(SERIF_B, name, INK)], LW, nsz)
    dl = flow([(SERIF, desc, INK)], DW, 18)
    chp = chip_flow(chips, LW) if chips else []
    y = 36
    ny = y + 40
    ly_end = ny + (len(nl) - 1) * (nsz + 4)
    if chips:
        ly_end += 20 + len(chp) * 36 - 8
    ry_end = 38 + (len(dl) - 1) * 28
    H = int(max(ly_end, ry_end, 72) + 36)
    s = Svg(W, H, f"{name}: {desc}" + (" Tecnologias: " + ", ".join(chips) if chips else ""))
    s.rect(0, 0, W, H, PAPER)
    s.rect(M, 0, W - 2 * M, 2, INK)
    s.text(MONO_B, idx, LX, y + 3, 15, RED, 2)
    draw_flow(s, nl, LX, ny, nsz, nsz + 4)
    yy = ny + (len(nl) - 1) * (nsz + 4) + 20
    for ln in chp:
        for c, x, w in ln:
            s.rect(LX + x + 1, yy - 1, w - 2, 28, "none", INK, 2)
            s.text(MONO, c, LX + x + w / 2, yy + 18.5, CHIP_FS, INK, .3, "middle")
        yy += 36
    s.rect(DX - 24, 24, 1.5, H - 48, INK, extra=' opacity=".25"')
    draw_flow(s, dl, DX, 42, 18, 28)
    bx = W - M - 40
    s.rect(bx, 24, 40, 40, PAPER, INK, 3)
    s.arrow(bx + 12, 35, 16, INK, 2.8)
    frame(s)
    save(fname, s)


OUTROS = [
    ("row-taskflow.svg", "05", "TaskFlow", ["Spring Cloud", "React", "Docker Compose"],
     "Gerenciador de tarefas em microsserviços (API Gateway, Eureka, auth, usuários, tarefas e notificações), um banco por serviço e JWT validado localmente."),
    ("row-itau.svg", "06", "Itaú Java AI Order System", ["Java", "Spring AI"],
     "API de pedidos com 4 padrões de projeto (State, Chain of Responsibility, Strategy, Observer) e comandos de voz via Spring AI. Desafio final do programa Itaú Java AI (DIO)."),
    ("row-burger.svg", "07", "Burger & Pizza House ERP", ["Node.js", "Angular", "Prisma"],
     "ERP para pizzarias e hamburguerias, com pedidos em transação atômica e baixa automática de estoque."),
    ("row-study.svg", "08", "Study Planner", ["Spring Boot", "React", "Vite"],
     "Rotina de estudos com matérias, tarefas, cronograma, Pomodoro e notificações em tempo real via WebSocket/STOMP, autenticado por JWT."),
]
IA = [
    ("row-geo.svg", "09", "Geo-Explorer", ["TypeScript", "MCP"],
     "Servidor MCP (Model Context Protocol) em TypeScript com ferramentas para trilhas de aprendizagem, desafios e certificados. Feito no Bootcamp IBM Bob."),
    ("row-livrocerto.svg", "10", "LivroCerto", [],
     "Assistente de recomendação de livros que só responde com base em uma base de conhecimento própria, com avaliação de métricas."),
    ("row-estudoativo.svg", "11", "EstudoAtivo-NotebookLM", [],
     "Estudo de finanças pessoais com IA fundamentada em fontes curadas e engenharia de prompt."),
]


# =====================================================================
# FOCO ATUAL
# =====================================================================
def foco():
    cols = [("01", "Java e Spring Boot", "Segurança, testes de integração e mensageria (RabbitMQ/Kafka)."),
            ("02", "CI/CD", "Levar o que já uso no AWOS Bank para os demais projetos."),
            ("03", "Time", "Contribuir e aprender com profissionais mais experientes.")]
    cw = 262
    xs = [M, 366, 684]
    laid = [flow([(SERIF, t, TINT)], cw, 19) for _, _, t in cols]
    H = 150 + max(len(l) for l in laid) * 29 + 40
    css = ".sp{transform-box:fill-box;transform-origin:center;animation:sp 24s linear infinite}@keyframes sp{to{transform:rotate(360deg)}}"
    s = Svg(W, H, "Foco atual. " + " ".join(f"{t}: {d}" for _, t, d in cols), css)
    s.rect(0, 0, W, H, INK)
    for (n, t, d), x, ln in zip(cols, xs, laid):
        s.text(MONO_B, n, x, 66, 16, RED, 2.5)
        s.rect(x, 80, 44, 4, RED)
        size = fit_size(SERIF_B, t, cw, 38, 24)
        s.text(SERIF_B, t, x, 138, size, PAPER, -.8)
        draw_flow(s, ln, x, 178, 19, 29)
    for x in (340, 658):
        s.rect(x, 52, 1.5, H - 104, PAPER, extra=' opacity=".25"')
    s.raw('<g class="sp">')
    s.sparkle(W - M - 8, 52, 20, RED)
    s.raw("</g>")
    frame(s, bottom=4)
    # moldura clara não aparece sobre tinta; usa papel
    save("foco.svg", s)


# =====================================================================
# CONTATO
# =====================================================================
def cta(name, label_top, l1, l2, bg, fg, side):
    H = 270
    CWD = 500
    s = Svg(CWD, H, f"{l1} {l2}")
    s.rect(0, 0, CWD, H, bg)
    px = 48 if side == "L" else 36
    s.text(MONO_B, label_top, px, 56, 15, fg, 2.4)
    s.text(SERIF_B, l1, px, 134, 58, fg, -1.5)
    s.text(SERIF_BI, l2, px, 200, 64, RED if bg == INK else INK, -1.5)
    bx = CWD - (48 if side == "L" else 60) - 52
    s.rect(bx, 26, 52, 52, bg, fg, 3)
    s.arrow(bx + 15, 41, 22, fg, 3.2)
    s.rect(0, H - 4, CWD, 4, INK)
    if side == "L":
        s.rect(0, 0, 3, H, INK)
        s.rect(CWD - 1.5, 0, 3, H, INK)
    else:
        s.rect(CWD - 3, 0, 3, H, INK)
    save(name, s)


def footer():
    H = 64
    s = Svg(W, H, "© 2026 Adan William. Feito à mão, em SVG.")
    s.rect(0, 0, W, H, PAPER)
    s.text(MONO_B, "© 2026 ADAN WILLIAM", M, 38, 14, INK, 2.2)
    s.text(MONO, "FEITO À MÃO, EM SVG", W - M - 26, 38, 14, MUTED, 2.2, "end")
    s.sparkle(W - M - 8, 33, 10, RED)
    frame(s, bottom=4)
    save("footer.svg", s)


if __name__ == "__main__":
    hero()
    button("btn-projetos.svg", "Ver projetos", RED, "down")
    button("btn-github.svg", "GitHub", CARD)
    button("btn-linkedin.svg", "LinkedIn", CARD)
    button("btn-portfolio.svg", "Portfólio", CARD)
    for n, num, t in [("sec-stack.svg", "01", "Stack"), ("sec-projetos.svg", "02", "Projetos em destaque"),
                      ("sec-outros.svg", "03", "Outros projetos"), ("sec-ia.svg", "04", "IA aplicada"),
                      ("sec-atividade.svg", "05", "Atividade"), ("sec-foco.svg", "06", "Foco atual"),
                      ("sec-contato.svg", "07", "Contato")]:
        section(n, num, t)
    stack()
    cards()
    for i, r in enumerate(OUTROS):
        row(*r, last=(i == len(OUTROS) - 1))
    for i, r in enumerate(IA):
        row(*r, last=(i == len(IA) - 1))
    foco()
    cta("cta-linkedin.svg", "01 — LINKEDIN", "Me chama no", "LinkedIn", RED, INK, "L")
    cta("cta-portfolio.svg", "02 — PORTFÓLIO", "Ver o meu", "portfólio", INK, PAPER, "R")
    footer()
