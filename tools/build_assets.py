import os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *

OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','assets')
os.makedirs(OUT,exist_ok=True)
def save(name, svg):
    open(f'{OUT}/{name}','w').write(svg); print(name, len(svg)//1024,'KB')

# ================================================================ HERO
def hero():
    W,H=1000,722
    BIO=("Sou **Adan William**. Passei mais de 5 anos em infraestrutura crítica de provedores de Internet (N2/N3) "
         "e hoje construo APIs e sistemas completos com **Java / Spring Boot**, PostgreSQL e Docker, com foco em regras "
         "de negócio, segurança e consistência de dados, levando para o código a visão de disponibilidade e SLA da operação.")
    s=Svg(W,H,"Adan William: Backend que não cai em produção. Desenvolvedor Java Júnior, disponível para vagas.",
          "Mais de 5 anos em infraestrutura e NOC, mais de 12,5 mil clientes monitorados, 11 projetos no GitHub.")
    s.add(f'<rect width="{W}" height="{H}" fill="{COBALT}"/>')
    # orelhas de rack
    for x in (0,W-30):
        s.add(f'<rect x="{x}" y="0" width="30" height="{H}" fill="{COBALT_D}"/>')
        for y in (46,H/2,H-46):
            s.add(screw(x+15,y,7,fill=INK))
    L=84
    # --- linha 1: etiqueta com o nome + cargo + status
    nm="Adan William"; nw=FONTS['d'].width(nm,30)+40
    o,c=tape(L,40,nw,54,rot=-1.3)
    s.add(o); s.text('d',nm,L+20,40+37,30,INK); s.add(c)
    s.text('b',"Desenvolvedor Java Júnior",L+nw+30,40+34,21,WHITE)
    pw,ph=300,68; px=W-56-pw
    s.add(f'<rect x="{px+4}" y="{34+4}" width="{pw}" height="{ph}" fill="{INK}"/>')
    s.add(f'<rect x="{px}" y="34" width="{pw}" height="{ph}" fill="{WHITE}" stroke="{INK}" stroke-width="2.4"/>')
    s.add(led(px+28,34+ph/2,'#2EE08C',7))
    s.text('b',"Disponível para vagas",px+54,34+31,21,INK)
    s.text('r',"Java Júnior / Full Stack Júnior",px+54,34+53,16,INK_SOFT)
    # --- headline
    lines=["Backend que não","cai em produção."]
    mw=max(FONTS['d'].width(t,100) for t in lines)
    size=100*(W-2*L-40)/mw
    y1=222
    for i,t in enumerate(lines):
        s.text('d',t,L-4,y1+i*size*1.04,size,WHITE,tracking=-0.018)
    y2=y1+size*1.04
    # --- fita que alterna frases (o único movimento da peça)
    ty=y2+46
    phrases=["Spring Boot e PostgreSQL","APIs seguras e consistentes","Docker, Testcontainers e CI/CD","SLA e disponibilidade"]
    tw,th=450,56
    o,c=tape(L,ty,tw,th,rot=-1.0)
    s.add(o)
    for i,p in enumerate(phrases):
        s.add(f'<g class="cyc c{i}">')
        s.text('b',p,L+24,ty+37,27,INK)
        s.add('</g>')
    s.add(c)
    s.css=(".cyc{opacity:0;animation:cyc 12s infinite}.c1{animation-delay:3s}.c2{animation-delay:6s}.c3{animation-delay:9s}"
           "@keyframes cyc{0%{opacity:0;transform:translateY(7px)}4%,22%{opacity:1;transform:none}27%,100%{opacity:0}}"
           "@media (prefers-reduced-motion: reduce){.c0{opacity:1!important}}")
    # --- bio
    by=ty+th+48
    ls=wrap(BIO,19,575)
    for i,ln in enumerate(ls):
        s.rich(ln,L,by+i*28,19,"#E6EAFF",WHITE)
    bio_bottom=by+(len(ls)-1)*28+14
    # --- placa de números
    sx=W-56-252; sy=ty-4; sh_=bio_bottom-sy+8
    s.add(f'<rect x="{sx+5}" y="{sy+5}" width="252" height="{sh_}" fill="{INK}"/>')
    s.add(f'<rect x="{sx}" y="{sy}" width="252" height="{sh_}" fill="{WHITE}" stroke="{INK}" stroke-width="2.4"/>')
    stats=[("5+","anos em infra e NOC"),("12,5k+","clientes monitorados"),("11","projetos no GitHub")]
    rh=sh_/3
    for i,(n,l) in enumerate(stats):
        yy=sy+i*rh
        if i: s.add(f'<path d="M{sx+22} {yy:.1f}H{sx+230}" stroke="{INK}" stroke-width="1.6" opacity=".25"/>')
        s.text('d',n,sx+22,yy+rh/2+2,40,COBALT)
        s.text('r',l,sx+22,yy+rh/2+28,17,INK)
    # --- faixa inferior: grupos de tecnologia + origem
    fy=H-96
    s.add(f'<rect x="30" y="{fy}" width="{W-60}" height="96" fill="{PANEL}"/>')
    s.add(f'<path d="M30 {fy}H{W-30}" stroke="{INK}" stroke-width="2.4"/>')
    groups=[("Backend","Java, Spring Boot, JPA"),("Dados e infra","PostgreSQL, Redis, Docker"),
            ("Também uso","Python, React, TypeScript"),("Vim de","ISP, NOC, Zabbix, PRTG, Linux")]
    ws=[44+max(FONTS['b'].width(a,16),FONTS['r'].width(b,16.5)) for a,b in groups]
    gap=(W-2*56-sum(ws))/(len(groups)-1)
    x=56
    for (a,b),w in zip(groups,ws):
        s.add(port(x,fy+34,32,27))
        s.text('b',a,x+44,fy+41,16,INK)
        s.text('r',b,x+44,fy+62,16.5,INK_SOFT)
        x+=w+gap
    return s


# ================================================================ SEÇÕES (cabo com etiqueta)
def plug_dir(x,y,boot,flip=False,w=46):
    g=plug(0,y,boot=boot,w=w)
    if flip: return f'<g transform="translate({x} 0) scale(-1 1)">{g}</g>'
    return f'<g transform="translate({x} 0)">{g}</g>'

def section(title, cable, label_fill=YELLOW):
    W,H=1000,78
    s=Svg(W,H,title)
    cy=44
    # cabo (contorno + cor)
    s.add(f'<path d="M30 {cy}H970" stroke="{INK}" stroke-width="12" stroke-linecap="butt"/>')
    s.add(f'<path d="M30 {cy}H970" stroke="{cable}" stroke-width="7" stroke-linecap="butt"/>')
    s.add(plug_dir(50,cy,cable,flip=True))
    s.add(plug_dir(950,cy,cable,flip=False))
    # etiqueta enrolada no cabo
    tw=FONTS['d'].width(title,32)+44
    lx=100
    o,c=tape(lx,cy-28,tw,56,fill=label_fill,rot=-1.0,stroke=INK)
    s.add(o); s.text('d',title,lx+22,cy+11,32,INK); s.add(c)
    return s

SECTIONS=[("sec-stack.svg","Stack",COBALT,YELLOW),
          ("sec-projetos.svg","Projetos em destaque",ORANGE,YELLOW),
          ("sec-outros.svg","Outros projetos",YELLOW,WHITE),
          ("sec-ia.svg","IA aplicada",GREEN,YELLOW),
          ("sec-atividade.svg","Atividade",COBALT,YELLOW),
          ("sec-foco.svg","Foco atual",ORANGE,YELLOW),
          ("sec-contato.svg","Contato",YELLOW,WHITE)]

# ================================================================ BOTÕES
def button(label, face, fg, port_body, port_hole):
    tw=FONTS['b'].width(label,18)
    w=int(14+34+10+tw+20); H=50
    s=Svg(w+6,H,label)
    s.add(f'<rect x="{6}" y="{6}" width="{w}" height="42" fill="{INK}"/>')
    s.add(f'<rect x="2" y="2" width="{w}" height="42" fill="{face}" stroke="{INK}" stroke-width="2.4"/>')
    s.add(port(16,12,32,22,body=port_body,hole=port_hole))
    s.text('b',label,58,30,18,fg)
    return s
BUTTONS=[("btn-projetos.svg","Ver projetos",COBALT,WHITE,WHITE,COBALT_D),
         ("btn-github.svg","GitHub",YELLOW,INK,INK,PANEL),
         ("btn-linkedin.svg","LinkedIn",YELLOW,INK,INK,PANEL),
         ("btn-portfolio.svg","Portfólio",YELLOW,INK,INK,PANEL),
         ("btn-linkedin-cta.svg","Me chama no LinkedIn",COBALT,WHITE,WHITE,COBALT_D),
         ("btn-portfolio-cta.svg","Ver portfólio",YELLOW,INK,INK,PANEL)]

# ================================================================ STACK (patch panel)
STACK=[("Backend",COBALT,WHITE,["Java 17/21","Spring Boot 3","Spring Security","Spring Data JPA","Hibernate","Spring Cloud Gateway","Spring AI","WebSocket/STOMP","Maven"]),
       ("Dados e infra",YELLOW,INK,["PostgreSQL","Redis","Flyway","Docker","Docker Compose","GitHub Actions","Git","Linux"]),
       ("Frontend",ORANGE_T,INK,["React","TypeScript","Angular","Next.js","Vite","Tailwind CSS","Thymeleaf","Bootstrap"]),
       ("Qualidade",WHITE,INK,["JUnit 5","Mockito","Testcontainers","JaCoCo","Swagger/OpenAPI"]),
       ("Também usei",WHITE,INK,["Python (FastAPI)","Node.js (Express, Prisma)"])]

def chip(s,x,y,label,fill,fg,size=15.5,h=34,stroke=INK):
    w=FONTS['b'].width(label,size)+28
    s.add(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    s.text('b',label,x+14,y+h/2+size*0.36,size,fg)
    return w

def balanced(items,size,maxw,gap=10,pad=28):
    ws=[FONTS['b'].width(i,size)+pad for i in items]
    def n_lines(limit):
        n,x=1,0
        for w in ws:
            if x and x+w>limit: n+=1; x=0
            x+=w+gap
        return n
    n=n_lines(maxw)
    lo,hi=max(ws),maxw
    for _ in range(40):                       # menor largura que ainda cabe em n linhas
        mid=(lo+hi)/2
        if n_lines(mid)<=n: hi=mid
        else: lo=mid
    lines=[[]]; x=0
    for it,w in zip(items,ws):
        if x and x+w>hi: lines.append([]); x=0
        lines[-1].append((it,w)); x+=w+gap
    return lines

def stack():
    W=1000; TW=max(FONTS['d'].width(t,21) for t,_,_,_ in STACK)+34
    X0=56+TW+28; XR=W-56
    rows=[]; y=26
    for title,fill,fg,items in STACK:
        lines=balanced(items,15.5,XR-X0)
        rh=len(lines)*34+(len(lines)-1)*10
        rows.append((title,fill,fg,lines,y,rh)); y+=rh+30
    H=y-30+26
    s=Svg(W,H,"Stack. Backend: Java 17/21, Spring Boot 3, Spring Security, Spring Data JPA, Hibernate, Spring Cloud Gateway, Spring AI, WebSocket/STOMP, Maven. Dados e infra: PostgreSQL, Redis, Flyway, Docker, Docker Compose, GitHub Actions, Git, Linux. Frontend: React, TypeScript, Angular, Next.js, Vite, Tailwind CSS, Thymeleaf, Bootstrap. Qualidade: JUnit 5, Mockito, Testcontainers, JaCoCo, Swagger/OpenAPI. Também usei: Python (FastAPI), Node.js (Express, Prisma).")
    s.add(f'<rect x="1.2" y="1.2" width="{W-2.4}" height="{H-2.4}" fill="{PANEL}" stroke="{INK}" stroke-width="2.4"/>')
    for x in (1.2,W-31.2):
        s.add(f'<rect x="{x}" y="1.2" width="30" height="{H-2.4}" fill="#D9DDEE" stroke="{INK}" stroke-width="2.4"/>')
        for yy in (24,H/2,H-24): s.add(screw(x+15,yy,6.5))
    for i,(title,fill,fg,lines,y,rh) in enumerate(rows):
        if i: s.add(f'<path d="M56 {y-15}H{W-56}" stroke="{INK}" stroke-width="1.6" opacity=".22"/>')
        ty=y+(rh-40)/2
        s.add(f'<rect x="56" y="{ty}" width="{TW}" height="40" fill="{INK}"/>')
        s.text('d',title,56+17,ty+27,21,WHITE)
        for li,ln in enumerate(lines):
            x=X0
            for it,w in ln:
                chip(s,x,y+li*44,it,fill,fg); x+=w+10
    return s

# ================================================================ CARDS DESTAQUE
FEATURED=[
 ("proj-awosbank.svg","AWOS Bank","Internet Banking com dashboard, extrato com filtros e chaves PIX.",
  ["Auditoria append-only: trigger do PostgreSQL bloqueia UPDATE/DELETE e registra também as tentativas que falham",
   "Testes de concorrência em transferências e Testcontainers com PostgreSQL real",
   "Cobertura com JaCoCo e CI/CD com GitHub Actions publicando a imagem no GHCR"],
  ["Java 17","Spring Boot","Spring Security","PostgreSQL","Flyway","Testcontainers","Docker"]),
 ("proj-torque_gestao.svg","Torque Gestão","Gestão de oficinas: clientes, veículos, orçamentos com aprovação e estoque com movimentações rastreáveis.",
  ["Ordens de serviço com fluxo de estados controlado","Perfis de acesso: admin, gerente, recepção e mecânico",
   "Controle de concorrência otimista no estoque","JWT com refresh token rotativo e CSRF na interface web",
   "Testes de integração com Testcontainers"],
  ["Java 21","Spring Boot","Spring Security","PostgreSQL","Flyway","Testcontainers","Docker"]),
 ("proj-ticketing-system.svg","Ticketing System","Reservas e pagamentos no estilo Ticketmaster, focado em alta concorrência.",
  ["Lock pessimista no banco e lock distribuído com Redisson/Redis","Reserva temporária com expiração automática",
   "Idempotência em pagamentos","Testes de reserva, expiração, idempotência e falha de gateway"],
  ["Java 21","Spring Boot","PostgreSQL","Redis","Flyway","Docker","JUnit 5","Mockito"]),
 ("proj-orbnoc.svg","OrbNOC","Monitoramento de rede em tempo real, nascido da minha rotina de NOC.",
  ["ICMP e TCP: o host só fica offline após N falhas seguidas, sem falsos alarmes",
   "Painel, mapa e wallboard para TVs de NOC atualizados via WebSocket",
   "Alertas de queda, recuperação e SLA, com Telegram opcional",
   "Relatórios de SLA (24h, 7d, 30d) em CSV e Excel; diagnóstico com ping, traceroute, DNS e portas",
   "Argon2, JWT em cookie httpOnly + SameSite, CSRF por origem e comandos sem shell"],
  ["Java 21","Spring Boot","Thymeleaf","PostgreSQL","WebSocket","Apache POI","Docker"]),
]
CW=500
def card_measure(name,desc,bullets,chips):
    inner=CW-12-48
    dl=wrap(desc,17,inner)
    bl=[wrap(b,15.5,inner-20) for b in bullets]
    # chips
    x=24; rows=1
    for c in chips:
        w=FONTS['b'].width(c,13.5)+24
        if x+w>CW-12-24: rows+=1; x=24
        x+=w+8
    h=2+64+24+len(dl)*24+16+sum(len(b)*21+9 for b in bl)+10+(rows*30+(rows-1)*8+32)+12
    return int(h+14),dl,bl,rows

def card(name,desc,bullets,chips,H,dl,bl):
    s=Svg(CW,H,f"{name}: {desc}")
    X,Y,Wd,Ht=2,2,CW-12,H-14
    s.add(f'<rect x="{X+5}" y="{Y+5}" width="{Wd}" height="{Ht}" fill="{INK}"/>')
    s.add(f'<rect x="{X}" y="{Y}" width="{Wd}" height="{Ht}" fill="{WHITE}" stroke="{INK}" stroke-width="2.4"/>')
    s.add(f'<rect x="{X}" y="{Y}" width="{Wd}" height="64" fill="{COBALT}" stroke="{INK}" stroke-width="2.4"/>')
    s.add(screw(X+22,Y+32,6,fill=INK))
    s.add(screw(X+Wd-22,Y+32,6,fill=INK))
    s.text('d',name,X+44,Y+43,27,WHITE,tracking=-0.005)
    s.add(port(X+Wd-22-18-34,Y+18,34,28,body=WHITE,hole=COBALT_D))
    y=Y+64+24+14
    for ln in dl:
        s.rich(ln,24,y,17,INK,INK); y+=24
    y+=14
    for b in bl:
        s.add(f'<rect x="25" y="{y-8}" width="7" height="7" fill="{ORANGE}" stroke="{INK}" stroke-width="1.2"/>')
        for ln in b:
            s.rich(ln,44,y,15.5,INK_SOFT,INK); y+=21
        y+=9
    # faixa de chips ancorada no rodapé
    rows_=1; x=24
    for c in chips:
        w=FONTS['b'].width(c,13.5)+24
        if x+w>CW-12-24: rows_+=1; x=24
        x+=w+8
    ph=rows_*30+(rows_-1)*8+32
    cy=Y+Ht-ph
    s.add(f'<rect x="{X}" y="{cy}" width="{Wd}" height="{ph}" fill="{PANEL}" stroke="{INK}" stroke-width="2.4"/>')
    x=24; yy=cy+16
    for c in chips:
        w=FONTS['b'].width(c,13.5)+24
        if x+w>CW-12-24: x=24; yy+=38
        chip(s,x,yy,c,YELLOW,INK,size=13.5,h=30)
        x+=w+8
    return s

# ================================================================ LINHAS (outros / IA)
ROWS=[
 ("row-taskflow.svg","TaskFlow","Gerenciador de tarefas em **microsserviços** (API Gateway, Eureka, auth, usuários, tarefas e notificações), um banco por serviço e JWT validado localmente.",["Spring Cloud","React","Docker Compose"],YELLOW,INK),
 ("row-itau.svg","Itaú Java AI Order System","API de pedidos com **4 padrões de projeto** (State, Chain of Responsibility, Strategy, Observer) e comandos de voz via Spring AI. Desafio final do programa Itaú Java AI (DIO).",["Java","Spring AI"],YELLOW,INK),
 ("row-burger.svg","Burger & Pizza House ERP","ERP para pizzarias e hamburguerias, com pedidos em transação atômica e baixa automática de estoque.",["Node.js","Angular","Prisma"],YELLOW,INK),
 ("row-study.svg","Study Planner","Rotina de estudos com matérias, tarefas, cronograma, Pomodoro e **notificações em tempo real via WebSocket/STOMP**, autenticado por JWT.",["Spring Boot","React","Vite"],YELLOW,INK),
 ("row-geo.svg","Geo-Explorer","Servidor **MCP** (Model Context Protocol) em TypeScript com ferramentas para trilhas de aprendizagem, desafios e certificados. Feito no Bootcamp IBM Bob.",["TypeScript","MCP"],ORANGE,WHITE),
 ("row-livrocerto.svg","LivroCerto","Assistente de recomendação de livros que só responde com base em uma base de conhecimento própria, com avaliação de métricas.",[],ORANGE,WHITE),
 ("row-estudoativo.svg","EstudoAtivo-NotebookLM","Estudo de finanças pessoais com IA fundamentada em fontes curadas e engenharia de prompt.",[],ORANGE,WHITE),
]
RW=1000; LW=340
def row(name,desc,chips,color,fg):
    dl=wrap(desc,17,RW-12-LW-30-100)
    nl=wrap(name,23,LW-52,base='d')
    # chips layout
    x=26; yrow=0; pos=[]
    for c in chips:
        w=FONTS['b'].width(c,13.5)+24
        if x+w>LW-20 and pos: x=26; yrow+=1
        pos.append((c,x,yrow,w)); x+=w+8
    nrows=(pos[-1][2]+1) if pos else 0
    left=26+len(nl)*28+(16+nrows*30+(nrows-1)*8 if nrows else 0)+24
    right=26+len(dl)*25+24
    ih=max(left,right,92)
    H=int(ih+4+8)
    s=Svg(RW,H,f"{name}: {desc.replace('**','')}")
    X,Y,Wd=2,4,RW-12
    s.add(f'<rect x="{X+5}" y="{Y+5}" width="{Wd}" height="{ih}" fill="{INK}"/>')
    s.add(f'<rect x="{X}" y="{Y}" width="{Wd}" height="{ih}" fill="{WHITE}" stroke="{INK}" stroke-width="2.4"/>')
    s.add(f'<rect x="{X}" y="{Y}" width="{LW}" height="{ih}" fill="{color}" stroke="{INK}" stroke-width="2.4"/>')
    block=len(nl)*28+((10+nrows*30+(nrows-1)*8) if nrows else 0)
    y0=Y+(ih-block)/2 if not nrows else Y+26
    y=y0+20
    for ln in nl:
        s.text('d',"".join(t for t,_ in ln),X+26,y,23,fg); y+=28
    for c,cx,r,w in pos:
        yy=y0+len(nl)*28+10+r*38
        chip(s,X+cx,yy,c,WHITE,INK,size=13.5,h=30)
    y=Y+(ih-len(dl)*25)/2+18
    for ln in dl:
        s.rich(ln,X+LW+30,y,17,INK,INK); y+=25
    s.add(port(X+Wd-22-34,Y+ih/2-14,34,28,body=INK,hole=PANEL))
    return s

# ================================================================ FOCO
def foco():
    W,H=1000,168
    s=Svg(W,H,"Foco atual. Java e Spring Boot: segurança, testes de integração e mensageria (RabbitMQ/Kafka). CI/CD: levar o que já uso no AWOS Bank para os demais projetos. Time: contribuir e aprender com profissionais mais experientes.")
    s.add(f'<rect x="1.2" y="1.2" width="{W-2.4}" height="{H-2.4}" fill="{PANEL}" stroke="{INK}" stroke-width="2.4"/>')
    for x in (1.2,W-31.2):
        s.add(f'<rect x="{x}" y="1.2" width="30" height="{H-2.4}" fill="#D9DDEE" stroke="{INK}" stroke-width="2.4"/>')
        for yy in (26,H-26): s.add(screw(x+15,yy,6.5))
    cols=[("Java e Spring Boot","Segurança, testes de integração e mensageria (RabbitMQ/Kafka).",COBALT),
          ("CI/CD","Levar o que já uso no AWOS Bank para os demais projetos.",ORANGE),
          ("Time","Contribuir e aprender com profissionais mais experientes.",YELLOW)]
    cw=(W-62-2)/3
    for i,(t,d,c) in enumerate(cols):
        x=32+i*cw
        if i: s.add(f'<path d="M{x:.1f} 22H{x:.1f}V{H-22}" stroke="{INK}" stroke-width="1.6" opacity=".22"/>')
        s.add(f'<rect x="{x+28:.1f}" y="30" width="46" height="10" fill="{c}" stroke="{INK}" stroke-width="2"/>')
        s.text('d',t,x+28,80,25,INK)
        for j,ln in enumerate(wrap(d,16.5,cw-60)):
            s.rich(ln,x+28,108+j*22,16.5,INK_SOFT,INK)
    return s

if __name__=='__main__':
    save('hero-2.svg',hero().render())
    for f,t,c,l in SECTIONS: save(f,section(t,c,l).render())
    for f,l,face,fg,pb,ph in BUTTONS: save(f,button(l,face,fg,pb,ph).render())
    save('stack.svg',stack().render())
    ms=[card_measure(n,d,b,c) for _,n,d,b,c in FEATURED]
    for (f,n,d,b,c),(h1,dl,bl,_) in zip(FEATURED,ms): pass
    H1=max(ms[0][0],ms[1][0]); H2=max(ms[2][0],ms[3][0])
    for i,(f,n,d,b,c) in enumerate(FEATURED):
        H=H1 if i<2 else H2
        save(f,card(n,d,b,c,H,ms[i][1],ms[i][2]).render())
    for f,n,d,c,col,fg in ROWS: save(f,row(n,d,c,col,fg).render())
    save('foco.svg',foco().render())
