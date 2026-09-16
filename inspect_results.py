import json

with open(
    "evidence_verification_results.json",
    "r",
    encoding="utf-8"
) as f:
    results = json.load(f)

for item in results:
    print("\n" + "=" * 70)
    print(item["app"])
    print("=" * 70)

    print("VERDICT:", item["mcp_verdict"])

    print("\nOFFICIAL URLS:")
    for url in item.get("official_evidence_urls", []):
        print(" ", url)

    print("\nANSWER:")
    print(item.get("answer", ""))

print("\nInspection complete.")