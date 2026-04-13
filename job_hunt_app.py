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
    
    # ターゲットを「求人ボックス」の沖縄×エンジニアに変更
    search_url = "https://求人ボックス.com/沖縄県のエンジニアの求人"
    
    print(f"ターゲットを変更して検索開始: {search_url}")
    new_jobs = []

    try:
        driver.get(search_url)
        time.sleep(10) # しっかり読み込み待機

        # 求人タイトルのクラス名を指定（求人ボックスの一般的な構成）
        items = driver.find_elements(By.CSS_SELECTOR, "span.k-p-title, h3, .s-jobTitle")
        
        for item in items[:5]:
            text = item.text.strip()
            if len(text) >= 5:
                new_jobs.append(f"📌 {text}")

    except Exception as e:
        print(f"エラー発生: {e}")
    
    current_title = driver.title
    driver.quit()

    if new_jobs:
        message = "【求人ボックス通知】沖縄のエンジニア求人を検出！\n\n" + "\n\n".join(new_jobs)
        send_line(line_token, user_id, message)
        print(f"成功: {len(new_jobs)}件送信しました。")
    else:
        print(f"取得失敗。現在のページタイトル: {current_title}")

def send_line(token, to, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": to, "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    scrape_jobs()
