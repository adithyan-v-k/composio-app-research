import json
import time
from urllib.parse import urlparse

from dotenv import load_dotenv
from composio import Composio

load_dotenv()

composio = Composio()

with open("structured_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# Official domains for the 61 apps that initially had Unknown MCP status.
OFFICIAL_DOMAINS = {
    "Pylon": ["pylon.com"],
    "LiveAgent": ["liveagent.com"],
    "Plain": ["plain.com"],
    "Help Scout": ["helpscout.com"],
    "Slack": ["slack.com", "api.slack.com"],
    "Twilio": ["twilio.com", "www.twilio.com"],
    "Zoho Cliq": ["zoho.com", "cliq.zoho.com"],
    "Lark/Larksuite": ["larksuite.com", "open.larksuite.com"],
    "Discord": ["discord.com", "discord.dev"],
    "Telegram": ["telegram.org", "core.telegram.org"],
    "WhatsApp Business": ["whatsapp.com", "business.whatsapp.com"],
    "Aircall": ["aircall.io"],
    "Google Ads": ["google.com", "developers.google.com", "ads.google.com"],
    "Meta Ads": ["facebook.com", "developers.facebook.com"],
    "GoHighLevel": ["gohighlevel.com", "help.gohighlevel.com"],
    "Mailchimp": ["mailchimp.com", "developer.mailchimp.com"],
    "Pinterest": ["pinterest.com", "developers.pinterest.com"],
    "Threads": ["threads.net", "developers.facebook.com"],
    "Shopify": ["shopify.com", "shopify.dev"],
    "WooCommerce": ["woocommerce.com", "developer.woocommerce.com"],
    "BigCommerce": ["bigcommerce.com", "developer.bigcommerce.com"],
    "Magento/Adobe Commerce": ["adobe.com", "developer.adobe.com", "magento.com"],
    "Ecwid": ["ecwid.com", "docs.ecwid.com"],
    "Gumroad": ["gumroad.com"],
    "Amazon Selling Partner API": ["amazon.com", "developer.amazonservices.com", "developer-docs.amazon.com"],
    "DataForSEO": ["dataforseo.com"],
    "Ahrefs": ["ahrefs.com"],
    "MrScraper": ["mrscraper.com"],
    "Apify": ["apify.com", "docs.apify.com"],
    "Sherlock": ["sherlockproject.xyz", "github.com"],
    "Waterfall.io": ["waterfall.io"],
    "Clay": ["clay.com"],
    "Supabase": ["supabase.com", "supabase.io"],
    "Snowflake": ["snowflake.com", "docs.snowflake.com"],
    "Datadog": ["datadoghq.com", "docs.datadoghq.com"],
    "Airtable": ["airtable.com", "airtable.com/developers"],
    "Asana": ["asana.com", "developers.asana.com"],
    "Coda": ["coda.io", "coda.io/developers"],
    "Smartsheet": ["smartsheet.com", "developers.smartsheet.com"],
    "Stripe": ["stripe.com", "docs.stripe.com"],
    "Plaid": ["plaid.com", "docs.plaid.com"],
    "Binance": ["binance.com", "developers.binance.com"],
    "Paygent Connect (NMI-powered)": ["paygentconnect.com", "nmi.com"],
    "iPayX": ["ipayx.com"],
    "QuickBooks": ["intuit.com", "developer.intuit.com"],
    "Xero": ["xero.com", "developer.xero.com"],
    "PitchBook": ["pitchbook.com"],
    "NotebookLM": ["notebooklm.google.com", "google.com"],
    "Otter AI": ["otter.ai"],
    "Fathom": ["fathom.video"],
    "higgsfield": ["higgsfield.ai"],
    "YouTube Transcript": ["youtube.com", "developers.google.com"],
}


def extract_urls(obj):
    urls = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in {"url", "uri", "link"} and isinstance(value, str):
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


unknown_apps = [x for x in data if x["mcp"] == "Unknown"]

print(f"Verifying {len(unknown_apps)} apps...")


for i, app in enumerate(unknown_apps, 1):
    name = app["name"]

    official_domains = OFFICIAL_DOMAINS.get(name, [])

    domain_query = " OR ".join(
        f"site:{domain}" for domain in official_domains
    )

    query = (
        f"{name} MCP Model Context Protocol official developer documentation "
        f"{domain_query}"
    )

    print(f"[{i}/{len(unknown_apps)}] Checking {name}...")

    try:
        result = composio.tools.execute(
            slug="COMPOSIO_SEARCH_WEB",
            arguments={"query": query},
            version="20260903_00"
        )

        urls = extract_urls(result)

        official_urls = []

        for url in urls:
            domain = get_domain(url)

            for official_domain in official_domains:
                official_domain = official_domain.replace("www.", "")

                if (
                    domain == official_domain
                    or domain.endswith("." + official_domain)
                ):
                    official_urls.append(url)
                    break

        result_text = json.dumps(
            result, ensure_ascii=False
        ).lower()

        has_mcp_term = (
            "mcp" in result_text
            or "model context protocol" in result_text
        )

        if official_urls and has_mcp_term:
            verification = "Official MCP evidence found"
        elif has_mcp_term:
            verification = "Third-party MCP evidence only"
        else:
            verification = "No MCP evidence found"

        app["mcp_verification"] = verification
        app["verification_query"] = query
        app["verification_official_urls"] = list(
            dict.fromkeys(official_urls)
        )

    except Exception as e:
        app["mcp_verification"] = "Verification failed"
        app["verification_error"] = str(e)

    time.sleep(1)


with open("verified_results.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nVerification complete.")
print("Saved to verified_results.json")