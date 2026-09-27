"""Build the project pages (tabular/, text/, timeseries/index.html).

Each page shows the assignment info required by section 6.2 (title, data type,
group, members, problem, dataset, notebook / PDF / video links) followed by the
executed notebook rendered in place.

Usage (from the repository root, after re-running a notebook):
    pip install nbconvert
    python tools/build_pages.py

To publish the PDF report or the YouTube video of a part, drop `report.pdf` into
its folder and/or fill in VIDEO_URLS below, then run the script again.
"""
import html
import json
import re
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]
REPO = "trungly-hcmut/CO5177_DataVisualization_Assignment"
GITHUB_BLOB = f"https://github.com/{REPO}/blob/main"

# Paste the YouTube link of each presentation here (Public or Unlisted).
VIDEO_URLS = {
    "tabular": None,
    "text": None,
    "timeseries": None,
}

MEMBERS = [
    ("Ly Minh Trung", "2570349", "Data Scientist", "LT", "var(--lime)"),
    ("Dinh Truong Tue Linh", "2570441", "Data Scientist", "DT", "var(--peach)"),
    ("Nguyen Hoang Nam", "2570261", "Analysis and Visualization", "NH", "var(--blue)"),
]


def fmt_int(x):
    return f"{x:,}"


def tabular_facts(r):
    base, final = r["test"]["Logistic Regression (baseline)"], r["test"]["HGB (tuned) + optimal threshold"]
    return [
        (fmt_int(r["dataset"]["rows_raw"]), f"bookings × {r['dataset']['cols_raw']} columns"),
        (f"{r['dataset']['duplicates'] / r['dataset']['rows_raw']:.1%}", "duplicate rows found and removed"),
        (f"{final['f1']:.3f}", f"test F1 (Logistic Regression baseline {base['f1']:.3f})"),
        (f"{final['roc_auc']:.3f}", f"test ROC-AUC (baseline {base['roc_auc']:.3f})"),
    ]


def text_facts(r):
    comp = r["comparison"]
    tfidf = comp["TF-IDF + Linear SVM (tuned)"]["test macro-F1"]
    return [
        (fmt_int(r["dataset"]["rows_raw"]), "articles crawled by the group"),
        (str(len(r["dataset"]["classes"])), "news sections to predict"),
        (f"{r['test_macro_f1']:.3f}", "test macro-F1 (TF-IDF ⊕ embedding)"),
        (f"+{r['test_macro_f1'] - tfidf:.3f}", f"over TF-IDF alone ({tfidf:.3f})"),
    ]


def timeseries_facts(r):
    test = r["test"]
    final = test[r["final_model"]]
    hz = r["horizon_mae"]
    useful = 0
    for h in sorted(hz, key=int):
        row = hz[h]
        best_base = min(row["Persistence"], row["Climatology"], row["Damped anomaly persistence"])
        if row[r["final_model"]] < best_base - 0.01:
            useful = int(h)
    return [
        (fmt_int(r["dataset"]["days"]), "days of Hanoi weather, 2005–2026"),
        (f"{final['MAE']:.2f} °C", "test MAE, 1 day ahead"),
        (f"{final['skill_vs_persistence']:.1%}", f"lower error than “tomorrow = today” ({test['Persistence']['MAE']:.2f} °C)"),
        (f"{useful} days", "horizon where the model beats every baseline"),
    ]


