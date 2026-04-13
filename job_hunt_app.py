import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def scrape_jobs():
    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('USER_ID')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 検索ワードをURLエンコードしたもの（沖縄 ITエンジニア 求人）
    search_url = "https://www.google.com/search?q=%E6%B2%96%E7%B8%84+IT%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2+%E6%B1%82%E4%BA%BA"
    
    print(f"Google検索を開始: {search_url}")
    new_jobs = []

    try:
        driver.get(search_url)
        time.sleep(5)

        # Googleの検索結果のタイトル（h3タグ）を取得
        items = driver.find_elements(By.TAG_NAME, "h3")
        
        for item in items[:5]:
            text = item.text.strip()
            if text:
                new_jobs.append(f"🔍 {text}")

    except Exception as e:
        print(f"エラー: {e}")
    
    driver.quit()

    if new_jobs:
        message = "【定期調査】沖縄のITエンジニア関連の検索結果です！\n\n" + "\n\n".join(new_jobs)
        send_line(line_token, user_id, message)
        print(f"成功: {len(new_jobs)}件を送信しました。")
    else:
        print("Googleからも情報を取得できませんでした。")

def send_line(token, to, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": to, "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    scrape_jobs()
