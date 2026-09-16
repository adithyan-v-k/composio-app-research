from dotenv import load_dotenv
from composio import Composio
import json

load_dotenv()
c = Composio()

apps = ["NotebookLM", "Twenty", "Threads"]

for app in apps:
    print("\n###", app)

    response = c.tools.execute(
        slug="COMPOSIO_SEARCH_WEB",
        arguments={
            "query": f'"{app}" "Model Context Protocol" official'
        },
        version="20260903_00"
    )

    print(json.dumps(response, indent=2, ensure_ascii=False)[:12000])