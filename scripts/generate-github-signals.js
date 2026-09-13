#!/usr/bin/env node
/**
 * Gera um card SVG "Live GitHub Signals" com dados reais do GitHub
 * (REST API + GraphQL API) e salva em assets/github-signals.svg.
 *
 * Variáveis de ambiente esperadas:
 *   GITHUB_USERNAME  - usuário a analisar (obrigatório)
 *   GH_TOKEN         - token com escopo "read:user" e "public_repo"
 *                       (obrigatório para os dados de contribuições/streak)
 */

const USERNAME = (process.env.GITHUB_USERNAME || "").replace(/[^\x21-\x7E]/g, "");
// .trim() evita erros de "invalid header value" quando o secret foi colado
// com espaço/quebra de linha extra no fim.
// Remove qualquer caractere fora do intervalo ASCII imprimível — cobre
// espaço/quebra de linha nas pontas E também caracteres invisíveis
// colados no meio do valor (ex: copiar de um PDF/app que insere \r ou
// caracteres unicode invisíveis), que fazem o header HTTP ser rejeitado.
const TOKEN = (process.env.GH_TOKEN || "").replace(/[^\x21-\x7E]/g, "");

if (TOKEN.length < 10) {
  console.error(
    "GH_TOKEN parece vazio ou inválido após sanitização. Recrie o secret " +
      "GH_SIGNALS_TOKEN colando o token diretamente (evite copiar de apps " +
      "que possam inserir caracteres invisíveis, como Word/Notas)."
  );
  process.exit(1);
}

if (!USERNAME) {
  console.error("Defina a variável de ambiente GITHUB_USERNAME.");
  process.exit(1);
}
if (!TOKEN) {
  console.error("Defina a variável de ambiente GH_TOKEN (secret do repositório).");
  process.exit(1);
}

const REST_HEADERS = {
  Authorization: `Bearer ${TOKEN}`,
  Accept: "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
  "User-Agent": `${USERNAME}-github-signals`,
};

const GRAPHQL_HEADERS = {
  Authorization: `Bearer ${TOKEN}`,
  "Content-Type": "application/json",
  "User-Agent": `${USERNAME}-github-signals`,
};

async function restGet(url) {
  const res = await fetch(url, { headers: REST_HEADERS });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`GET ${url} -> ${res.status}: ${body}`);
  }
  return res.json();
}

async function restGetAllPages(url) {
  let results = [];
  let page = 1;
  for (;;) {
    const sep = url.includes("?") ? "&" : "?";
    const pageData = await restGet(`${url}${sep}per_page=100&page=${page}`);
    results = results.concat(pageData);
    if (pageData.length < 100) break;
    page += 1;
  }
  return results;
}

async function graphql(query, variables) {
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: GRAPHQL_HEADERS,
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors) {
    throw new Error(`GraphQL error: ${JSON.stringify(json.errors)}`);
  }
  return json.data;
}

// ---------- Coleta de dados ----------

async function getUser() {
  return restGet(`https://api.github.com/users/${USERNAME}`);
}

async function getOwnRepos() {
  const all = await restGetAllPages(
    `https://api.github.com/users/${USERNAME}/repos?type=owner`
  );
  return all.filter((r) => !r.fork);
}

async function getLanguageSpectrum(repos) {
  const totals = {};
  // Limita chamadas em paralelo para não estourar rate limit
  const chunkSize = 8;
  for (let i = 0; i < repos.length; i += chunkSize) {
    const chunk = repos.slice(i, i + chunkSize);
    const results = await Promise.all(
      chunk.map((r) =>
        restGet(`https://api.github.com/repos/${USERNAME}/${r.name}/languages`).catch(
          () => ({})
        )
      )
    );
    for (const langs of results) {
      for (const [lang, bytes] of Object.entries(langs)) {
        totals[lang] = (totals[lang] || 0) + bytes;
      }
    }
  }
  const totalBytes = Object.values(totals).reduce((a, b) => a + b, 0) || 1;
  const spectrum = Object.entries(totals)
    .map(([lang, bytes]) => ({ lang, pct: (bytes / totalBytes) * 100 }))
    .sort((a, b) => b.pct - a.pct)
    .slice(0, 6);
  return spectrum;
}

