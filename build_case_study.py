import json
import html
from pathlib import Path
from datetime import datetime

BASE = Path(".")

with open("structured_results.json", "r", encoding="utf-8") as f:
    apps = json.load(f)

with open("analysis_summary.json", "r", encoding="utf-8") as f:
    summary = json.load(f)

total = len(apps)
categories = sorted(set(a.get("category", "Unknown") for a in apps))

def get(a, *keys, default="Unknown"):
    for k in keys:
        v = a.get(k)
        if v not in (None, "", [], {}):
            return v
    return default

def txt(v):
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    if isinstance(v, dict):
        return ", ".join(f"{k}: {v}" for k, v in v.items())
    return str(v)

def esc(v):
    return html.escape(txt(v))

def evidence(a):
    value = get(a, "evidence_urls", "citations", "sources", "urls", default=[])
    result = []

    if isinstance(value, list):
        for x in value:
            if isinstance(x, dict):
                u = x.get("url") or x.get("uri") or x.get("link")
                if u:
                    result.append(str(u))
            elif str(x).startswith(("http://", "https://")):
                result.append(str(x))
    elif isinstance(value, str) and value.startswith(("http://", "https://")):
        result.append(value)

    return list(dict.fromkeys(result))

rows = []

for i, a in enumerate(apps, 1):
    ev = evidence(a)

    links = " ".join(
        f'<a href="{html.escape(u, quote=True)}" target="_blank">Source</a>'
        for u in ev[:3]
    ) or "—"

    rows.append(f"""
    <tr data-category="{esc(get(a, 'category'))}"
        data-search="{esc((txt(get(a,'app','name')) + ' ' + txt(get(a,'category')) + ' ' + txt(get(a,'description','summary'))).lower())}">
        <td>{i}</td>
        <td><strong>{esc(get(a,'app','name'))}</strong></td>
        <td>{esc(get(a,'category'))}</td>
        <td>{esc(get(a,'description','one_line_description','summary'))}</td>
        <td>{esc(get(a,'auth_methods','authentication','auth'))}</td>
        <td>{esc(get(a,'access_model','access'))}</td>
        <td>{esc(get(a,'api_surface','api','api_surface_breadth'))}</td>
        <td>{esc(get(a,'mcp'))}</td>
        <td>{esc(get(a,'buildability','buildability_verdict','verdict'))}</td>
        <td>{links}</td>
    </tr>
    """)

category_cards = ""

for c in categories:
    count = sum(1 for a in apps if get(a, "category") == c)
    category_cards += f"""
    <div class="card">
        <div class="big">{count}</div>
        <div>{esc(c)}</div>
    </div>
    """

access = summary.get("access_model", {})
auth = summary.get("authentication", {})
api = summary.get("api_surface", {})
mcp = summary.get("mcp", {})

def stats(data):
    return "".join(
        f"<div class='statrow'><span>{esc(k)}</span><b>{v}</b></div>"
        for k, v in data.items()
    )

html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Composio 100-App Research</title>

<style>
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #08111f;
    color: #eef5ff;
    line-height: 1.5;
}}

.container {{
    max-width: 1200px;
    margin: auto;
    padding: 40px 24px;
}}

.hero {{
    padding: 90px 24px;
    background: #0d1b2e;
}}

h1 {{
    font-size: 64px;
    margin: 10px 0;
}}

h2 {{
    font-size: 36px;
    margin-top: 0;
}}

.subtitle {{
    color: #a9bbcf;
    font-size: 20px;
    max-width: 800px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}}

.card, .panel {{
    background: #102238;
    border: 1px solid #223b58;
    border-radius: 14px;
    padding: 22px;
}}

.big {{
    font-size: 38px;
    font-weight: bold;
    color: #63b3ff;
}}

.statrow {{
    display: flex;
    justify-content: space-between;
    padding: 9px 0;
    border-bottom: 1px solid #223b58;
    color: #b8c8d9;
}}

.statrow b {{
    color: white;
}}

.two {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}}