PARTS = [
    {
        "slug": "tabular", "number": "01", "type": "Tabular", "accent": "var(--lime)",
        "notebook": "G3_Tabular_HotelBooking.ipynb",
        "title": "Predicting hotel booking cancellations",
        "h1": "Will this booking<br><em>be cancelled?</em>",
        "lede": "A classifier that flags risky hotel bookings using only what is known at booking time — "
                "and a close look at two evaluation traps that make scores look far better than they are.",
        "problem": [
            "More than a third of the bookings in this dataset are cancelled. A hotel that sees cancellations coming "
            "can overbook in a controlled way, ask guests to reconfirm, or require a deposit.",
            "We predict <code>is_canceled</code> from booking-time attributes — lead time, sales channel, deposit type, "
            "price, special requests, guest history — compare five models, handle the class imbalance, and pick a "
            "decision threshold that balances missed cancellations against false alarms.",
        ],
        "dataset": [
            ("Source", 'Hotel Booking Demand — Antonio, Almeida &amp; Nunes, <a href="https://doi.org/10.1016/j.dib.2018.11.126" '
                       'target="_blank" rel="noreferrer"><em>Data in Brief</em> (2019)</a>, CC BY 4.0'),
            ("Size", "119,390 bookings × 32 columns, two hotels in Portugal, arrivals Jul 2015 – Aug 2017"),
            ("Target", "<code>is_canceled</code> — 37.0% raw, 27.6% after removing duplicates"),
            ("Challenges", "missing values (company 94%, agent 14%, hidden <code>Undefined</code>), 27.8% duplicates, "
                           "target leakage, outliers (ADR up to 5,400), class imbalance"),
            ("File", '<a href="data/hotel_bookings.csv.gz">data/hotel_bookings.csv.gz</a> (1.1 MB)'),
        ],
        "facts": tabular_facts,
    },
    {
        "slug": "text", "number": "02", "type": "Text", "accent": "var(--peach)",
        "notebook": "G3_Text_VnExpressNews.ipynb",
        "title": "Vietnamese news topic classification",
        "h1": "What is this<br><em>news story about?</em>",
        "lede": "A Vietnamese news-topic classifier trained on headlines and lead paragraphs that we crawled ourselves "
                "from VnExpress — comparing bag-of-words models with a multilingual sentence-embedding model.",
        "problem": [
            "Given only the headline and the two-sentence lead of a Vietnamese article, predict which of 10 newspaper "
            "sections it belongs to: News, World, Business, Sci-Tech, Entertainment, Sports, Law, Education, Health, Travel.",
            "We compare 4 text representations × 4 classifiers, tune the best, test which field carries the signal and "
            "whether more data would help, and compare TF-IDF with a pretrained multilingual encoder "
            "(<code>multilingual-e5-small</code>) used as a frozen feature extractor.",
        ],
        "dataset": [
            ("Source", 'Self-collected from <a href="https://vnexpress.net" target="_blank" rel="noreferrer">VnExpress</a> with '
                       f'<a href="{GITHUB_BLOB}/text/crawler/crawl_vnexpress.py" target="_blank" rel="noreferrer">our crawler</a> '
                       "(requests + BeautifulSoup) on 27 Sep 2026"),
            ("Size", "3,780 articles (3,769 after de-duplication), 10 sections × 12 listing pages"),
            ("Fields", "headline, lead paragraph, dateline, URL, section (= label)"),
            ("Language", "Vietnamese; only headlines and leads are stored (no article bodies), for coursework use"),
            ("File", '<a href="data/vnexpress_news.csv">data/vnexpress_news.csv</a> (1.5 MB)'),
        ],
        "facts": text_facts,
    },
    {
        "slug": "timeseries", "number": "03", "type": "Time series", "accent": "var(--blue)",
        "notebook": "G3_TimeSeries_HanoiWeather.ipynb",
        "title": "Forecasting Hanoi's daily temperature",
        "h1": "How warm will<br><em>Hanoi be tomorrow?</em>",
        "lede": "Forecasting Hanoi's daily mean temperature 1–7 days ahead from 21 years of weather history — "
                "with a close eye on the winter cold surges that make forecasting hard.",
        "problem": [
            "Predict tomorrow's daily mean temperature in Hanoi from today's and past weather, then measure how fast "
            "forecast skill decays up to a week ahead.",
            "Hanoi has a real winter: north-east monsoon cold surges can cut the temperature by 5–10 °C within a day — "
            "exactly the days when a forecast matters most. Models are compared against persistence, climatology and "
            "damped-anomaly baselines on a strictly chronological split.",
        ],
        "dataset": [
            ("Source", '<a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noreferrer">'
                       "Open-Meteo Historical Weather API</a> (ERA5 reanalysis) — weather data by Open-Meteo.com, CC BY 4.0"),
            ("Location", "central Hanoi, 21.03 °N 105.85 °E"),
            ("Size", "7,939 consecutive days (1 Jan 2005 – 26 Sep 2026) × 14 daily variables"),
            ("Split", "train 2005–2021 · validation 2022–2023 · test Jan 2024 – Sep 2026"),
            ("File", '<a href="data/hanoi_weather_daily.csv">data/hanoi_weather_daily.csv</a> (0.6 MB)'),
        ],
        "facts": timeseries_facts,
    },
]


