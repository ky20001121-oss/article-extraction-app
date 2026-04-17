import os
import requests
import xml.etree.ElementTree as ET

def scrape_rss():
    # 1. 環境変数からLINEの認証情報を取得（セキュリティ対策：非機能要件）
    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('USER_ID')

    # 2. 取得先のURL（Qiitaのトレンド記事RSS）
    # RSSはデータ構造が定義されているため、サイトのデザイン変更に強い（疎結合）
    rss_url = "https://qiita.com/popular-items/feed"
    
    print(f"記事の抽出を開始します: {rss_url}")
    new_items = []

    try:
        # 3. データの取得
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status() # エラーがあればここで例外を出す

        # 4. XML形式のデータを解析、見やすいように切り取りする
        root = ET.fromstring(response.content)
        
        # Atom形式のXML名前空間を定義
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # 記事タイトルとリンクを最大5件抽出
        for entry in root.findall('atom:entry', ns)[:5]:
            title = entry.find('atom:title', ns).text
            link = entry.find('atom:link', ns).attrib['href']
            new_items.append(f"📖 {title}\n🔗 {link}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    # 5. LINEに通知を送信
    if new_items:
        message = "【記事抽出アプリ】本日の注目IT記事をお届けします！\n\n" + "\n\n".join(new_items)
        send_line(line_token, user_id, message)
        print(f"成功: {len(new_items)}件の記事を送信しました。")
    else:
        print("記事が見つかりませんでした。")

def send_line(token, to, text):
    """LINE Messaging APIを使ってプッシュ通知を送信する関数"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "to": to,
        "messages": [{"type": "text", "text": text}]
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"LINE API応答ステータス: {res.status_code}")

if __name__ == "__main__":
    scrape_rss()
