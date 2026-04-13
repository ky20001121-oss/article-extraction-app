import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_send_line():
    # 1. 鍵の読み込み
    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('USER_ID')

    print("自動化テストを開始します...")

    # 2. ブラウザ起動（ヘッドレスモード）
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    
    # テストとしてGoogleを開く
    driver.get("https://www.google.com")
    page_title = driver.title
    driver.quit()

    # 3. LINEへ強制送信
    message = f"【ついに成功！】\n自動化システムが正常に起動しました。\n取得したタイトル: {page_title}\n\nこれが届いたら、接続設定は完璧です！"
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {line_token}"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("💡LINE送信に成功しました！スマホをチェック！")
    else:
        print(f"❌LINE送信エラー: {response.text}")

if __name__ == "__main__":
    test_send_line()