def render_notebook(path):
    """Executed notebook -> HTML fragment (header cell dropped, stderr hidden) + table of contents."""
    nb = nbformat.read(path, as_version=4)
    # The first markdown cell repeats the title / members / contents shown in the page header.
    if nb.cells and nb.cells[0].cell_type == "markdown" and nb.cells[0].source.lstrip().startswith("# "):
        nb.cells = nb.cells[1:]
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = [o for o in cell.get("outputs", []) if not (o.get("output_type") == "stream" and o.get("name") == "stderr")]
    body, _ = HTMLExporter(template_name="basic").from_notebook_node(nb)
    toc = []
    for anchor, inner in re.findall(r'<h2 id="([^"]+)">(.*?)<a class="anchor-link"', body):
        toc.append((anchor, re.sub(r"<[^>]+>", "", inner).strip()))
    return body, toc


def link_button(label, href, cls, note=None, download=False):
    if href is None:
        return f'<span class="button {cls}" aria-disabled="true">{label}<small>{note or "coming soon"}</small></span>'
    extra = " download" if download else ' target="_blank" rel="noreferrer"'
    return f'<a class="button {cls}" href="{href}"{extra}>{label} <span>↗</span></a>'


def build_page(part, index):
    slug = part["slug"]
    folder = ROOT / slug
    results = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    body, toc = render_notebook(folder / part["notebook"])

    nb_path = f"{slug}/{part['notebook']}"
    report = "report.pdf" if (folder / "report.pdf").exists() else None
    buttons = "\n        ".join([
        link_button("Notebook on GitHub", f"{GITHUB_BLOB}/{nb_path}", "button-primary"),
        link_button("PDF report", report, "button-lime"),
        link_button("Video on YouTube", VIDEO_URLS.get(slug), "button-outline"),
    ])
    facts = "\n      ".join(
        f'<div class="fact"><span class="fact-value">{v}</span><span class="fact-label">{html.escape(l)}</span></div>'
        for v, l in part["facts"](results))
    problem = "\n        ".join(f"<p>{p}</p>" for p in part["problem"])
    dataset = "\n          ".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in part["dataset"])
    team = "\n          ".join(
        f'<li><span class="avatar" style="background:{color}">{ini}</span>'
        f"<div><strong>{name}</strong><span>{sid} / {role}</span></div></li>"
        for name, sid, role, ini, color in MEMBERS)
    toc_items = "\n            ".join(f'<li><a href="#{a}">{html.escape(html.unescape(t))}</a></li>' for a, t in toc)
    nav = "\n      ".join(
        f'<a href="../{p["slug"]}/index.html"{" aria-current=\"page\"" if p is part else ""}>{p["type"]}</a>' for p in PARTS)
    prev_p, next_p = PARTS[index - 1], PARTS[(index + 1) % len(PARTS)]

    page = PAGE.format(
        title=html.escape(part["title"]), type=part["type"], number=part["number"], slug=slug,
        description=html.escape(part["lede"]), h1=part["h1"], lede=part["lede"], buttons=buttons, facts=facts,
        problem=problem, dataset=dataset, team=team, toc=toc_items, nav=nav, notebook_file=part["notebook"],
        github_nb=f"{GITHUB_BLOB}/{nb_path}", prev_slug=prev_p["slug"], prev_type=prev_p["type"],
        prev_title=html.escape(prev_p["title"]), next_slug=next_p["slug"], next_type=next_p["type"],
        next_title=html.escape(next_p["title"]), repo=f"https://github.com/{REPO}",
    ).replace("<!--NOTEBOOK-->", body)
    (folder / "index.html").write_text(page, encoding="utf-8")
    print(f"{slug}/index.html  {len(page) / 1e6:.2f} MB  {len(toc)} sections")


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#101514">
  <title>{type}: {title} — G3</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../style.css">
  <link rel="stylesheet" href="../assets/project.css">