async function getSearchCount(q) {
  const data = await restGet(
    `https://api.github.com/search/issues?q=${encodeURIComponent(q)}&per_page=1`
  );
  return data.total_count || 0;
}

async function getRecentPublicWork() {
  const events = await restGet(
    `https://api.github.com/users/${USERNAME}/events/public?per_page=30`
  );
  // Ignora eventos no próprio repositório de perfil (username/username),
  // já que os commits automáticos do workflow poluiriam a lista com
  // "Pushed updates to" repetido a cada execução.
  const ownProfileRepo = `${USERNAME}/${USERNAME}`.toLowerCase();
  const lines = [];
  for (const ev of events) {
    if (lines.length >= 5) break;
    const repo = ev.repo.name;
    if (repo.toLowerCase() === ownProfileRepo) continue;
    if (ev.type === "PushEvent") {
      lines.push({ text: "Pushed updates to", repo });
    } else if (ev.type === "CreateEvent" && ev.payload.ref_type === "branch") {
      lines.push({ text: `Created branch \`${ev.payload.ref}\` in`, repo });
    } else if (ev.type === "CreateEvent" && ev.payload.ref_type === "tag") {
      lines.push({ text: `Created tag \`${ev.payload.ref}\` in`, repo });
    } else if (ev.type === "PullRequestEvent") {
      lines.push({ text: `${ev.payload.action === "opened" ? "Opened" : "Updated"} a pull request in`, repo });
    } else if (ev.type === "IssuesEvent") {
      lines.push({ text: `${ev.payload.action === "opened" ? "Opened" : "Updated"} an issue in`, repo });
    } else if (ev.type === "WatchEvent") {
      lines.push({ text: "Starred", repo });
    }
  }
  return lines;
}