section {{
    padding: 60px 0;
    border-top: 1px solid #1d334c;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}}

th {{
    background: #162c45;
    padding: 12px;
    text-align: left;
    position: sticky;
    top: 0;
}}

td {{
    padding: 11px;
    border-bottom: 1px solid #223b58;
    vertical-align: top;
    color: #c8d6e5;
}}

a {{
    color: #63b3ff;
}}

.controls {{
    display: flex;
    gap: 12px;
    margin-bottom: 18px;
}}

input, select {{
    background: #102238;
    color: white;
    border: 1px solid #34506e;
    padding: 12px;
    border-radius: 8px;
}}

input {{
    width: 320px;
}}

.table {{
    overflow: auto;
    max-height: 700px;
    border: 1px solid #223b58;
    border-radius: 12px;
}}

.note {{
    background: #16283b;
    border-left: 4px solid #ffd166;
    padding: 18px;
}}

@media(max-width:800px) {{
    .grid, .two {{
        grid-template-columns: 1fr 1fr;
    }}

    h1 {{
        font-size: 44px;
    }}
}}

@media(max-width:500px) {{
    .grid, .two {{
        grid-template-columns: 1fr;
    }}

    input {{
        width: 100%;
    }}
}}
</style>
</head>

<body>

<div class="hero">
<div class="container">
<div>COMPOSIO TAKE-HOME · RESEARCH + AUTOMATION</div>
<h1>100 Apps.<br>One Integration Map.</h1>
<p class="subtitle">
A systematic research pipeline covering authentication, access models,
API surfaces, MCP availability, buildability constraints and evidence
across 100 applications in 10 categories.
</p>
</div>
</div>

<section>
<div class="container">
<h2>Executive Summary</h2>

<div class="grid">
<div class="card">
<div class="big">{total}</div>
Apps researched
</div>

<div class="card">
<div class="big">{len(categories)}</div>
Categories
</div>

<div class="card">
<div class="big">100%</div>
Research records completed
</div>

<div class="card">
<div class="big">20</div>
Verification sample
</div>
</div>
</div>
</section>

<section>
<div class="container">
<h2>Research Coverage</h2>
<div class="grid">
{category_cards}
</div>
</div>
</section>

<section>
<div class="container">
<h2>What the Data Shows</h2>

<div class="two">

<div class="panel">
<h3>Access Model</h3>
{stats(access)}
</div>

<div class="panel">
<h3>Authentication</h3>
{stats(auth)}
</div>

<div class="panel">
<h3>API Surface</h3>
{stats(api)}
</div>

<div class="panel">
<h3>MCP Classification</h3>
{stats(mcp)}
</div>

</div>
</div>
</section>

<section>
<div class="container">
<h2>Cross-App Findings</h2>

<div class="two">

<div class="panel">
<h3>Authentication is fragmented</h3>
<p>
OAuth, API keys, bearer tokens and vendor-specific schemes appear
across the ecosystem. Integration logic therefore needs
authentication-aware handling.
</p>
</div>

<div class="panel">
<h3>Access can be the real constraint</h3>
<p>
APIs may be technically available while production use still
depends on paid plans, trials, enterprise relationships,
approval or sales contact.
</p>
</div>

<div class="panel">
<h3>REST dominates</h3>
<p>
REST is the most common API surface in the dataset. GraphQL,
SDKs, CLIs and webhooks appear as complementary surfaces.
</p>
</div>

<div class="panel">
<h3>MCP evidence needs provenance</h3>
<p>
Search results can surface third-party implementations or generic
MCP references. Explicit first-party product-level evidence is
therefore stronger than keyword matching alone.
</p>
</div>

</div>
</div>
</section>

<section>
<div class="container">
<h2>Verification Experiment</h2>

<div class="two">

<div class="panel">
<h3>First automated pass</h3>
<div class="big">25%</div>
<p>5 / 20 matched the initial human-reviewed labels.</p>
</div>

<div class="panel">
<h3>Improved pass</h3>
<div class="big">90%</div>
<p>18 / 20 matched the corrected human-reviewed labels.</p>
</div>

</div>

<br>

<div class="note">
The benchmark applies only to the fixed 20-app verification sample,
not to all 100 applications. The experiment showed that explicit
first-party MCP evidence is more reliable than broad keyword matching.
</div>
</div>
</section>

<section>
<div class="container">
<h2>Research Methodology</h2>

<div class="two">

<div class="panel">
<h3>1 · Discover</h3>
<p>
Use Composio Search for product-specific research covering APIs,
authentication, access, MCP and developer documentation.
</p>
</div>

<div class="panel">
<h3>2 · Structure</h3>
<p>
Normalize the results into comparable fields for all 100 apps.
</p>
</div>

<div class="panel">
<h3>3 · Verify</h3>
<p>
Review a stratified 20-app sample against first-party evidence.
</p>
</div>

<div class="panel">
<h3>4 · Analyze</h3>
<p>
Aggregate the dataset to identify cross-category patterns and
integration constraints.
</p>
</div>

</div>
</div>
</section>

<section>
<div class="container">
<h2>100-App Research Dataset</h2>

<div class="controls">
<input id="search" placeholder="Search apps...">

<select id="category">
<option value="">All categories</option>
{"".join(f'<option value="{html.escape(c)}">{html.escape(c)}</option>' for c in categories)}
</select>
</div>

<div class="table">
<table>
<thead>
<tr>
<th>#</th>
<th>App</th>
<th>Category</th>
<th>Description</th>
<th>Auth</th>
<th>Access</th>
<th>API</th>
<th>MCP</th>
<th>Buildability</th>
<th>Evidence</th>
</tr>
</thead>

<tbody id="appTable">
{"".join(rows)}
</tbody>

</table>
</div>

</div>
</section>

<footer>
<div class="container">
Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}
<br>
Composio 100-App Research Case Study
</div>
</footer>

<script>
const search = document.getElementById("search");
const category = document.getElementById("category");
const rows = Array.from(document.querySelectorAll("#appTable tr"));

function filter() {{
    const q = search.value.toLowerCase();
    const c = category.value;

    rows.forEach(row => {{
        const text = row.dataset.search || "";
        const cat = row.dataset.category || "";

        row.style.display =
            (!q || text.includes(q)) &&
            (!c || cat === c)
            ? ""
            : "none";
    }});
}}

search.addEventListener("input", filter);
category.addEventListener("change", filter);
</script>

</body>
</html>
"""

with open("case_study.html", "w", encoding="utf-8") as f:
    f.write(html_doc)

print("=" * 60)
print("CASE STUDY GENERATED")
print("=" * 60)
print(f"Apps included: {total}")
print(f"Categories: {len(categories)}")
print("Output: case_study.html")
print("=" * 60)