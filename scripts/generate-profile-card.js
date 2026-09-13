#!/usr/bin/env node
/**
 * Gera UM ÚNICO card SVG vertical com todas as informações do perfil:
 * Sobre, Sinais do GitHub, Projetos, Stack e Certificações.
 * Salva em assets/profile-card.svg
 */

const USERNAME = (process.env.GITHUB_USERNAME || "").replace(/[^\x21-\x7E]/g, "");
const TOKEN = (process.env.GH_TOKEN || "").replace(/[^\x21-\x7E]/g, "");

if (TOKEN.length < 10) { console.error("GH_TOKEN inválido."); process.exit(1); }
if (!USERNAME) { console.error("Defina GITHUB_USERNAME."); process.exit(1); }

const REST_HEADERS = {
  Authorization: `Bearer ${TOKEN}`,
  Accept: "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
  "User-Agent": `${USERNAME}-profile-card`,
};
const GRAPHQL_HEADERS = {
  Authorization: `Bearer ${TOKEN}`,
  "Content-Type": "application/json",
  "User-Agent": `${USERNAME}-profile-card`,
};

async function restGet(url) {
  const res = await fetch(url, { headers: REST_HEADERS });
  if (!res.ok) throw new Error(`GET ${url} -> ${res.status}`);
  return res.json();
}
async function restGetAllPages(url) {
  let results = [], page = 1;
  for (;;) {
    const sep = url.includes("?") ? "&" : "?";
    const data = await restGet(`${url}${sep}per_page=100&page=${page}`);
    results = results.concat(data);
    if (data.length < 100) break;
    page++;
  }
  return results;
}
async function graphql(query, variables) {
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST", headers: GRAPHQL_HEADERS,
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors) throw new Error(`GraphQL: ${JSON.stringify(json.errors)}`);
  return json.data;
}

// ---------- Coleta de dados ----------

async function getUser() { return restGet(`https://api.github.com/users/${USERNAME}`); }

async function getOwnRepos() {
  const all = await restGetAllPages(`https://api.github.com/users/${USERNAME}/repos?type=owner`);
  return all.filter(r => !r.fork);
}

async function getLanguageSpectrum(repos) {
  const totals = {};
  const chunkSize = 8;
  for (let i = 0; i < repos.length; i += chunkSize) {
    const chunk = repos.slice(i, i + chunkSize);
    const results = await Promise.all(chunk.map(r =>
      restGet(`https://api.github.com/repos/${USERNAME}/${r.name}/languages`).catch(() => ({}))
    ));
    for (const langs of results) {
      for (const [l, b] of Object.entries(langs)) totals[l] = (totals[l] || 0) + b;
    }
  }
  const total = Object.values(totals).reduce((a, b) => a + b, 0) || 1;
  return Object.entries(totals)
    .map(([lang, b]) => ({ lang, pct: (b / total) * 100 }))
    .sort((a, b) => b.pct - a.pct)
    .slice(0, 6);
}

async function getSearchCount(q) {
  const d = await restGet(`https://api.github.com/search/issues?q=${encodeURIComponent(q)}&per_page=1`);
  return d.total_count || 0;
}

async function getContributionData(createdAt) {
  const query = `
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }`;
  const start = new Date(createdAt), now = new Date();
  const allDays = [], totals = { commits: 0, contributions: 0 };
  let ws = new Date(start);
  while (ws < now) {
    let we = new Date(ws);
    we.setFullYear(we.getFullYear() + 1);
    if (we > now) we = now;
    const data = await graphql(query, { login: USERNAME, from: ws.toISOString(), to: we.toISOString() });
    const cc = data.user.contributionsCollection;
    totals.commits += cc.totalCommitContributions;
    totals.contributions += cc.contributionCalendar.totalContributions;
    for (const w of cc.contributionCalendar.weeks) {
      for (const d of w.contributionDays) allDays.push(d);
    }
    ws = we;
  }
  allDays.sort((a, b) => new Date(a.date) - new Date(b.date));

  let longest = 0, running = 0, runStart = null, longestRange = null;
  for (const d of allDays) {
    if (d.contributionCount > 0) {
      if (running === 0) runStart = d.date;
      running++;
      if (running > longest) { longest = running; longestRange = [runStart, d.date]; }
    } else running = 0;
  }

  let current = 0, currentStart = null;
  for (let i = allDays.length - 1; i >= 0; i--) {
    const d = allDays[i];
    if (d.contributionCount > 0) { current++; currentStart = d.date; }
    else if (i === allDays.length - 1) continue;
    else break;
  }

  return {
    ...totals,
    totalContributions: totals.contributions,
    currentStreak: current,
    currentStreakStart: currentStart,
    longestStreak: longest,
    longestStreakRange: longestRange,
    firstDay: allDays[0]?.date,
  };
}

