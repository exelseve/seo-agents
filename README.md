# SEO Agents for Claude Code

🇷🇺 [Русская версия](README.ru.md)

A set of 10 specialized SEO subagents for [Claude Code](https://claude.com/claude-code). Each agent is a focused specialist: give it a URL (or a keyword) and it runs its own audit and returns a structured, scored report. They can be spawned individually or in parallel for a full site audit.

## Installation

**Download everything at once** — [ZIP archive](https://github.com/exelseve/seo-agents/archive/refs/heads/main.zip) (no GitHub account needed), or via terminal:

```bash
git clone https://github.com/exelseve/seo-agents.git
cp seo-agents/sb-*.md ~/.claude/agents/
cp -r seo-agents/scripts ~/.claude/skills/seo/scripts   # helper scripts (optional, see below)
```

Copy the `.md` files into either:

- `~/.claude/agents/` — available in every project
- `<your-project>/.claude/agents/` — available in that project only

Then ask Claude Code to use them, e.g. *"run sb-tech-audit and sb-ai-search on https://example.com in parallel"*.

## Helper scripts

The `scripts/` folder ships the Python helpers the agents look for at `~/.claude/skills/seo/scripts/` — a JS-rendering page fetcher, CrUX/PageSpeed API clients, screenshot capture, and the drift-tracking toolchain. They are **optional**: without them every agent except `sb-drift` degrades gracefully to `curl`/WebSearch. `sb-drift` is the only one that requires them (SQLite baseline storage).

To enable them:

```bash
cp -r seo-agents/scripts ~/.claude/skills/seo/scripts
pip install -r ~/.claude/skills/seo/scripts/requirements.txt
playwright install chromium   # for render_page / capture_screenshot
```

| Script | What it does |
|---|---|
| `render_page.py` | Headless Chromium (Playwright) page renderer: executes JavaScript and returns the final DOM, extracted main text, and publication date. The difference between "what the crawler sees without JS" and the rendered page is a core signal for several agents. |
| `fetch_page.py` | Plain HTTP fetcher with realistic headers, redirect tracing, and a Googlebot-UA mode for detecting dynamic rendering. All URL fetches go through SSRF protection. |
| `parse_html.py` | Extracts SEO-critical elements from HTML (title, meta, canonical, headings, JSON-LD, OG tags) as JSON; the parsing backend for drift snapshots. |
| `capture_screenshot.py` | Playwright screenshots per viewport (desktop/mobile) for the visual audit. |
| `pagespeed_check.py` | PageSpeed Insights v5 + CrUX combined report: Lighthouse lab data merged with real-user field data. Needs a Google API key. |
| `crux_history.py` | Core Web Vitals trends: up to 25 weeks of CrUX History API data with per-metric improving/degrading classification. |
| `drift_baseline.py` | Snapshots a page's SEO-critical elements into SQLite (`~/.cache/seo-agents/drift/`) as the "known good" state. |
| `drift_compare.py` | Diffs the live page against the stored baseline: 17 rules across CRITICAL / WARNING / INFO. |
| `drift_history.py` | Timeline of baselines and comparisons for a URL. |
| `drift_report.py` | Renders a comparison result as a severity-coded HTML report. |
| `url_safety.py` | Shared SSRF/DNS-rebinding protection: blocks fetches that resolve to private or reserved IPs. |
| `google_auth.py` | Google API key loader (`~/.config/seo-agents/google-api.json` or `GOOGLE_API_KEY` env var) used by the PageSpeed/CrUX clients. Run `python google_auth.py --setup` for instructions. |

## The agents

| Agent | What it does |
|---|---|
| `sb-tech-audit` | Technical SEO audit across 9 areas: crawlability, indexability, security headers, URL hygiene, mobile, Core Web Vitals risk, structured data presence, rendering model (SSR/CSR), IndexNow. Verdict per category + 0–100 score + prioritized fixes. |
| `sb-content-quality` | Reviews content like a Google quality rater: E-E-A-T scoring (weighted T30/E25/A25/E20), topical depth vs page-type floors, readability, keyword naturalness, AI-citability, and detection of low-effort AI-generated text. |
| `sb-schema-audit` | Everything Schema.org: detects existing JSON-LD/Microdata/RDFa, validates against currently supported rich result types, knows which types are dead (HowTo, SpecialAnnouncement…) and that FAQ rich results are gov/health-only, generates ready-to-paste JSON-LD. |
| `sb-ai-search` | GEO (Generative Engine Optimization): will AI search engines *cite* this page? Checks AI-crawler access in robots.txt, `llms.txt`, passage-level citability (130–170-word extractable answers), authority signals, and per-platform readiness for Google AI Overviews, ChatGPT, Perplexity, Bing Copilot. |
| `sb-sxo` | Answers "why doesn't this page rank?" by reading the SERP backwards: classifies the top-10 results, detects page-type mismatch (the #1 silent killer), derives user stories from SERP signals, scores the page across 7 gap dimensions and 4–7 searcher personas. |
| `sb-performance` | Core Web Vitals diagnosis (LCP / INP / CLS, 2026 thresholds, 75th-percentile rule). Prefers CrUX field data over lab data, falls back through PageSpeed API → Lighthouse → source inspection. Names the specific bottleneck and ranks fixes by impact. |
| `sb-sitemap` | XML sitemap validation (format, 50k limit, dead/redirected/noindexed URLs, lastmod hygiene) and generation. Enforces anti-doorway quality gates: warns at 30+ programmatic location pages, hard-stops at 50+. |
| `sb-visual` | Screenshots pages with Playwright across 4 viewports and audits what users actually see: above-the-fold H1/CTA visibility, mobile tap targets, horizontal scroll, overlapping/clipped elements. |
| `sb-cluster` | Keyword clustering by evidence, not text similarity: pairwise SERP-overlap measurement (shared top-10 URLs), intent classification, hub-and-spoke architecture design, and a complete internal-link adjacency matrix. Outputs `cluster-plan.json` + human-readable summary. |
| `sb-drift` | Version control for on-page SEO: snapshots title/meta/canonical/robots/headings/schema/OG/CWV per URL into SQLite, diffs live state against the baseline with 17 rules across CRITICAL / WARNING / INFO tiers, and routes findings to the right specialist agent. |

## Typical combos

- **Full audit**: `sb-tech-audit` + `sb-content-quality` + `sb-schema-audit` + `sb-ai-search` + `sb-sxo` in parallel, then merge into one report
- **"Rankings dropped"**: `sb-drift` (what changed?) → the specialist it points to
- **New content planning**: `sb-cluster` → write → `sb-content-quality` before publishing
- **Post-deploy check**: `sb-visual` + `sb-performance` + `sb-drift`

## Notes

- Frontmatter (`model`, `maxTurns`, `tools`) is tuned per agent; adjust to taste.
- Agents never fetch user-supplied URLs with raw `requests.get`; they use the safe fetcher when available or plain `curl`.
- Facts baked into the prompts (CWV thresholds, schema deprecation dates, QRG references) are current as of mid-2026.

## License

[MIT](LICENSE)
