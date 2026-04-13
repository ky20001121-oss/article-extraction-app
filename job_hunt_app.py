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
    # サイト側から「ロボット」だと見破られにくくする設定（おまじない）
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # キーワードを「エンジニア」だけに広げ、エリアは沖縄(47)のままにします
    search_url = "https://en-gage.net/user/search/list/?keyword=%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2&area=47"
    
    print(f"検索を開始します: {search_url}")
    driver.get(search_url)
    time.sleep(10)  # 読み込み時間をさらに長く確保

    new_jobs = []
    try:
        # 見出し(h3)を全て取得
        titles = driver.find_elements(By.TAG_NAME, "h3")
        
        for item in titles[:5]:
            text = item.text.strip()
            # 無関係な見出し（メニューなど）を弾くため、文字数やキーワードで軽くフィルタ
            if len(text) > 5: 
                new_jobs.append(f"📌 {text}\n🔗 {search_url}") # ひとまず検索URLを添えて通知
                
    except Exception as e:
        print(f"解析中にエラー: {e}")

    driver.quit()

    if new_jobs:
        message = "【本番通知】沖縄のエンジニア関連情報を取得しました！\n\n" + "\n\n".join(new_jobs)
        send_line(line_token, user_id, message)
        print(f"成功: {len(new_jobs)}件送信しました。")
    else:
        print("依然としてヒットしません。ブラウザの読み込み待機が必要です。")

def send_line(token, to, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": to, "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    scrape_jobs()
