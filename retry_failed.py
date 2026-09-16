import json
import time
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

composio = Composio()

with open("research_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

failed = [r for r in results if not r["successful"]]

print(f"Retrying {len(failed)} failed apps...")

for item in failed:
    name = item["name"]
    category = item["category"]
    website = item["website"]

    print(f"\nRetrying {name}...")

    query = f"""
Research the app "{name}" in the "{category}" category.

Official website: {website}

Find factual evidence for:
1. One-line product description
2. API authentication methods
3. API access model: self-serve, trial, paid, approval, contact sales, enterprise, or unknown
4. API surface: REST, GraphQL, SDKs, CLI, webhooks
5. Official MCP support: yes, no, or unknown
6. Main practical integration blocker
7. Official evidence URLs

Prioritize official developer, API, authentication,
pricing/developer-plan, and MCP documentation.
Do not invent information.
Return a concise factual answer with citations.
"""

    success = False

    for attempt in range(1, 4):
        try:
            result = composio.tools.execute(
                "COMPOSIO_SEARCH_WEB",
                arguments={"query": query},
                dangerously_skip_version_check=True,
            )

            if result.get("successful"):
                item["successful"] = True
                item["answer"] = result.get("data", {}).get("answer")
                item["citations"] = result.get("data", {}).get("citations", [])
                item["error"] = None
                success = True

                print(f"Success on attempt {attempt}")
                break

            print(f"Attempt {attempt} failed.")

        except Exception as e:
            print(f"Attempt {attempt} error: {e}")

        if attempt < 3:
            wait = 2 ** attempt
            print(f"Waiting {wait} seconds...")
            time.sleep(wait)

    if not success:
        print(f"Still failed: {name}")

    time.sleep(2)

with open("research_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

successful = sum(r["successful"] is True for r in results)
failed_count = len(results) - successful

print("\nRetry complete.")
print("Successful:", successful)
print("Failed:", failed_count)
print("Saved to research_results.json")