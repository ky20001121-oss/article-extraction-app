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
    driver = webdriver.Chrome(options=chrome_options)
    
    # 検索キーワードを少し広げて「沖縄 IT」などにするとヒットしやすくなります
    search_url = "https://en-gage.net/user/search/list/?keyword=IT%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2&area=47"
    
    print(f"検索を開始します: {search_url}")
    driver.get(search_url)
    time.sleep(7)  # 読み込み時間を少し延長

    new_jobs = []
    # より広い範囲のクラス名（articleやsectionなど）で探すように変更
    try:
        # 求人タイトルの要素を直接探す
        items = driver.find_elements(By.CSS_SELECTOR, "h3")
        
        for item in items[:5]: # 上位5件
            title = item.text.strip()
            if title:
                # リンクは親要素などから探す
                try:
                    link = item.find_element(By.XPATH, "./ancestor::a").get_attribute("href")
                except:
                    link = search_url # リンクが取れない場合は検索結果URLを代用
                
                new_jobs.append(f"📌 {title}\n🔗 {link}")
    except Exception as e:
        print(f"解析中にエラー: {e}")

    driver.quit()

    if new_jobs:
        message = "【本番通知】沖縄のIT求人をピックアップしました！\n\n" + "\n\n".join(new_jobs)
        send_line(line_token, user_id, message)
        print(f"成功: {len(new_jobs)}件送信しました。")
    else:
        print("ヒットしませんでした。キーワードを変えて試す価値があります。")

def send_line(token, to, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": to, "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    scrape_jobs()