// Contribuições ano a ano (o campo contributionsCollection só aceita
// janelas de até 1 ano, então somamos desde a criação da conta).
async function getContributionData(createdAt) {
  const query = `
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
  `;

  // Consulta separada, sem from/to (equivale aos últimos 12 meses da API),
  // só para o número de repositórios contribuídos "no último ano".
  const lastYearQuery = `
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalRepositoriesWithContributedCommits
        }
      }
    }
  `;
  const lastYearData = await graphql(lastYearQuery, { login: USERNAME });
  const contributedLastYear =
    lastYearData.user.contributionsCollection.totalRepositoriesWithContributedCommits;

  const start = new Date(createdAt);
  const now = new Date();
  const allDays = [];
  const totals = {
    commits: 0,
    issues: 0,
    prs: 0,
    prReviews: 0,
    contributedLastYear,
    contributions: 0,
  };

  let windowStart = new Date(start);
  while (windowStart < now) {
    let windowEnd = new Date(windowStart);
    windowEnd.setFullYear(windowEnd.getFullYear() + 1);
    if (windowEnd > now) windowEnd = now;

    const data = await graphql(query, {
      login: USERNAME,
      from: windowStart.toISOString(),
      to: windowEnd.toISOString(),
    });
    const cc = data.user.contributionsCollection;
    totals.commits += cc.totalCommitContributions;
    totals.issues += cc.totalIssueContributions;
    totals.prs += cc.totalPullRequestContributions;
    totals.prReviews += cc.totalPullRequestReviewContributions;
    totals.contributions += cc.contributionCalendar.totalContributions;

    for (const week of cc.contributionCalendar.weeks) {
      for (const day of week.contributionDays) {
        allDays.push(day);
      }
    }

    windowStart = windowEnd;
  }

  // Ordena por data e calcula streak atual / maior streak
  allDays.sort((a, b) => new Date(a.date) - new Date(b.date));
  let longest = 0;
  let running = 0;
  let longestRange = null;
  let runStart = null;
  for (const day of allDays) {
    if (day.contributionCount > 0) {
      if (running === 0) runStart = day.date;
      running += 1;
      if (running > longest) {
        longest = running;
        longestRange = [runStart, day.date];
      }
    } else {
      running = 0;
    }
  }

  let current = 0;
  let currentStart = null;
  for (let i = allDays.length - 1; i >= 0; i -= 1) {
    const day = allDays[i];
    if (day.contributionCount > 0) {
      current += 1;
      currentStart = day.date;
    } else if (i === allDays.length - 1) {
      // hoje ainda sem contribuição registrada, não quebra a streak
      continue;
    } else {
      break;
    }
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

// ---------- Renderização SVG ----------

const LANG_COLORS = {
  JavaScript: "#f1e05a",
  TypeScript: "#3178c6",
  HTML: "#e34c26",
  CSS: "#563d7c",
  Python: "#59a5e0",
  Java: "#b07219",
  PHP: "#4F5D95",
  "C#": "#178600",
  Vue: "#41b883",
  Astro: "#ff5a03",
  Shell: "#89e051",
  Dockerfile: "#384d54",
};
const FALLBACK_COLORS = ["#ff4757", "#b3102a", "#ff8787", "#8a6a6a", "#e0cccc", "#5c1a1a"];

function colorFor(lang, idx) {
  return LANG_COLORS[lang] || FALLBACK_COLORS[idx % FALLBACK_COLORS.length];
}

function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function fmtDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function renderSVG({ user, stars, prs, issues, contrib, spectrum, recent }) {
  const W = 900;
  const H = 820;
  const name = (user.name || user.login).trim();

  const spectrumBar = (() => {
    let x = 492;
    const barW = 356;
    const y = 190;
    const segs = spectrum.map((s, i) => {
      const w = (s.pct / 100) * barW;
      const rect = `<rect x="${x.toFixed(1)}" y="${y}" width="${w.toFixed(1)}" height="10" rx="0" fill="${colorFor(s.lang, i)}" />`;
      x += w;
      return rect;
    });
    return segs.join("\n");
  })();

  const spectrumLegend = spectrum
    .map((s, i) => {
      const col = i % 2 === 0 ? 492 : 700;
      const row = 224 + Math.floor(i / 2) * 26;
      return `
        <circle cx="${col}" cy="${row - 5}" r="5" fill="${colorFor(s.lang, i)}" />
        <text x="${col + 14}" y="${row}" class="legend">${esc(s.lang)} ${s.pct.toFixed(2)}%</text>`;
    })
    .join("\n");

  const statsRows = [
    ["Total Stars Earned:", stars],
    ["Total Commits:", contrib.commits],
    ["Total PRs:", prs.opened],
    ["Total PRs Merged:", prs.merged],
    ["Total PRs Reviewed:", prs.reviewed],
    ["Total Issues:", issues],
    ["Contributed to (last year):", contrib.contributedLastYear],
  ]
    .map(
      (row, i) => `
      <text x="52" y="${196 + i * 26}" class="stat-label">${esc(row[0])}</text>
      <text x="440" y="${196 + i * 26}" text-anchor="end" class="stat-value">${esc(row[1])}</text>`
    )
    .join("\n");

  const recentRows = recent
    .map((r, i) => {
      const y = 656 + i * 28;
      return `
      <text x="48" y="${y}" class="recent-text">${i + 1}. ${esc(r.text)} <tspan class="recent-repo">${esc(r.repo)}</tspan></text>`;
    })
    .join("\n");

  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" font-family="'Segoe UI', Helvetica, Arial, sans-serif">
  <defs>
    <linearGradient id="spectrumFallback" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ff6b6b"/>
      <stop offset="50%" stop-color="#a463f2"/>
      <stop offset="100%" stop-color="#ffd166"/>
    </linearGradient>
  </defs>
  <style>
    .bg { fill: #060404; }
    .panel { fill: #120909; stroke: #3a1414; stroke-width: 1; }
    .title { fill: #f5efef; font-size: 26px; font-weight: 700; }
    .subtitle { fill: #a35a5a; font-size: 11px; letter-spacing: 2px; }
    .badge-text { fill: #f0dcdc; font-size: 12px; font-weight: 600; }
    .panel-title { fill: #ff4757; font-size: 15px; font-weight: 700; }
    .stat-label { fill: #c9adad; font-size: 13px; }
    .stat-value { fill: #f7f0f0; font-size: 13px; font-weight: 700; }
    .legend { fill: #ddc9c9; font-size: 12px; }
    .big-number { fill: #ffffff; font-size: 40px; font-weight: 800; }
    .big-label { fill: #ff6b6b; font-size: 13px; font-weight: 700; }
    .big-sub { fill: #8a6a6a; font-size: 11px; }
    .section-title { fill: #f7f0f0; font-size: 16px; font-weight: 700; }
    .recent-text { fill: #e0cccc; font-size: 13px; }
    .recent-repo { fill: #ff4757; }
    .divider { stroke: #3a1414; stroke-width: 1; }
  </style>

  <rect class="bg" width="${W}" height="${H}" rx="14" />

  <!-- Cabeçalho -->
  <text x="${W / 2}" y="42" text-anchor="middle" class="title">⚡ Live GitHub Signals</text>
  <text x="${W / 2}" y="66" text-anchor="middle" class="subtitle">REAL ACTIVITY · CODE VELOCITY · BUILD CONSISTENCY</text>

  <rect x="${W / 2 - 210}" y="82" width="160" height="24" rx="12" fill="#2a0d0d" />
  <text x="${W / 2 - 130}" y="98" text-anchor="middle" class="badge-text">📡 Live metrics · 4x daily</text>

  <rect x="${W / 2 + 50}" y="82" width="190" height="24" rx="12" fill="#3a1015" />
  <text x="${W / 2 + 145}" y="98" text-anchor="middle" class="badge-text">🤖 Automated pulse · 4x daily</text>

  <!-- Painel de estatísticas -->
  <rect class="panel" x="32" y="132" width="420" height="212" rx="12" />
  <text x="52" y="164" class="panel-title">${esc(name)}'s GitHub Signal</text>
  ${statsRows}

  <!-- Espectro de código -->
  <rect class="panel" x="472" y="132" width="396" height="212" rx="12" />
  <text x="492" y="164" class="panel-title">Code Spectrum</text>
  ${spectrumBar}
  ${spectrumLegend}

  <!-- Contribuições -->
  <rect class="panel" x="32" y="368" width="836" height="200" rx="12" />
  <text x="180" y="440" text-anchor="middle" class="big-number">${contrib.totalContributions}</text>
  <text x="180" y="466" text-anchor="middle" class="big-label">Total Contributions</text>
  <text x="180" y="486" text-anchor="middle" class="big-sub">${fmtDate(contrib.firstDay)} - Present</text>

  <line x1="310" y1="400" x2="310" y2="536" class="divider" />
  <circle cx="450" cy="450" r="44" fill="none" stroke="#ff4757" stroke-width="3" />
  <text x="450" y="462" text-anchor="middle" class="big-number" font-size="34">${contrib.currentStreak}</text>
  <text x="450" y="500" text-anchor="middle" class="big-label">Current Streak</text>
  <text x="450" y="520" text-anchor="middle" class="big-sub">${fmtDate(contrib.currentStreakStart)} - Present</text>

  <line x1="590" y1="400" x2="590" y2="536" class="divider" />
  <text x="720" y="440" text-anchor="middle" class="big-number">${contrib.longestStreak}</text>
  <text x="720" y="466" text-anchor="middle" class="big-label">Longest Streak</text>
  <text x="720" y="486" text-anchor="middle" class="big-sub">${
    contrib.longestStreakRange
      ? `${fmtDate(contrib.longestStreakRange[0])} - ${fmtDate(contrib.longestStreakRange[1])}`
      : ""
  }</text>

  <!-- Trabalho público recente -->
  <text x="32" y="612" class="section-title">🚀 Recent public work</text>
  ${recentRows}

  <text x="${W / 2}" y="${H - 14}" text-anchor="middle" class="big-sub">Atualizado automaticamente via GitHub Actions</text>
</svg>`;
}

// ---------- Execução principal ----------

(async () => {
  const fs = await import("node:fs/promises");

  console.log(`Coletando dados públicos de @${USERNAME}...`);
  const user = await getUser();
  const repos = await getOwnRepos();
  const stars = repos.reduce((sum, r) => sum + r.stargazers_count, 0);

  const [spectrum, prs, issues, contrib, recent] = await Promise.all([
    getLanguageSpectrum(repos),
    getPRCounts(),
    getSearchCount(`type:issue author:${USERNAME}`),
    getContributionData(user.created_at),
    getRecentPublicWork(),
  ]);

  const svg = renderSVG({ user, stars, prs, issues, contrib, spectrum, recent });

  await fs.mkdir("assets", { recursive: true });
  await fs.writeFile("assets/github-signals.svg", svg, "utf8");
  console.log("assets/github-signals.svg gerado com sucesso.");
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
