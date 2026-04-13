import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_jobs():
    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('USER_ID')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 検索条件
    search_url = "https://en-gage.net/user/search/list/?keyword=%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2&area=47"
    
    print(f"検索を開始します: {search_url}")
    new_jobs = []

    try:
        driver.get(search_url)
        
        # 1. ページが読み込まれるまで最大15秒待機
        wait = WebDriverWait(driver, 15)
        # 求人リストの共通クラスまたはh3が現れるのを待つ
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h3")))
        
        # 2. 念のため少し追加待機
        time.sleep(5)

        # 3. 求人タイトルの抽出
        items = driver.find_elements(By.TAG_NAME, "h3")
        for item in items:
            text = item.text.strip()
            # 求人タイトルっぽい長さのものだけ採用
            if len(text) >= 10:
                new_jobs.append(f"📌 {text}")
                if len(new_jobs) >= 5: break

    except Exception as e:
        print(f"エラーが発生しました。詳細はログを確認してください。")
    
    # ★ポイント: 閉じる前にタイトルを保存しておく
    current_title = driver.title
    driver.quit()

    if new_jobs:
        message = "【本番通知】沖縄のエンジニア求人を検出しました！\n\n" + "\n\n".join(new_jobs)
        send_line(line_token, user_id, message)
        print(f"成功: {len(new_jobs)}件送信しました。")
    else:
        print(f"取得できませんでした。サイト名: {current_title}")

def send_line(token, to, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": to, "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    scrape_jobs()
