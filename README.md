<p align="center">
  <a href="https://adanwilliamdev.github.io/"><img src="banner.svg" alt="Adan William: Backend que não cai em produção. Python e FastAPI." /></a>
</p>

<p align="center">
  <a href="#destaques"><img src="btn-projetos.svg" alt="Ver projetos" /></a>
  <a href="https://adanwilliamdev.github.io/"><img src="btn-portfolio.svg" alt="Portfólio" /></a>
  <a href="https://www.linkedin.com/in/awosantos/"><img src="btn-linkedin.svg" alt="LinkedIn" /></a>
</p>

## ~/resumo

Passei mais de 5 anos em **infraestrutura crítica** (N2/N3, monitorando mais de 12.500 clientes de um provedor de Internet). Hoje construo **APIs assíncronas, sistemas em tempo real e aplicações orientadas a dados** com Python/FastAPI e serviços em Java/Spring Boot, levando para o código o que aprendi no NOC: disponibilidade, observabilidade e atenção ao que acontece em produção.

```
buscando:     Desenvolvedor Backend Júnior (Python e Java)
foco:         Python (FastAPI, Pydantic, SQLAlchemy) + PostgreSQL + Redis
diferencial:  visão de operação, SLA e incidentes aplicada ao design de software
```

## ~/destaques

### [OrbNOC](https://github.com/adanwilliamdev/OrbNOC)
Monitoramento de redes em tempo real: disponibilidade, latência, jitter, perda de pacotes, alertas, SLA, diagnóstico (ping, traceroute, DNS) e wallboard. Nasceu da minha rotina de NOC: a primeira versão foi em Java e depois foi reescrita em Python.

- Worker Python independente, ICMP com fallback TCP
- WebSocket com Redis Pub/Sub
- Argon2, JWT em cookie httpOnly, testes com PostgreSQL e Redis reais, CI

`FastAPI` `Next.js` `PostgreSQL` `Redis` `Docker`

### [Ticketing System](https://github.com/adanwilliamdev/ticketing-system)
Reserva e venda de ingressos pensada para concorrência e consistência transacional.

- Lock distribuído com Redisson e pessimistic locking no banco
- Pagamentos com chave de idempotência
- Expiração automática de reservas

`Java 21` `Spring Boot` `PostgreSQL` `Redis` `Flyway` `Docker`

### [SVA — Sua Vaga Aqui](https://github.com/adanwilliamdev/sva-platform)
Plataforma de recrutamento que conecta candidatos e recrutadores, com score de compatibilidade entre currículo e vaga, chat, agendamento de entrevistas e analytics.

- WebSocket nativo + Redis Pub/Sub
- Validação ponta a ponta com Pydantic v2 e Zod
- Suíte de testes de backend com PostgreSQL e Redis reais

`FastAPI` `Next.js` `PostgreSQL` `Redis` `Docker`

### [Mecânica+](https://github.com/adanwilliamdev/Mecanica_Plus)
Gestão para oficinas mecânicas: clientes, veículos, mecânicos, orçamentos, ordens de serviço e estoque.

- Estoque com controle de concorrência por versão e auditoria
- JWT com refresh token rotativo
- Acesso baseado em perfis (RBAC)

`FastAPI` `Next.js` `PostgreSQL` `Redis` `Docker`

### [Dashboard Analytics](https://github.com/adanwilliamdev/Dashboard_Analytics)
Análise de finanças pessoais: API REST, importação de CSV/OFX, detecção de despesas atípicas e previsão de 30 dias.

- Migrations com Alembic, valores monetários em NUMERIC
- Testes automatizados e CI

`FastAPI` `PostgreSQL` `Pandas` `Streamlit` `Docker`

### [ETL de qualidade de dados](https://github.com/adanwilliamdev/etl_pipeline_qualidade)
Pipeline que valida CSV, isola registros inválidos em quarentena, faz upsert e gera relatório de execução.

`Python` `Pydantic` `SQLite` `Docker` `GitHub Actions`

## ~/outros-projetos

| Projeto | Descrição | Stack |
| --- | --- | --- |
| [Uptime SaaS](https://github.com/adanwilliamdev/uptime-saas) | Monitor de disponibilidade de APIs com fila de checagens, incidentes automáticos e WebSocket | FastAPI · Taskiq · Redis · Next.js |
| [Detecção de fraude](https://github.com/adanwilliamdev/deteccao_fraude_transacoes) | Pipeline de ML para fraude em transações, com avaliação por custo e API opcional | Python · scikit-learn · FastAPI |
| [Real Estate Monitor](https://github.com/adanwilliamdev/real-estate-monitor) | Análise de mercado imobiliário e previsão de preços | Python · FastAPI · Scikit-learn · Streamlit |
| [Price Tracker](https://github.com/adanwilliamdev/price_tracker) | Monitor de preços com alertas por e-mail | Django · Celery · Redis |
| [Gestão de Estoque Inteligente](https://github.com/adanwilliamdev/Sistema-de-Gest-o-de-Estoque-Inteligente) | API de estoque com alertas de estoque mínimo via mensageria | .NET 7 · EF Core · RabbitMQ |
| [Burger & Pizza House](https://github.com/adanwilliamdev/Burger-Pizza-House) | Gestão para pizzarias e hamburguerias, com baixa automática de estoque | Node.js · Express · Angular · SQLite |

## ~/stack

```
no dia a dia:  Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, Docker, Linux, Git
também uso:    Java/Spring Boot, TypeScript/Next.js, GitHub Actions, Zabbix, PRTG
já usei:       .NET, Node.js (Express), RabbitMQ
estudando:     Kubernetes, AWS, OpenTelemetry, Microsserviços, CI/CD
```

## ~/jornada

```
2020 → 2026   Analista de TI N2/N3 · Conectv
              Ambiente crítico para ISP, alta disponibilidade e SLA.
              Monitoramento de mais de 12.500 clientes, resolução de incidentes,
              runbooks (MTTR -20%) e automação de processos.

2025 → hoje   Desenvolvimento de software · projetos e formação
              Backend com Python e Java; projetos publicados aqui no GitHub.
```

## ~/formacao

**Graduação:** Análise e Desenvolvimento de Sistemas · UniFatecie (2025 – 2027)

| Certificação | Instituição |
| --- | --- |
| Python para Análise e Automação de Dados | Accenture |
| Banco de Dados: Oracle PL/SQL | Instituto Federal do RS |
| Java com Inteligência Artificial / Java AI Copilot | Itaú · CI&T / DIO |
| AI-900: Fundamentos de IA no Azure | Fundação Bradesco |

## ~/contato

[LinkedIn](https://www.linkedin.com/in/awosantos/) · [Portfólio](https://adanwilliamdev.github.io/) · adan.william.dev@gmail.com
