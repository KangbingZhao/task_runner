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

    def page_exists(date_str, headers, database_id):
        query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
        query_payload = {
            "filter": {
                "property": "日期",
                "date": {
                    "equals": date_str
                }
            }
        }
        resp = requests.post(query_url, headers=headers, json=query_payload)
        if resp.status_code != 200:
            print(f"查询失败: {resp.status_code}, {resp.text}")
            return False
        results = resp.json().get("results", [])
        return len(results) > 0

    today = datetime.date.today().isoformat()
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    if page_exists(today, headers, DATABASE_ID):
        print(f"{today} 的日记已存在，跳过创建。")
        return

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

    try:
        response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"页面创建失败: {e}")
    else:
        print("页面创建成功:", response.json().get("url"))

if __name__ == "__main__":
    run()