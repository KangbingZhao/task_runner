import os
import requests
import datetime
from core.utils import load_env

def run():
    load_env()
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    TEMPLATE_ID = os.getenv("NOTION_TEMPLATE_ID")
    if not NOTION_TOKEN or not DATABASE_ID or not TEMPLATE_ID:
        print("Missing NOTION_TOKEN, DATABASE_ID or NOTION_TEMPLATE_ID")
        return

    def page_exists(date_str, headers, database_id):
        query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
        query_payload = {
            "filter": {
                "property": "Date",
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

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    for offset in range(3):  # 创建当天及后续两天
        target_date = (datetime.date.today() + datetime.timedelta(days=offset)).isoformat()

        if page_exists(target_date, headers, DATABASE_ID):
            print(f"{target_date} 的日记已存在，跳过创建。")
            continue

        data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": f"🌤 Daily Reflection - {target_date}"}}]
                },
                "Date": {
                    "date": {"start": target_date}
                }
            },
            "template_id": TEMPLATE_ID
        }

        try:
            response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"{target_date} 页面创建失败: {e}")
        else:
            print(f"{target_date} 页面创建成功:", response.json().get("url"))

if __name__ == "__main__":
    run()