async function getPRCounts() {
  const [opened, merged, reviewed] = await Promise.all([
    getSearchCount(`type:pr author:${USERNAME}`),
    getSearchCount(`type:pr author:${USERNAME} is:merged`),
    getSearchCount(`type:pr reviewed-by:${USERNAME} -author:${USERNAME}`),
  ]);
  return { opened, merged, reviewed };
}

// ---------- Constantes visuais ----------

const LANG_COLORS = {
  JavaScript: "#f1e05a", TypeScript: "#3178c6", HTML: "#e34c26", CSS: "#563d7c",
  Python: "#59a5e0", Java: "#b07219", PHP: "#4F5D95", "C#": "#178600",
  Vue: "#41b883", Astro: "#ff5a03", Shell: "#89e051", Dockerfile: "#384d54",
};
const FALLBACK = ["#ff4757", "#b3102a", "#ff8787", "#8a6a6a", "#e0cccc", "#5c1a1a"];
const colorFor = (lang, i) => LANG_COLORS[lang] || FALLBACK[i % FALLBACK.length];
const esc = s => String(s)
  .replace(/&/g, "&amp;")
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;")
  .replace(/'/g, "&apos;");
const fmtDate = iso => iso
  ? new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
  : "";

// ---------- Renderização ----------

function renderSVG({ user, stars, prs, issues, contrib, spectrum }) {
  const W = 900;
  const H = 1620;
  const name = (user.name || user.login).trim();

  const headerH = 260;
  const signalsY = headerH + 20;
  const signalsH = 380;
  const contribY = signalsY + signalsH + 20;
  const contribH = 200;
  const projectsY = contribY + contribH + 20;
  const projectsH = 420;
  const stackY = projectsY + projectsH + 20;
  const stackH = 260;

  // Spectrum bar
  const spectrumBar = (() => {
    let x = 492; const barW = 356, y = signalsY + 58;
    return spectrum.map((s, i) => {
      const w = (s.pct / 100) * barW;
      const rect = `<rect x="${x.toFixed(1)}" y="${y}" width="${w.toFixed(1)}" height="10" fill="${colorFor(s.lang, i)}" />`;
      x += w; return rect;
    }).join("\n");
  })();

  const spectrumLegend = spectrum.map((s, i) => {
    const col = i % 2 === 0 ? 492 : 700;
    const row = signalsY + 92 + Math.floor(i / 2) * 26;
    return `<circle cx="${col}" cy="${row - 5}" r="5" fill="${colorFor(s.lang, i)}" />
            <text x="${col + 14}" y="${row}" class="legend">${esc(s.lang)} ${s.pct.toFixed(2)}%</text>`;
  }).join("\n");

  const statsRows = [
    ["Total Stars Earned:", stars],
    ["Total Commits:", contrib.commits],
    ["Total PRs:", prs.opened],
    ["Total PRs Merged:", prs.merged],
    ["Total PRs Reviewed:", prs.reviewed],
    ["Total Issues:", issues],
  ].map((row, i) => `
    <text x="52" y="${signalsY + 64 + i * 26}" class="stat-label">${esc(row[0])}</text>
    <text x="440" y="${signalsY + 64 + i * 26}" text-anchor="end" class="stat-value">${esc(row[1])}</text>
  `).join("\n");

  const projects = [
    { name: "OrbNOC", desc: "NOC de monitoramento de rede em tempo real", stack: "Next.js · Node.js · PostgreSQL" },
    { name: "AutoCare", desc: "ERP para oficinas mecânicas", stack: "Java 21 · Spring Boot · React" },
    { name: "Ticketing System", desc: "Reserva de ingressos de alta concorrência", stack: "Java · Spring Boot · Redis" },
    { name: "Itaú Java AI Order System", desc: "Pedidos com design patterns + IA de voz", stack: "Java · Spring AI · OpenAI" },
  ];
  const projectRows = projects.map((p, i) => {
    const y = projectsY + 60 + i * 80;
    return `
      <text x="52" y="${y}" class="proj-name">${esc(p.name)}</text>
      <text x="52" y="${y + 22}" class="proj-desc">${esc(p.desc)}</text>
      <text x="52" y="${y + 44}" class="proj-stack">${esc(p.stack)}</text>
    `;
  }).join("\n");

  const stackItems = [
    "Java", "Spring Boot", "Node.js", "Python", "React", "Angular", "Vue",
    "TypeScript", "PostgreSQL", "Redis", "Docker", "Git",
  ];
  const stackBadges = stackItems.map((item, i) => {
    const col = i % 6;
    const row = Math.floor(i / 6);
    const x = 52 + col * 140;
    const y = stackY + 70 + row * 36;
    const w = item.length * 8 + 20;
    return `
      <rect x="${x}" y="${y - 18}" width="${w}" height="26" rx="13" fill="#2a0d0d" stroke="#3a1414" />
      <text x="${x + w / 2}" y="${y}" text-anchor="middle" class="badge-text" font-size="11">${esc(item)}</text>
    `;
  }).join("\n");

  const certs = [
    "CI&T — Java AI Copilot · DIO · 53h",
    "Itaú — Java with AI · DIO · 45h",
  ];
  const certRows = certs.map((c, i) => `
    <text x="52" y="${stackY + 170 + i * 24}" class="cert-text">• ${esc(c)}</text>
  `).join("\n");

  // Fallback robusto para evitar "undefined"
  const totalContrib = contrib.totalContributions ?? contrib.contributions ?? 0;

  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" font-family="'Segoe UI', Helvetica, Arial, sans-serif">
  <style>
    .bg { fill: #060404; }
    .panel { fill: #120909; stroke: #3a1414; stroke-width: 1; }
    .title { fill: #f5efef; font-size: 32px; font-weight: 800; }
    .subtitle { fill: #a35a5a; font-size: 13px; letter-spacing: 2px; }
    .section-title { fill: #ff4757; font-size: 16px; font-weight: 700; }
    .stat-label { fill: #c9adad; font-size: 13px; }
    .stat-value { fill: #f7f0f0; font-size: 13px; font-weight: 700; }
    .legend { fill: #ddc9c9; font-size: 12px; }
    .big-number { fill: #ffffff; font-size: 40px; font-weight: 800; }
    .big-label { fill: #ff6b6b; font-size: 13px; font-weight: 700; }
    .big-sub { fill: #8a6a6a; font-size: 11px; }
    .proj-name { fill: #ff4757; font-size: 17px; font-weight: 700; }
    .proj-desc { fill: #e0cccc; font-size: 13px; }
    .proj-stack { fill: #8a6a6a; font-size: 11px; font-style: italic; }
    .badge-text { fill: #f0dcdc; font-weight: 600; }
    .cert-text { fill: #c9adad; font-size: 13px; }
    .divider { stroke: #3a1414; stroke-width: 1; }
  </style>

  <rect class="bg" width="${W}" height="${H}" rx="16" />

  <!-- ===== SEÇÃO 1: HEADER / SOBRE ===== -->
  <text x="${W / 2}" y="56" text-anchor="middle" class="title">${esc(name)}</text>
  <text x="${W / 2}" y="84" text-anchor="middle" class="subtitle">FULL STACK DEVELOPER · JAVA · SPRING BOOT · REACT</text>

  <text x="52" y="140" class="stat-label" font-size="14">
    Profissional de TI com +5 anos em infraestrutura e operações, em transição para desenvolvimento de software.
  </text>
  <text x="52" y="164" class="stat-label" font-size="14">
    Foco em backend com Java e Spring Boot, construindo APIs REST, microsserviços e integrações.
  </text>
  <text x="52" y="188" class="stat-label" font-size="14">
    Frontend em React para fechar o ciclo full stack.
  </text>

  <line x1="32" y1="${headerH - 10}" x2="${W - 32}" y2="${headerH - 10}" class="divider" />

  <!-- ===== SEÇÃO 2: SINAIS DO GITHUB ===== -->
  <text x="32" y="${signalsY + 24}" class="section-title">📊 Sinais do GitHub</text>

  <rect class="panel" x="32" y="${signalsY + 40}" width="420" height="200" rx="12" />
  <text x="52" y="${signalsY + 64}" class="stat-label" font-weight="700">${esc(name)}'s Signal</text>
  ${statsRows}

  <rect class="panel" x="472" y="${signalsY + 40}" width="396" height="200" rx="12" />
  <text x="492" y="${signalsY + 64}" class="stat-label" font-weight="700">Code Spectrum</text>
  ${spectrumBar}
  ${spectrumLegend}

  <!-- ===== SEÇÃO 3: CONTRIBUIÇÕES ===== -->
  <rect class="panel" x="32" y="${contribY}" width="836" height="${contribH}" rx="12" />
  <text x="180" y="${contribY + 70}" text-anchor="middle" class="big-number">${totalContrib}</text>
  <text x="180" y="${contribY + 96}" text-anchor="middle" class="big-label">Total Contributions</text>
  <text x="180" y="${contribY + 116}" text-anchor="middle" class="big-sub">${fmtDate(contrib.firstDay)} - Present</text>

  <line x1="310" y1="${contribY + 30}" x2="310" y2="${contribY + contribH - 30}" class="divider" />
  <circle cx="450" cy="${contribY + 80}" r="44" fill="none" stroke="#ff4757" stroke-width="3" />
  <text x="450" y="${contribY + 92}" text-anchor="middle" class="big-number" font-size="34">${contrib.currentStreak}</text>
  <text x="450" y="${contribY + 130}" text-anchor="middle" class="big-label">Current Streak</text>
  <text x="450" y="${contribY + 150}" text-anchor="middle" class="big-sub">${fmtDate(contrib.currentStreakStart)} - Present</text>

  <line x1="590" y1="${contribY + 30}" x2="590" y2="${contribY + contribH - 30}" class="divider" />
  <text x="720" y="${contribY + 70}" text-anchor="middle" class="big-number">${contrib.longestStreak}</text>
  <text x="720" y="${contribY + 96}" text-anchor="middle" class="big-label">Longest Streak</text>
  <text x="720" y="${contribY + 116}" text-anchor="middle" class="big-sub">${
    contrib.longestStreakRange
      ? `${fmtDate(contrib.longestStreakRange[0])} - ${fmtDate(contrib.longestStreakRange[1])}`
      : ""
  }</text>

  <!-- ===== SEÇÃO 4: PROJETOS ===== -->
  <text x="32" y="${projectsY + 24}" class="section-title">🏆 Projetos em Destaque</text>
  <rect class="panel" x="32" y="${projectsY + 40}" width="836" height="${projectsH - 40}" rx="12" />
  ${projectRows}

  <!-- ===== SEÇÃO 5: STACK + CERTIFICAÇÕES ===== -->
  <text x="32" y="${stackY + 24}" class="section-title">💻 Tech Stack &amp; Certificações</text>
  <rect class="panel" x="32" y="${stackY + 40}" width="836" height="${stackH - 40}" rx="12" />
  ${stackBadges}
  <line x1="52" y1="${stackY + 150}" x2="${W - 52}" y2="${stackY + 150}" class="divider" />
  <text x="52" y="${stackY + 170}" class="stat-label" font-weight="700" font-size="12">Certificações:</text>
  ${certRows}

  <text x="${W / 2}" y="${H - 16}" text-anchor="middle" class="big-sub">Atualizado automaticamente via GitHub Actions</text>
</svg>`;
}

// ---------- Main ----------

(async () => {
  const fs = await import("node:fs/promises");
  console.log(`Coletando dados de @${USERNAME}...`);
  const user = await getUser();
  const repos = await getOwnRepos();
  const stars = repos.reduce((s, r) => s + r.stargazers_count, 0);

  const [spectrum, prs, issues, contrib] = await Promise.all([
    getLanguageSpectrum(repos),
    getPRCounts(),
    getSearchCount(`type:issue author:${USERNAME}`),
    getContributionData(user.created_at),
  ]);

  const svg = renderSVG({ user, stars, prs, issues, contrib, spectrum });
  await fs.mkdir("assets", { recursive: true });
  await fs.writeFile("assets/profile-card.svg", svg, "utf8");
  console.log("assets/profile-card.svg gerado com sucesso.");
})().catch(err => { console.error(err); process.exit(1); });