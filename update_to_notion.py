from notion_client import Client
import os
import json
import datetime
import pytz

def upload_to_notion(papers_info, notion_api, notion_db_id):
    notion = Client(auth=notion_api)
    database_id = notion_db_id

    for paper in papers_info:
        paper_id = paper["paper"]["id"]
        paper_url = f"https://huggingface.co/papers/{paper_id}"
        
        page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Title": {"title": [{"text": {"content": paper["translation_title"]}}]},
                "Update_date": {"date": {"start": paper["paper"]["publishedAt"]}},
                "Keyword": {
                    "multi_select": [{"name": item} for item in paper["keywords"]]
                },
                "Upvote": {
                    "rich_text": [{"type": "text", "text": {"content": str(paper["paper"]["upvotes"])}}]
                },
                "Link": {"url": paper_url}
            },
            children=[
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": paper["paper"]["title"]}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "한국어 요약 ✍🏼"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": paper["translation_summary"]}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "요약 원문 👀"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": paper["paper"]["summary"].replace("\n"," ")}}]
                    }
                }
            ]
        )


def main():
    
    # 어제 날짜 문자열 생성
    yesterday = datetime.datetime.now(pytz.timezone("Asia/Seoul")) - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    
    output_file = os.path.join('hf-daily-paper-ko-gpt', f"{yesterday_str}_paper_ko.json")
    with open("hf-daily-paper-ko-gpt/2024-12-16_paper_ko.json", "r", encoding="utf-8") as f:
        papers_info = json.load(f)

    notion_api = os.getenv('NOTION_API_KEY')
    notion_db_id = os.getenv('NOTION_DB_ID')

    print(f"notion_api: {notion_api}")
    print(f"notion_db_id: {notion_db_id}")

    for i in range(0, len(papers_info), 10):
        print(f"Uploading {i} to {i+10} papers to Notion")
        upload_to_notion(papers_info[i : i + 10], notion_api, notion_db_id)

if __name__ == "__main__":
    main()
