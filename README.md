# Adan William

**Desenvolvedor Java Júnior / Full Stack Júnior** · Disponível para vagas

Passei mais de 5 anos em infraestrutura crítica de provedores de Internet (N2/N3) e hoje construo APIs e sistemas completos com Java / Spring Boot, PostgreSQL e Docker, com foco em regras de negócio, segurança e consistência de dados, levando para o código a visão de disponibilidade e SLA da operação.

- 5+ anos em infra e NOC
- 12,5k+ clientes monitorados
- 11 projetos no GitHub

[GitHub](https://github.com/adanwilliamdev) · [LinkedIn](https://www.linkedin.com/in/awosantos) · [Portfólio](https://adanwilliamdev.github.io/)

Meus projetos têm testes, Docker Compose para subir tudo com um comando e README com instruções para rodar.

## Stack

| Área | Tecnologias |
|---|---|
| Backend | Java 17/21, Spring Boot 3, Spring Security, Spring Data JPA, Hibernate, Spring Cloud Gateway, Spring AI, WebSocket/STOMP, Maven |
| Dados e infra | PostgreSQL, Redis, Flyway, Docker, Docker Compose, GitHub Actions, Git, Linux |
| Frontend | React, TypeScript, Angular, Next.js, Vite, Tailwind CSS, Thymeleaf, Bootstrap |
| Qualidade | JUnit 5, Mockito, Testcontainers, JaCoCo, Swagger/OpenAPI |
| Também usei | Python (FastAPI), Node.js (Express, Prisma) |

## Projetos em destaque

### [AWOS Bank](https://github.com/adanwilliamdev/awosbank)
Internet Banking com dashboard, extrato com filtros e chaves PIX.
- Auditoria append-only: trigger do PostgreSQL bloqueia UPDATE/DELETE e registra também as tentativas que falham
- Testes de concorrência em transferências e Testcontainers com PostgreSQL real
- Cobertura com JaCoCo e CI/CD com GitHub Actions publicando a imagem no GHCR

`Java 17` `Spring Boot` `Spring Security` `PostgreSQL` `Flyway` `Testcontainers` `Docker`

### [Torque Gestão](https://github.com/adanwilliamdev/Torque_Gestao)
Gestão de oficinas: clientes, veículos, orçamentos com aprovação e estoque com movimentações rastreáveis.
- Ordens de serviço com fluxo de estados controlado
- Perfis de acesso: admin, gerente, recepção e mecânico
- Controle de concorrência otimista no estoque
- JWT com refresh token rotativo e CSRF na interface web
- Testes de integração com Testcontainers

`Java 21` `Spring Boot` `Spring Security` `PostgreSQL` `Flyway` `Testcontainers` `Docker`

### [Ticketing System](https://github.com/adanwilliamdev/ticketing-system)
Reservas e pagamentos no estilo Ticketmaster, focado em alta concorrência.
- Lock pessimista no banco e lock distribuído com Redisson/Redis
- Reserva temporária com expiração automática
- Idempotência em pagamentos
- Testes de reserva, expiração, idempotência e falha de gateway

`Java 21` `Spring Boot` `PostgreSQL` `Redis` `Flyway` `Docker` `JUnit 5` `Mockito`

### [OrbNOC](https://github.com/adanwilliamdev/OrbNOC)
Monitoramento de rede em tempo real, nascido da minha rotina de NOC.
- ICMP e TCP: o host só fica offline após N falhas seguidas, sem falsos alarmes
- Painel, mapa e wallboard para TVs de NOC atualizados via WebSocket
- Alertas de queda, recuperação e SLA, com Telegram opcional
- Relatórios de SLA (24h, 7d, 30d) em CSV e Excel; diagnóstico com ping, traceroute, DNS e portas
- Argon2, JWT em cookie httpOnly + SameSite, CSRF por origem e comandos sem shell

`Java 21` `Spring Boot` `Thymeleaf` `PostgreSQL` `WebSocket` `Apache POI` `Docker`

## Outros projetos

| Projeto | Descrição | Tecnologias |
|---|---|---|
| [TaskFlow](https://github.com/adanwilliamdev/task-management) | Gerenciador de tarefas em microsserviços (API Gateway, Eureka, auth, usuários, tarefas e notificações), um banco por serviço e JWT validado localmente. | Spring Cloud, React, Docker Compose |
| [Itaú Java AI Order System](https://github.com/adanwilliamdev/itau-java-ai-order-system) | API de pedidos com 4 padrões de projeto (State, Chain of Responsibility, Strategy, Observer) e comandos de voz via Spring AI. Desafio final do programa Itaú Java AI (DIO). | Java, Spring AI |
| [Burger & Pizza House ERP](https://github.com/adanwilliamdev/Burger-Pizza-House) | ERP para pizzarias e hamburguerias, com pedidos em transação atômica e baixa automática de estoque. | Node.js, Angular, Prisma |
| [Study Planner](https://github.com/adanwilliamdev/study-planner) | Rotina de estudos com matérias, tarefas, cronograma, Pomodoro e notificações em tempo real via WebSocket/STOMP, autenticado por JWT. | Spring Boot, React, Vite |

## IA aplicada

| Projeto | Descrição | Tecnologias |
|---|---|---|
| [Geo-Explorer](https://github.com/adanwilliamdev/Geo-Explorer) | Servidor MCP (Model Context Protocol) em TypeScript com ferramentas para trilhas de aprendizagem, desafios e certificados. Feito no Bootcamp IBM Bob. | TypeScript, MCP |
| [LivroCerto](https://github.com/adanwilliamdev/assistente-virtual-ia) | Assistente de recomendação de livros que só responde com base em uma base de conhecimento própria, com avaliação de métricas. | — |
| [EstudoAtivo-NotebookLM](https://github.com/adanwilliamdev/EstudoAtivo-NotebookLM) | Estudo de finanças pessoais com IA fundamentada em fontes curadas e engenharia de prompt. | — |

## Foco atual

- **Java e Spring Boot:** segurança, testes de integração e mensageria (RabbitMQ/Kafka)
- **CI/CD:** levar o que já uso no AWOS Bank para os demais projetos
- **Time:** contribuir e aprender com profissionais mais experientes

## Contato

[LinkedIn](https://www.linkedin.com/in/awosantos) · [Portfólio](https://adanwilliamdev.github.io/) · [GitHub](https://github.com/adanwilliamdev)
