import json
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
from composio import Composio

load_dotenv()
composio = Composio()

with open("verification.json", "r", encoding="utf-8") as f:
    verification = json.load(f)

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
        for k, v in obj.items():
            if isinstance(v, str) and k.lower() in ("url", "uri", "link"):
                if v.startswith(("http://", "https://")):
                    urls.append(v)
            else:
                urls.extend(extract_urls(v))

    elif isinstance(obj, list):
        for item in obj:
            urls.extend(extract_urls(item))

    return urls


def domain(url):
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def official(url, domains):
    d = domain(url)
    return any(
        d == x or d.endswith("." + x)
        for x in domains
    )


results = []

for i, (name, domains) in enumerate(SAMPLE.items(), 1):
    print(f"[{i}/20] Checking {name}...")

    queries = [
        f'"{name}" MCP site:{domains[0]}',
        f'"{name}" "Model Context Protocol" site:{domains[0]}',
        f'"{name}" "MCP server" site:{domains[0]}',
    ]

    all_urls = []
    evidence_found = False

    for query in queries:
        try:
            response = composio.tools.execute(
                slug="COMPOSIO_SEARCH_WEB",
                arguments={"query": query},
                version="20260903_00"
            )

            urls = extract_urls(response)
            all_urls.extend(urls)

            text = json.dumps(
                response,
                ensure_ascii=False
            ).lower()

            strong_mcp_terms = [
                "mcp server",
                "native mcp",
                "mcp support",
                "supports mcp",
                "support for mcp",
                "model context protocol (mcp)",
                "via mcp",
                "connect via mcp",
                "mcp endpoint",
            ]

            mcp_url_evidence = any(
                official(u, domains)
                and any(
                    term in u.lower()
                    for term in [
                        "/mcp",
                        "-mcp",
                        "_mcp",
                        "mcp-server",
                        "mcp_server",
                    ]
                )
                for u in urls
            )

            has_strong_mcp_evidence = (
                any(
                    term in text
                    for term in strong_mcp_terms
                )
                and mcp_url_evidence
            )

            if has_strong_mcp_evidence:
                evidence_found = True

        except Exception as e:
            print("  Search error:", e)

        time.sleep(0.5)

    verdict = "Yes" if evidence_found else "Not confirmed"

    results.append({
        "app": name,
        "improved_mcp": verdict,
        "queries_run": len(queries),
        "official_evidence_urls": list(
            dict.fromkeys(
                u
                for u in all_urls
                if official(u, domains)
            )
        ),
    })

    print("  ->", verdict)


with open(
    "improved_verification_results.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\nImproved verification complete.")
print("Saved to improved_verification_results.json")