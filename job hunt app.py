import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_and_search():
    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('USER_ID')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=chrome_options)
    
    # 制限の厳しい求人サイトではなく、Googleで「那覇 エンジニア 求人」を検索
    # これなら高確率で情報を取得できます
    search_url = "https://www.google.com/search?q=%E9%82%A3%E8%A6%87+%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2+%E6%B1%82%E4%BA%BA"
    driver.get(search_url)
    page_title = driver.title
    driver.quit()

    # 強制的にLINEを送るメッセージ
    message = f"【動作確認：成功】\nGoogleへの接続に成功しました！\n検索結果：{page_title}\n\nこのメッセージが届いていれば、LINEとの連携は100%成功です。"
    
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
        print("LINEへメッセージを送信しました！スマホを確認してください。")
    else:
        print(f"LINE送信失敗: {response.text}")

if __name__ == "__main__":
    test_and_search()
