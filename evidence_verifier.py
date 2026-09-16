import json
import time
from urllib.parse import urlparse

from dotenv import load_dotenv
from composio import Composio

load_dotenv()
composio = Composio()

SAMPLE = {
    "Otter AI": ["otter.ai"],
    "NotebookLM": ["google.com", "notebooklm.google.com"],
    "Twenty": ["twenty.com"],
    "Attio": ["attio.com"],
    "Lark/Larksuite": ["larksuite.com", "open.larksuite.com"],
    "Zoho Cliq": ["zoho.com"],
    "Intercom": ["intercom.com"],
    "Gorgias": ["gorgias.com"],
    "Vercel": ["vercel.com"],
    "Snowflake": ["snowflake.com"],
    "Shopify": ["shopify.dev", "shopify.com"],
    "fanbasis": ["fanbasis.com"],
    "Plaid": ["plaid.com"],
    "Paygent Connect (NMI-powered)": ["nmi.com", "paygentconnect.com"],
    "GoHighLevel": ["gohighlevel.com"],
    "Threads": ["developers.facebook.com", "threads.net"],
    "Harvest": ["getharvest.com"],
    "Notion": ["notion.com"],
    "Waterfall.io": ["waterfall.io"],
    "MrScraper": ["mrscraper.com"],
}


def extract_urls(obj):
    urls = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and key.lower() in ("url", "uri", "link"):
                if value.startswith(("http://", "https://")):
                    urls.append(value)
            else:
                urls.extend(extract_urls(value))

    elif isinstance(obj, list):
        for item in obj:
            urls.extend(extract_urls(item))

    return urls


def get_domain(url):
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def is_official(url, domains):
    domain = get_domain(url)

    return any(
        domain == d or domain.endswith("." + d)
        for d in domains
    )


def get_answer(response):
    try:
        return response.get("data", {}).get("answer", "")
    except Exception:
        return ""


def classify_evidence(response, urls, domains):
    answer = get_answer(response).lower()

    official_urls = [
        url for url in urls
        if is_official(url, domains)
    ]

    if not answer:
        return "No MCP evidence"

    # ---------------------------------------------------------
    # 1. Explicit negative statements about THIS product
    # ---------------------------------------------------------

    negative_patterns = [
        "does not provide an official",
        "does not provide official",
        "doesn't provide an official",
        "does not currently provide an official",
        "does not currently provide official",
        "no official mcp server",
        "no official model context protocol server",
        "no native mcp server",
        "not an official mcp server",
        "not officially supported",
        "not officially provide",
    ]

    has_negative = any(
        pattern in answer
        for pattern in negative_patterns
    )

    # ---------------------------------------------------------
    # 2. Explicit third-party/community-only statements
    # ---------------------------------------------------------

    third_party_patterns = [
        "third-party",
        "third party",
        "community-developed",
        "community developed",
        "community-maintained",
        "community maintained",
        "unofficial",
        "not affiliated with",
        "not endorsed by",
    ]

    has_third_party = any(
        pattern in answer
        for pattern in third_party_patterns
    )

    # If the product itself is explicitly negative,
    # that takes priority over MCP belonging to another
    # product/company.
    if has_negative:
        if has_third_party:
            return "Third-party MCP only"
        return "No MCP support"

    # ---------------------------------------------------------
    # 3. Explicit first-party MCP support
    # ---------------------------------------------------------

    official_patterns = [
        "provides an official, first-party",
        "provides official, first-party",
        "provides official first-party",
        "official, first-party model context protocol",
        "official, first-party mcp server",
        "official first-party mcp server",
        "official mcp server",
        "official model context protocol server",
        "native mcp server",
        "native mcp implementation",
        "native model context protocol",
        "official mcp support",
        "first-party mcp support",
        "supports mcp",
        "support for the model context protocol",
        "support for mcp",
        "mcp support",
        "provides mcp support",
        "provides an mcp server",
        "provides an official mcp server",
        "hosts its own remote mcp server",
        "official connection",
        "official mcp connection",
    ]

    has_official_claim = any(
        pattern in answer
        for pattern in official_patterns
    )

    # Official support requires both:
    #   - an explicit first-party relationship
    #   - first-party source evidence
    if has_official_claim and official_urls:
        return "Official MCP support"

    # ---------------------------------------------------------
    # 4. Community/third-party MCP without official support
    # ---------------------------------------------------------

    if has_third_party:
        return "Third-party MCP only"

    # ---------------------------------------------------------
    # 5. MCP mentioned, but relationship is unclear
    # ---------------------------------------------------------

    if "model context protocol" in answer or "mcp" in answer:
        return "No MCP evidence"

    return "No MCP evidence"


results = []

for i, (name, domains) in enumerate(SAMPLE.items(), 1):
    print(f"[{i}/20] Checking {name}...")

    queries = [
        f'"{name}" "Model Context Protocol" official',
        f'"{name}" "MCP server" official',
        f'"{name}" MCP integration official',
    ]

    all_urls = []
    classifications = []

    for query in queries:
        try:
            response = composio.tools.execute(
                slug="COMPOSIO_SEARCH_WEB",
                arguments={"query": query},
                version="20260903_00"
            )

            urls = extract_urls(response)
            all_urls.extend(urls)

            classification = classify_evidence(
                response,
                urls,
                domains
            )

            classifications.append(classification)

        except Exception as e:
            print("  Search error:", e)

        time.sleep(0.5)

    # Strongest evidence wins.
    if "Official MCP support" in classifications:
        verdict = "Official MCP support"

    elif "Third-party MCP only" in classifications:
        verdict = "Third-party MCP only"

    else:
        verdict = "No MCP support"

    results.append({
        "app": name,
        "mcp_verdict": verdict,
        "queries_run": len(queries),
        "official_evidence_urls": list(
            dict.fromkeys(
                url
                for url in all_urls
                if is_official(url, domains)
            )
        ),
    })

    print("  ->", verdict)


with open(
    "evidence_verification_results.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\nEvidence-aware verification complete.")
print("Saved to evidence_verification_results.json")