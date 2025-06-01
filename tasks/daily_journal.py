import os
import requests
import datetime
from core.utils import load_env

def run():
    load_env()
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    if not NOTION_TOKEN or not DATABASE_ID:
        print("Missing NOTION_TOKEN or DATABASE_ID")
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

    def get_template_content(template_id, headers):
        url = f"https://api.notion.com/v1/blocks/{template_id}/children"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("results", [])

    def append_template_to_page(page_id, template_content, headers):
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        data = {"children": template_content}
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()

    def get_template_properties(template_id, headers):
        url = f"https://api.notion.com/v1/pages/{template_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        properties = response.json().get("properties", {})
        # 过滤掉只读属性
        filtered_properties = {
            key: value for key, value in properties.items()
            if key not in ["created_time", "last_edited_time", "created_by", "last_edited_by"]
        }
        return filtered_properties

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    TEMPLATE_ID = os.getenv("NOTION_TEMPLATE_ID")
    if not TEMPLATE_ID:
        print("Missing NOTION_TEMPLATE_ID")
        return

    for offset in range(3):  # 创建当天及后续两天
        target_date = (datetime.date.today() + datetime.timedelta(days=offset)).isoformat()

        if page_exists(target_date, headers, DATABASE_ID):
            print(f"{target_date} 的日记已存在，跳过创建。")
            continue

        # 获取模板的 properties
        template_properties = get_template_properties(TEMPLATE_ID, headers)

        # 自定义的 properties
        custom_properties = {
            "Name": {
                "title": [{"text": {"content": f"🌤 Daily Reflection - {target_date}"}}]
            },
            "Date": {
                "date": {"start": target_date}
            }
        }

        # 合并模板 properties 和自定义 properties
        merged_properties = {**template_properties, **custom_properties}

        data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": merged_properties
        }

        try:
            response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
            response.raise_for_status()
            new_page_id = response.json().get("id")

            # 获取模板内容并追加到新页面
            template_content = get_template_content(TEMPLATE_ID, headers)
            append_template_to_page(new_page_id, template_content, headers)

        except requests.exceptions.RequestException as e:
            print(f"{target_date} 页面创建失败: {e}")
        else:
            print(f"{target_date} 页面创建成功:", response.json().get("url"))

if __name__ == "__main__":
    run()