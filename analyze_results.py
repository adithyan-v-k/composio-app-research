import json
from collections import Counter, defaultdict

with open("structured_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 70)
print("100-APP RESEARCH ANALYSIS")
print("=" * 70)

# ---------------------------------------------------------
# Category breakdown
# ---------------------------------------------------------

categories = defaultdict(list)

for app in data:
    categories[app["category"]].append(app)

print("\nCATEGORY COUNTS")
print("-" * 70)

for category, apps in categories.items():
    print(f"{category}: {len(apps)} apps")


# ---------------------------------------------------------
# Access model
# ---------------------------------------------------------

access = Counter(
    app.get("access_model", "Unknown")
    for app in data
)

print("\nACCESS MODEL")
print("-" * 70)

for key, value in access.most_common():
    print(f"{key}: {value}")


# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------

auth = Counter()

for app in data:
    value = app.get("auth_methods", "Unknown")

    if isinstance(value, list):
        for item in value:
            auth[item] += 1
    else:
        auth[value] += 1

print("\nAUTHENTICATION METHODS")
print("-" * 70)

for key, value in auth.most_common():
    print(f"{key}: {value}")


# ---------------------------------------------------------
# API surface
# ---------------------------------------------------------

api = Counter()

for app in data:
    value = app.get("api_surface", [])

    if isinstance(value, list):
        for item in value:
            api[item] += 1
    elif isinstance(value, str):
        api[value] += 1

print("\nAPI SURFACE")
print("-" * 70)

for key, value in api.most_common():
    print(f"{key}: {value}")


# ---------------------------------------------------------
# MCP
# ---------------------------------------------------------

mcp = Counter()

for app in data:
    value = app.get("mcp", "Unknown")
    mcp[value] += 1

print("\nMCP CLASSIFICATION")
print("-" * 70)

for key, value in mcp.most_common():
    print(f"{key}: {value}")


# ---------------------------------------------------------
# Buildability
# ---------------------------------------------------------

build = Counter()

for app in data:
    value = app.get("buildability", "Unknown")
    build[value] += 1

print("\nBUILDABILITY")
print("-" * 70)

for key, value in build.most_common():
    print(f"{key}: {value}")


# ---------------------------------------------------------
# Category-level patterns
# ---------------------------------------------------------

print("\nCATEGORY PATTERNS")
print("=" * 70)

for category, apps in categories.items():

    print(f"\n{category}")
    print("-" * 70)

    category_access = Counter(
        app.get("access_model", "Unknown")
        for app in apps
    )

    category_mcp = Counter(
        app.get("mcp", "Unknown")
        for app in apps
    )

    print("Access:", dict(category_access))
    print("MCP:", dict(category_mcp))


# ---------------------------------------------------------
# Apps with blockers
# ---------------------------------------------------------

print("\nBUILDABILITY BLOCKERS / NOTES")
print("=" * 70)

for app in data:

    verdict = str(app.get("buildability", "")).lower()

    if "blocked" in verdict or "limited" in verdict or "gated" in verdict:
        print(
            f"- {app.get('app')}: "
            f"{app.get('buildability')}"
        )


# ---------------------------------------------------------
# Save machine-readable summary
# ---------------------------------------------------------

summary = {
    "total_apps": len(data),
    "categories": {
        category: len(apps)
        for category, apps in categories.items()
    },
    "access_model": dict(access),
    "authentication": dict(auth),
    "api_surface": dict(api),
    "mcp": dict(mcp),
    "buildability": dict(build),
}

with open(
    "analysis_summary.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        summary,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\n" + "=" * 70)
print("Analysis complete.")
print("Saved to analysis_summary.json")
print("=" * 70)