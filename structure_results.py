import json
import re

with open("research_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)


def find_matches(text, terms):
    text_lower = text.lower()
    found = []

    for term in terms:
        if term.lower() in text_lower:
            found.append(term)

    return found


def classify_auth(text):
    matches = find_matches(text, [
        "OAuth 2.0", "OAuth2", "API key", "Bearer Token",
        "Bearer", "Basic Auth", "JWT", "HMAC"
    ])

    if len(matches) == 0:
        return ["Unknown"]

    return matches


def classify_api(text):
    matches = find_matches(text, [
        "REST", "GraphQL", "SDK", "CLI", "webhook", "MCP"
    ])

    if len(matches) == 0:
        return ["Unknown"]

    return matches


def classify_access(text):
    t = text.lower()

    if "contact sales" in t or "contact your sales" in t:
        return "Contact sales"
    if "enterprise only" in t or "enterprise plan" in t:
        return "Enterprise only"
    if "admin approval" in t or "administrator approval" in t:
        return "Admin approval"
    if "partner approval" in t:
        return "Partner approval"
    if "paid plan" in t or "paid plans" in t:
        return "Paid plan required"
    if "free trial" in t or "trial" in t:
        return "Self-serve trial"
    if "self-serve" in t or "self serve" in t:
        return "Self-serve free"

    return "Unknown"


def classify_mcp(text):
    t = text.lower()

    if "mcp" not in t:
        return "Unknown"

    negative = [
        "no official evidence",
        "no official mcp",
        "official mcp support is no",
        "does not support mcp",
        "does not officially support mcp",
        "mcp is not supported",
        "without mcp support",
        "no mcp support"
    ]

    if any(x in t for x in negative):
        return "No"

    positive = [
        "official mcp support exists",
        "official mcp support is available",
        "officially supported via mcp",
        "officially supports mcp",
        "supports the model context protocol",
        "mcp is officially supported",
        "official mcp server"
    ]

    if any(x in t for x in positive):
        return "Yes"

    return "Unknown"


def extract_blocker(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    keywords = [
        "blocker",
        "difficult",
        "requires",
        "permission",
        "permissions",
        "scope",
        "approval",
        "rate limit",
        "rate-limit",
        "plan",
        "security",
        "complex"
    ]

    for sentence in sentences:
        if any(k in sentence.lower() for k in keywords):
            return sentence.strip()

    return "No specific blocker identified."


structured = []

for item in results:
    answer = item.get("answer") or ""

    sentences = re.split(r'(?<=[.!?])\s+', answer.strip())
    description = sentences[0].strip() if sentences else ""

    structured.append({
        "name": item["name"],
        "category": item["category"],
        "website": item["website"],
        "description": description,
        "auth_methods": classify_auth(answer),
        "access_model": classify_access(answer),
        "api_surface": classify_api(answer),
        "mcp": classify_mcp(answer),
        "buildability": "See research evidence; requires verification.",
        "blocker": extract_blocker(answer),
        "evidence_urls": [
            c.get("url")
            for c in item.get("citations", [])
            if isinstance(c, dict) and c.get("url")
        ],
        "raw_answer": answer
    })


with open("structured_results.json", "w", encoding="utf-8") as f:
    json.dump(structured, f, indent=2, ensure_ascii=False)

print("Structured records:", len(structured))
print("Saved to structured_results.json")