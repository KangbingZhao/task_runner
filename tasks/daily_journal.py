import os
import requests
import datetime
from dotenv import load_dotenv

def run():
    load_dotenv()
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    if not NOTION_TOKEN or not DATABASE_ID:
        print("Missing NOTION_TOKEN or DATABASE_ID")
        return

    today = datetime.date.today().isoformat()
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": f"日记 {today}"}}]
            },
            "日期": {
                "date": {"start": today}
            }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "今天的感受"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": []}
            }
        ]
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    print(response.status_code, response.text)
