import json
import time
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

composio = Composio()

with open("apps.json", "r", encoding="utf-8") as f:
    apps = json.load(f)

results = []

for i, app in enumerate(apps, start=1):
    name = app["name"]
    category = app["category"]
    website = app["website"]

    print(f"[{i}/100] Researching {name}...")

    query = f"""
Research the app "{name}" in the "{category}" category.

Official website: {website}

Find factual evidence for these fields:

1. description:
   One concise sentence describing the product.

2. auth_methods:
   How developers authenticate API requests.
   Examples: OAuth2, API Key, Bearer Token, Basic Auth, JWT,
   HMAC, or Multiple.

3. access_model:
   Is API access self-serve, trial-based, paid-plan required,
   admin approval, partner approval, contact-sales, enterprise-only,
   or unknown?

4. api_surface:
   Identify whether the platform provides REST, GraphQL, SDKs,
   CLI, webhooks, or other developer interfaces.

5. mcp:
   State whether official MCP support exists:
   yes, no, or unknown.
   Only say yes when there is official evidence.

6. buildability:
   Give a short factual assessment of what would make integration
   straightforward or difficult.

7. blocker:
   Identify the main practical integration blocker, if any.

Use official developer/API/authentication documentation whenever
possible. Do not invent information.

Return a concise factual answer with citations/evidence URLs.
"""

    try:
        result = composio.tools.execute(
            "COMPOSIO_SEARCH_WEB",
            arguments={"query": query},
            dangerously_skip_version_check=True,
        )

        results.append({
            "name": name,
            "category": category,
            "website": website,
            "successful": result.get("successful"),
            "answer": result.get("data", {}).get("answer"),
            "citations": result.get("data", {}).get("citations", []),
            "error": result.get("error"),
        })

    except Exception as e:
        results.append({
            "name": name,
            "category": category,
            "website": website,
            "successful": False,
            "answer": None,
            "citations": [],
            "error": str(e),
        })

    time.sleep(1)

with open("research_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nResearch complete.")
print("Saved to research_results.json")
print("Successful:", sum(r["successful"] is True for r in results))
print("Failed:", sum(r["successful"] is not True for r in results))