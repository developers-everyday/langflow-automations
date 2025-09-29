import httpx
from langflow.custom.custom_component.component import Component
from langflow.io import SecretStrInput, StrInput, IntInput, Output
from langflow.schema.data import Data


class NotionAPIComponent(Component):
    display_name = "Notion API"
    description = "Fetch text content from a Notion page or block."
    documentation: str = "https://developers.notion.com/reference/get-block-children"
    icon = "Notion"
    name = "NotionAPI"

    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="Notion API Key",
            info="Your Notion integration secret (starts with `ntn_...`).",
            required=True,
        ),
        StrInput(
            name="block_id",
            display_name="Block/Page ID",
            info="The ID of the page or block to fetch children for.",
            required=True,
        ),
        StrInput(
            name="notion_version",
            display_name="Notion API Version",
            value="2022-06-28",
            required=True,
        ),
        IntInput(
            name="page_size",
            display_name="Page Size",
            value=100,
            info="Maximum number of child blocks to fetch per request.",
        ),
    ]

    outputs = [
        Output(display_name="Text Content", name="data", method="fetch_text"),
    ]

    async def fetch_text(self) -> Data:
        """Fetch children blocks from Notion API and return plain text only."""
        url = f"https://api.notion.com/v1/blocks/{self.block_id}/children?page_size={self.page_size}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.notion_version,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()

                texts = []
                for block in result.get("results", []):
                    rich_text = block.get(block["type"], {}).get("rich_text", [])
                    for t in rich_text:
                        if "plain_text" in t:
                            texts.append(t["plain_text"])

                return Data(data={"text": texts})
            except Exception as e:
                return Data(data={"error": str(e)})