</head>
<body class="project-page">
  <div class="noise" aria-hidden="true"></div>
  <header class="site-header">
    <a class="brand" href="../index.html" aria-label="G3 home"><span class="brand-mark">G3</span><span>Signal / Story</span></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu <span>+</span></button>
    <nav class="site-nav" id="site-nav" aria-label="Primary navigation">
      <a href="../index.html#work">All projects</a>
      {nav}
      <a class="nav-cta" href="{repo}" target="_blank" rel="noreferrer">GitHub <span>↗</span></a>
    </nav>
  </header>

  <main id="top">
    <section class="project-hero section-shell">
      <div class="project-kicker"><span class="kicker-index">{number}</span><span class="kicker-type">Data type: {type}</span><span>Group G3</span><span>Semester 261 / 2026–2027</span></div>
      <h1>{h1}</h1>
      <p class="project-lede">{lede}</p>
      <div class="project-actions">
        {buttons}
      </div>
    </section>

    <section class="project-facts section-shell" aria-label="Key numbers">
      {facts}
    </section>

    <section class="project-brief section-shell">
      <div class="brief-block">
        <h2>The problem</h2>
        {problem}
      </div>
      <div class="brief-block">
        <h2>The dataset</h2>
        <dl class="data-list">
          {dataset}
        </dl>
      </div>
      <div class="brief-block brief-team">
        <h2>The team</h2>
        <p class="team-group"><b>Group G3</b> · Nền tảng lập trình cho phân tích và trực quan dữ liệu · Lecturer: Dr. Lê Thành Sách</p>
        <ul class="team-list">
          {team}
        </ul>
      </div>
    </section>

    <section class="notebook-section section-shell" id="notebook">
      <div class="notebook-head">
        <div>
          <h2>The notebook</h2>
          <p>Rendered from <a href="{github_nb}" target="_blank" rel="noreferrer"><code>{notebook_file}</code></a> with all outputs, exactly as executed.</p>
        </div>
        <div class="notebook-tools">
          <a class="button button-outline" href="{notebook_file}" download>Download .ipynb</a>
          <button class="code-toggle" type="button" aria-pressed="false">Hide code</button>
        </div>
      </div>
      <div class="notebook-layout">
        <details class="notebook-toc" open>
          <summary>Contents</summary>
          <ol>
            {toc}
          </ol>
        </details>
        <article class="notebook">
<!--NOTEBOOK-->
        </article>
      </div>
    </section>

    <nav class="project-pager section-shell" aria-label="Other projects">
      <a href="../{prev_slug}/index.html"><small>← {prev_type}</small><span>{prev_title}</span></a>
      <a href="../{next_slug}/index.html"><small>{next_type} →</small><span>{next_title}</span></a>
    </nav>
  </main>

  <footer class="site-footer section-shell"><span>© 2026 Group G3</span><span>Built to make data legible.</span><a href="#top">Back to top ↑</a></footer>
  <script src="../script.js"></script>
  <script>
    (() => {{
      const toggle = document.querySelector('.code-toggle');
      const apply = (hidden) => {{
        document.body.classList.toggle('hide-code', hidden);
        toggle.textContent = hidden ? 'Show code' : 'Hide code';
        toggle.setAttribute('aria-pressed', String(hidden));
      }};
      let saved = false;
      try {{ saved = localStorage.getItem('g3-hide-code') === '1'; }} catch (e) {{}}
      apply(saved);
      toggle.addEventListener('click', () => {{
        const hidden = !document.body.classList.contains('hide-code');
        apply(hidden);
        try {{ localStorage.setItem('g3-hide-code', hidden ? '1' : '0'); }} catch (e) {{}}
      }});

      const toc = document.querySelector('.notebook-toc');
      if (window.matchMedia('(max-width: 1000px)').matches) toc.removeAttribute('open');
      const links = [...toc.querySelectorAll('a')];
      const byId = new Map(links.map((a) => [decodeURIComponent(a.hash.slice(1)), a]));
      const heads = [...document.querySelectorAll('.notebook h2[id]')];
      const spy = new IntersectionObserver((entries) => {{
        entries.forEach((e) => {{
          if (e.isIntersecting) {{
            links.forEach((a) => a.classList.remove('active'));
            byId.get(e.target.id)?.classList.add('active');
          }}
        }});
      }}, {{ rootMargin: '0px 0px -70% 0px' }});
      heads.forEach((h) => spy.observe(h));
    }})();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    for i, part in enumerate(PARTS):
        build_page(part, i)
